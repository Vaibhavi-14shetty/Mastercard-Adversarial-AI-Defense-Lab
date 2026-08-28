import pandas as pd

from blue_team.feature_engineering import build_features
from blue_team.fraud_model import FraudModel
from blue_team.behavioral_engine import calculate_behavior_score
from blue_team.graph_risk import GraphRiskEngine
from blue_team.risk_fusion import RiskFusionEngine
from blue_team.decision_engine import DecisionEngine
from blue_team.explainability import ExplainabilityEngine
from blue_team.transaction_schema import Transaction


class BlueTeamPipeline:
    def __init__(self):
        self.historical_data = None

        self.fraud_model = FraudModel()
        self.graph_engine = None

        self.fusion_engine = RiskFusionEngine()
        self.decision_engine = DecisionEngine()
        self.explainability_engine = ExplainabilityEngine()

        self.behavior_profiles = None
        self.is_ready = False

    def initialize(self):
        """Load data and initialize all Blue Team components."""

        print("Loading historical transaction data...")

        self.historical_data = build_features()

        print("Training fraud model...")
        self.fraud_model.train(self.historical_data)

        print("Building transaction graph...")

        raw_transactions = pd.read_csv("simulator/data/transactions_historical.csv")

        self.graph_engine = GraphRiskEngine(raw_transactions)

        print("Loading behavioral profiles...")

        self.behavior_profiles = pd.read_csv("simulator/data/behavior_profiles.csv")

        self.is_ready = True

        print("Blue Team pipeline initialized successfully.")

    def _get_behavior_profile(self, customer_id):
        """Build the behavioral profile expected by the behavioral engine."""

        profile = self.behavior_profiles[
            self.behavior_profiles["customer_id"] == customer_id
        ]

        if profile.empty:
            return {
                "max_normal_amount": float("inf"),
                "usual_locations": [],
                "usual_devices": [],
                "usual_transaction_hours": list(range(24)),
            }

        row = profile.iloc[0]

        typical_amount = float(row["typical_amount"])
        amount_std = float(row["amount_std"])

        max_normal_amount = typical_amount + (3 * amount_std)

        usual_locations = [str(row["typical_location"]).strip()]

        usual_devices = [
            device.strip() for device in str(row["typical_device_ids"]).split(",")
        ]

        start_hour = int(row["typical_hour_start"])
        end_hour = int(row["typical_hour_end"])

        if start_hour <= end_hour:
            usual_transaction_hours = list(range(start_hour, end_hour + 1))
        else:
            usual_transaction_hours = list(range(start_hour, 24)) + list(
                range(0, end_hour + 1)
            )

        return {
            "max_normal_amount": max_normal_amount,
            "usual_locations": usual_locations,
            "usual_devices": usual_devices,
            "usual_transaction_hours": usual_transaction_hours,
        }

    def analyze(self, transaction):
        """Run one transaction through the complete Blue Team."""

        if not self.is_ready:
            raise RuntimeError("Blue Team pipeline has not been initialized.")

        if isinstance(transaction, Transaction):
            transaction_dict = transaction.model_dump()
        else:
            transaction_dict = transaction

        transaction_df = pd.DataFrame([transaction_dict])

        # --------------------------------------------------
        # 1. Feature Engineering
        # --------------------------------------------------

        features = build_features(transaction_df)

        # --------------------------------------------------
        # 2. Fraud ML
        # --------------------------------------------------

        fraud_result = self.fraud_model.predict(features)[0]

        # --------------------------------------------------
        # 3. Behavioral Detection
        # --------------------------------------------------

        customer_id = transaction_dict["customer_id"]

        profile = self._get_behavior_profile(customer_id)

        # Normalize values before Pydantic validation
        transaction_dict["timestamp"] = str(transaction_dict["timestamp"])

        if pd.isna(transaction_dict.get("attack_id")):
            transaction_dict["attack_id"] = None
        else:
            transaction_dict["attack_id"] = str(transaction_dict["attack_id"])

        transaction_object = Transaction(**transaction_dict)

        behavior_result = calculate_behavior_score(transaction_object, profile)

        # --------------------------------------------------
        # 4. Graph Risk
        # --------------------------------------------------

        graph_result = self.graph_engine.calculate_risk(transaction_dict)

        # --------------------------------------------------
        # 5. Risk Fusion
        # --------------------------------------------------

        fusion_result = self.fusion_engine.calculate_risk(
            fraud_probability=fraud_result["fraud_probability"],
            behavior_score=behavior_result["behavior_score"],
            graph_risk_score=graph_result["graph_risk_score"],
        )

        # --------------------------------------------------
        # 6. Decision
        # --------------------------------------------------

        decision_result = self.decision_engine.decide(fusion_result["final_risk_score"])

        # --------------------------------------------------
        # 7. Explainability
        # --------------------------------------------------

        explanation = self.explainability_engine.generate_explanation(
            fraud_result,
            behavior_result,
            graph_result,
            fusion_result["final_risk_score"],
            decision_result["decision"],
        )

        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------

        return {
            "transaction_id": transaction_dict["transaction_id"],
            "fraud": fraud_result,
            "behavior": behavior_result,
            "graph": graph_result,
            "risk": fusion_result,
            "decision": decision_result,
            "explanation": explanation,
        }


if __name__ == "__main__":
    print("=== BLUE TEAM PIPELINE TEST ===")

    pipeline = BlueTeamPipeline()

    pipeline.initialize()

    # Use a real historical transaction from the dataset
    transaction = pipeline.historical_data.iloc[0].to_dict()

    result = pipeline.analyze(transaction)

    print("\n=== FINAL ANALYSIS ===")

    print("Transaction:", result["transaction_id"])
    print("Fraud:", result["fraud"])
    print("Behavior:", result["behavior"])
    print("Graph:", result["graph"])
    print("Risk:", result["risk"])
    print("Decision:", result["decision"])
    print("Explanation:", result["explanation"])
