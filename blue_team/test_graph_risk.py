import pandas as pd

from blue_team.graph_risk import GraphRiskEngine


print("Loading historical transactions...")

data = pd.read_csv("simulator/data/transactions_historical.csv")

engine = GraphRiskEngine(data)

print("Graph loaded successfully.\n")


# Use a transaction with no beneficiary if possible
normal_candidates = data[data["beneficiary_id"].isna()]

if not normal_candidates.empty:
    normal_transaction = normal_candidates.iloc[0].to_dict()
else:
    normal_transaction = data.iloc[0].to_dict()


# -----------------------------------
# TEST 1 — Baseline transaction
# -----------------------------------

baseline_result = engine.calculate_risk(normal_transaction)

print("=== BASELINE TRANSACTION ===")
print(baseline_result)


# -----------------------------------
# TEST 2 — Shared device
# -----------------------------------

shared_device_transaction = normal_transaction.copy()

device_counts = data["device_id"].value_counts()

shared_device = device_counts.idxmax()

shared_device_transaction["device_id"] = shared_device

shared_device_result = engine.calculate_risk(shared_device_transaction)

print("\n=== SHARED DEVICE SCENARIO ===")
print("Device:", shared_device)
print(shared_device_result)


# -----------------------------------
# TEST 3 — Shared beneficiary
# -----------------------------------

shared_beneficiary_transaction = normal_transaction.copy()

beneficiary_counts = data["beneficiary_id"].dropna().value_counts()

if not beneficiary_counts.empty:
    shared_beneficiary = beneficiary_counts.idxmax()

    shared_beneficiary_transaction["beneficiary_id"] = shared_beneficiary

    shared_beneficiary_result = engine.calculate_risk(shared_beneficiary_transaction)

    print("\n=== SHARED BENEFICIARY SCENARIO ===")
    print("Beneficiary:", shared_beneficiary)
    print(shared_beneficiary_result)

else:
    print("\nNo beneficiary data available.")
