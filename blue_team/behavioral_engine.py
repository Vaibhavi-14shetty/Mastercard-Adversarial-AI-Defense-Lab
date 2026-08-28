from datetime import datetime
from blue_team.transaction_schema import Transaction


def calculate_behavior_score(transaction: Transaction, profile: dict):
    """
    Compare a transaction against a customer's normal behavior.

    Returns:
        {
            "behavior_score": int,
            "anomalies": list[str]
        }
    """

    score = 0
    anomalies = []

    # 1. Amount check
    if transaction.amount > profile["max_normal_amount"]:
        score += 30
        anomalies.append("Unusually high transaction amount")

    # 2. Location check
    if transaction.location not in profile["usual_locations"]:
        score += 25
        anomalies.append("Unusual transaction location")

    # 3. Device check
    if transaction.device_id not in profile["usual_devices"]:
        score += 25
        anomalies.append("Unrecognized device")

    # 4. Transaction time check
    transaction_time = datetime.fromisoformat(transaction.timestamp)
    transaction_hour = transaction_time.hour

    if transaction_hour not in profile["usual_transaction_hours"]:
        score += 20
        anomalies.append("Unusual transaction time")

    score = min(score, 100)

    return {"behavior_score": score, "anomalies": anomalies}
