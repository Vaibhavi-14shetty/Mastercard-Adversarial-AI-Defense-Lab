class BlueTeamFeedbackAdapter:
    """
    Converts Blue Team analysis output into normalized
    feedback signals for the Red Team adaptive engine.
    """

    @staticmethod
    def extract(analysis: dict) -> dict:

        fraud_score = float(
            analysis["risk"].get("fraud_score", 0)
        )

        behavior_score = float(
            analysis["risk"].get("behavior_score", 0)
        )

        graph_score = float(
            analysis["risk"].get("graph_risk_score", 0)
        )

        temporal_score = float(
            analysis["risk"].get("temporal_risk_score", 0)
        )

        risk_score = float(
            analysis["risk"].get("final_risk_score", 0)
        )

        decision = analysis["decision"]["decision"]

        detected_signals = []

        # Fraud model signal
        if fraud_score >= 50:
            detected_signals.append("fraud")

        # Behavioral signal
        if behavior_score >= 40:
            detected_signals.append("behavior")

        # Graph signal
        if graph_score >= 40:
            detected_signals.append("graph")

        # Temporal signal
        if temporal_score >= 10:
            detected_signals.append("temporal")

        return {
            "risk_score": risk_score,
            "decision": decision,
            "detected_signals": detected_signals,
        }