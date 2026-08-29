from typing import Any, Dict, List

from red_team.schemas.feedback import AttackFeedback


class FeedbackBuilder:
    """
    Converts Blue Team analysis into structured feedback
    that can be consumed by the Red Team.
    """

    def build(
        self,
        attack_id: str,
        attack_type: str,
        transaction_id: str,
        analysis: Dict[str, Any],
    ) -> AttackFeedback:

        risk = analysis.get("risk", {})
        fraud = analysis.get("fraud", {})
        behavior = analysis.get("behavior", {})
        explanation = analysis.get("explanation", {})
        decision_data = analysis.get("decision", {})

        risk_score = float(risk.get("final_risk_score", 0.0))

        fraud_probability = float(fraud.get("fraud_probability", 0.0))

        behavior_score = float(behavior.get("behavior_score", 0.0))

        graph_risk_score = float(risk.get("graph_risk_score", 0.0))

        temporal_risk_score = float(risk.get("temporal_risk_score", 0.0))

        security_decision = decision_data.get(
            "decision",
            "UNKNOWN",
        )

        reasons = explanation.get("reasons", [])

        if not isinstance(reasons, list):
            reasons = [str(reasons)]

        detected_signals = self._extract_signals(
            behavior_score=behavior_score,
            graph_risk_score=graph_risk_score,
            temporal_risk_score=temporal_risk_score,
            reasons=reasons,
        )

        detection_success = security_decision in {"BLOCK", "CHALLENGE"}

        return AttackFeedback(
            attack_id=attack_id,
            attack_type=attack_type,
            transaction_id=transaction_id,
            risk_score=risk_score,
            security_decision=security_decision,
            fraud_probability=fraud_probability,
            behavior_score=behavior_score,
            graph_risk_score=graph_risk_score,
            temporal_risk_score=temporal_risk_score,
            detected_signals=detected_signals,
            detection_success=detection_success,
        )

    @staticmethod
    def _extract_signals(
        behavior_score: float,
        graph_risk_score: float,
        temporal_risk_score: float,
        reasons: List[str],
    ) -> List[str]:

        signals = []

        if behavior_score > 0:
            signals.append("behavior")

        if graph_risk_score > 0:
            signals.append("graph")

        if temporal_risk_score > 0:
            signals.append("temporal")

        reason_text = " ".join(str(reason).lower() for reason in reasons)

        if "device" in reason_text:
            signals.append("device")

        if "location" in reason_text:
            signals.append("location")

        if "amount" in reason_text:
            signals.append("amount")

        if "beneficiary" in reason_text:
            signals.append("beneficiary")

        return list(dict.fromkeys(signals))
