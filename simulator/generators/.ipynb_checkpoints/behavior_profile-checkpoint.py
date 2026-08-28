"""
behavior_profile.py

Builds a per-customer behavioral baseline: what does "normal" look like
for this customer? This baseline is what transaction_generator.py samples
from to produce realistic legit transactions, and it's also the reference
point fraud/attacks will later deviate from.

Depends on: customers.csv, devices.csv, merchants.csv (from entity_generator.py)

Run this file directly to generate behavior_profiles.csv into simulator/data/.
"""

import random
import json
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# Typical spending bands (mean, sigma for log-normal draw, in INR)
AMOUNT_BANDS = {
    "low": {"mean_log": 6.2, "sigma": 0.6},      # ~ centered around 500
    "medium": {"mean_log": 7.3, "sigma": 0.7},   # ~ centered around 1500
    "high": {"mean_log": 8.5, "sigma": 0.8},     # ~ centered around 5000
}

# Common transaction-hour windows people fall into (24hr clock)
HOUR_PROFILES = {
    "morning_person": (7, 11),
    "lunch_shopper": (12, 15),
    "evening_shopper": (18, 22),
    "night_owl": (21, 24),
}


def assign_spending_band(risk_segment: str) -> str:
    """Maps risk_segment loosely to a spending band, with some noise
    so it's not a perfect 1:1 (real life isn't that clean)."""
    if risk_segment == "high":
        return random.choices(["medium", "high"], weights=[0.3, 0.7])[0]
    elif risk_segment == "medium":
        return random.choices(["low", "medium", "high"], weights=[0.2, 0.6, 0.2])[0]
    else:
        return random.choices(["low", "medium"], weights=[0.75, 0.25])[0]


def build_behavior_profiles(
    customers: pd.DataFrame,
    devices: pd.DataFrame,
    merchants: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    devices_by_customer = devices.groupby("customer_id")["device_id"].apply(list).to_dict()
    merchant_ids_by_category = merchants.groupby("category")["merchant_id"].apply(list).to_dict()
    all_categories = list(merchant_ids_by_category.keys())

    for _, cust in customers.iterrows():
        customer_id = cust["customer_id"]
        spending_band = assign_spending_band(cust["risk_segment"])
        band = AMOUNT_BANDS[spending_band]

        # Typical amount: draw a representative "usual" amount for this customer
        typical_amount = round(float(np.random.lognormal(mean=band["mean_log"], sigma=0.3)), 2)
        amount_std = round(typical_amount * 0.35, 2)  # ~35% natural variation around typical

        # Preferred merchant categories: each customer sticks to 2-4 categories habitually
        num_categories = random.randint(2, 4)
        preferred_categories = random.sample(all_categories, num_categories)
        preferred_merchants = []
        for cat in preferred_categories:
            pool = merchant_ids_by_category.get(cat, [])
            if pool:
                preferred_merchants.extend(random.sample(pool, min(len(pool), random.randint(1, 3))))

        # Typical devices: customer's own device list (already generated)
        typical_devices = devices_by_customer.get(customer_id, [])

        # Typical hour window
        hour_profile_name = random.choice(list(HOUR_PROFILES.keys()))
        hour_start, hour_end = HOUR_PROFILES[hour_profile_name]

        # Transaction frequency per week
        freq_per_week = round(np.random.gamma(shape=2.0, scale=2.0), 1)  # right-skewed, most people moderate
        freq_per_week = max(0.5, min(freq_per_week, 20))  # clip to sane bounds

        rows.append({
            "customer_id": customer_id,
            "spending_band": spending_band,
            "typical_amount": typical_amount,
            "amount_std": amount_std,
            "preferred_merchant_ids": json.dumps(preferred_merchants),
            "preferred_categories": json.dumps(preferred_categories),
            "typical_device_ids": json.dumps(typical_devices),
            "typical_location": cust["home_location"],
            "hour_profile": hour_profile_name,
            "typical_hour_start": hour_start,
            "typical_hour_end": hour_end,
            "txns_per_week": freq_per_week,
        })

    return pd.DataFrame(rows)


def generate_and_save(data_dir: str = "simulator/data") -> pd.DataFrame:
    out_dir = Path(data_dir)
    customers = pd.read_csv(out_dir / "customers.csv")
    devices = pd.read_csv(out_dir / "devices.csv")
    merchants = pd.read_csv(out_dir / "merchants.csv")

    print(f"Building behavior profiles for {len(customers)} customers...")
    profiles = build_behavior_profiles(customers, devices, merchants)

    profiles.to_csv(out_dir / "behavior_profiles.csv", index=False)
    print(f"Done. behavior_profiles.csv written with {len(profiles)} rows to {out_dir.resolve()}")

    return profiles


if __name__ == "__main__":
    generate_and_save()