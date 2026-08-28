import pandas as pd
from sklearn.ensemble import IsolationForest

from blue_team.feature_engineering import build_features


class FraudModel:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100, contamination=0.05, random_state=42
        )

        self.feature_columns = [
            "amount",
            "hour",
            "day_of_week",
            "customer_avg_amount",
            "amount_deviation",
            "profile_amount_deviation",
            "location_anomaly",
            "hour_anomaly",
            "is_trusted",
            "merchant_risk_score",
        ]

        self.is_trained = False

    def train(self, data):
        """Train the anomaly detector on legitimate historical transactions."""

        X = data[self.feature_columns].copy()

        X = X.fillna(0)

        self.model.fit(X)

        self.is_trained = True

    def predict(self, transaction_data):
        """Return anomaly and fraud-risk information."""

        if not self.is_trained:
            raise RuntimeError("Fraud model has not been trained yet.")

        X = transaction_data[self.feature_columns].copy()
        X = X.fillna(0)

        predictions = self.model.predict(X)
        anomaly_scores = self.model.decision_function(X)

        results = []

        for prediction, score in zip(predictions, anomaly_scores):
            # Isolation Forest:
            # negative score = more anomalous
            # positive score = more normal

            anomaly_score = max(0, min(1, 0.5 - score))

            results.append(
                {
                    "is_anomaly": prediction == -1,
                    "fraud_probability": round(float(anomaly_score), 3),
                }
            )

        return results


if __name__ == "__main__":
    print("Loading historical transaction data...")

    data = build_features()

    model = FraudModel()

    print("Training Isolation Forest...")

    model.train(data)

    print("Model training successful.")

    # Test using a few historical transactions
    sample = data.head(5)

    results = model.predict(sample)

    print("\nSample predictions:")

    for i, result in enumerate(results):
        print(f"Transaction {i + 1}: {result}")
