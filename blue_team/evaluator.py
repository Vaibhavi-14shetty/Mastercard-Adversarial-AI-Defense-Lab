class Evaluator:
    def evaluate(self, results):
        """
        Evaluate Blue Team decisions against actual transaction outcomes.

        Each result should contain:
        - is_fraud: actual fraud label
        - decision: ALLOW / CHALLENGE / BLOCK
        - attack_id: optional attack identifier
        """

        total_transactions = len(results)

        fraud_transactions = [r for r in results if r.get("is_fraud") is True]

        normal_transactions = [r for r in results if r.get("is_fraud") is False]

        detected_attacks = [
            r for r in fraud_transactions if r.get("decision") in ("CHALLENGE", "BLOCK")
        ]

        missed_attacks = [r for r in fraud_transactions if r.get("decision") == "ALLOW"]

        false_positives = [
            r
            for r in normal_transactions
            if r.get("decision") in ("CHALLENGE", "BLOCK")
        ]

        total_attacks = len(fraud_transactions)

        if total_attacks > 0:
            detection_rate = (len(detected_attacks) / total_attacks) * 100

            attack_success_rate = (len(missed_attacks) / total_attacks) * 100
        else:
            detection_rate = 0
            attack_success_rate = 0

        if len(normal_transactions) > 0:
            false_positive_rate = (
                len(false_positives) / len(normal_transactions)
            ) * 100
        else:
            false_positive_rate = 0

        return {
            "total_transactions": total_transactions,
            "total_attacks": total_attacks,
            "detected_attacks": len(detected_attacks),
            "missed_attacks": len(missed_attacks),
            "false_positives": len(false_positives),
            "detection_rate": round(detection_rate, 2),
            "attack_success_rate": round(attack_success_rate, 2),
            "false_positive_rate": round(false_positive_rate, 2),
        }


if __name__ == "__main__":
    evaluator = Evaluator()

    # Small synthetic evaluation set
    test_results = [
        # Normal transaction correctly allowed
        {
            "transaction_id": "TX001",
            "is_fraud": False,
            "decision": "ALLOW",
            "attack_id": None,
        },
        # Normal transaction incorrectly challenged
        {
            "transaction_id": "TX002",
            "is_fraud": False,
            "decision": "CHALLENGE",
            "attack_id": None,
        },
        # Fraud correctly blocked
        {
            "transaction_id": "TX003",
            "is_fraud": True,
            "decision": "BLOCK",
            "attack_id": "ATTACK001",
        },
        # Fraud correctly challenged
        {
            "transaction_id": "TX004",
            "is_fraud": True,
            "decision": "CHALLENGE",
            "attack_id": "ATTACK002",
        },
        # Fraud missed by Blue Team
        {
            "transaction_id": "TX005",
            "is_fraud": True,
            "decision": "ALLOW",
            "attack_id": "ATTACK003",
        },
    ]

    metrics = evaluator.evaluate(test_results)

    print("=== EVALUATOR TEST ===")

    for key, value in metrics.items():
        print(f"{key}: {value}")
