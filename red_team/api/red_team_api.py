"""
red_team_api.py

FastAPI endpoints for the Red Team.

Flow:

Request
   ↓
Attack Composer
   ↓
Attack DNA
   ↓
Attack Generator
   ↓
Adversarial Transaction
   ↓
Response
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from red_team.composer.attack_composer import AttackComposer
from red_team.generator.attack_generator import AttackGenerator
from red_team.schemas.transaction import Transaction
from red_team.agent.adaptive_attack import AdaptiveAttackEngine
from red_team.agent.feedback_adapter import BlueTeamFeedbackAdapter


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/red-team",
    tags=["Red Team"]
)


# ============================================================
# COMPONENTS
# ============================================================

generator = AttackGenerator()
feedback_adapter = BlueTeamFeedbackAdapter()
composer = AttackComposer()
adaptive_engine = AdaptiveAttackEngine()


# ============================================================
# DATA
# ============================================================

DATA_DIR = Path("simulator/data")


def load_customer_mappings():

    accounts = pd.read_csv(
        DATA_DIR / "accounts.csv"
    )

    cards = pd.read_csv(
        DATA_DIR / "cards.csv"
    )

    account_by_customer = (
        accounts
        .drop_duplicates("customer_id")
        .set_index("customer_id")["account_id"]
        .to_dict()
    )

    card_by_customer = (
        cards
        .drop_duplicates("customer_id")
        .set_index("customer_id")["card_id"]
        .to_dict()
    )

    return (
        account_by_customer,
        card_by_customer,
    )


ACCOUNT_BY_CUSTOMER, CARD_BY_CUSTOMER = (
    load_customer_mappings()
)


# ============================================================
# FRONTEND TRANSACTION REQUEST
# ============================================================

class FrontendTransaction(BaseModel):

    customer_id: str

    amount: float = Field(gt=0)

    merchant_id: str

    device_id: str

    location: str

    beneficiary_id: Optional[str] = None

    payment_method: str

    is_fraud: bool = False

    attack_id: Optional[str] = None


# ============================================================
# ATTACK REQUEST
# ============================================================

class AttackRequest(BaseModel):

    transaction: FrontendTransaction

    attack_id: Optional[str] = None


# ============================================================
# ATTACK RESPONSE
# ============================================================

class AttackResponse(BaseModel):

    attack_id: str

    attack_type: str

    transaction: Transaction


# ============================================================
# ADAPTATION FEEDBACK
# ============================================================

class AdaptationFeedback(BaseModel):

    attack_id: str

    risk_score: float

    decision: str

    detected_signals: list[str]


# ============================================================
# ADAPTATION REQUEST
# ============================================================

class AdaptationRequest(BaseModel):

    transaction: Transaction

    feedback: AdaptationFeedback


# ============================================================
# BUILD COMPLETE TRANSACTION
# ============================================================

def build_complete_transaction(
    request: FrontendTransaction
) -> Transaction:

    customer_id = request.customer_id

    account_id = ACCOUNT_BY_CUSTOMER.get(
        customer_id
    )

    card_id = CARD_BY_CUSTOMER.get(
        customer_id
    )

    if account_id is None:

        raise ValueError(
            f"No account mapping found for customer "
            f"'{customer_id}'."
        )

    if card_id is None:

        raise ValueError(
            f"No card mapping found for customer "
            f"'{customer_id}'."
        )

    transaction_id = (
        f"TX{uuid.uuid4().hex[:10].upper()}"
    )

    timestamp = datetime.now(timezone.utc)

    return Transaction(

        transaction_id=transaction_id,

        customer_id=customer_id,

        account_id=account_id,

        card_id=card_id,

        device_id=request.device_id,

        merchant_id=request.merchant_id,

        beneficiary_id=request.beneficiary_id,

        amount=request.amount,

        currency="INR",

        location=request.location,

        timestamp=timestamp,

        payment_method=request.payment_method,

        is_fraud=request.is_fraud,

        attack_id=request.attack_id,
    )


# ============================================================
# GENERATE ATTACK
# ============================================================

@router.post(
    "/generate",
    response_model=AttackResponse
)
def generate_attack(request: AttackRequest):

    try:

        # ----------------------------------------------------
        # 1. Build complete transaction
        # ----------------------------------------------------

        transaction = build_complete_transaction(
            request.transaction
        )

        # ----------------------------------------------------
        # 2. Select attack
        # ----------------------------------------------------

        if request.attack_id:

            attack = composer.get_attack(
                request.attack_id
            )

        else:

            attack = composer.random_attack()

        # ----------------------------------------------------
        # 3. Generate adversarial transaction
        # ----------------------------------------------------

        adversarial_transaction = generator.generate(
            transaction,
            attack
        )

        # ----------------------------------------------------
        # 4. Return
        # ----------------------------------------------------

        return AttackResponse(

            attack_id=attack.attack_id,

            attack_type=attack.attack_type,

            transaction=adversarial_transaction
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Attack generation failed: {str(e)}"
        )


# ============================================================
# ADAPT ATTACK
# ============================================================

@router.post("/adapt")
def adapt_attack(request: AdaptationRequest):

    try:

        # ----------------------------------------------------
        # 1. Recover original attack
        # ----------------------------------------------------

        base_attack_id = (
            request.feedback.attack_id
            .split("-V")[0]
        )

        attack = composer.get_attack(
            base_attack_id
        )

        # ----------------------------------------------------
        # 2. Adapt attack DNA
        # ----------------------------------------------------

        evolved_attack = adaptive_engine.adapt(

            attack=attack,

            risk_score=request.feedback.risk_score,

            decision=request.feedback.decision,

            detected_signals=(
                request.feedback.detected_signals
            ),
        )

        # ----------------------------------------------------
        # 3. Generate evolved transaction
        # ----------------------------------------------------

        evolved_transaction = generator.generate(

            request.transaction,

            evolved_attack,
        )

        # ----------------------------------------------------
        # 4. Return
        # ----------------------------------------------------

        return {

            "original_attack_id":
                attack.attack_id,

            "evolved_attack_id":
                evolved_attack.attack_id,

            "attack_type":
                evolved_attack.attack_type,

            "evasion_level":
                evolved_attack.evasion_level,

            "adapted_parameters": {

                "amount_pattern":
                    evolved_attack.amount_pattern,

                "device_pattern":
                    evolved_attack.device_pattern,

                "location_pattern":
                    evolved_attack.location_pattern,

                "velocity":
                    evolved_attack.velocity,
            },

            "feedback_used":
                request.feedback.model_dump(),

            "transaction":
                evolved_transaction,
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Adaptive attack generation failed: "
                f"{str(e)}"
            )
        )


# ============================================================
# ADAPT FROM BLUE TEAM ANALYSIS
# ============================================================

@router.post("/adapt-from-analysis")
def adapt_from_analysis(
    transaction: Transaction,
    blue_team_analysis: dict,
):

    try:

        # ----------------------------------------------------
        # 1. Extract Blue Team feedback
        # ----------------------------------------------------

        feedback = feedback_adapter.extract(
            blue_team_analysis
        )

        # ----------------------------------------------------
        # 2. Recover original attack
        # ----------------------------------------------------

        attack_id = transaction.attack_id

        if not attack_id:

            raise ValueError(
                "Transaction does not contain an attack_id."
            )

        base_attack_id = (
            attack_id.split("-V")[0]
        )

        attack = composer.get_attack(
            base_attack_id
        )

        # ----------------------------------------------------
        # 3. Adapt attack DNA
        # ----------------------------------------------------

        evolved_attack = adaptive_engine.adapt(

            attack=attack,

            risk_score=feedback["risk_score"],

            decision=feedback["decision"],

            detected_signals=(
                feedback["detected_signals"]
            ),
        )

        # ----------------------------------------------------
        # 4. Generate V2
        # ----------------------------------------------------

        evolved_transaction = generator.generate(

            transaction,

            evolved_attack,
        )

        # ----------------------------------------------------
        # 5. Return
        # ----------------------------------------------------

        return {

            "original_attack_id":
                attack.attack_id,

            "evolved_attack_id":
                evolved_attack.attack_id,

            "feedback":
                feedback,

            "adapted_parameters": {

                "amount_pattern":
                    evolved_attack.amount_pattern,

                "device_pattern":
                    evolved_attack.device_pattern,

                "location_pattern":
                    evolved_attack.location_pattern,

                "velocity":
                    evolved_attack.velocity,

                "evasion_level":
                    evolved_attack.evasion_level,
            },

            "transaction":
                evolved_transaction,
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Adaptive attack generation failed: "
                f"{str(e)}"
            )
        )