from datetime import datetime
from pathlib import Path
import uuid

import pandas as pd
from fastapi import FastAPI, HTTPException

from simulator.schemas.transaction_schema import (
    SimulateRequest,
    SimulateResponse,
    Transaction,
)

from blue_team.pipeline import BlueTeamPipeline


app = FastAPI(
    title="Mastercard AI Defense Lab - Transaction Simulator",
    description="Simulator API connected to the Blue Team fraud defense pipeline.",
    version="1.0.0",
)


# --------------------------------------------------
# Blue Team initialization
# --------------------------------------------------

blue_team = BlueTeamPipeline()


@app.on_event("startup")
def initialize_blue_team():
    """Initialize the Blue Team when the API starts."""

    print("Initializing Blue Team...")

    blue_team.initialize()

    print("Blue Team ready.")


# --------------------------------------------------
# Health Check
# --------------------------------------------------


@app.get("/")
def root():
    return {
        "service": "Mastercard AI Defense Lab Simulator",
        "status": "running",
        "blue_team": blue_team.is_ready,
    }


# --------------------------------------------------
# Simulate Transaction
# --------------------------------------------------


@app.post("/simulate", response_model=SimulateResponse)
def simulate_transaction(request: SimulateRequest):
    """
    Simulate one payment transaction and send it
    through the Blue Team detection pipeline.
    """

    if not blue_team.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Blue Team is not initialized.",
        )

    # --------------------------------------------------
    # Generate transaction ID and timestamp
    # --------------------------------------------------

    transaction_id = f"TX{uuid.uuid4().hex[:10].upper()}"

    timestamp = datetime.now()

    # --------------------------------------------------
    # Resolve account and card for customer
    # --------------------------------------------------

    customer_accounts = blue_team.historical_data[
        blue_team.historical_data["customer_id"] == request.customer_id
    ]

    if customer_accounts.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {request.customer_id} not found.",
        )

    account_id = customer_accounts.iloc[0]["account_id"]
    card_id = customer_accounts.iloc[0]["card_id"]

    # --------------------------------------------------
    # Build frozen Transaction schema
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Run Blue Team analysis
    # --------------------------------------------------

    transaction_dict = transaction.model_dump()

    # Convert datetime to ISO string because the
    # feature engineering layer expects timestamp strings.
    transaction_dict["timestamp"] = timestamp.isoformat()

    try:
        analysis = blue_team.analyze(transaction_dict)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Blue Team analysis failed: {str(exc)}",
        )

    # --------------------------------------------------
    # Determine simulation status
    # --------------------------------------------------

    decision = analysis["decision"]["decision"]

    if decision == "BLOCK":
        simulation_status = "rejected"
    else:
        simulation_status = "success"

    # --------------------------------------------------
    # Return simulator response
    # --------------------------------------------------

    return SimulateResponse(
        transaction_id=transaction_id,
        timestamp=timestamp,
        simulation_status=simulation_status,
        transaction=transaction,
    )


# --------------------------------------------------
# Run directly
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "simulator.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
