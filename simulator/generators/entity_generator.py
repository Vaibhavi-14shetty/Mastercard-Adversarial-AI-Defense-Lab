"""
entity_generator.py

Generates the core synthetic entities for the Payment World:
Customer, Account, Card, Device, Merchant, Beneficiary.

Relationships enforced here:
- Each Customer has 1 Account (keep it simple for the hackathon; extend later if needed)
- Each Account has 1-2 Cards
- Each Customer has 1-3 Devices (their "usual" devices)
- Merchants and Beneficiaries are shared pools that customers transact with

Run this file directly to generate all entity CSVs into simulator/data/.
"""

import random
import uuid
from pathlib import Path

import pandas as pd
from faker import Faker

# India locale for realistic names/addresses
fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# Cities we'll operate in (keep it realistic + limited for behavioral consistency)
CITIES = ["Pune", "Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]

MERCHANT_CATEGORIES = [
    "Grocery", "Electronics", "Fashion", "Food Delivery", "Fuel",
    "Travel", "Entertainment", "Utilities", "Healthcare", "E-commerce"
]

DEVICE_TYPES = ["mobile", "desktop", "tablet", "pos_terminal"]


def generate_customers(n: int) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        customer_id = f"C{i:04d}"
        rows.append({
            "customer_id": customer_id,
            "name": fake.name(),
            "age": random.randint(18, 70),
            "home_location": random.choice(CITIES),
            "signup_date": fake.date_between(start_date="-3y", end_date="-30d"),
            "risk_segment": random.choices(
                ["low", "medium", "high"], weights=[0.7, 0.25, 0.05]
            )[0],
        })
    return pd.DataFrame(rows)


def generate_accounts(customers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, cust in customers.iterrows():
        account_id = f"A{cust['customer_id'][1:]}"
        rows.append({
            "account_id": account_id,
            "customer_id": cust["customer_id"],
            "account_type": random.choices(
                ["savings", "current"], weights=[0.8, 0.2]
            )[0],
            "opened_date": cust["signup_date"],
            "balance": round(random.uniform(2000, 500000), 2),
        })
    return pd.DataFrame(rows)


def generate_cards(accounts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, acc in accounts.iterrows():
        num_cards = random.choices([1, 2], weights=[0.75, 0.25])[0]
        for c in range(1, num_cards + 1):
            card_id = f"CARD{acc['account_id'][1:]}{'' if c == 1 else c}"
            rows.append({
                "card_id": card_id,
                "account_id": acc["account_id"],
                "customer_id": acc["customer_id"],
                "card_type": random.choices(
                    ["debit", "credit"], weights=[0.65, 0.35]
                )[0],
                "card_network": random.choice(["Mastercard", "Visa", "RuPay"]),
                "issued_date": acc["opened_date"],
            })
    return pd.DataFrame(rows)


def generate_devices(customers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    device_counter = 1
    for _, cust in customers.iterrows():
        num_devices = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        for _ in range(num_devices):
            device_id = f"D{device_counter:05d}"
            device_counter += 1
            rows.append({
                "device_id": device_id,
                "customer_id": cust["customer_id"],
                "device_type": random.choices(
                    DEVICE_TYPES, weights=[0.6, 0.25, 0.1, 0.05]
                )[0],
                "first_seen": fake.date_between(start_date="-2y", end_date="-1d"),
                "is_trusted": True,  # all generated devices are "known/trusted" by default;
                                      # Red Team will introduce untrusted/new devices in attacks
            })
    return pd.DataFrame(rows)


def generate_merchants(n: int = 150) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        merchant_id = f"M{i:04d}"
        rows.append({
            "merchant_id": merchant_id,
            "merchant_name": fake.company(),
            "category": random.choice(MERCHANT_CATEGORIES),
            "location": random.choice(CITIES),
            "risk_level": random.choices(
                ["low", "medium", "high"], weights=[0.75, 0.2, 0.05]
            )[0],
        })
    return pd.DataFrame(rows)


def generate_beneficiaries(n: int = 200) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        beneficiary_id = f"B{i:04d}"
        rows.append({
            "beneficiary_id": beneficiary_id,
            "beneficiary_name": fake.name(),
            "bank_name": fake.company() + " Bank",
            "location": random.choice(CITIES),
        })
    return pd.DataFrame(rows)


def generate_all_entities(num_customers: int = 300, data_dir: str = "simulator/data"):
    """Generates all entities and saves them as CSVs."""
    out_dir = Path(data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {num_customers} customers...")
    customers = generate_customers(num_customers)

    print("Generating accounts...")
    accounts = generate_accounts(customers)

    print("Generating cards...")
    cards = generate_cards(accounts)

    print("Generating devices...")
    devices = generate_devices(customers)

    print("Generating merchants...")
    merchants = generate_merchants()

    print("Generating beneficiaries...")
    beneficiaries = generate_beneficiaries()

    customers.to_csv(out_dir / "customers.csv", index=False)
    accounts.to_csv(out_dir / "accounts.csv", index=False)
    cards.to_csv(out_dir / "cards.csv", index=False)
    devices.to_csv(out_dir / "devices.csv", index=False)
    merchants.to_csv(out_dir / "merchants.csv", index=False)
    beneficiaries.to_csv(out_dir / "beneficiaries.csv", index=False)

    print(f"\nDone. Files written to {out_dir.resolve()}")
    print(f"  customers.csv     : {len(customers)} rows")
    print(f"  accounts.csv      : {len(accounts)} rows")
    print(f"  cards.csv         : {len(cards)} rows")
    print(f"  devices.csv       : {len(devices)} rows")
    print(f"  merchants.csv     : {len(merchants)} rows")
    print(f"  beneficiaries.csv : {len(beneficiaries)} rows")

    return {
        "customers": customers,
        "accounts": accounts,
        "cards": cards,
        "devices": devices,
        "merchants": merchants,
        "beneficiaries": beneficiaries,
    }


if __name__ == "__main__":
    generate_all_entities(num_customers=300)