import random
import uuid
from datetime import datetime, timedelta

from red_team.schemas.transaction import Transaction
from red_team.schemas.attack_dna import AttackDNA


class AttackGenerator:
    """
    Generates adversarial transactions by modifying
    a legitimate synthetic transaction according to Attack DNA.
    """

    def __init__(self):
        self.unusual_locations = [
            "Mumbai",
            "Delhi",
            "Bengaluru",
            "Hyderabad",
            "Chennai",
            "Kolkata",
        ]

    def generate(
        self,
        transaction: Transaction,
        attack: AttackDNA,
    ) -> Transaction:

        modified = transaction.model_copy(deep=True)

        # Generate a new transaction ID
        modified.transaction_id = (
            f"{transaction.transaction_id}_{attack.attack_id}_{uuid.uuid4().hex[:6]}"
        )

        # Mark ground truth
        modified.is_fraud = True
        modified.attack_id = attack.attack_id

        # ----------------------------------------
        # Amount manipulation
        # ----------------------------------------

        if attack.amount_pattern == "high":
            modified.amount = round(
                transaction.amount * random.uniform(2.0, 5.0),
                2,
            )

        elif attack.amount_pattern == "near_normal":
            modified.amount = round(
                transaction.amount * random.uniform(0.8, 1.2),
                2,
            )

        elif attack.amount_pattern == "normal":
            modified.amount = transaction.amount

        # ----------------------------------------
        # Device manipulation
        # ----------------------------------------

        if attack.device_pattern in {"new", "synthetic"}:
            modified.device_id = f"D{random.randint(100, 999)}"

        # ----------------------------------------
        # Location manipulation
        # ----------------------------------------

        if attack.location_pattern == "unusual":
            possible_locations = [
                location
                for location in self.unusual_locations
                if location != transaction.location
            ]

            if possible_locations:
                modified.location = random.choice(possible_locations)

        # ----------------------------------------
        # Velocity / timestamp manipulation
        # ----------------------------------------

        if attack.velocity == "high":
            modified.timestamp = transaction.timestamp + timedelta(seconds=30)

        elif attack.velocity == "medium":
            modified.timestamp = transaction.timestamp + timedelta(minutes=5)

        elif attack.velocity == "normal":
            modified.timestamp = transaction.timestamp + timedelta(minutes=30)

        elif attack.velocity == "variable":
            modified.timestamp = transaction.timestamp + timedelta(
                seconds=random.randint(10, 300)
            )

        return modified