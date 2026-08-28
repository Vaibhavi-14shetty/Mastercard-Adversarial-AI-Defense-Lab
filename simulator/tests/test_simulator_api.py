"""
test_simulator_api.py

Automated test suite for POST /simulate — covers realistic edge cases,
not just the happy path. Run with:

    pytest simulator/tests/test_simulator_api.py -v

Requires: pytest, httpx (pip install pytest httpx --break-system-packages if needed)
"""

import pytest
from fastapi.testclient import TestClient

from simulator.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------
# 1. Core success case
# ---------------------------------------------------------------------

def test_valid_transaction_succeeds():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["simulation_status"] == "success"
    assert body["transaction"]["customer_id"] == "C0001"
    assert body["transaction"]["account_id"] == "A0001"
    assert body["transaction"]["card_id"] == "CARD0001"


def test_new_device_and_merchant_still_succeeds():
    """Core design requirement: unknown device/merchant should NOT be
    rejected on existence, only format — since this is what real attacks
    and legitimate new-merchant transactions look like."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M9999",   # not in merchants.csv
        "device_id": "D99999",    # not in devices.csv
        "location": "Pune",
    })
    assert r.status_code == 200
    assert r.json()["simulation_status"] == "success"


# ---------------------------------------------------------------------
# 2. Customer existence (the ONE thing that should be existence-checked)
# ---------------------------------------------------------------------

def test_nonexistent_customer_is_rejected():
    r = client.post("/simulate", json={
        "customer_id": "C9999",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["simulation_status"] == "rejected"
    assert body["transaction"] is None


# ---------------------------------------------------------------------
# 3. Format validity edge cases
# ---------------------------------------------------------------------

def test_malformed_customer_id_rejected():
    r = client.post("/simulate", json={
        "customer_id": "not_an_id",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["simulation_status"] == "rejected"


def test_empty_string_customer_id_rejected():
    r = client.post("/simulate", json={
        "customer_id": "",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["simulation_status"] == "rejected"


def test_lowercase_customer_id_rejected():
    """Real customer IDs are uppercase C-prefixed. Lowercase should fail
    format validation — catches a common data-entry inconsistency bug."""
    r = client.post("/simulate", json={
        "customer_id": "c0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["simulation_status"] == "rejected"


def test_whitespace_only_merchant_id_rejected():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "   ",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["simulation_status"] == "rejected"


def test_malformed_beneficiary_id_rejected():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
        "beneficiary_id": "XYZ123",  # wrong prefix, should be B####
    })
    assert r.json()["simulation_status"] == "rejected"


def test_null_beneficiary_id_is_fine():
    """beneficiary_id is optional — omitting it entirely should NOT
    cause a rejection."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["simulation_status"] == "success"


# ---------------------------------------------------------------------
# 4. Amount edge cases (schema-level validation via Pydantic)
# ---------------------------------------------------------------------

def test_negative_amount_returns_422():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": -100,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 422


def test_zero_amount_returns_422():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 0,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 422


def test_extremely_large_amount_is_accepted():
    """No upper bound is currently enforced — large amounts should still
    succeed at the simulator layer. Flagging risk-based blocking is
    Blue Team's job, not the simulator's."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 10_000_000,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 200
    assert r.json()["simulation_status"] == "success"


def test_amount_as_string_returns_422():
    """Type safety check — amount must be numeric, not a numeric string."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": "five hundred",
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.status_code == 422


# ---------------------------------------------------------------------
# 5. Missing / extra fields
# ---------------------------------------------------------------------

def test_missing_required_field_returns_422():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        # device_id missing entirely
        "location": "Pune",
    })
    assert r.status_code == 422


def test_missing_multiple_required_fields_returns_422():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
    })
    assert r.status_code == 422


def test_extra_unexpected_field_is_ignored_not_rejected():
    """Pydantic's default behavior ignores unrecognized fields rather
    than erroring — verifies the API doesn't break if Red Team sends
    extra metadata fields."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
        "some_future_field": "unexpected_value",
    })
    assert r.status_code == 200


# ---------------------------------------------------------------------
# 6. Payment method enum validation
# ---------------------------------------------------------------------

def test_invalid_payment_method_returns_422():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
        "payment_method": "bitcoin",  # not in the allowed enum
    })
    assert r.status_code == 422


def test_all_valid_payment_methods_accepted():
    for method in ["card", "upi", "netbanking", "wallet"]:
        r = client.post("/simulate", json={
            "customer_id": "C0001",
            "amount": 500,
            "merchant_id": "M0001",
            "device_id": "D00001",
            "location": "Pune",
            "payment_method": method,
        })
        assert r.status_code == 200, f"payment_method={method} should be valid"


# ---------------------------------------------------------------------
# 7. Attack-specific fields (Red Team usage)
# ---------------------------------------------------------------------

def test_attack_id_is_passed_through():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
        "attack_id": "ATTACK_001",
    })
    body = r.json()
    assert body["transaction"]["attack_id"] == "ATTACK_001"


def test_is_fraud_always_false_from_simulator():
    """Simulator never sets is_fraud itself — ground truth comes from
    evaluation, not the simulator. Even with an attack_id present."""
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
        "attack_id": "ATTACK_001",
    })
    assert r.json()["transaction"]["is_fraud"] is False


# ---------------------------------------------------------------------
# 8. Response shape / schema conformance
# ---------------------------------------------------------------------

def test_response_matches_frozen_schema_fields():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    txn = r.json()["transaction"]
    expected_fields = {
        "transaction_id", "customer_id", "account_id", "card_id",
        "device_id", "merchant_id", "beneficiary_id", "amount",
        "currency", "location", "timestamp", "payment_method",
        "is_fraud", "attack_id",
    }
    assert set(txn.keys()) == expected_fields


def test_currency_always_inr():
    r = client.post("/simulate", json={
        "customer_id": "C0001",
        "amount": 500,
        "merchant_id": "M0001",
        "device_id": "D00001",
        "location": "Pune",
    })
    assert r.json()["transaction"]["currency"] == "INR"


# ---------------------------------------------------------------------
# 9. Health check
# ---------------------------------------------------------------------

def test_health_check_reports_customer_count():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["known_customers"] == 300