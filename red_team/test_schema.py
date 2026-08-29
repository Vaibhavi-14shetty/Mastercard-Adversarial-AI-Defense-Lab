from datetime import datetime

from red_team.schemas.transaction import Transaction
from red_team.schemas.attack_dna import AttackDNA


transaction = Transaction(
    transaction_id="TX1001",
    customer_id="C102",
    account_id="A102",
    card_id="CARD102",
    device_id="D45",
    merchant_id="M21",
    beneficiary_id="B77",
    amount=4500,
    currency="INR",
    location="Pune",
    timestamp=datetime.fromisoformat("2026-08-28T10:30:00"),
    payment_method="card",
    is_fraud=False,
    attack_id=None,
)


attack = AttackDNA(
    attack_id="ATK001",
    attack_type="New Device Fraud",
    target="device",
    amount_pattern="high",
    device_pattern="new",
    location_pattern="normal",
    velocity="medium",
    evasion_level=3,
    description="Fraudulent transaction using a previously unseen device.",
)


print("TRANSACTION")
print(transaction.model_dump())

print("\nATTACK DNA")
print(attack.model_dump())

print("\nSchema test successful!")