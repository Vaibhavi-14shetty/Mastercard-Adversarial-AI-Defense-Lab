"""
main.py

Payment Simulator API — POST /simulate

Design principle (important, discussed with team):
- customer_id MUST exist in our synthetic world, because account_id/card_id
  are resolved from it (a transaction always belongs to a real account).
- merchant_id, device_id, beneficiary_id are validated for FORMAT only,
  not existence. A brand-new device or merchant is often exactly what a
  real (or simulated) attack looks like — rejecting on non-existence would
  break Red Team's ability to simulate realistic fraud.
- amount and payment_method are validated structurally (positive amount,
  valid enum) — these are genuine data-contract violations, not "new" data.

Run with: uvicorn simulator.api.main:app --reload
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from fastapi import FastAPI

from simulator.schemas.transaction_schema import (
    SimulateRequest,
    SimulateResponse,
    Transaction,
)

app = FastAPI(title="Adversarial AI Defense Lab — Payment Simulator")

DATA_DIR = Path("simulator/data")

# ID format patterns — structural validity, not existence
ID_PATTERNS = {
    "customer_id": re.compile(r"^C\d{4,}$"),
    "merchant_id": re.compile(r"^M\d{4,}$"),
    "device_id": re.compile(r"^D\d{4,}$"),
    "beneficiary_id": re.compile(r"^B\d{4,}$"),
}


def _load_lookup_tables():
    """Loads customer -> (account_id, card_id) mapping.
    Cached at module load; refresh by restarting the server if you
    regenerate entities."""
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    accounts = pd.read_csv(DATA_DIR / "accounts.csv")
    cards = pd.read_csv(DATA_DIR / "cards.csv")

    account_by_customer = (
        accounts.drop_duplicates("customer_id")
        .set_index("customer_id")["account_id"]
        .to_dict()
    )
    card_by_customer = (
        cards.drop_duplicates("customer_id")
        .set_index("customer_id")["card_id"]
        .to_dict()
    )
    known_customer_ids = set(customers["customer_id"])

    return known_customer_ids, account_by_customer, card_by_customer


KNOWN_CUSTOMER_IDS, ACCOUNT_BY_CUSTOMER, CARD_BY_CUSTOMER = _load_lookup_tables()


def validate_format(field_name: str, value: str) -> bool:
    """Checks if an ID LOOKS structurally valid — not whether it exists."""
    pattern = ID_PATTERNS.get(field_name)
    if pattern is None:
        return True  # no pattern defined, skip
    return bool(pattern.match(value))


@app.post("/simulate", response_model=SimulateResponse)
def simulate_transaction(request: SimulateRequest) -> SimulateResponse:
    rejection_reasons = []

    # 1. Format validity checks (apply to all provided IDs, regardless of existence)
    if not validate_format("customer_id", request.customer_id):
        rejection_reasons.append(f"customer_id '{request.customer_id}' has invalid format")

    if not validate_format("merchant_id", request.merchant_id):
        rejection_reasons.append(f"merchant_id '{request.merchant_id}' has invalid format")

    if not validate_format("device_id", request.device_id):
        rejection_reasons.append(f"device_id '{request.device_id}' has invalid format")

    if request.beneficiary_id and not validate_format("beneficiary_id", request.beneficiary_id):
        rejection_reasons.append(f"beneficiary_id '{request.beneficiary_id}' has invalid format")

    # 2. Existence check — ONLY for customer_id, since account/card resolve from it
    if request.customer_id not in KNOWN_CUSTOMER_IDS:
        rejection_reasons.append(
            f"customer_id '{request.customer_id}' does not exist in the synthetic world"
        )

    # 3. If any rejection reason exists, short-circuit with a rejected response
    if rejection_reasons:
        return SimulateResponse(
            transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
            timestamp=datetime.now(timezone.utc),
            simulation_status="rejected",
            transaction=None,
        )

    # 4. Resolve account_id / card_id from the (now confirmed valid) customer_id
    account_id = ACCOUNT_BY_CUSTOMER[request.customer_id]
    card_id = CARD_BY_CUSTOMER[request.customer_id]

    # 5. Build the transaction record matching the frozen schema
    transaction = Transaction(
        transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
        customer_id=request.customer_id,
        account_id=account_id,
        card_id=card_id,
        device_id=request.device_id,
        merchant_id=request.merchant_id,
        beneficiary_id=request.beneficiary_id,
        amount=request.amount,
        currency="INR",
        location=request.location,
        timestamp=datetime.now(timezone.utc),
        payment_method=request.payment_method,
        is_fraud=False,  # ground truth is set later by evaluation, not by the simulator itself
        attack_id=request.attack_id,
    )

    return SimulateResponse(
        transaction_id=transaction.transaction_id,
        timestamp=transaction.timestamp,
        simulation_status="success",
        transaction=transaction,
    )


@app.get("/health")
def health_check():
    return {"status": "ok", "known_customers": len(KNOWN_CUSTOMER_IDS)}