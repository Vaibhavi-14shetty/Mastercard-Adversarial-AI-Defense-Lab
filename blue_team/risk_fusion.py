class RiskFusionEngine:
    def __init__(
        self,
        fraud_weight=0.40,
        behavior_weight=0.35,
        graph_weight=0.25,
    ):
        self.fraud_weight = fraud_weight
        self.behavior_weight = behavior_weight
        self.graph_weight = graph_weight

    def calculate_risk(
        self,
        fraud_probability,
        behavior_score,
        graph_risk_score,
    ):
        """
        Combine fraud ML, behavioral, and graph signals
        into a single risk score from 0 to 100.
        """

        fraud_score = float(fraud_probability) * 100
        behavior_score = float(behavior_score)
        graph_score = float(graph_risk_score)

        final_score = (
            fraud_score * self.fraud_weight
            + behavior_score * self.behavior_weight
            + graph_score * self.graph_weight
        )

        final_score = round(max(0, min(100, final_score)), 2)

        return {
            "fraud_score": round(fraud_score, 2),
            "behavior_score": round(behavior_score, 2),
            "graph_risk_score": round(graph_score, 2),
            "final_risk_score": final_score,
        }


if __name__ == "__main__":
    engine = RiskFusionEngine()

    result = engine.calculate_risk(
        fraud_probability=0.70,
        behavior_score=80,
        graph_risk_score=60,
    )

    print("=== RISK FUSION TEST ===")
    print(result)
