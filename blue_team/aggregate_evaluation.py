from blue_team.evaluator import Evaluator


def main():
    evaluator = Evaluator()

    results = [
        {
            "transaction_id": "TXTEST_ATK001",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK001",
        },
        {
            "transaction_id": "TXTEST_ATK002",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK002",
        },
        {
            "transaction_id": "TXTEST_ATK003",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK003",
        },
        {
            "transaction_id": "TXTEST_ATK004",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK004",
        },
        {
            "transaction_id": "TXTEST_ATK005",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK005",
        },
        {
            "transaction_id": "TXTEST_ATK006",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATK006",
        },
    ]

    metrics = evaluator.evaluate(results)

    print("=== AGGREGATE BLUE TEAM EVALUATION ===")

    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
