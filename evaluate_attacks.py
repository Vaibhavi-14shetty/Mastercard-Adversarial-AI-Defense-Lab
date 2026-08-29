import pandas as pd
import json
import urllib.request

from blue_team.evaluator import Evaluator


URL = "http://127.0.0.1:8000/simulate"

data = pd.read_csv(
    "simulator/data/adversarial_transactions.csv"
)

results = []

print("\n=== RUNNING FULL ADVERSARIAL EVALUATION ===\n")

for index, x in data.iterrows():

    payload = {
        "transaction_id": str(x.transaction_id),
        "customer_id": str(x.customer_id),
        "amount": float(x.amount),
        "merchant_id": str(x.merchant_id),
        "device_id": str(x.device_id),
        "location": str(x.location),
        "beneficiary_id": (
            None
            if str(x.beneficiary_id) == "B_NONE"
            else str(x.beneficiary_id)
        ),
        "payment_method": str(x.payment_method),
        "attack_id": str(x.attack_id),
        "timestamp": str(x.timestamp),
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    try:

        response = urllib.request.urlopen(request)

        result = json.loads(
            response.read().decode("utf-8")
        )

        results.append(
            {
                "transaction_id": str(x.transaction_id),
                "is_fraud": True,
                "decision": result["security_decision"],
                "attack_id": str(x.attack_id),
                "risk_score": result["risk_score"],
            }
        )

    except Exception as e:

        print(
            f"Error on {x.transaction_id}: {e}"
        )


print("\n=== EVALUATION ===\n")

evaluator = Evaluator()

metrics = evaluator.evaluate(results)

for key, value in metrics.items():

    print(
        f"{key}: {value}"
    )


print("\n=== ATTACK BREAKDOWN ===\n")

df = pd.DataFrame(results)

if not df.empty:

    breakdown = (
        df.groupby("attack_id")
        .agg(
            transactions=("attack_id", "count"),
            average_risk=("risk_score", "mean"),
            blocked=(
                "decision",
                lambda x: (x == "BLOCK").sum()
            ),
            challenged=(
                "decision",
                lambda x: (x == "CHALLENGE").sum()
            ),
            allowed=(
                "decision",
                lambda x: (x == "ALLOW").sum()
            ),
        )
    )

    print(
        breakdown.round(2)
    )