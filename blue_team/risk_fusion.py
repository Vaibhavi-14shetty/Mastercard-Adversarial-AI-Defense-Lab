class RiskFusionEngine:

    def __init__(
        self,
        fraud_weight=0.35,
        behavior_weight=0.25,
        graph_weight=0.20,
        temporal_weight=0.20,
    ):

        self.fraud_weight = fraud_weight
        self.behavior_weight = behavior_weight
        self.graph_weight = graph_weight
        self.temporal_weight = temporal_weight

    def calculate_risk(
        self,
        fraud_probability,
        behavior_score,
        graph_risk_score,
        temporal_risk_score,
    ):
        """
        Combine ML, behavioral, graph, and temporal signals
        into a final 0-100 adversarial payment risk score.

        The fusion layer also detects compound attack patterns
        where several individually moderate signals become
        significantly more suspicious when observed together.
        """

        fraud_score = float(fraud_probability) * 100
        behavior_score = float(behavior_score)
        graph_score = float(graph_risk_score)
        temporal_score = float(temporal_risk_score)

        # --------------------------------------------------
        # BASE FUSION
        # --------------------------------------------------

        base_score = (
            fraud_score * self.fraud_weight
            + behavior_score * self.behavior_weight
            + graph_score * self.graph_weight
            + temporal_score * self.temporal_weight
        )

        # --------------------------------------------------
        # COMPOUND SIGNALS
        # --------------------------------------------------

        compound_bonus = 0
        compound_signals = []

        # --------------------------------------------------
        # 1. Moderate fraud + suspicious graph
        # --------------------------------------------------

        if fraud_score >= 30 and graph_score >= 30:

            compound_bonus += 8

            compound_signals.append(
                "Moderate fraud signal combined with "
                "suspicious graph activity"
            )

        # --------------------------------------------------
        # 2. Fraud + graph + temporal convergence
        # --------------------------------------------------
        # Important for adversarial attacks that keep
        # individual features close to normal.

        if (
            fraud_score >= 30
            and graph_score >= 30
            and temporal_score >= 10
        ):

            compound_bonus += 8

            compound_signals.append(
                "Fraud, relationship, and temporal signals "
                "converge on suspicious activity"
            )

        # --------------------------------------------------
        # 3. Strong temporal + graph anomaly
        # --------------------------------------------------

        if temporal_score >= 25 and graph_score >= 30:

            compound_bonus += 10

            compound_signals.append(
                "Rapid transaction activity combined "
                "with suspicious graph behavior"
            )

        # --------------------------------------------------
        # 4. Very strong temporal + graph relationship
        # --------------------------------------------------

        if temporal_score >= 35 and graph_score >= 30:

            compound_bonus += 8

            compound_signals.append(
                "Rapid transaction combined with "
                "new or suspicious relationship"
            )

        # --------------------------------------------------
        # 5. Behavioral + graph convergence
        # --------------------------------------------------

        if behavior_score >= 30 and graph_score >= 30:

            compound_bonus += 6

            compound_signals.append(
                "Behavioral anomaly combined with "
                "suspicious transaction relationships"
            )

        # --------------------------------------------------
        # 6. Strong multi-signal convergence
        # --------------------------------------------------

        active_signals = sum(
            [
                fraud_score >= 40,
                behavior_score >= 40,
                graph_score >= 40,
                temporal_score >= 40,
            ]
        )

        if active_signals >= 3:

            compound_bonus += 10

            compound_signals.append(
                "Multiple independent security signals "
                "converge on elevated transaction risk"
            )

        # --------------------------------------------------
        # 7. Three moderate independent signals
        # --------------------------------------------------
        # This is specifically useful for subtle attacks
        # such as adversarial evasion.

        moderate_signals = sum(
            [
                fraud_score >= 30,
                behavior_score >= 20,
                graph_score >= 25,
                temporal_score >= 10,
            ]
        )

        if moderate_signals >= 3:

            compound_bonus += 6

            compound_signals.append(
                "Multiple moderate security signals "
                "indicate coordinated suspicious activity"
            )

        # --------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------

        final_score = base_score + compound_bonus

        final_score = round(
            max(0, min(100, final_score)),
            2,
        )

        return {
            "fraud_score": round(
                fraud_score,
                2,
            ),

            "behavior_score": round(
                behavior_score,
                2,
            ),

            "graph_risk_score": round(
                graph_score,
                2,
            ),

            "temporal_risk_score": round(
                temporal_score,
                2,
            ),

            "base_risk_score": round(
                base_score,
                2,
            ),

            "compound_bonus": compound_bonus,

            "compound_signals": compound_signals,

            "final_risk_score": final_score,
        }


if __name__ == "__main__":

    engine = RiskFusionEngine()

    result = engine.calculate_risk(
        fraud_probability=0.70,
        behavior_score=80,
        graph_risk_score=60,
        temporal_risk_score=50,
    )

    print("=== RISK FUSION TEST ===")
    print(result)