import pandas as pd
import networkx as nx


class GraphRiskEngine:
    def __init__(self, transaction_data):
        self.data = transaction_data.copy()
        self.graph = nx.Graph()

        self._build_graph()

    def _build_graph(self):
        """Build a relationship graph from historical transactions."""

        for _, row in self.data.iterrows():
            customer = f"customer:{row['customer_id']}"

            # Customer -> Device
            if pd.notna(row["device_id"]):
                device = f"device:{row['device_id']}"
                self.graph.add_edge(customer, device)

            # Customer -> Merchant
            if pd.notna(row["merchant_id"]):
                merchant = f"merchant:{row['merchant_id']}"
                self.graph.add_edge(customer, merchant)

            # Customer -> Beneficiary
            if pd.notna(row["beneficiary_id"]):
                beneficiary = f"beneficiary:{row['beneficiary_id']}"
                self.graph.add_edge(customer, beneficiary)

    def calculate_risk(self, transaction):
        """Calculate graph-based risk for one transaction."""

        customer = f"customer:{transaction['customer_id']}"

        risk_score = 0
        signals = []

        # Check whether the customer exists in the graph.
        if customer not in self.graph:
            return {
                "graph_risk_score": 50,
                "signals": ["Customer not found in historical graph"],
            }

        # Device risk
        device_id = transaction.get("device_id")

        if device_id:
            device = f"device:{device_id}"

            if device in self.graph:
                connected_customers = [
                    node
                    for node in self.graph.neighbors(device)
                    if node.startswith("customer:")
                ]

                if len(connected_customers) > 1:
                    risk_score += 40
                    signals.append("Device shared across multiple customers")

        # Beneficiary risk
        beneficiary_id = transaction.get("beneficiary_id")

        if beneficiary_id:
            beneficiary = f"beneficiary:{beneficiary_id}"

            if beneficiary in self.graph:
                connected_customers = [
                    node
                    for node in self.graph.neighbors(beneficiary)
                    if node.startswith("customer:")
                ]

                if len(connected_customers) > 2:
                    risk_score += 40
                    signals.append("Beneficiary connected to multiple customers")

        # Merchant connectivity
        merchant_id = transaction.get("merchant_id")

        if merchant_id:
            merchant = f"merchant:{merchant_id}"

            if merchant in self.graph:
                transaction_connections = self.graph.degree(merchant)

                if transaction_connections > 10:
                    risk_score += 20
                    signals.append("Merchant has high customer connectivity")

        risk_score = min(risk_score, 100)

        return {
            "graph_risk_score": risk_score,
            "signals": signals,
        }


if __name__ == "__main__":
    print("Loading historical transactions...")

    data = pd.read_csv("simulator/data/transactions_historical.csv")

    print("Building transaction graph...")

    engine = GraphRiskEngine(data)

    print("Graph construction successful.")

    print("\nGraph statistics:")
    print("Nodes:", engine.graph.number_of_nodes())
    print("Edges:", engine.graph.number_of_edges())

    sample_transaction = data.iloc[0].to_dict()

    result = engine.calculate_risk(sample_transaction)

    print("\nSample graph risk:")
    print(result)
