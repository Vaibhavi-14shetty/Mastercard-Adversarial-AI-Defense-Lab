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

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from red_team.composer.attack_composer import AttackComposer
from red_team.generator.attack_generator import AttackGenerator
from red_team.schemas.transaction import Transaction
from red_team.schemas.attack_dna import AttackDNA


router = APIRouter(
    prefix="/red-team",
    tags=["Red Team"]
)


class AttackRequest(BaseModel):
    """
    Request for generating an adversarial transaction.
    """

    transaction: Transaction
    attack_id: Optional[str] = None


class AttackResponse(BaseModel):
    """
    Response returned after generating an attack.
    """

    attack_id: str
    attack_type: str
    transaction: Transaction


composer = AttackComposer()
generator = AttackGenerator()


@router.post("/generate", response_model=AttackResponse)
def generate_attack(request: AttackRequest):

    try:
        # -----------------------------------------
        # 1. Select attack
        # -----------------------------------------

        if request.attack_id:
            attack = composer.get_attack(request.attack_id)
        else:
            attack = composer.random_attack()

        # -----------------------------------------
        # 2. Generate adversarial transaction
        # -----------------------------------------

        adversarial_transaction = generator.generate(
            request.transaction,
            attack
        )

        # -----------------------------------------
        # 3. Return result
        # -----------------------------------------

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