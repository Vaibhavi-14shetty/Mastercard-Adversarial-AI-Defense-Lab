class DecisionEngine:
    def __init__(self):
        self.allow_threshold = 30
        self.challenge_threshold = 70

    def decide(self, risk_score):
        """
        Convert the final risk score into a transaction decision.
        """

        risk_score = float(risk_score)

        if risk_score <= self.allow_threshold:
            decision = "ALLOW"

        elif risk_score <= self.challenge_threshold:
            decision = "CHALLENGE"

        else:
            decision = "BLOCK"

        return {
            "risk_score": round(risk_score, 2),
            "decision": decision,
        }


if __name__ == "__main__":
    engine = DecisionEngine()

    test_scores = [20, 50, 70, 71, 90]

    print("=== DECISION ENGINE TEST ===")

    for score in test_scores:
        result = engine.decide(score)
        print(result)
