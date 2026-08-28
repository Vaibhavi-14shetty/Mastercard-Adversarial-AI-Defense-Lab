import json
import random
from pathlib import Path

from red_team.schemas.attack_dna import AttackDNA

class AttackComposer:
    """
    Selects attack strategies from the Red Team knowledge base
    and converts them into validated AttackDNA objects.
    """

    def __init__(self):
        knowledge_base_path = (
            Path(__file__).resolve().parent.parent
            / "knowledge_base"
            / "attacks.json"
        )

        with open(knowledge_base_path, "r", encoding="utf-8") as file:
            self.attacks = json.load(file)

    def get_attack(self, attack_id: str) -> AttackDNA:
        """
        Return a specific attack strategy by attack ID.
        """

        for attack in self.attacks:
            if attack["attack_id"] == attack_id:
                return AttackDNA(**attack)

        raise ValueError(f"Attack ID not found: {attack_id}")

    def random_attack(self) -> AttackDNA:
        """
        Randomly select an attack strategy.
        """

        attack = random.choice(self.attacks)

        return AttackDNA(**attack)