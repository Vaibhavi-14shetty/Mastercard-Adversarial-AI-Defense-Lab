import pandas as pd


DATA_PATH = "simulator/data/transactions_historical.csv"
PROFILE_PATH = "simulator/data/behavior_profiles.csv"
DEVICE_PATH = "simulator/data/devices.csv"
MERCHANT_PATH = "simulator/data/merchants.csv"


def build_features(data=None):
    """
    Build features for either:
    1. Historical transaction data (data=None)
    2. A supplied transaction DataFrame (data=<DataFrame>)
    """

    # --------------------------------------------------
    # Load transaction data
    # --------------------------------------------------

    if data is None:
        data = pd.read_csv(DATA_PATH)
    else:
        data = data.copy()

    # --------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data["hour"] = data["timestamp"].dt.hour
    data["day_of_week"] = data["timestamp"].dt.dayofweek

    # --------------------------------------------------
    # Customer historical average amount
    # --------------------------------------------------

    if "customer_avg_amount" not in data.columns:
        customer_avg = data.groupby("customer_id")["amount"].transform("mean")

        data["customer_avg_amount"] = customer_avg

    # --------------------------------------------------
    # Amount deviation
    # --------------------------------------------------

    data["amount_deviation"] = (data["amount"] - data["customer_avg_amount"]).abs()

    # --------------------------------------------------
    # Behavioral profiles
    # --------------------------------------------------

    profiles = pd.read_csv(PROFILE_PATH)

    profile_columns = [
        "customer_id",
        "typical_amount",
        "amount_std",
        "typical_location",
        "typical_hour_start",
        "typical_hour_end",
    ]

    profiles = profiles[profile_columns]

    data = data.merge(
        profiles,
        on="customer_id",
        how="left",
    )

    # --------------------------------------------------
    # Profile amount deviation
    # --------------------------------------------------

    data["profile_amount_deviation"] = (
        data["amount"] - data["typical_amount"]
    ).abs() / data["amount_std"].replace(0, 1)

    # --------------------------------------------------
    # Location anomaly
    # --------------------------------------------------

    data["location_anomaly"] = (data["location"] != data["typical_location"]).astype(
        int
    )

    # --------------------------------------------------
    # Hour anomaly
    # --------------------------------------------------

    data["hour_anomaly"] = (
        (data["hour"] < data["typical_hour_start"])
        | (data["hour"] > data["typical_hour_end"])
    ).astype(int)

    # --------------------------------------------------
    # Device trust
    # --------------------------------------------------

    if "is_trusted" not in data.columns:
        devices = pd.read_csv(DEVICE_PATH)

        devices = devices[["device_id", "is_trusted"]].drop_duplicates("device_id")

        data = data.merge(
            devices,
            on="device_id",
            how="left",
        )

    data["is_trusted"] = data["is_trusted"].fillna(False).astype(int)

    # --------------------------------------------------
    # Merchant risk
    # --------------------------------------------------

    if "risk_level" not in data.columns:
        merchants = pd.read_csv(MERCHANT_PATH)

        merchants = merchants[["merchant_id", "risk_level"]].drop_duplicates(
            "merchant_id"
        )

        data = data.merge(
            merchants,
            on="merchant_id",
            how="left",
        )

    risk_mapping = {
        "low": 0,
        "medium": 50,
        "high": 100,
    }

    data["merchant_risk_score"] = data["risk_level"].map(risk_mapping).fillna(0)
    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    data = data.drop(
        columns=[
            "typical_amount",
            "amount_std",
            "typical_location",
            "typical_hour_start",
            "typical_hour_end",
        ],
        errors="ignore",
    )

    return data


if __name__ == "__main__":
    print("Feature engineering test...")

    features = build_features()

    print("Feature engineering successful.")
    print("Rows:", len(features))

    print("\nGenerated features:")

    print(
        [
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
    )

    print("\nSample:")

    print(features.head())
