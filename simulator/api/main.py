"""
main.py
Payment Simulator API

Flow:

    Simulator Transaction
          ↓
    Red Team Attack Generation
          ↓
    Blue Team Pipeline
          ↓
    Fraud + Behavior + Graph + Temporal Risk
          ↓
    Risk Fusion
          ↓
    Decision
          ↓
    Evaluation
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from simulator.schemas.transaction_schema import (
    SimulateRequest,
    SimulateResponse,
    Transaction,
)

from blue_team.pipeline import BlueTeamPipeline
from blue_team.evaluator import Evaluator

from red_team.api.red_team_api import router as red_team_router
from red_team.schemas.transaction import Transaction as RedTeamTransaction
from red_team.composer.attack_composer import AttackComposer
from red_team.generator.attack_generator import AttackGenerator


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Adversarial AI Defense Lab — Payment Simulator",
    description=(
        "Synthetic payment simulator connected to the "
        "Blue Team fraud detection pipeline."
    ),
    version="1.0.0",
)


# ============================================================
# CORS — FRONTEND CONNECTION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(red_team_router)


# ============================================================
# DATA / VALIDATION
# ============================================================

DATA_DIR = Path("simulator/data")

ID_PATTERNS = {
    "customer_id": re.compile(r"^C\d{4,}$"),
    "merchant_id": re.compile(r"^M\d{4,}$"),
    "device_id": re.compile(r"^(D\d{2,}|SYN\d{4,})$"),
    "beneficiary_id": re.compile(r"^B\d{2,}$"),
}


def _load_lookup_tables():
    """Load customer -> account/card mappings."""

    customers = pd.read_csv(DATA_DIR / "customers.csv")
    accounts = pd.read_csv(DATA_DIR / "accounts.csv")
    cards = pd.read_csv(DATA_DIR / "cards.csv")

    account_by_customer = (
        accounts.drop_duplicates("customer_id")
        .set_index("customer_id")["account_id"]
        .to_dict()
    )

    card_by_customer = (
        cards.drop_duplicates("customer_id")
        .set_index("customer_id")["card_id"]
        .to_dict()
    )

    known_customer_ids = set(customers["customer_id"])

    return (
        known_customer_ids,
        account_by_customer,
        card_by_customer,
    )


(
    KNOWN_CUSTOMER_IDS,
    ACCOUNT_BY_CUSTOMER,
    CARD_BY_CUSTOMER,
) = _load_lookup_tables()


def validate_format(field_name: str, value: str) -> bool:
    """Validate ID structure without requiring existence."""

    pattern = ID_PATTERNS.get(field_name)

    if pattern is None:
        return True

    return bool(pattern.match(value))


# ============================================================
# BLUE TEAM / RED TEAM
# ============================================================

blue_team = BlueTeamPipeline()
evaluator = Evaluator()

attack_composer = AttackComposer()
attack_generator = AttackGenerator()


# ============================================================
# HELPERS
# ============================================================


def make_json_safe(obj):
    """Convert NumPy/Python objects into JSON-safe values."""

    if isinstance(obj, dict):
        return {key: make_json_safe(value) for key, value in obj.items()}

    if isinstance(obj, list):
        return [make_json_safe(value) for value in obj]

    if isinstance(obj, tuple):
        return [make_json_safe(value) for value in obj]

    if isinstance(obj, np.generic):
        return obj.item()

    return obj


def rejected_response(reasons=None):
    """Create a standard rejected simulation response."""

    return SimulateResponse(
        transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
        timestamp=datetime.now(timezone.utc),
        simulation_status="rejected",
        security_decision="BLOCK",
        risk_score=100.0,
        fraud_probability=1.0,
        behavior_score=0.0,
        graph_risk_score=0.0,
        temporal_risk_score=0.0,
        reasons=reasons or [],
        transaction=None,
    )


# ============================================================
# STARTUP
# ============================================================


@app.on_event("startup")
def initialize_blue_team():
    """Initialize Blue Team when API starts."""

    print("Initializing Blue Team...")

    blue_team.initialize()

    print("Blue Team ready.")


# ============================================================
# HEALTH CHECK
# ============================================================


@app.get("/")
def root():
    return {
        "service": "Mastercard AI Defense Lab",
        "status": "running",
        "blue_team": blue_team.is_ready,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "known_customers": len(KNOWN_CUSTOMER_IDS),
        "blue_team_ready": blue_team.is_ready,
    }


# ============================================================
# SIMULATE TRANSACTION
# ============================================================


@app.post("/simulate", response_model=SimulateResponse)
def simulate_transaction(request: SimulateRequest):

    if not blue_team.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Blue Team is not initialized.",
        )

    rejection_reasons = []

    # --------------------------------------------------------
    # 1. Validate ID formats
    # --------------------------------------------------------

    if not validate_format(
        "customer_id",
        request.customer_id,
    ):
        rejection_reasons.append(
            f"customer_id '{request.customer_id}' has invalid format"
        )

    if not validate_format(
        "merchant_id",
        request.merchant_id,
    ):
        rejection_reasons.append(
            f"merchant_id '{request.merchant_id}' has invalid format"
        )

    if not validate_format(
        "device_id",
        request.device_id,
    ):
        rejection_reasons.append(f"device_id '{request.device_id}' has invalid format")

    if request.beneficiary_id and not validate_format(
        "beneficiary_id",
        request.beneficiary_id,
    ):
        rejection_reasons.append(
            f"beneficiary_id '{request.beneficiary_id}' has invalid format"
        )

    # --------------------------------------------------------
    # 2. Validate customer existence
    # --------------------------------------------------------

    if request.customer_id not in KNOWN_CUSTOMER_IDS:
        rejection_reasons.append(
            f"customer_id '{request.customer_id}' does not exist in the synthetic world"
        )

    # --------------------------------------------------------
    # 3. Reject invalid transaction
    # --------------------------------------------------------

    if rejection_reasons:
        return rejected_response(rejection_reasons)

    # --------------------------------------------------------
    # 4. Resolve account and card
    # --------------------------------------------------------

    account_id = ACCOUNT_BY_CUSTOMER.get(request.customer_id)

    card_id = CARD_BY_CUSTOMER.get(request.customer_id)

    if account_id is None or card_id is None:
        return rejected_response(["Customer account/card mapping not found."])

    # --------------------------------------------------------
    # 5. Build transaction
    # --------------------------------------------------------

    transaction_id = request.transaction_id or (f"TX{uuid.uuid4().hex[:10].upper()}")

    timestamp = request.timestamp or datetime.now(timezone.utc)

    transaction = Transaction(
        transaction_id=transaction_id,
        customer_id=request.customer_id,
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
        is_fraud=False,
        attack_id=None,
    )

    # --------------------------------------------------------
    # 6. RED TEAM ATTACK GENERATION
    # --------------------------------------------------------

    if request.attack_id:
        try:
            attack = attack_composer.get_attack(request.attack_id)

            transaction = attack_generator.generate(
                transaction,
                attack,
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Attack generation failed: {str(exc)}",
            )

    # --------------------------------------------------------
    # 7. Send transaction to Blue Team
    # --------------------------------------------------------

    transaction_dict = transaction.model_dump()

    # Preserve timestamp modifications made by Red Team.
    transaction_dict["timestamp"] = transaction.timestamp.isoformat()

    try:
        analysis = blue_team.analyze(transaction_dict)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Blue Team analysis failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # 8. Determine simulator status
    # --------------------------------------------------------

    decision = analysis["decision"]["decision"]

    if decision == "BLOCK":
        simulation_status = "rejected"

    elif decision == "CHALLENGE":
        simulation_status = "challenge"

    else:
        simulation_status = "success"

    # --------------------------------------------------------
    # 9. Return transaction + Blue Team analysis
    # --------------------------------------------------------

    return SimulateResponse(
        transaction_id=transaction_id,
        timestamp=transaction.timestamp,
        simulation_status=simulation_status,
        security_decision=decision,
        risk_score=analysis["risk"]["final_risk_score"],
        fraud_probability=analysis["fraud"]["fraud_probability"],
        behavior_score=analysis["behavior"]["behavior_score"],
        graph_risk_score=analysis["risk"]["graph_risk_score"],
        temporal_risk_score=analysis["risk"]["temporal_risk_score"],
        reasons=analysis["explanation"]["reasons"],
        transaction=transaction,
    )


# ============================================================
# RED TEAM → SIMULATOR → BLUE TEAM
# ============================================================


@app.post(
    "/simulate/adversarial",
    response_model=SimulateResponse,
)
def simulate_adversarial_transaction(
    transaction: RedTeamTransaction,
) -> SimulateResponse:
    """
    Send a Red Team generated adversarial transaction
    through the Simulator and Blue Team pipeline.
    """

    if not blue_team.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Blue Team is not initialized.",
        )

    transaction_dict = transaction.model_dump()

    # Blue Team feature engineering expects timestamp as a string.
    transaction_dict["timestamp"] = transaction.timestamp.isoformat()

    try:
        analysis = blue_team.analyze(transaction_dict)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Blue Team analysis failed: {str(exc)}",
        )

    decision = analysis["decision"]["decision"]

    simulation_status = "rejected" if decision == "BLOCK" else "success"

    # --------------------------------------------------------
    # Evaluate Blue Team decision
    # --------------------------------------------------------

    evaluation_input = {
        "transaction_id": transaction.transaction_id,
        "is_fraud": transaction.is_fraud,
        "decision": decision,
        "attack_id": transaction.attack_id,
    }

    evaluation = evaluator.evaluate([evaluation_input])

    clean_transaction = make_json_safe(transaction.model_dump())

    clean_analysis = make_json_safe(analysis)

    clean_evaluation = make_json_safe(evaluation)

    return SimulateResponse(
        transaction_id=transaction.transaction_id,
        timestamp=transaction.timestamp,
        simulation_status=simulation_status,
        security_decision=decision,
        risk_score=analysis["risk"]["final_risk_score"],
        fraud_probability=analysis["fraud"]["fraud_probability"],
        behavior_score=analysis["behavior"]["behavior_score"],
        graph_risk_score=analysis["risk"]["graph_risk_score"],
        temporal_risk_score=analysis["risk"]["temporal_risk_score"],
        reasons=analysis["explanation"]["reasons"],
        transaction=clean_transaction,
        blue_team_result={
            **clean_analysis,
            "evaluation": clean_evaluation,
        },
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "simulator.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
