from typing import List, Optional

from pydantic import BaseModel, Field


class AttackFeedback(BaseModel):
    """
    Feedback generated from the Blue Team result.

    This object represents what the Red Team learned
    after an adversarial transaction was analyzed.
    """

    attack_id: str
    attack_type: Optional[str] = None

    risk_score: float
    security_decision: str
    fraud_probability: float

    behavior_score: float
    graph_risk_score: float
    temporal_risk_score: float

    detected_signals: List[str] = Field(default_factory=list)

    detection_success: bool

    transaction_id: Optional[str] = None
