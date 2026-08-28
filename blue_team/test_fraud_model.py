import pandas as pd

from blue_team.fraud_model import FraudModel
from blue_team.feature_engineering import build_features


def main():
    print("Loading historical data...")
    historical_data = build_features()

    print("Training model...")
    model = FraudModel()
    model.train(historical_data)

    test_transactions = pd.DataFrame(
        [
            {
                "amount": 2500,
                "hour": 14,
                "day_of_week": 4,
                "customer_avg_amount": 2800,
                "amount_deviation": 300,
                "profile_amount_deviation": 0.11,
                "location_anomaly": 0,
                "hour_anomaly": 0,
                "is_trusted": 1,
                "merchant_risk_score": 0,
            },
            {
                "amount": 25000,
                "hour": 3,
                "day_of_week": 4,
                "customer_avg_amount": 2800,
                "amount_deviation": 22200,
                "profile_amount_deviation": 7.9,
                "location_anomaly": 1,
                "hour_anomaly": 1,
                "is_trusted": 0,
                "merchant_risk_score": 100,
            },
        ]
    )

    results = model.predict(test_transactions)

    print("\n--- MODEL VALIDATION ---")

    print("\nNormal transaction:")
    print(results[0])

    print("\nSuspicious transaction:")
    print(results[1])


if __name__ == "__main__":
    main()
