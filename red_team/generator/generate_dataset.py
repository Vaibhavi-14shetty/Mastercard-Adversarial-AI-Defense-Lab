"""
generate_dataset.py

Creates adversarial payment transactions from the synthetic
historical transaction dataset.

Pipeline:

historical transactions
        ↓
Attack Composer
        ↓
Attack DNA
        ↓
Attack Generator
        ↓
adversarial transactions

Output:
simulator/data/adversarial_transactions.csv
"""

from pathlib import Path

import pandas as pd

from red_team.schemas.transaction import Transaction
from red_team.composer.attack_composer import AttackComposer
from red_team.generator.attack_generator import AttackGenerator


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

HISTORICAL_DATASET = (
    BASE_DIR
    / "simulator"
    / "data"
    / "transactions_historical.csv"
)

OUTPUT_DATASET = (
    BASE_DIR
    / "simulator"
    / "data"
    / "adversarial_transactions.csv"
)

# Number of adversarial transactions to generate
NUM_ATTACKS = 1000

# Six attacks that our project supports
ATTACK_IDS = [
    "ATK001",
    "ATK002",
    "ATK003",
    "ATK004",
    "ATK005",
    "ATK006",
]


# ---------------------------------------------------------
# Load historical transactions
# ---------------------------------------------------------

def load_historical_transactions() -> pd.DataFrame:
    """Load legitimate synthetic transactions."""

    if not HISTORICAL_DATASET.exists():
        raise FileNotFoundError(
            f"Historical dataset not found:\n{HISTORICAL_DATASET}"
        )

    df = pd.read_csv(HISTORICAL_DATASET)

    print(f"Loaded historical transactions: {len(df)}")
    return df


# ---------------------------------------------------------
# Convert CSV row into frozen Transaction schema
# ---------------------------------------------------------

def row_to_transaction(row: pd.Series) -> Transaction:
    """Convert one CSV row into the common Transaction schema."""

    # Pydantic schema requires a string for beneficiary_id in the
    # current project implementation. For historical transactions
    # where no beneficiary exists, use a neutral placeholder.
    beneficiary_id = (
        "B_NONE"
        if pd.isna(row["beneficiary_id"])
        else str(row["beneficiary_id"])
    )

    return Transaction(
        transaction_id=str(row["transaction_id"]),
        customer_id=str(row["customer_id"]),
        account_id=str(row["account_id"]),
        card_id=str(row["card_id"]),
        device_id=str(row["device_id"]),
        merchant_id=str(row["merchant_id"]),
        beneficiary_id=beneficiary_id,
        amount=float(row["amount"]),
        currency=str(row["currency"]),
        location=str(row["location"]),
        timestamp=pd.to_datetime(row["timestamp"]).to_pydatetime(),
        payment_method=str(row["payment_method"]),
        is_fraud=False,
        attack_id=None,
    )


# ---------------------------------------------------------
# Generate adversarial transactions
# ---------------------------------------------------------

def generate_adversarial_transactions(
    historical_df: pd.DataFrame,
    num_attacks: int = NUM_ATTACKS,
) -> pd.DataFrame:

    composer = AttackComposer()
    generator = AttackGenerator()

    # Only use legitimate transactions as attack starting points
    legitimate_df = historical_df[
        historical_df["is_fraud"].astype(str).str.lower() == "false"
    ].copy()

    if legitimate_df.empty:
        raise ValueError("No legitimate transactions available.")

    # Make sure we don't request more transactions than available
    num_attacks = min(num_attacks, len(legitimate_df))

    # Reproducible selection
    selected_df = legitimate_df.sample(
        n=num_attacks,
        random_state=42,
    )

    adversarial_transactions = []

    print(f"Generating {num_attacks} adversarial transactions...")
    print()

    for index, (_, row) in enumerate(selected_df.iterrows()):

        # Convert historical row to Transaction schema
        transaction = row_to_transaction(row)

        # Distribute attacks across all six attack types
        attack_id = ATTACK_IDS[index % len(ATTACK_IDS)]

        # Load Attack DNA
        attack = composer.get_attack(attack_id)

        # Generate adversarial transaction
        adversarial = generator.generate(
            transaction,
            attack,
        )

        adversarial_transactions.append(
            adversarial.model_dump()
        )

    result_df = pd.DataFrame(adversarial_transactions)

    # Convert datetime to ISO format for CSV consistency
    result_df["timestamp"] = result_df["timestamp"].apply(
        lambda x: x.isoformat()
    )

    return result_df


# ---------------------------------------------------------
# Save dataset
# ---------------------------------------------------------

def save_dataset(df: pd.DataFrame) -> None:
    """Save adversarial transactions to CSV."""

    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_DATASET,
        index=False,
    )

    print()
    print("==========================================")
    print("ADVERSARIAL DATASET GENERATED")
    print("==========================================")
    print(f"Output file : {OUTPUT_DATASET}")
    print(f"Transactions: {len(df)}")
    print()

    print("Attack distribution:")
    print(df["attack_id"].value_counts().sort_index())

    print()
    print("Fraud labels:")
    print(df["is_fraud"].value_counts())


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("==========================================")
    print("RED TEAM DATASET GENERATOR")
    print("==========================================")
    print()

    historical_df = load_historical_transactions()

    adversarial_df = generate_adversarial_transactions(
        historical_df,
        NUM_ATTACKS,
    )

    save_dataset(adversarial_df)


if __name__ == "__main__":
    main()