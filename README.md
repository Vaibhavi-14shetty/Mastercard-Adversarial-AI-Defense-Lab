# 🛡️ Sentinel-X — Adversarial AI Defense Lab

### Build the Attack. Test the Defense. Learn. Adapt.

> An AI-powered adversarial security laboratory for simulating evolving
> payment fraud attacks and testing how effectively a multi-signal defense
> system can detect, analyze, and respond to them.

---

## 🚨 Problem Statement

Generative AI is changing the payment-fraud landscape.

Attackers can increasingly create convincing social-engineering scams,
synthetic identities, account takeovers, credential attacks, and
evasion-oriented transaction patterns.

Traditional fraud detection systems are generally optimized around
historical fraud patterns.

But an adaptive attacker does not have to repeat the same behavior.

If an attacker changes the device, location, transaction amount,
beneficiary, or timing of an attack, a defense model may become less
effective.

### The attacker evolves. Shouldn't the defense evolve too?

**Sentinel-X** approaches payment security as an adversarial learning
problem.

Instead of waiting for new fraud patterns to appear in production,
Sentinel-X creates a controlled synthetic payment environment where a
Red Team continuously generates adversarial transactions and a Blue Team
analyzes and responds to them.

The result is a closed-loop system:

```text
Generate Attack
      ↓
Create Synthetic Transaction
      ↓
Blue Team Detection
      ↓
Risk Analysis
      ↓
Security Decision
      ↓
Feedback
      ↓
Adapt Attack
      ↓
Generate V2 Attack
      ↓
Re-analyze
      ↺



💡 What is Sentinel-X?

Sentinel-X is an adversarial payment-security simulation platform
consisting of two major components:

🔴 Red Team

The Red Team acts as the attacker.

It:

Selects an attack strategy
Generates adversarial transaction variations
Modifies transaction characteristics according to Attack DNA
Sends attacks to the payment simulator
Receives Blue Team feedback
Adapts the attack strategy
Generates an evolved V2 attack
🔵 Blue Team

The Blue Team acts as the defense.

It:

Analyzes incoming transactions
Calculates fraud probability
Performs behavioral analysis
Performs graph-based risk analysis
Evaluates temporal signals
Combines multiple signals
Produces an overall risk score
Generates an ALLOW / CHALLENGE / BLOCK decision
Provides security reasons
Sends analysis results back to the Red Team
🎯 Core Objectives

Sentinel-X is designed around six core objectives:

1. Simulate

Create a completely synthetic payment environment for controlled
security experimentation.

2. Attack

Generate realistic adversarial payment transactions using multiple
fraud strategies.

3. Detect

Analyze attacks using multiple independent security signals.

4. Decide

Convert security signals into a unified risk score and response.

5. Evaluate

Determine whether the generated attack was successfully detected,
challenged, or blocked.

6. Adapt

Use Blue Team feedback to modify the next attack and create an evolving
adversarial loop.

🏗️ System Architecture
                    🛡️ SENTINEL-X
             ADVERSARIAL PAYMENT LAB
                         │
                         ▼
                🧬 ATTACK KNOWLEDGE
                       / DNA
                         │
                         ▼
                  🔴 RED TEAM
                         │
                 Attack Generator
                         │
                         ▼
             Synthetic Adversarial
                 Transaction
                         │
                         ▼
              💳 PAYMENT SIMULATOR
                         │
                         ▼
                  🔵 BLUE TEAM
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Fraud ML       Behavioral       Graph
      Analysis       Analysis         Analysis
          │              │              │
          └──────────────┼──────────────┘
                         │
                         ▼
                 Temporal Analysis
                         │
                         ▼
                  🧠 RISK FUSION
                         │
                         ▼
                  RISK SCORE 0–100
                         │
                         ▼
               🚦 DECISION ENGINE
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           ALLOW      CHALLENGE     BLOCK
                         │
                         ▼
                  📊 EXPLANATION
                         │
                         ▼
                 🔄 FEEDBACK
                         │
                         ▼
                FEEDBACK ADAPTER
                         │
                         ▼
                 ADAPTIVE ENGINE
                         │
                         ▼
                  🔴 RED TEAM V2
                         │
                         └──────────────►
🧪 Synthetic Payment Environment

Sentinel-X operates using synthetic payment data.

The simulated environment contains entities such as:

Customer
   │
   ├── Account
   │      └── Card
   │
   ├── Device
   │
   └── Transactions
            │
            ├── Merchant
            ├── Beneficiary
            ├── Location
            ├── Amount
            ├── Timestamp
            └── Payment Method

A transaction can contain fields such as:

{
  "transaction_id": "TX1001",
  "customer_id": "C0001",
  "account_id": "A0001",
  "card_id": "CARD0001",
  "device_id": "D00001",
  "merchant_id": "M0044",
  "beneficiary_id": "B425",
  "amount": 550,
  "currency": "INR",
  "location": "Mumbai",
  "timestamp": "2026-08-29T10:30:00",
  "payment_method": "card",
  "is_fraud": true,
  "attack_id": "ATK006"
}

The system uses synthetic transactions so that adversarial experiments can
be performed without interacting with real financial systems or real
customer information.

🔴 Red Team — Adversarial Attack Generation

The Red Team is responsible for generating adversarial transactions.

It does not simply generate random fraudulent payments.

Instead, it uses structured Attack DNA to describe the characteristics
of an attack.

Attack DNA can define parameters such as:

Attack type
Target
Amount pattern
Device pattern
Location pattern
Transaction velocity
Evasion level
Attack description

The Attack Generator uses these parameters to modify a legitimate
transaction and create a synthetic adversarial transaction.

🧬 Attack DNA

Attack DNA acts as the structured representation of an attack strategy.

Example:

{
  "attack_type": "Adversarial Evasion",
  "amount_pattern": "near_normal",
  "device_pattern": "known",
  "location_pattern": "normal",
  "velocity": "normal",
  "evasion_level": 4
}

The Red Team can therefore create multiple variations of the same attack
family instead of relying on one fixed fraud example.

⚔️ Implemented Attack Types

Sentinel-X currently implements six adversarial attack strategies.

ID	Attack Type	Description
ATK001	Account Takeover	Uses a new device/location with a believable transaction amount
ATK002	Card Payment Fraud	Creates a higher-value transaction with device/location changes
ATK003	Credential Stuffing	Simulates suspicious access characteristics using device, location and timing changes
ATK004	Social Engineering / GenAI Scam	Uses the legitimate device/location but introduces a new beneficiary and meaningful amount deviation
ATK005	Synthetic Identity Fraud	Uses synthetic device and beneficiary relationships with altered transaction behavior
ATK006	Adversarial Evasion	Keeps several transaction characteristics close to normal while introducing subtle anomalies

All six attack types have been manually tested through the system.

🔴 Attack Generation Process

The Red Team follows this process:

Select Attack DNA
       ↓
Load Legitimate Transaction
       ↓
Modify Transaction Features
       ↓
Mark Transaction as Fraud
       ↓
Attach Attack ID
       ↓
Generate Adversarial Transaction
       ↓
Send to Simulator

For example:

Legitimate Transaction
₹550
Mumbai
Known Device
Known Customer
      ↓
      ↓ Attack Generation
      ↓
Adversarial Transaction
₹556.39
Mumbai
Known Device
New Beneficiary
Short Time Interval
      ↓
Blue Team
🔵 Blue Team — Detection & Defense

The Blue Team evaluates every generated transaction using multiple
security signals.

The objective is not to rely on a single fraud model.

Instead, Sentinel-X combines multiple detection surfaces.

🤖 Fraud ML Detection

The fraud detection component estimates the probability that a transaction
is fraudulent.

Example:

Fraud Probability
       ↓
     0.325

This signal contributes to the overall security analysis.

🧠 Behavioral Detection

Behavioral analysis evaluates whether the transaction differs from
expected customer behavior.

Examples of behavioral characteristics include:

Transaction amount
Transaction frequency
Typical activity
Device behavior
Transaction patterns

A deviation from normal behavior can increase the risk associated with
the transaction.

🕸️ Graph-Based Risk Detection

Payment relationships are modeled as connected entities.

Customer
   │
   ├── Account
   │
   ├── Device
   │
   ├── Merchant
   │
   └── Transaction
           │
           └── Beneficiary

Graph analysis can identify suspicious relationships such as:

New beneficiary relationships
Suspicious transaction connections
Highly connected merchants
Device relationships
Unusual entity connections

Example:

Graph Risk Score → 40
⏱️ Temporal Risk Detection

The system also evaluates transaction timing.

Very short intervals between related transactions can become a temporal
risk signal.

Example:

Previous Transaction
        ↓
   10–45 seconds
        ↓
New Transaction
        ↓
Temporal Risk

Example:

Temporal Risk Score → 25
🧠 Multi-Signal Risk Fusion

Sentinel-X combines multiple signals instead of depending on one detector.

Fraud ML
   +
Behavior
   +
Graph Risk
   +
Temporal Risk
   ↓
🧠 Risk Fusion
   ↓
Final Risk Score

The resulting score is normalized to a:

0 – 100

Example:

Fraud Probability → 0.325
Behavior Score    → 0.0
Graph Risk        → 40.0
Temporal Risk     → 25.0

Final Risk Score  → 56.38
🚦 Decision Engine

The final risk score is converted into a security decision.

Risk Score
    │
    ├── Low Risk
    │      ↓
    │    ALLOW
    │
    ├── Medium Risk
    │      ↓
    │  CHALLENGE
    │
    └── High Risk
           ↓
         BLOCK

The system supports:

🟢 ALLOW
🟡 CHALLENGE
🔴 BLOCK

The decision is accompanied by security reasons explaining why the
transaction received its risk classification.

Example:

Risk Score: 56.38

Decision: CHALLENGE

Reasons:
• Suspicious transaction relationships
• New beneficiary relationship
• Merchant has high customer connectivity
📊 Transaction Trace

Every generated transaction maintains its attack identity.

Example:

Transaction ID:
TX_TEST_ATK006_ATK006-V2_51b6c8

Attack ID:
ATK006-V2

Amount:
₹569.33

Location:
Mumbai

Device:
D00001

Beneficiary:
B425

Fraud:
True

This allows the complete lifecycle of an attack to be traced.

🔄 Adaptive Adversarial Feedback Loop

The key feature of Sentinel-X is its adaptive Red Team.

The system does not stop after detecting an attack.

The Blue Team's analysis is converted into structured feedback and passed
back to the Red Team.

              V1 ATTACK
                  │
                  ▼
             BLUE TEAM
                  │
                  ▼
             ANALYSIS
                  │
                  ▼
         FEEDBACK ADAPTER
                  │
                  ▼
          ADAPTIVE ENGINE
                  │
                  ▼
              V2 ATTACK
                  │
                  ▼
             BLUE TEAM
                  │
                  ▼
             RE-ANALYSIS
                  │
                  └──────────────►
🔁 V1 → V2 Attack Evolution

Suppose the Red Team generates:

ATK006

The Blue Team detects signals such as:

Graph
Temporal

The Feedback Adapter converts the Blue Team result into normalized
feedback.

The Adaptive Engine then modifies the Attack DNA.

For example:

ATK006
   ↓
Detected:
Graph + Temporal
   ↓
Adaptation
   ↓
Known Device
Normal Location
Normal Velocity
Near-Normal Amount
   ↓
ATK006-V2

The evolved transaction is then sent back to the Blue Team.

This creates a real adversarial feedback cycle rather than a one-time
fraud detection process.

🧩 Feedback Adapter

The BlueTeamFeedbackAdapter converts Blue Team analysis into a
normalized structure that the Adaptive Engine can understand.

It extracts:

Risk score
Security decision
Detected signals

Example:

{
  "risk_score": 56.38,
  "decision": "CHALLENGE",
  "detected_signals": [
    "graph",
    "temporal"
  ]
}

This provides a clean interface between the defensive system and the
adaptive Red Team.

🧬 Adaptive Engine

The Adaptive Engine modifies an existing Attack DNA based on Blue Team
feedback.

For example:

If behavior is detected
        ↓
Reduce amount anomaly

If graph is detected
        ↓
Move toward known device/location

If temporal anomaly is detected
        ↓
Reduce transaction velocity

If fraud signal is detected
        ↓
Reduce obvious transaction characteristics

The evolved attack receives a versioned identifier:

ATK006
  ↓
ATK006-V2

The system therefore preserves the original attack identity while
documenting how the attack evolved.

🔬 Example End-to-End Run

A tested ATK006 example produced:

Attack:
ATK006 — Adversarial Evasion

V1 Transaction:
Amount → ₹556.39
Device → D00001
Location → Mumbai
Beneficiary → B425

Blue Team:
Fraud Probability → 0.325
Behavior Score    → 0.0
Graph Risk        → 40.0
Temporal Risk     → 25.0
Final Risk        → 56.38

Decision:
CHALLENGE

Detected Signals:
Graph
Temporal

The feedback was then used to evolve the attack:

ATK006
   ↓
Blue Team Feedback
   ↓
Adaptive Engine
   ↓
ATK006-V2

The evolved attack was generated with adapted parameters such as:

Amount Pattern → near_normal
Device Pattern → known
Location       → normal
Velocity       → normal
Evasion Level  → 5

The V2 transaction was then re-analyzed by the Blue Team.

Example result:

Risk Score → 56.55
Decision   → CHALLENGE

This demonstrates the complete:

Attack → Detect → Feedback → Adapt → Re-attack

cycle.

🌐 API Architecture

Sentinel-X exposes its functionality through FastAPI endpoints.

Current major endpoints include:

GET /
GET /health

POST /red-team/generate

POST /red-team/adapt

POST /red-team/adapt-from-analysis

POST /simulate

POST /simulate/adversarial
Red Team
/red-team/generate

Generates an adversarial transaction from an attack strategy.

/red-team/adapt

Adapts an attack using structured feedback.

/red-team/adapt-from-analysis

Directly converts Blue Team analysis into feedback and generates an
evolved attack.

Simulator
/simulate

Runs a transaction through the simulation and security pipeline.

/simulate/adversarial

Analyzes an adversarial transaction through the Blue Team pipeline.

🖥️ Frontend Dashboard

Sentinel-X includes a web-based dashboard for demonstrating the
adversarial pipeline.

The dashboard displays information such as:

Selected attack
Generated transaction
Attack version
Fraud probability
Behavioral risk
Graph risk
Temporal risk
Overall risk score
Security decision
Security reasons
Adaptive attack results
V1 → V2 evolution

The frontend provides a visual interface over the underlying FastAPI
services.

🧪 Testing

The system has been manually tested across all six attack types:

ATK001 → Account Takeover              ✅
ATK002 → Card Payment Fraud            ✅
ATK003 → Credential Stuffing           ✅
ATK004 → Social Engineering / GenAI    ✅
ATK005 → Synthetic Identity Fraud      ✅
ATK006 → Adversarial Evasion           ✅

The adaptive loop has also been tested:

V1 Attack
   ↓
Blue Team Analysis
   ↓
Feedback Extraction
   ↓
Attack Adaptation
   ↓
V2 Attack
   ↓
Blue Team Re-analysis
🛠️ Technology Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
Machine Learning / Detection
Scikit-learn
Fraud detection models
Behavioral anomaly analysis
Graph-based risk analysis
Temporal analysis
Graph Intelligence
NetworkX
Data Processing
Python data-processing utilities
JSON-based synthetic datasets
Frontend
HTML
CSS
JavaScript
API Communication
REST APIs
JSON
Development & Version Control
Git
GitHub
PowerShell
VS Code
📁 Project Structure
Mastercard-Adversarial-AI-Defense-Lab/
│
├── blue_team/
│   ├── __pycache__/
│   │
│   ├── aggregate_evaluation.py
│   ├── behavioral_engine.py
│   ├── behavioral_profiles.json
│   ├── decision_engine.py
│   ├── evaluator.py
│   ├── explainability.py
│   ├── feature_engineering.py
│   ├── fraud_model.py
│   ├── graph_risk.py
│   ├── pipeline.py
│   ├── risk_fusion.py
│   ├── temporal_risk.py
│   │
│   ├── test_fraud_model.py
│   ├── test_graph_risk.py
│   └── transaction_schema.py
│
├── docs/
│   └── SENTINEL_X_INTEGRATION...
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── red_team/
│   ├── __pycache__/
│   │
│   ├── adaptive/
│   │   ├── __init__.py
│   │   └── adaptive_engine.py
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── adaptive_attack.py
│   │   └── feedback_adapter.py
│   │
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── red_team_api.py
│   │
│   ├── composer/
│   │
│   ├── feedback/
│   │   ├── __init__.py
│   │   └── feedback_builder.py
│   │
│   ├── generator/
│   │
│   ├── knowledge_base/
│   │
│   └── schemas/
│       ├── __pycache__/
│       ├── __init__.py
│       ├── attack_dna.py
│       ├── transaction.py
│       └── test_schema.py
│
├── simulator/
│   ├── __pycache__/
│   │
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── data/
│   ├── generators/
│   ├── schemas/
│   ├── tests/
│   │
│   └── __init__.py
│
├── .gitignore
├── evaluate_attacks.py
├── README.md
├── requirements.txt
└── test_attacks.py


🚀 How to Run
1. Clone the repository
git clone https://github.com/Vaibhavi-14shetty/Mastercard-Adversarial-AI-Defense-Lab.git
cd Mastercard-Adversarial-AI-Defense-Lab
2. Create a virtual environment
Windows
python -m venv venv

Activate it:

venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Start the FastAPI backend
python -m uvicorn simulator.api.main:app --reload

The API will be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs

OpenAPI specification:

http://127.0.0.1:8000/openapi.json
5. Run the frontend

Open:

frontend/index.html

in a browser and ensure the FastAPI backend is running.

🔗 End-to-End Workflow

The complete Sentinel-X workflow is:

                     START
                       │
                       ▼
              Select Attack Type
                       │
                       ▼
                 Attack DNA
                       │
                       ▼
              🔴 RED TEAM V1
                       │
                       ▼
          Generate Synthetic Transaction
                       │
                       ▼
              💳 PAYMENT SIMULATOR
                       │
                       ▼
                🔵 BLUE TEAM
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Fraud        Behavior         Graph
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                   Temporal
                       │
                       ▼
                 Risk Fusion
                       │
                       ▼
                Risk Score 0–100
                       │
                       ▼
              ALLOW / CHALLENGE / BLOCK
                       │
                       ▼
                  Explanation
                       │
                       ▼
              Blue Team Feedback
                       │
                       ▼
              Feedback Adapter
                       │
                       ▼
               Adaptive Engine
                       │
                       ▼
                🔴 RED TEAM V2
                       │
                       ▼
              Re-generate Attack
                       │
                       ▼
                🔵 BLUE TEAM
                       │
                       ▼
                  Re-analysis
                       │
                       └──────────────►
📌 Key Features
🔴 Adversarial Red Team
Structured Attack DNA
Six attack families
Synthetic fraud generation
Attack-specific transaction manipulation
Versioned attack evolution
Adaptive attack generation
🔵 Blue Team Defense
Fraud probability
Behavioral risk
Graph risk
Temporal risk
Multi-signal risk fusion
Risk score from 0–100
ALLOW / CHALLENGE / BLOCK
Explainable security reasons
🔄 Adaptive Intelligence
Blue Team feedback extraction
Feedback normalization
Attack adaptation
V1 → V2 evolution
Re-analysis of evolved attacks
Closed-loop adversarial testing
🌐 Demonstration
FastAPI backend
REST API endpoints
Interactive API documentation
Web-based Sentinel-X dashboard
End-to-end transaction tracing
🌟 What Makes Sentinel-X Different?

Traditional fraud detection generally follows:

Historical Fraud Data
        ↓
Train Detection Model
        ↓
Detect Fraud
        ↓
Respond

Sentinel-X introduces an adversarial security layer:

Synthetic Payment Environment
        ↓
🔴 Red Team
        ↓
Generate Attack
        ↓
Payment Simulation
        ↓
🔵 Blue Team
        ↓
Detect + Analyze + Decide
        ↓
Feedback
        ↓
Adaptive Red Team
        ↓
Generate Stronger / Different Attack
        ↓
Re-test Defense

The attacker itself becomes a mechanism for testing the defense.

Instead of only asking:

"Can our system detect this fraud?"

Sentinel-X asks:

"What happens when the attacker learns from our detection behavior
and changes the attack?"

This makes the platform suitable for exploring adversarial resilience,
evasion behavior, and defensive weaknesses in controlled payment-security
simulations.

🏆 Project Outcome

Sentinel-X successfully demonstrates a complete adversarial payment
security pipeline:

                🔴 RED TEAM
                     │
                     ▼
             ATTACK GENERATION
                     │
                     ▼
          SYNTHETIC TRANSACTION
                     │
                     ▼
                🔵 BLUE TEAM
                     │
                     ▼
          MULTI-SIGNAL DETECTION
                     │
                     ▼
             RISK + DECISION
                     │
                     ▼
               FEEDBACK
                     │
                     ▼
             ADAPTIVE ENGINE
                     │
                     ▼
              🔴 V2 ATTACK
                     │
                     ▼
              RE-ANALYSIS

The implemented system demonstrates that payment-security testing can be
treated as a continuous adversarial process rather than a one-time fraud
detection task.

🔐 Safety & Responsible Use

Sentinel-X is designed strictly for defensive security research and
controlled simulation.

No real payment credentials are used.
No real financial transactions are executed.
No real customer financial data is processed.
Transactions are synthetic.
Attack generation operates within the simulated environment.
The system is intended for security testing, research, demonstration,
and defensive analysis.

The project does not interact with real payment networks.

📚 Documentation

Additional integration documentation is available in:

docs/SENTINEL_X_INTEGRATION.md
👥 Project

Sentinel-X — Adversarial AI Defense Lab

Built as an adversarial payment-security system combining:

🔴 Red Team
+
💳 Payment Simulation
+
🔵 Blue Team
+
🧠 Multi-Signal Detection
+
🔄 Adaptive Feedback
Build the Attack. Test the Defense. Learn. Adapt.
