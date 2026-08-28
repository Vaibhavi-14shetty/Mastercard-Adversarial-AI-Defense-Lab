"""
transaction_schema.py

THE frozen data contract for the AI Defense Lab project.
Every module (Synthetic World, Red Team, Simulator, Blue Team) must
produce/consume transactions in exactly this shape.

Do not modify field names/types here without syncing with the whole team —
this file is the single source of truth.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str = Field(..., examples=["TX1001"])
    customer_id: str = Field(..., examples=["C102"])
    account_id: str = Field(..., examples=["A102"])
    card_id: str = Field(..., examples=["CARD102"])
    device_id: str = Field(..., examples=["D45"])
    merchant_id: str = Field(..., examples=["M21"])
    beneficiary_id: Optional[str] = Field(None, examples=["B77"])

    amount: float = Field(..., gt=0, examples=[4500])
    currency: Literal["INR"] = "INR"
    location: str = Field(..., examples=["Pune"])
    timestamp: datetime = Field(..., examples=["2026-08-28T10:30:00"])
    payment_method: Literal["card", "upi", "netbanking", "wallet"] = "card"

    is_fraud: bool = False
    attack_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TX1001",
                "customer_id": "C102",
                "account_id": "A102",
                "card_id": "CARD102",
                "device_id": "D45",
                "merchant_id": "M21",
                "beneficiary_id": "B77",
                "amount": 4500,
                "currency": "INR",
                "location": "Pune",
                "timestamp": "2026-08-28T10:30:00",
                "payment_method": "card",
                "is_fraud": False,
                "attack_id": None,
            }
        }


class SimulateRequest(BaseModel):
    """Input to POST /simulate — what Red Team (or you) sends in."""
    customer_id: str
    amount: float = Field(..., gt=0)
    merchant_id: str
    device_id: str
    location: str
    beneficiary_id: Optional[str] = None
    payment_method: Literal["card", "upi", "netbanking", "wallet"] = "card"
    attack_id: Optional[str] = None  # set by Red Team if this is an attack


class SimulateResponse(BaseModel):
    """Output of POST /simulate."""
    transaction_id: str
    timestamp: datetime
    simulation_status: Literal["success", "rejected"]
    transaction: Optional[Transaction] = None