from copy import deepcopy

from red_team.schemas.attack_dna import AttackDNA


class AdaptiveEngine:
    """
    Evolves an existing AttackDNA based on Blue Team feedback.

    The engine does not create a new attack family.
    It modifies the existing attack strategy so that the
    next generation can test a different detection surface.
    """

    def adapt(
        self,
        attack: AttackDNA,
        risk_score: float,
        decision: str,
        detected_signals: list[str],
    ) -> AttackDNA:

        evolved = deepcopy(attack)

        signals = {
            signal.lower().strip()
            for signal in detected_signals
        }

        decision = decision.upper()

        # --------------------------------------------------
        # Increase evasion pressure when the attack is caught
        # --------------------------------------------------

        if decision in {"BLOCK", "CHALLENGE"}:
            evolved.evasion_level = min(
                5,
                evolved.evasion_level + 1
            )

        # --------------------------------------------------
        # Adapt against behavioral detection
        # --------------------------------------------------

        if "behavior" in signals:

            if evolved.amount_pattern == "high":
                evolved.amount_pattern = "near_normal"

            elif evolved.amount_pattern == "near_normal":
                evolved.amount_pattern = "normal"

        # --------------------------------------------------
        # Adapt against graph detection
        # --------------------------------------------------

        if "graph" in signals:

            if evolved.device_pattern in {"new", "synthetic"}:
                evolved.device_pattern = "known"

            if evolved.location_pattern == "unusual":
                evolved.location_pattern = "normal"

        # --------------------------------------------------
        # Adapt against temporal detection
        # --------------------------------------------------

        if "temporal" in signals:

            if evolved.velocity == "high":
                evolved.velocity = "medium"

            elif evolved.velocity == "medium":
                evolved.velocity = "normal"

            elif evolved.velocity == "variable":
                evolved.velocity = "normal"

        # --------------------------------------------------
        # Adapt against fraud-model detection
        # --------------------------------------------------

        if "fraud" in signals:

            if evolved.amount_pattern == "high":
                evolved.amount_pattern = "near_normal"

            if evolved.location_pattern == "unusual":
                evolved.location_pattern = "normal"

        # --------------------------------------------------
        # ATK006 is already an evasion attack.
        # Keep it subtle rather than increasing the level
        # beyond the valid AttackDNA range.
        # --------------------------------------------------

        if attack.attack_id == "ATK006":

            evolved.amount_pattern = (
                "normal"
                if "fraud" in signals or "behavior" in signals
                else evolved.amount_pattern
            )

            evolved.velocity = (
                "normal"
                if "temporal" in signals
                else evolved.velocity
            )

            evolved.device_pattern = (
                "known"
                if "graph" in signals
                else evolved.device_pattern
            )

        # --------------------------------------------------
        # Create a versioned attack ID
        # --------------------------------------------------

        evolved.attack_id = f"{attack.attack_id}-V2"

        # --------------------------------------------------
        # Preserve attack identity while documenting evolution
        # --------------------------------------------------

        evolved.description = (
            f"Evolved version of {attack.attack_id}. "
            f"Adapted after Blue Team feedback: "
            f"risk={risk_score:.2f}, "
            f"decision={decision}, "
            f"signals={sorted(signals)}."
        )

        return evolved