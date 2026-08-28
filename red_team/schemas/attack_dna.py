from typing import Literal, Optional

from pydantic import BaseModel, Field


class AttackDNA(BaseModel):
    attack_id: str

    attack_type: str
    target: str

    amount_pattern: str
    device_pattern: str
    location_pattern: str

    velocity: str

    evasion_level: int = Field(ge=1, le=5)

    description: Optional[str] = None