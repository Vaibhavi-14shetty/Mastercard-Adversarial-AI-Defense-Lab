from pydantic import BaseModel
from typing import Optional


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    account_id: str
    card_id: str
    device_id: str
    merchant_id: str
    beneficiary_id: Optional[str] = None

    amount: float
    currency: str

    location: str
    timestamp: str
    payment_method: str

    is_fraud: bool
    attack_id: Optional[str] = None
