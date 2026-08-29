class BlueTeamFeedbackAdapter:
    """
    Converts Blue Team analysis output into normalized
    feedback signals for the Red Team adaptive engine.
    """

    @staticmethod
    def extract(analysis: dict) -> dict:

        risk = analysis.get("risk", {})
        fraud = analysis.get("fraud", {})
        behavior = analysis.get("behavior", {})
        decision_data = analysis.get("decision", {})

        fraud_probability = float(fraud.get("fraud_probability", 0.0))

        behavior_score = float(behavior.get("behavior_score", 0.0))

        graph_score = float(risk.get("graph_risk_score", 0.0))

        temporal_score = float(risk.get("temporal_risk_score", 0.0))

        risk_score = float(risk.get("final_risk_score", 0.0))

        decision = decision_data.get("decision", "UNKNOWN")

        detected_signals = []

        # Fraud model signal
        # fraud_probability is 0-1
        if fraud_probability >= 0.5:
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
