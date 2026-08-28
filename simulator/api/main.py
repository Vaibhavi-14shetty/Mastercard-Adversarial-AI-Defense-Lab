"""
main.py

Payment Simulator API

Flow:
    Simulator Transaction
          ↓
    Blue Team Pipeline
          ↓
    Fraud + Behavior + Graph
          ↓
    Risk Fusion
          ↓
    Decision
"""

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from simulator.schemas.transaction_schema import (
    SimulateRequest,
    SimulateResponse,
    Transaction,
)

from blue_team.pipeline import BlueTeamPipeline


app = FastAPI(
    title="Adversarial AI Defense Lab — Payment Simulator",
    description="Synthetic payment simulator connected to the Blue Team fraud detection pipeline.",
    version="1.0.0",
)


# ============================================================
# DATA / VALIDATION
# ============================================================

DATA_DIR = Path("simulator/data")

ID_PATTERNS = {
    "customer_id": re.compile(r"^C\d{4,}$"),
    "merchant_id": re.compile(r"^M\d{4,}$"),
    "device_id": re.compile(r"^D\d{2,}$"),
    "beneficiary_id": re.compile(r"^B\d{2,}$"),
}


def _load_lookup_tables():
    """Load customer -> account/card mappings."""

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

    return (
        known_customer_ids,
        account_by_customer,
        card_by_customer,
    )


KNOWN_CUSTOMER_IDS, ACCOUNT_BY_CUSTOMER, CARD_BY_CUSTOMER = (
    _load_lookup_tables()
)


def validate_format(field_name: str, value: str) -> bool:
    """Validate ID structure without requiring existence."""

    pattern = ID_PATTERNS.get(field_name)

    if pattern is None:
        return True

    return bool(pattern.match(value))


# ============================================================
# BLUE TEAM
# ============================================================

blue_team = BlueTeamPipeline()


@app.on_event("startup")
def initialize_blue_team():
    """Initialize Blue Team when API starts."""

    print("Initializing Blue Team...")

    blue_team.initialize()

    print("Blue Team ready.")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "service": "Mastercard AI Defense Lab",
        "status": "running",
        "blue_team": blue_team.is_ready,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "known_customers": len(KNOWN_CUSTOMER_IDS),
        "blue_team_ready": blue_team.is_ready,
    }


# ============================================================
# SIMULATE TRANSACTION
# ============================================================

@app.post("/simulate", response_model=SimulateResponse)
def simulate_transaction(request: SimulateRequest):

    if not blue_team.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Blue Team is not initialized.",
        )

    rejection_reasons = []

    # --------------------------------------------------------
    # 1. Validate ID formats
    # --------------------------------------------------------

    if not validate_format(
        "customer_id",
        request.customer_id
    ):
        rejection_reasons.append(
            f"customer_id '{request.customer_id}' has invalid format"
        )

    if not validate_format(
        "merchant_id",
        request.merchant_id
    ):
        rejection_reasons.append(
            f"merchant_id '{request.merchant_id}' has invalid format"
        )

    if not validate_format(
        "device_id",
        request.device_id
    ):
        rejection_reasons.append(
            f"device_id '{request.device_id}' has invalid format"
        )

    if (
        request.beneficiary_id
        and not validate_format(
            "beneficiary_id",
            request.beneficiary_id
        )
    ):
        rejection_reasons.append(
            f"beneficiary_id '{request.beneficiary_id}' has invalid format"
        )

    # --------------------------------------------------------
    # 2. Validate customer existence
    # --------------------------------------------------------

    if request.customer_id not in KNOWN_CUSTOMER_IDS:
        rejection_reasons.append(
            f"customer_id '{request.customer_id}' "
            "does not exist in the synthetic world"
        )

    # --------------------------------------------------------
    # 3. Reject invalid transaction
    # --------------------------------------------------------

    if rejection_reasons:
        return SimulateResponse(
            transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
            timestamp=datetime.now(timezone.utc),
            simulation_status="rejected",
            transaction=None,
        )

    # --------------------------------------------------------
    # 4. Resolve account and card
    # --------------------------------------------------------

    account_id = ACCOUNT_BY_CUSTOMER[request.customer_id]
    card_id = CARD_BY_CUSTOMER[request.customer_id]

    transaction_id = f"TX{uuid.uuid4().hex[:10].upper()}"

    timestamp = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # 5. Build transaction
    # --------------------------------------------------------

    transaction = Transaction(
        transaction_id=transaction_id,
        customer_id=request.customer_id,
        account_id=account_id,
        card_id=card_id,
        device_id=request.device_id,
        merchant_id=request.merchant_id,
        beneficiary_id=request.beneficiary_id,
        amount=request.amount,
        currency="INR",
        location=request.location,
        timestamp=timestamp,
        payment_method=request.payment_method,
        is_fraud=False,
        attack_id=request.attack_id,
    )

    # --------------------------------------------------------
    # 6. Send transaction to Blue Team
    # --------------------------------------------------------

    transaction_dict = transaction.model_dump()

    transaction_dict["timestamp"] = timestamp.isoformat()

    try:

        analysis = blue_team.analyze(transaction_dict)

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Blue Team analysis failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # 7. Determine simulator status
    # --------------------------------------------------------

    decision = analysis["decision"]["decision"]

    if decision == "BLOCK":
        simulation_status = "rejected"
    else:
        simulation_status = "success"

    # --------------------------------------------------------
    # 8. Return transaction
    # --------------------------------------------------------

    return SimulateResponse(
        transaction_id=transaction_id,
        timestamp=timestamp,
        simulation_status=simulation_status,
        transaction=transaction,
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "simulator.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )