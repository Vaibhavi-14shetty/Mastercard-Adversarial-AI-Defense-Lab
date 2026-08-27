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

🎯 Objectives
1. Simulate

Create a realistic but completely synthetic payment environment.

2. Attack

Generate diverse and evolving GenAI-powered fraud scenarios through an
AI-assisted Red Team.

3. Detect

Use machine learning, behavioral analysis, and graph-based signals to
identify suspicious payment activity.

4. Decide

Convert multiple risk signals into an explainable risk score and response.

5. Evaluate

Measure whether the defense successfully detected or missed adversarial
attacks.

6. Adapt

Feed attack outcomes back into the adversarial loop to generate stronger
future attacks and expose defensive weaknesses.

🏗️ System Architecture

The platform is organized into interconnected adversarial and defensive
layers.

                         🛡️ ADVERSARIAL PAYMENT SECURITY LAB
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
          🌐 THREAT INTELLIGENCE                🧪 SYNTHETIC PAYMENT
                 LAYER                                WORLD
                    │                                   │
                    ▼                                   ▼
          ATTACK KNOWLEDGE BASE              Customers • Accounts
                    │                         Cards • Devices
                    ▼                         Merchants • Beneficiaries
              🧬 ATTACK DNA                   • Transactions
                    │                                   │
                    ▼                                   │
              🔴 RED AGENT                              │
                    │                                   │
                    ▼                                   │
             ATTACK COMPOSER                            │
                    │                                   │
                    ▼                                   │
          SYNTHETIC ATTACK GENERATOR                    │
                    │                                   │
                    └──────────────┬────────────────────┘
                                   ▼
                           FIDELITY ENGINE
                                   │
                              ┌────┴────┐
                              ▼         ▼
                           REJECT    ACCEPT
                                        │
                                        ▼
                            THREAT-TO-PAYMENT GRAPH
                                        │
                                        ▼
                                  🔵 BLUE TEAM
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                     FRAUD ML      BEHAVIOR      GRAPH RISK
                         └──────────────┼──────────────┘
                                        ▼
                               RISK FUSION ENGINE
                                        │
                                        ▼
                                  RISK SCORE 0–100
                                        │
                                        ▼
                                  EXPLAINABILITY
                                        │
                             ┌──────────┼──────────┐
                             ▼          ▼          ▼
                          🟢 ALLOW  🟡 CHALLENGE 🔴 BLOCK
                                        │
                                        ▼
                             ADVERSARIAL EVALUATOR
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                     DETECTED        MISSED      FALSE POSITIVE
                         └──────────────┼──────────────┘
                                        ▼
                                VULNERABILITY MAP
                                        │
                                        ▼
                                  READINESS SCORE
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                  🔴 RED FEEDBACK                🔵 BLUE FEEDBACK
                         │                             │
                         └──────────────┬──────────────┘
                                        ▼
                                   🔄 NEXT ROUND
🧪 Synthetic Payment World

Before attacking a payment system, we need a realistic environment to attack.

Our synthetic world contains interconnected entities:

👤 Customer
   │
   ├── 💰 Account
   │      └── 💳 Card
   │
   ├── 📱 Device
   │
   └── 🏪 Merchant

👤 Customer
   │
   └── 💸 Transaction
           ├── Merchant
           ├── Beneficiary
           ├── Device
           ├── Location
           └── Amount

Every customer also has a synthetic behavioral baseline, such as:

Typical transaction amount
Typical transaction frequency
Typical location
Typical devices
Typical merchants
Typical transaction hours

This allows the system to compare:

What is normal for the customer?

against:

What is happening now?

🔴 Red Team — Adversarial Intelligence

The Red Team acts as an adaptive attacker inside the synthetic environment.

It does not simply generate random fraudulent transactions.

It uses structured Attack DNA to construct different attack variations.

Example Attack DNA
{
  "attack_type": "behavioral_evasion",
  "target": "high_value_customer",
  "amount_pattern": "near_normal",
  "device_pattern": "trusted",
  "location_pattern": "normal",
  "velocity": "moderate",
  "evasion_level": "high"
}

The Red Agent can modify these characteristics to create new attack
variations.

Example
Attack A
₹25,000 + New Device + New Location
             ↓
         DETECTED
             ↓
Attack B
₹4,500 + Known Device + Normal Location
             ↓
          MISSED
             ↓
Attack C
₹4,200 + Known Device + Slight Behavior Change

This allows us to explore where the defense becomes vulnerable.

🔵 Blue Team — Adaptive Defense

The Blue Team evaluates every simulated transaction using multiple
independent signals.

Fraud ML

Estimates the probability that a transaction is fraudulent.

Behavioral Analysis

Compares current activity against the customer's historical behavior.

Graph Risk

Analyzes relationships between:

Customers
   ↓
Accounts
   ↓
Devices
   ↓
Merchants
   ↓
Beneficiaries
   ↓
Transactions

Suspicious relationships can increase the overall risk.

🧠 Risk Fusion

Instead of trusting one model, the system combines multiple signals.

Fraud ML Score
      +
Behavior Score
      +
Graph Risk
      +
