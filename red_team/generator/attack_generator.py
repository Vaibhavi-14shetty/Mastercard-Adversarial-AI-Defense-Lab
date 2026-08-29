import random
import uuid
from datetime import timedelta

from red_team.schemas.transaction import Transaction
from red_team.schemas.attack_dna import AttackDNA


class AttackGenerator:
    """
    Generates realistic adversarial transactions by modifying
    legitimate transactions according to Attack DNA.

    Each attack type creates a distinct but realistic attack fingerprint.
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

        # --------------------------------------------------
        # Transaction identity
        # --------------------------------------------------

        modified.transaction_id = (
            f"{transaction.transaction_id}_"
            f"{attack.attack_id}_"
            f"{uuid.uuid4().hex[:6]}"
        )

        # Ground truth for evaluation
        modified.is_fraud = True
        modified.attack_id = attack.attack_id

        # --------------------------------------------------
        # AMOUNT MANIPULATION
        # --------------------------------------------------

        if attack.amount_pattern == "high":

            modified.amount = round(
                transaction.amount * random.uniform(2.5, 5.0),
                2,
            )

        elif attack.amount_pattern == "near_normal":

            modified.amount = round(
                transaction.amount * random.uniform(0.8, 1.2),
                2,
            )

        elif attack.amount_pattern == "normal":

            modified.amount = transaction.amount

        # --------------------------------------------------
        # DEVICE MANIPULATION
        # --------------------------------------------------

        if attack.device_pattern in {"new", "synthetic"}:

            modified.device_id = f"D{random.randint(100, 999)}"

        # --------------------------------------------------
        # LOCATION MANIPULATION
        # --------------------------------------------------

        if attack.location_pattern == "unusual":

            possible_locations = [
                location
                for location in self.unusual_locations
                if location != transaction.location
            ]

            if possible_locations:
                modified.location = random.choice(possible_locations)

        # --------------------------------------------------
        # VELOCITY / TIME
        # --------------------------------------------------

        if attack.velocity == "high":

            modified.timestamp = (
                transaction.timestamp +
                timedelta(seconds=random.randint(10, 45))
            )

        elif attack.velocity == "medium":

            modified.timestamp = (
                transaction.timestamp +
                timedelta(minutes=random.randint(3, 7))
            )

        elif attack.velocity == "normal":

            modified.timestamp = (
                transaction.timestamp +
                timedelta(minutes=random.randint(20, 40))
            )

        elif attack.velocity == "variable":

            modified.timestamp = (
                transaction.timestamp +
                timedelta(seconds=random.randint(5, 120))
            )

        # ==================================================
        # ATTACK-SPECIFIC BEHAVIOR
        # ==================================================

        # --------------------------------------------------
        # ATK001 — Account Takeover
        # --------------------------------------------------

        if attack.attack_id == "ATK001":

            modified.device_id = f"D{random.randint(100, 999)}"

            if transaction.location:
                locations = [
                    x for x in self.unusual_locations
                    if x != transaction.location
                ]

                if locations:
                    modified.location = random.choice(locations)

            modified.amount = round(
                transaction.amount * random.uniform(0.9, 1.3),
                2,
            )

        # --------------------------------------------------
        # ATK002 — Card Payment Fraud
        # --------------------------------------------------

        elif attack.attack_id == "ATK002":

            modified.device_id = f"D{random.randint(100, 999)}"

            modified.amount = round(
                transaction.amount * random.uniform(2.5, 5.0),
                2,
            )

            locations = [
                x for x in self.unusual_locations
                if x != transaction.location
            ]

            if locations:
                modified.location = random.choice(locations)

        # --------------------------------------------------
        # ATK003 — Credential Stuffing
        # --------------------------------------------------

        elif attack.attack_id == "ATK003":

            modified.device_id = f"D{random.randint(100, 999)}"

            locations = [
                x for x in self.unusual_locations
                if x != transaction.location
            ]

            if locations:
                modified.location = random.choice(locations)

            modified.timestamp = (
                transaction.timestamp +
                timedelta(seconds=random.randint(10, 60))
            )

                # --------------------------------------------------
        # ATK004 — Social Engineering / GenAI Scam
        # --------------------------------------------------

        elif attack.attack_id == "ATK004":

            # Social-engineering attacks are performed from the
            # legitimate customer's device and location.
            # The key anomaly is the new beneficiary combined
            # with a meaningful but believable amount change.

            modified.device_id = transaction.device_id
            modified.location = transaction.location

            # Moderate spending deviation.
            modified.amount = round(
                transaction.amount * random.uniform(1.8, 2.8),
                2,
            )

            # Fraudulent destination introduced by the scam.
            modified.beneficiary_id = (
                f"B{random.randint(100, 999)}"
            )

            # Social-engineering transactions occur shortly
            # after the customer's previous activity.
            modified.timestamp = (
                transaction.timestamp +
                timedelta(seconds=random.randint(30, 180))
            )

        # --------------------------------------------------
        # ATK005 — Synthetic Identity Fraud
        # --------------------------------------------------

        elif attack.attack_id == "ATK005":

            # Synthetic identity uses a previously unseen but
            # structurally valid device ID.
            modified.device_id = (
                f"D{random.randint(10000, 99999)}"
            )

            modified.beneficiary_id = (
                f"B{random.randint(100, 999)}"
            )

            modified.amount = round(
                transaction.amount * random.uniform(1.2, 2.5),
                2,
            )

        # --------------------------------------------------
        # ATK006 — Adversarial Evasion
        # --------------------------------------------------

        elif attack.attack_id == "ATK006":

            # Keep individual features close to normal,
            # but introduce subtle inconsistencies.

            modified.amount = round(
                transaction.amount * random.uniform(0.85, 1.15),
                2,
            )

            modified.device_id = transaction.device_id
            modified.location = transaction.location

            # Very short transaction interval.
            modified.timestamp = (
                transaction.timestamp +
                timedelta(seconds=random.randint(5, 90))
            )

            # New beneficiary provides a subtle relationship anomaly.
            modified.beneficiary_id = (
                f"B{random.randint(100, 999)}"
            )

        return modified