from datetime import datetime
from pathlib import Path
import uuid
import re
import numpy as np

import pandas as pd
from fastapi import FastAPI, HTTPException

from simulator.schemas.transaction_schema import (
    SimulateRequest,
    SimulateResponse,
    Transaction,
)

from blue_team.pipeline import BlueTeamPipeline
from red_team.api.red_team_api import router as red_team_router
from red_team.schemas.transaction import Transaction as RedTeamTransaction
from blue_team.evaluator import Evaluator


def make_json_safe(obj):
    if isinstance(obj, dict):
        return {key: make_json_safe(value) for key, value in obj.items()}

    if isinstance(obj, list):
        return [make_json_safe(value) for value in obj]

    if isinstance(obj, tuple):
        return [make_json_safe(value) for value in obj]

    if isinstance(obj, np.generic):
        return obj.item()

    return obj


app = FastAPI(
    title="Mastercard AI Defense Lab - Transaction Simulator",
    description="Simulator API connected to the Blue Team fraud defense pipeline.",
    version="1.0.0",
)
app.include_router(red_team_router)

# --------------------------------------------------
# Blue Team initialization
# --------------------------------------------------

blue_team = BlueTeamPipeline()
evaluator = Evaluator()


def rejected_response():
    return SimulateResponse(
        transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
        timestamp=datetime.now(),
        simulation_status="rejected",
        transaction=None,
        blue_team_result=None,
    )


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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "known_customers": (
            len(blue_team.historical_data["customer_id"].unique())
            if blue_team.historical_data is not None
            else 0
        ),
    }


# --------------------------------------------------
# Simulate Transaction
# --------------------------------------------------

# --------------------------------------------------
# Helper for rejected simulations
# --------------------------------------------------


def rejected_response():
    return SimulateResponse(
        transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
        timestamp=datetime.now(),
        simulation_status="rejected",
        transaction=None,
        blue_team_result=None,
    )


# --------------------------------------------------
# Helper for rejected simulations
# --------------------------------------------------


def rejected_response():
    return SimulateResponse(
        transaction_id=f"TX{uuid.uuid4().hex[:10].upper()}",
        timestamp=datetime.now(),
        simulation_status="rejected",
        transaction=None,
        blue_team_result=None,
    )


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
    # Validate ID formats
    # --------------------------------------------------

    if not re.fullmatch(r"C\d{4}", request.customer_id):
        return rejected_response()

    if not request.merchant_id.strip():
        return rejected_response()

    if request.beneficiary_id is not None:
        if not re.fullmatch(r"B\d{4}", request.beneficiary_id):
            return rejected_response()

    # --------------------------------------------------
    # Customer existence check
    # --------------------------------------------------

    customer_accounts = blue_team.historical_data[
        blue_team.historical_data["customer_id"] == request.customer_id
    ]

    if customer_accounts.empty:
        return rejected_response()

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
        return rejected_response()

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
# Red Team → Simulator → Blue Team
# --------------------------------------------------


@app.post("/simulate/adversarial", response_model=SimulateResponse)
def simulate_adversarial_transaction(
    transaction: RedTeamTransaction,
) -> SimulateResponse:
    """
    Send a Red Team generated adversarial transaction
    through the Simulator and Blue Team pipeline.
    """

    if not blue_team.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Blue Team is not initialized.",
        )

    transaction_dict = transaction.model_dump()

    # Blue Team feature engineering expects timestamp as a string.
    transaction_dict["timestamp"] = transaction.timestamp.isoformat()

    try:
        analysis = blue_team.analyze(transaction_dict)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Blue Team analysis failed: {str(exc)}",
        )

    decision = analysis["decision"]["decision"]
    simulation_status = "rejected" if decision == "BLOCK" else "success"

    # --------------------------------------------------
    # Evaluate Blue Team decision
    # --------------------------------------------------

    evaluation_input = {
        "transaction_id": transaction.transaction_id,
        "is_fraud": transaction.is_fraud,
        "decision": decision,
        "attack_id": transaction.attack_id,
    }

    evaluation = evaluator.evaluate([evaluation_input])

    clean_transaction = make_json_safe(transaction.model_dump())
    clean_analysis = make_json_safe(analysis)
    clean_evaluation = make_json_safe(evaluation)

    return SimulateResponse(
        transaction_id=transaction.transaction_id,
        timestamp=transaction.timestamp,
        simulation_status=simulation_status,
        transaction=clean_transaction,
        blue_team_result={
            **clean_analysis,
            "evaluation": clean_evaluation,
        },
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
