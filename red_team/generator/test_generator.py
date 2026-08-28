from datetime import datetime

from red_team.schemas.transaction import Transaction
from red_team.composer.attack_composer import AttackComposer
from red_team.generator.attack_generator import AttackGenerator


# ----------------------------------------
# Create a legitimate transaction
# ----------------------------------------

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


# ----------------------------------------
# Select an attack
# ----------------------------------------

composer = AttackComposer()

attack = composer.get_attack("ATK001")


# ----------------------------------------
# Generate adversarial transaction
# ----------------------------------------

generator = AttackGenerator()

adversarial_transaction = generator.generate(
    transaction,
    attack,
)


# ----------------------------------------
# Display results
# ----------------------------------------

print("===== ORIGINAL TRANSACTION =====")

print(transaction.model_dump())


print("\n===== ATTACK DNA =====")

print(attack.model_dump())


print("\n===== ADVERSARIAL TRANSACTION =====")

print(adversarial_transaction.model_dump())


print("\n===== CHANGES =====")

print("Original Device :", transaction.device_id)
print("Attack Device   :", adversarial_transaction.device_id)

print("Original Location :", transaction.location)
print("Attack Location   :", adversarial_transaction.location)

print("Original Amount :", transaction.amount)
print("Attack Amount   :", adversarial_transaction.amount)

print("Fraud Label :", adversarial_transaction.is_fraud)
print("Attack ID   :", adversarial_transaction.attack_id)


print("\nAttack Generator test successful!")
