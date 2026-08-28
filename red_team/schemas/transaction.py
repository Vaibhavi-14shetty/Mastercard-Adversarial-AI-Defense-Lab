from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    account_id: str
    card_id: str
    device_id: str
    merchant_id: str
    beneficiary_id: str

    amount: float = Field(gt=0)
    currency: str = "INR"

    location: str
    timestamp: datetime

    payment_method: str

    is_fraud: bool = False
    attack_id: Optional[str] = None