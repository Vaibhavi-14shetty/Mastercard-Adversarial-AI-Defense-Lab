import json
from pathlib import Path


ATTACK_FILE = Path(__file__).parent / "attacks.json"


with open(ATTACK_FILE, "r", encoding="utf-8") as file:
    attacks = json.load(file)


print(f"Loaded {len(attacks)} attack strategies\n")

for attack in attacks:
    print(
        f"{attack['attack_id']} | "
        f"{attack['attack_type']} | "
        f"Evasion Level: {attack['evasion_level']}"
    )

print("\nAttack Knowledge Base test successful!")