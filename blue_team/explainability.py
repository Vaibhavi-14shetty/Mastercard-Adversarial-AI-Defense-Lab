class ExplainabilityEngine:
    def generate_explanation(
        self,
        fraud_result,
        behavior_result,
        graph_result,
        final_risk_score,
        decision,
    ):
        reasons = []

        # Fraud ML signal
        fraud_probability = fraud_result.get("fraud_probability", 0)

        if fraud_probability >= 0.70:
            reasons.append("High fraud model risk")
        elif fraud_probability >= 0.50:
            reasons.append("Moderate fraud model risk")

        # Behavioral signal
        behavior_score = behavior_result.get("behavior_score", 0)

        anomalies = behavior_result.get("anomalies", [])

        if behavior_score >= 70:
            reasons.append("High behavioral anomaly")

        elif behavior_score >= 40:
            reasons.append("Moderate behavioral anomaly")

        # Add specific behavioral anomalies
        for anomaly in anomalies:
            if anomaly not in reasons:
                reasons.append(anomaly)

        # Graph signal
        graph_score = graph_result.get("graph_risk_score", 0)

        signals = graph_result.get("signals", [])

        if graph_score >= 70:
            reasons.append("High graph risk")

        elif graph_score >= 40:
            reasons.append("Suspicious transaction relationships")

        # Add graph signals
        for signal in signals:
            if signal not in reasons:
                reasons.append(signal)

        # Fallback
        if not reasons:
            reasons.append("No significant risk indicators detected")

        return {
            "risk_score": round(float(final_risk_score), 2),
            "decision": decision,
            "reasons": reasons,
        }


if __name__ == "__main__":
    engine = ExplainabilityEngine()

    fraud_result = {
        "fraud_probability": 0.82,
        "is_anomaly": True,
    }

    behavior_result = {
        "behavior_score": 76,
        "anomalies": [
            "Unusual transaction amount",
            "Unrecognized device",
        ],
    }

    graph_result = {
        "graph_risk_score": 85,
        "signals": ["Beneficiary connected to multiple customers"],
    }

    result = engine.generate_explanation(
        fraud_result,
        behavior_result,
        graph_result,
        87,
        "BLOCK",
    )

    print("=== EXPLAINABILITY TEST ===")
    print(result)
