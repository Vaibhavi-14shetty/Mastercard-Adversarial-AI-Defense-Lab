from datetime import datetime


def calculate_behavior_score(transaction, profile):
    """
    Analyze a transaction against the customer's behavioral profile.

    Produces a score from 0-100 and human-readable anomaly signals.
    """

    score = 0
    anomalies = []

    # ==========================================================
    # 1. AMOUNT ANOMALY
    # ==========================================================

    amount = float(transaction.amount)

    max_normal_amount = float(
        profile.get("max_normal_amount", float("inf"))
    )

    if amount > max_normal_amount:
        score += 25
        anomalies.append("Unusually high transaction amount")

    # Strong deviation from typical amount
    typical_amount = profile.get("typical_amount")

    if typical_amount is not None:
        typical_amount = float(typical_amount)

        if typical_amount > 0:
            deviation_ratio = abs(amount - typical_amount) / typical_amount

            if deviation_ratio >= 2:
                score += 15
                anomalies.append(
                    "Transaction amount strongly deviates from customer profile"
                )

    # ==========================================================
    # 2. LOCATION ANOMALY
    # ==========================================================

    location = str(transaction.location)

    usual_locations = [
        str(x).strip()
        for x in profile.get("usual_locations", [])
    ]

    if usual_locations and location not in usual_locations:
        score += 20
        anomalies.append("Unusual transaction location")

    # ==========================================================
    # 3. DEVICE ANOMALY
    # ==========================================================

    device_id = str(transaction.device_id)

    usual_devices = [
        str(x).strip()
        for x in profile.get("usual_devices", [])
    ]

    if usual_devices and device_id not in usual_devices:
        score += 20
        anomalies.append("Unrecognized device")

    # ==========================================================
    # 4. TRANSACTION TIME
    # ==========================================================

    timestamp = transaction.timestamp

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

    transaction_hour = timestamp.hour

    usual_hours = profile.get(
        "usual_transaction_hours",
        list(range(24))
    )

    if transaction_hour not in usual_hours:
        score += 15
        anomalies.append("Unusual transaction time")

    # ==========================================================
    # 5. MERCHANT ANOMALY
    # ==========================================================

    merchant_id = str(transaction.merchant_id)

    usual_merchants = [
        str(x).strip()
        for x in profile.get("usual_merchants", [])
    ]

    if usual_merchants and merchant_id not in usual_merchants:
        score += 10
        anomalies.append("Unusual merchant for customer")

    # ==========================================================
    # 6. VELOCITY
    # ==========================================================

    transaction_count_recent = profile.get(
        "recent_transaction_count",
        0
    )

    normal_transactions_per_hour = profile.get(
        "normal_transactions_per_hour",
        999
    )

    if transaction_count_recent > normal_transactions_per_hour:
        score += 20
        anomalies.append("Abnormally high transaction velocity")

    # ==========================================================
    # 7. BENEFICIARY
    # ==========================================================

    beneficiary_id = getattr(
        transaction,
        "beneficiary_id",
        None
    )

    known_beneficiaries = profile.get(
        "known_beneficiaries",
        []
    )

    if beneficiary_id:

        if known_beneficiaries:

            if beneficiary_id not in known_beneficiaries:
                score += 15
                anomalies.append(
                    "Unrecognized beneficiary"
                )

    # ==========================================================
    # 8. PAYMENT METHOD
    # ==========================================================

    payment_method = str(
        getattr(transaction, "payment_method", "")
    ).lower()

    usual_payment_methods = profile.get(
        "usual_payment_methods",
        []
    )

    if usual_payment_methods:

        if payment_method not in [
            str(x).lower()
            for x in usual_payment_methods
        ]:
            score += 10
            anomalies.append(
                "Unusual payment method"
            )

    # ==========================================================
    # FINAL SCORE
    # ==========================================================

    score = min(score, 100)

    return {
        "behavior_score": score,
        "anomalies": anomalies,
    }