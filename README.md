# 🛡️ Mastercard : Adversarial AI Defense Lab

### **Build the Attack. Test the Defense. Learn. Adapt.**

> An AI-powered adversarial security laboratory for discovering, simulating,
> evaluating, and defending against evolving GenAI-powered payment fraud.

---

## 🚨 The Problem

Generative AI is changing the fraud landscape.

Fraudsters can now create highly convincing social-engineering attacks,
impersonation attempts, synthetic identities, and adaptive payment behaviors
at unprecedented speed.

Traditional fraud detection systems are generally trained on historical
patterns.

But what happens when the attacker continuously changes the pattern?

### **The attacker evolves. Shouldn't the defense evolve too?**

This project approaches payment security as an **adversarial learning
problem**.

Instead of waiting for new fraud to appear in the real world, we create a
controlled synthetic payment ecosystem where an AI-powered **Red Team**
continuously attempts to bypass an AI-powered **Blue Team**.

---

# 💡 Our Approach

The system creates a continuous adversarial loop:

```text
        🧪 SYNTHETIC PAYMENT WORLD
                    │
                    ▼
              🔴 RED TEAM
           Generate Attack
                    │
                    ▼
            💳 PAYMENT SIMULATION
                    │
                    ▼
              🔵 BLUE TEAM
             Detect Attack
                    │
                    ▼
             🧠 RISK ENGINE
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       ALLOW    CHALLENGE    BLOCK
                    │
                    ▼
          📊 ADVERSARIAL EVALUATION
                    │
                    ▼
              🔄 FEEDBACK LOOP
                    │
                    ▼
           STRONGER NEXT ATTACK
                    │
                    └──────────► 🔴
