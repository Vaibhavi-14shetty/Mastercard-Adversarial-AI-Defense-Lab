"""
transaction_generator.py

Generates realistic legitimate transactions for each customer, sampled
around their behavioral baseline (from behavior_profile.py).

Depends on: customers.csv, accounts.csv, cards.csv, devices.csv,
            merchants.csv, beneficiaries.csv, behavior_profiles.csv

Output matches the team's frozen Transaction schema exactly
(see simulator/schemas/transaction_schema.py).

Run this file directly to generate transactions_historical.csv into simulator/data/.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

SIMULATION_WINDOW_DAYS = 90
PREFERRED_MERCHANT_PROB = 0.85  # how often customer sticks to their usual merchants
BENEFICIARY_TXN_PROB = 0.15     # fraction of txns that are P2P transfers (have a beneficiary)


def load_data(data_dir: str = "simulator/data") -> dict:
    d = Path(data_dir)
    return {
        "customers": pd.read_csv(d / "customers.csv"),
        "accounts": pd.read_csv(d / "accounts.csv"),
        "cards": pd.read_csv(d / "cards.csv"),
        "devices": pd.read_csv(d / "devices.csv"),
        "merchants": pd.read_csv(d / "merchants.csv"),
        "beneficiaries": pd.read_csv(d / "beneficiaries.csv"),
        "behavior_profiles": pd.read_csv(d / "behavior_profiles.csv"),
    }


def random_timestamp_in_window(hour_start: int, hour_end: int, window_days: int) -> datetime:
    """Pick a random day within the window, and a random hour within the
    customer's typical hour range (with a little spillover for realism)."""
    days_ago = random.randint(0, window_days - 1)
    base_date = datetime.now() - timedelta(days=days_ago)

    # 85% inside typical hours, 15% spillover elsewhere (nobody is 100% predictable)
    if random.random() < 0.85:
        hour = random.randint(hour_start, min(hour_end, 23))
    else:
        hour = random.randint(0, 23)

    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second, microsecond=0)


def generate_transactions_for_customer(
    customer_id: str,
    profile_row: pd.Series,
    account_id: str,
    card_id: str,
    all_merchant_ids: list,
    beneficiary_ids: list,
    window_days: int = SIMULATION_WINDOW_DAYS,
) -> list:
    txns = []

    preferred_merchants = json.loads(profile_row["preferred_merchant_ids"])
    typical_devices = json.loads(profile_row["typical_device_ids"])
    if not typical_devices:
        typical_devices = ["D00000"]  # fallback safety net, shouldn't normally trigger

    txns_per_week = profile_row["txns_per_week"]
    num_txns = max(1, int(round(txns_per_week * (window_days / 7))))

    for _ in range(num_txns):
        # Amount: normal distribution around typical, clipped positive
        amount = float(np.random.normal(profile_row["typical_amount"], profile_row["amount_std"]))
        amount = round(max(50.0, amount), 2)  # floor at 50 INR, no negative/zero amounts

        # Merchant: mostly habitual, occasionally novel
        if random.random() < PREFERRED_MERCHANT_PROB and preferred_merchants:
            merchant_id = random.choice(preferred_merchants)
        else:
            merchant_id = random.choice(all_merchant_ids)

        # Device: almost always a known device
        device_id = random.choice(typical_devices)

        # Location: mostly home location, occasional travel
        location = profile_row["typical_location"]
        if random.random() < 0.05:
            location = random.choice(["Pune", "Mumbai", "Bangalore", "Delhi",
                                       "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"])

        # Beneficiary: only for P2P-style transactions
        beneficiary_id = random.choice(beneficiary_ids) if random.random() < BENEFICIARY_TXN_PROB else None

        payment_method = random.choices(
            ["card", "upi", "netbanking", "wallet"], weights=[0.4, 0.4, 0.1, 0.1]
        )[0]

        timestamp = random_timestamp_in_window(
            int(profile_row["typical_hour_start"]),
            int(profile_row["typical_hour_end"]),
            window_days,
        )

        txns.append({
            "transaction_id": f"TX{uuid.uuid4().hex[:10].upper()}",
            "customer_id": customer_id,
            "account_id": account_id,
            "card_id": card_id,
            "device_id": device_id,
            "merchant_id": merchant_id,
            "beneficiary_id": beneficiary_id,
            "amount": amount,
            "currency": "INR",
            "location": location,
            "timestamp": timestamp.isoformat(),
            "payment_method": payment_method,
            "is_fraud": False,
            "attack_id": None,
        })

    return txns


def generate_all_transactions(data_dir: str = "simulator/data") -> pd.DataFrame:
    data = load_data(data_dir)

    all_merchant_ids = data["merchants"]["merchant_id"].tolist()
    beneficiary_ids = data["beneficiaries"]["beneficiary_id"].tolist()

    # Map customer -> their primary account and card (first one found)
    account_by_customer = data["accounts"].drop_duplicates("customer_id").set_index("customer_id")["account_id"].to_dict()
    card_by_customer = data["cards"].drop_duplicates("customer_id").set_index("customer_id")["card_id"].to_dict()

    profiles = data["behavior_profiles"].set_index("customer_id")

    all_txns = []
    print(f"Generating transactions for {len(profiles)} customers...")

    for customer_id, profile_row in profiles.iterrows():
        account_id = account_by_customer.get(customer_id)
        card_id = card_by_customer.get(customer_id)
        if not account_id or not card_id:
            continue  # skip if somehow missing (shouldn't happen, but safe)

        txns = generate_transactions_for_customer(
            customer_id, profile_row, account_id, card_id,
            all_merchant_ids, beneficiary_ids,
        )
        all_txns.extend(txns)

    df = pd.DataFrame(all_txns)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def generate_and_save(data_dir: str = "simulator/data") -> pd.DataFrame:
    df = generate_all_transactions(data_dir)
    out_path = Path(data_dir) / "transactions_historical.csv"
    df.to_csv(out_path, index=False)
    print(f"\nDone. {len(df)} transactions written to {out_path.resolve()}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Amount range: ₹{df['amount'].min():.2f} to ₹{df['amount'].max():.2f}")
    return df


if __name__ == "__main__":
    generate_and_save()