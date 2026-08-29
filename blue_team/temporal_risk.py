import pandas as pd


class TemporalRiskEngine:
    """
    Detects suspicious temporal patterns by comparing an incoming
    transaction against the customer's historical transactions.

    Designed to detect attacks that keep individual transaction
    attributes close to normal but manipulate transaction timing.
    """

    def __init__(self, historical_data: pd.DataFrame):

        self.data = historical_data.copy()

        if self.data.empty:
            self.data["_timestamp"] = pd.NaT
            return

        self.data["_timestamp"] = pd.to_datetime(
            self.data["timestamp"],
            errors="coerce",
            utc=True,
        )

    def calculate_risk(self, transaction):

        customer_id = str(
            transaction.get("customer_id", "")
        )

        timestamp = pd.to_datetime(
            transaction.get("timestamp"),
            errors="coerce",
            utc=True,
        )

        if pd.isna(timestamp):

            return {
                "temporal_risk_score": 0,
                "signals": [],
            }

        customer_history = self.data[
            self.data["customer_id"].astype(str) == customer_id
            ].copy()

        # IMPORTANT:
        # When evaluating a historical transaction, remove the
        # transaction itself so it cannot appear as a 0-second
        # "previous transaction".
        transaction_id = str(
            transaction.get("transaction_id", "")
        )

        if "transaction_id" in customer_history.columns:
            customer_history = customer_history[
                customer_history["transaction_id"].astype(str)
                != transaction_id
            ].copy()
            

        if customer_history.empty:

            return {
                "temporal_risk_score": 10,
                "signals": [
                    "No historical temporal profile available"
                ],
            }

        customer_history = customer_history[
            customer_history["_timestamp"].notna()
        ]

        if customer_history.empty:

            return {
                "temporal_risk_score": 10,
                "signals": [
                    "No valid historical timestamps available"
                ],
            }

        # --------------------------------------------------
        # Find closest historical transaction
        # --------------------------------------------------

        customer_history["_time_delta"] = (
            customer_history["_timestamp"] - timestamp
        ).abs()

        closest = customer_history[
            "_time_delta"
        ].min()

        closest_seconds = closest.total_seconds()

        score = 0
        signals = []

        # --------------------------------------------------
        # 1. Extremely short temporal gap
        # --------------------------------------------------

        if closest_seconds <= 30:

            score += 35

            signals.append(
                "Transaction occurs within 30 seconds "
                "of a previous customer transaction"
            )

        elif closest_seconds <= 90:

            score += 25

            signals.append(
                "Transaction occurs within 90 seconds "
                "of a previous customer transaction"
            )

        elif closest_seconds <= 300:

            score += 10

            signals.append(
                "Transaction occurs within 5 minutes "
                "of a previous customer transaction"
            )

        # --------------------------------------------------
        # 2. Same device as historical transaction
        # --------------------------------------------------

        device_id = transaction.get("device_id")

        if device_id:

            same_device = customer_history[
                customer_history["device_id"].astype(str)
                == str(device_id)
            ]

            if not same_device.empty:

                same_device["_time_delta"] = (
                    same_device["_timestamp"] - timestamp
                ).abs()

                device_gap = (
                    same_device["_time_delta"].min()
                    .total_seconds()
                )

                if device_gap <= 90:

                    score += 10

                    signals.append(
                        "Rapid transaction uses a previously "
                        "recognized customer device"
                    )

        # --------------------------------------------------
        # 3. New beneficiary
        # --------------------------------------------------

        beneficiary_id = transaction.get(
            "beneficiary_id"
        )

        if beneficiary_id:

            # Ignore neutral placeholder
            if str(beneficiary_id) not in {
                "None",
                "nan",
                "B_NONE",
            }:

                historical_beneficiaries = set(
                    customer_history[
                        "beneficiary_id"
                    ]
                    .dropna()
                    .astype(str)
                )

                if (
                    str(beneficiary_id)
                    not in historical_beneficiaries
                ):

                    score += 25

                    signals.append(
                        "New beneficiary introduced during "
                        "rapid transaction activity"
                    )

        # --------------------------------------------------
        # 4. Same merchant
        # --------------------------------------------------

        merchant_id = transaction.get(
            "merchant_id"
        )

        if merchant_id:

            nearby = customer_history[
                customer_history["_time_delta"]
                <= pd.Timedelta(seconds=90)
            ]

            if not nearby.empty:

                if (
                    nearby["merchant_id"]
                    .astype(str)
                    .eq(str(merchant_id))
                    .any()
                ):

                    score += 10

                    signals.append(
                        "Rapid transaction repeats a "
                        "recent merchant relationship"
                    )

        score = min(score, 100)

        return {
            "temporal_risk_score": score,
            "signals": signals,
            "nearest_historical_gap_seconds": round(
                closest_seconds,
                2,
            ),
        }