from copy import deepcopy

from red_team.schemas.attack_dna import AttackDNA


class AdaptiveAttackEngine:
    """
    Evolves an existing attack strategy using Blue Team feedback.

    The goal is not to randomly change an attack.
    The goal is to reduce the signals that exposed the previous attack.
    """

    def adapt(
        self,
        attack: AttackDNA,
        risk_score: float,
        decision: str,
        detected_signals: list[str] | None = None,
    ) -> AttackDNA:

        detected_signals = detected_signals or []

        evolved = deepcopy(attack)

        # --------------------------------------------------
        # Create a new attack version
        # --------------------------------------------------

        base_attack_id = attack.attack_id.split("-V")[0]

        version = 2

        if "-V" in attack.attack_id:
            try:
                previous_version = int(
                    attack.attack_id.split("-V")[-1]
                )
                version = previous_version + 1
            except ValueError:
                version = 2

        evolved.attack_id = f"{base_attack_id}-V{version}"

        # --------------------------------------------------
        # Increase evasion when Blue Team detects the attack
        # --------------------------------------------------

        if decision in {"BLOCK", "CHALLENGE"}:

            evolved.evasion_level = min(
                5,
                attack.evasion_level + 1
            )

        # --------------------------------------------------
        # Adapt based on detected signals
        # --------------------------------------------------

        signals = {
            str(signal).lower()
            for signal in detected_signals
        }

        # Temporal detection:
        # make timing less suspicious.
        if "temporal" in signals:
            evolved.velocity = "normal"

        # Graph detection:
        # reduce suspicious relationship changes.
        if "graph" in signals:
            evolved.device_pattern = "known"

        # Behavioral detection:
        # keep spending closer to normal.
        if "behavior" in signals:
            evolved.amount_pattern = "near_normal"

        # Fraud model detection:
        # reduce obvious transaction anomalies.
        if "fraud" in signals:
            evolved.amount_pattern = "near_normal"

        # --------------------------------------------------
        # If the attack was strongly detected,
        # make the overall strategy more evasive.
        # --------------------------------------------------

        if risk_score >= 80:

            evolved.evasion_level = min(
                5,
                evolved.evasion_level + 1
            )

            if evolved.velocity == "high":
                evolved.velocity = "variable"

        # --------------------------------------------------
        # If only challenged, make a smaller adaptation.
        # --------------------------------------------------

        elif decision == "CHALLENGE":

            evolved.evasion_level = min(
                5,
                evolved.evasion_level + 1
            )

        evolved.description = (
            f"Adaptive evolution of {base_attack_id} based on "
            f"Blue Team feedback. Previous risk={risk_score:.2f}, "
            f"decision={decision}."
        )

        return evolved