import pandas as pd
import networkx as nx


class GraphRiskEngine:

    def __init__(self, transaction_data):

        self.data = transaction_data.copy()
        self.graph = nx.Graph()

        self._build_graph()

    def _build_graph(self):

        for _, row in self.data.iterrows():

            customer = f"customer:{row['customer_id']}"

            if pd.notna(row.get("device_id")):

                device = f"device:{row['device_id']}"

                self.graph.add_edge(
                    customer,
                    device
                )

            if pd.notna(row.get("merchant_id")):

                merchant = f"merchant:{row['merchant_id']}"

                self.graph.add_edge(
                    customer,
                    merchant
                )

            if pd.notna(row.get("beneficiary_id")):

                beneficiary = (
                    f"beneficiary:{row['beneficiary_id']}"
                )

                self.graph.add_edge(
                    customer,
                    beneficiary
                )

    def calculate_risk(self, transaction):

        customer = (
            f"customer:{transaction['customer_id']}"
        )

        risk_score = 0
        signals = []

        if customer not in self.graph:

            return {
                "graph_risk_score": 60,
                "signals": [
                    "Customer not found in historical graph"
                ],
            }

        # ==================================================
        # DEVICE
        # ==================================================

        device_id = transaction.get("device_id")

        if device_id:

            device = f"device:{device_id}"

            if device not in self.graph:

                risk_score += 20

                signals.append(
                    "Device not previously seen in graph"
                )

            else:

                connected_customers = [
                    node
                    for node in self.graph.neighbors(device)
                    if node.startswith("customer:")
                ]

                if len(connected_customers) > 1:

                    risk_score += 35

                    signals.append(
                        "Device shared across multiple customers"
                    )

        # ==================================================
        # BENEFICIARY
        # ==================================================

        beneficiary_id = transaction.get(
            "beneficiary_id"
        )

        if beneficiary_id:

            beneficiary = (
                f"beneficiary:{beneficiary_id}"
            )

            if beneficiary not in self.graph:

                risk_score += 25

                signals.append(
                    "New beneficiary relationship"
                )

            else:

                connected_customers = [
                    node
                    for node in self.graph.neighbors(
                        beneficiary
                    )
                    if node.startswith("customer:")
                ]

                if len(connected_customers) > 1:

                    risk_score += 30

                    signals.append(
                        "Beneficiary connected to multiple customers"
                    )

        # ==================================================
        # MERCHANT
        # ==================================================

        merchant_id = transaction.get("merchant_id")

        if merchant_id:

            merchant = f"merchant:{merchant_id}"

            if merchant in self.graph:

                transaction_connections = (
                    self.graph.degree(merchant)
                )

                if transaction_connections > 10:

                    risk_score += 15

                    signals.append(
                        "Merchant has high customer connectivity"
                    )

            else:

                risk_score += 15

                signals.append(
                    "Merchant not previously observed"
                )

        # ==================================================
        # CUSTOMER-MERCHANT RELATIONSHIP
        # ==================================================

        if merchant_id:

            merchant = f"merchant:{merchant_id}"

            if not self.graph.has_edge(
                customer,
                merchant
            ):

                risk_score += 15

                signals.append(
                    "Customer has no previous relationship with merchant"
                )

        # ==================================================
        # FINAL
        # ==================================================

        risk_score = min(risk_score, 100)

        return {
            "graph_risk_score": risk_score,
            "signals": signals,
        }