Contextual Signals
      ↓
🧠 RISK FUSION
      ↓
RISK SCORE: 0–100

Example:

Fraud ML       → 82
Behavior       → 74
Graph Risk     → 91
Context        → 80

Final Risk     → 84
🚦 Decision Engine

The final risk score determines the response.

Risk	Response
🟢 0–30	ALLOW
🟡 31–70	CHALLENGE
🔴 71–100	BLOCK

The system also provides an explanation for the decision.

Example:

Risk Score: 87

Decision: BLOCK

Reasons:
• Unusual transaction velocity
• Suspicious beneficiary relationship
• Significant behavioral deviation
🧬 Attack DNA

Attack DNA is a structured representation of an attack's
characteristics.

It describes:

Attack type
Target
Payment behavior
Device behavior
Location behavior
Transaction velocity
Evasion strategy
Difficulty

This allows the Red Team to generate variations, rather than relying
on a fixed set of fraud examples.

🕸️ Threat-to-Payment Graph

Payment fraud rarely exists as an isolated transaction.

The system therefore models payment relationships as a graph.

              Customer A
              /        \
          Device X    Account A
              │           │
              │       Transaction
              │           │
          Customer B   Beneficiary Z
              │
          Device X

Shared devices, repeated beneficiaries, unusual transaction relationships,
and connected entities can become important risk signals.

🔬 Adversarial Evaluation

After every Red-vs-Blue interaction, the system evaluates the outcome.

              ATTACK
                │
                ▼
          BLUE RESPONSE
                │
                ▼
       ┌────────┼────────┐
       ▼        ▼        ▼
   DETECTED   MISSED   FALSE POSITIVE
Key Metrics

Defense

Precision
Recall
F1 Score
False Positive Rate
False Negative Rate
Detection Rate

Adversarial

Attack Success Rate
Evasion Rate
Attack Detection Rate
Average Attack Difficulty
Defense Readiness Score
🗺️ Vulnerability Map

Instead of only reporting:

"Fraud detection = 87%"

the system identifies where the defense is weak.

Example:

VULNERABILITY MAP

Behavioral Evasion       █████████░  High
New Device Attacks       ███████░░░  Medium
Beneficiary Attacks      █████░░░░░  Low
High-Value Transactions  ███░░░░░░░  Low

This converts model performance into actionable security intelligence.

🔄 Continuous Adversarial Feedback

The most important part of the system is the feedback loop.

When Red Team succeeds:
Attack
  ↓
Blue misses
  ↓
Weakness identified
  ↓
Red learns successful characteristics
  ↓
Generate stronger variation
When Blue Team succeeds:
Attack
  ↓
Blue detects
  ↓
Attack becomes less effective
  ↓
Red changes strategy

The result is a continuous:

Attack → Defense → Evaluation → Adaptation cycle

🌟 What Makes the System Different?

The system is designed around proactive adversarial resilience rather
than only reactive fraud detection.

Traditional Fraud Detection
Historical Data
      ↓
Train Model
      ↓
Detect Known Patterns
Adversarial Defense Lab
Synthetic World
      ↓
AI Red Team
      ↓
Generate Novel Attack
      ↓
Simulate
      ↓
AI Blue Team
      ↓
Detect + Explain + Respond
      ↓
Evaluate
      ↓
Find Vulnerability
      ↓
Adapt
      ↓
Generate Next Attack

The system therefore treats the attacker itself as a testing mechanism
for improving payment security.

🛠️ Technology Stack
Frontend
Next.js
TypeScript
Tailwind CSS
Recharts
Backend
Python
FastAPI
AI / Machine Learning
Scikit-learn
XGBoost
Generative AI / LLM
Data
Pandas
NumPy
PostgreSQL / Supabase
Graph Intelligence
NetworkX
Development
Git
GitHub
📁 Project Structure
Mastercard-Adversarial-AI-Defense-Lab/
│
├── backend/             # API and backend services
│
├── frontend/            # Web dashboard
│
├── data/                # Synthetic payment data
│
├── red_team/            # Attack generation and adversarial logic
│
├── blue_team/           # Detection and defense models
│
├── simulator/           # Payment simulation engine
│
├── evaluation/          # Metrics and adversarial evaluation
│
├── docs/                # Architecture and documentation
│
├── README.md
├── requirements.txt
└── .gitignore
🗺️ Development Roadmap
Phase 1
🧪 Synthetic Payment World
        ↓
Phase 2
💳 Payment Simulator
        ↓
Phase 3
🔴 Red Team
        ↓
Phase 4
🔵 Blue Team
        ↓
Phase 5
🧠 Risk + Decision Engine
        ↓
Phase 6
📊 Adversarial Evaluation
        ↓
Phase 7
🔄 Feedback Loop
        ↓
Phase 8
🖥️ Frontend Integration
        ↓
Phase 9
🚀 End-to-End Demonstration
🔐 Safety & Responsible Use

This project operates entirely inside a controlled synthetic environment.

No real payment credentials are used.
No real financial transactions are executed.
No real customer data is processed.
Attack generation is restricted to the simulated environment.
The system is designed for defensive security research and adversarial
testing.
