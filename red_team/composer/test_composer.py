from red_team.composer.attack_composer import AttackComposer


composer = AttackComposer()

print("Testing specific attack...\n")

attack = composer.get_attack("ATK001")

print(attack.model_dump())

print("\nTesting random attack...\n")

random_attack = composer.random_attack()

print(random_attack.model_dump())

print("\nAttack Composer test successful!")