import pandas as pd
import json
import urllib.request

URL = "http://127.0.0.1:8000/simulate"

data = pd.read_csv(
    "simulator/data/adversarial_transactions.csv"
)

print("\n=== BLUE TEAM ATTACK RESULTS ===\n")

for attack_id, group in data.groupby("attack_id"):

    x = group.iloc[0]

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

        print(
            f"{attack_id}: "
            f"Risk={result['risk_score']}, "
            f"Decision={result['security_decision']}, "
            f"Fraud={result['fraud_probability']}"
        )

    except Exception as e:

        print(
            f"{attack_id}: ERROR -> {e}"
        )