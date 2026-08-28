"""
test_data_integrity.py

Validates referential integrity across the synthetic payment world's CSVs.
Run this any time entities/behavior_profiles/transactions are regenerated
to catch breakage early, instead of silently shipping bad data downstream
to Blue Team / Red Team.

Run with:
    pytest simulator/tests/test_data_integrity.py -v
"""

from pathlib import Path

import pandas as pd
import pytest

DATA_DIR = Path("simulator/data")


@pytest.fixture(scope="module")
def data():
    return {
        "customers": pd.read_csv(DATA_DIR / "customers.csv"),
        "accounts": pd.read_csv(DATA_DIR / "accounts.csv"),
        "cards": pd.read_csv(DATA_DIR / "cards.csv"),
        "devices": pd.read_csv(DATA_DIR / "devices.csv"),
        "merchants": pd.read_csv(DATA_DIR / "merchants.csv"),
        "beneficiaries": pd.read_csv(DATA_DIR / "beneficiaries.csv"),
        "behavior_profiles": pd.read_csv(DATA_DIR / "behavior_profiles.csv"),
        "transactions": pd.read_csv(DATA_DIR / "transactions_historical.csv"),
    }


# ---------------------------------------------------------------------
# Foreign key integrity — every ID referenced in transactions must
# actually exist in its source table
# ---------------------------------------------------------------------

def test_no_orphan_customer_ids(data):
    orphans = set(data["transactions"]["customer_id"]) - set(data["customers"]["customer_id"])
    assert not orphans, f"Transactions reference unknown customer_ids: {orphans}"


def test_no_orphan_account_ids(data):
    orphans = set(data["transactions"]["account_id"]) - set(data["accounts"]["account_id"])
    assert not orphans, f"Transactions reference unknown account_ids: {orphans}"


def test_no_orphan_card_ids(data):
    orphans = set(data["transactions"]["card_id"]) - set(data["cards"]["card_id"])
    assert not orphans, f"Transactions reference unknown card_ids: {orphans}"


def test_no_orphan_device_ids(data):
    orphans = set(data["transactions"]["device_id"]) - set(data["devices"]["device_id"])
    assert not orphans, f"Transactions reference unknown device_ids: {orphans}"


def test_no_orphan_merchant_ids(data):
    orphans = set(data["transactions"]["merchant_id"]) - set(data["merchants"]["merchant_id"])
    assert not orphans, f"Transactions reference unknown merchant_ids: {orphans}"


def test_no_orphan_beneficiary_ids(data):
    non_null = data["transactions"]["beneficiary_id"].dropna()
    orphans = set(non_null) - set(data["beneficiaries"]["beneficiary_id"])
    assert not orphans, f"Transactions reference unknown beneficiary_ids: {orphans}"


def test_every_customer_has_a_behavior_profile(data):
    missing = set(data["customers"]["customer_id"]) - set(data["behavior_profiles"]["customer_id"])
    assert not missing, f"Customers missing a behavior profile: {missing}"


# ---------------------------------------------------------------------
# Uniqueness / data quality
# ---------------------------------------------------------------------

def test_transaction_ids_are_unique(data):
    dupes = data["transactions"]["transaction_id"].duplicated().sum()
    assert dupes == 0, f"Found {dupes} duplicate transaction_ids"


def test_customer_ids_are_unique(data):
    dupes = data["customers"]["customer_id"].duplicated().sum()
    assert dupes == 0, f"Found {dupes} duplicate customer_ids"


def test_no_zero_or_negative_amounts(data):
    bad = (data["transactions"]["amount"] <= 0).sum()
    assert bad == 0, f"Found {bad} transactions with amount <= 0"


def test_all_transactions_are_inr(data):
    non_inr = (data["transactions"]["currency"] != "INR").sum()
    assert non_inr == 0, f"Found {non_inr} transactions not in INR"


def test_base_dataset_has_no_fraud_flagged(data):
    """This generator only produces legitimate transactions —
    fraud gets injected later by Red Team, not here."""
    fraud_count = data["transactions"]["is_fraud"].sum()
    assert fraud_count == 0, (
        f"Found {fraud_count} transactions flagged is_fraud=True in the "
        "base historical dataset — this file should only contain legit transactions"
    )


def test_base_dataset_has_no_attack_ids(data):
    attack_tagged = data["transactions"]["attack_id"].notna().sum()
    assert attack_tagged == 0, (
        f"Found {attack_tagged} transactions with a non-null attack_id "
        "in the base historical dataset"
    )


# ---------------------------------------------------------------------
# Relationship consistency — a device used in a transaction must
# actually belong to the customer making that transaction
# ---------------------------------------------------------------------

def test_devices_belong_to_the_transacting_customer(data):
    device_owner = data["devices"].set_index("device_id")["customer_id"].to_dict()
    mismatches = 0
    for _, row in data["transactions"].iterrows():
        owner = device_owner.get(row["device_id"])
        if owner is not None and owner != row["customer_id"]:
            mismatches += 1
    assert mismatches == 0, (
        f"{mismatches} transactions use a device belonging to a different customer"
    )


def test_cards_belong_to_the_transacting_customer(data):
    card_owner = data["cards"].set_index("card_id")["customer_id"].to_dict()
    mismatches = 0
    for _, row in data["transactions"].iterrows():
        owner = card_owner.get(row["card_id"])
        if owner is not None and owner != row["customer_id"]:
            mismatches += 1
    assert mismatches == 0, (
        f"{mismatches} transactions use a card belonging to a different customer"
    )


# ---------------------------------------------------------------------
# Sanity checks on distributions (not hard failures, but flags if the
# generator logic silently broke and started producing degenerate data)
# ---------------------------------------------------------------------

def test_transaction_volume_is_reasonable(data):
    n = len(data["transactions"])
    assert n > 1000, f"Only {n} transactions generated — seems too low for {len(data['customers'])} customers"


def test_every_customer_has_at_least_one_transaction(data):
    customers_with_txns = set(data["transactions"]["customer_id"])
    all_customers = set(data["customers"]["customer_id"])
    missing = all_customers - customers_with_txns
    assert not missing, f"{len(missing)} customers have zero transactions: {missing}"