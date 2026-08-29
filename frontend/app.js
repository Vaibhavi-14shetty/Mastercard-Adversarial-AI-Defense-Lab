// ============================================================
// SENTINEL-X FRONTEND
// Connects the dashboard to the FastAPI Payment Simulator
// ============================================================

const API_BASE = "http://127.0.0.1:8000";


// ============================================================
// DOM ELEMENTS
// ============================================================

const simulateBtn = document.getElementById("simulateBtn");
const loading = document.getElementById("loading");

const decisionBadge = document.getElementById("decisionBadge");
const riskScore = document.getElementById("riskScore");
const riskFill = document.getElementById("riskFill");

const fraudScore = document.getElementById("fraudScore");
const behaviorScore = document.getElementById("behaviorScore");
const graphScore = document.getElementById("graphScore");
const temporalScore = document.getElementById("temporalScore");

const fraudProbability = document.getElementById("fraudProbability");
const attackResult = document.getElementById("attackResult");

const reasonList = document.getElementById("reasonList");

const transactionSection =
    document.getElementById("transactionSection");

const transactionDetails =
    document.getElementById("transactionDetails");


// ============================================================
// RUN SIMULATION
// ============================================================

async function runSimulation() {

    const attack = document.getElementById("attack").value;
    const customer = document.getElementById("customer").value.trim();
    const amount = Number(document.getElementById("amount").value);
    const merchant = document.getElementById("merchant").value.trim();
    const device = document.getElementById("device").value.trim();
    const location = document.getElementById("location").value.trim();
    const beneficiary =
        document.getElementById("beneficiary").value.trim();

    const payment =
        document.getElementById("payment").value;


    // --------------------------------------------------------
    // Basic validation
    // --------------------------------------------------------

    if (!customer || !merchant || !device || !location) {

        alert("Please fill all required transaction fields.");

        return;
    }

    if (!amount || amount <= 0) {

        alert("Transaction amount must be greater than zero.");

        return;
    }


    // --------------------------------------------------------
    // UI loading state
    // --------------------------------------------------------

    setLoading(true);


    try {

        // ----------------------------------------------------
        // Build request
        // ----------------------------------------------------

        const payload = {

            customer_id: customer,

            amount: amount,

            merchant_id: merchant,

            device_id: device,

            location: location,

            beneficiary_id:
                beneficiary === ""
                    ? null
                    : beneficiary,

            payment_method: payment,

            attack_id: attack

        };


        // ----------------------------------------------------
        // Send transaction to FastAPI
        // ----------------------------------------------------

        const response = await fetch(
            `${API_BASE}/simulate`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(payload)
            }
        );


        // ----------------------------------------------------
        // Handle HTTP errors
        // ----------------------------------------------------

        if (!response.ok) {

            let errorMessage =
                `Server error: ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    errorMessage =
                        errorData.detail;
                }

            } catch (error) {
                // Ignore JSON parsing error
            }

            throw new Error(errorMessage);
        }


        // ----------------------------------------------------
        // Read response
        // ----------------------------------------------------

        const data =
            await response.json();


        // ----------------------------------------------------
        // Update dashboard
        // ----------------------------------------------------

        displaySecurityAnalysis(data);

        displayTransaction(data);

    }

    catch (error) {

        console.error(
            "Simulation error:",
            error
        );

        alert(
            "Unable to connect to Sentinel-X backend.\n\n" +
            error.message +
            "\n\nMake sure FastAPI is running on port 8000."
        );

        resetDashboard();

    }

    finally {

        setLoading(false);

    }
}


// ============================================================
// DISPLAY SECURITY ANALYSIS
// ============================================================

function displaySecurityAnalysis(data) {

    const decision =
        data.security_decision;

    const risk =
        Number(data.risk_score || 0);

    const fraudProbabilityValue =
        Number(data.fraud_probability || 0);

    const behavior =
        Number(data.behavior_score || 0);

    const graph =
        Number(data.graph_risk_score || 0);


    // --------------------------------------------------------
    // Decision
    // --------------------------------------------------------

    decisionBadge.textContent =
        decision;

    decisionBadge.className =
        "decision-badge " +
        decision.toLowerCase();


    // --------------------------------------------------------
    // Risk score
    // --------------------------------------------------------

    riskScore.textContent =
        risk.toFixed(2);

    riskFill.style.width =
        `${Math.min(risk, 100)}%`;


    // --------------------------------------------------------
    // Detection signals
    // --------------------------------------------------------

    fraudScore.textContent =
        `${(fraudProbabilityValue * 100).toFixed(1)}%`;

    behaviorScore.textContent =
        behavior.toFixed(1);

    graphScore.textContent =
        graph.toFixed(1);


    // Temporal score is not currently returned
    // as a top-level API field, so derive it from
    // the response if available.

    if (data.temporal_risk_score !== undefined) {

        temporalScore.textContent =
            Number(data.temporal_risk_score).toFixed(1);

    }
    else {

        temporalScore.textContent =
            "--";

    }


    // --------------------------------------------------------
    // Fraud probability
    // --------------------------------------------------------

    fraudProbability.textContent =
        `${(fraudProbabilityValue * 100).toFixed(1)}%`;


    // --------------------------------------------------------
    // Attack ID
    // --------------------------------------------------------

    attackResult.textContent =
        data.transaction?.attack_id ||
        document.getElementById("attack").value;


    // --------------------------------------------------------
    // Reasons
    // --------------------------------------------------------

    reasonList.innerHTML = "";

    const reasons =
        Array.isArray(data.reasons)
            ? data.reasons
            : [];


    if (reasons.length === 0) {

        const li =
            document.createElement("li");

        li.textContent =
            "No additional security signals.";

        reasonList.appendChild(li);

    }
    else {

        reasons.forEach(reason => {

            const li =
                document.createElement("li");

            li.textContent =
                reason;

            reasonList.appendChild(li);

        });

    }

}


// ============================================================
// DISPLAY TRANSACTION TRACE
// ============================================================

function displayTransaction(data) {

    const transaction =
        data.transaction;

    if (!transaction) {

        transactionSection.classList.add("hidden");

        return;
    }


    transactionSection.classList.remove("hidden");


    transactionDetails.innerHTML = `

        <div class="transaction-item">
            <span>Transaction ID</span>
            <strong>${escapeHTML(transaction.transaction_id)}</strong>
        </div>

        <div class="transaction-item">
            <span>Customer</span>
            <strong>${escapeHTML(transaction.customer_id)}</strong>
        </div>

        <div class="transaction-item">
            <span>Amount</span>
            <strong>₹${Number(transaction.amount).toLocaleString("en-IN")}</strong>
        </div>

        <div class="transaction-item">
            <span>Merchant</span>
            <strong>${escapeHTML(transaction.merchant_id)}</strong>
        </div>

        <div class="transaction-item">
            <span>Device</span>
            <strong>${escapeHTML(transaction.device_id)}</strong>
        </div>

        <div class="transaction-item">
            <span>Location</span>
            <strong>${escapeHTML(transaction.location)}</strong>
        </div>

        <div class="transaction-item">
            <span>Payment Method</span>
            <strong>${escapeHTML(transaction.payment_method)}</strong>
        </div>

        <div class="transaction-item">
            <span>Attack ID</span>
            <strong>${escapeHTML(transaction.attack_id || "N/A")}</strong>
        </div>

    `;
}


// ============================================================
// LOADING STATE
// ============================================================

function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove("hidden");

        simulateBtn.disabled = true;

        simulateBtn.innerHTML =
            "<span>⏳</span> ANALYZING...";

    }
    else {

        loading.classList.add("hidden");

        simulateBtn.disabled = false;

        simulateBtn.innerHTML =
            "<span>⚡</span> GENERATE & ANALYZE ATTACK";

    }

}


// ============================================================
// RESET DASHBOARD
// ============================================================

function resetDashboard() {

    decisionBadge.textContent =
        "WAITING";

    decisionBadge.className =
        "decision-badge neutral";

    riskScore.textContent =
        "--";

    riskFill.style.width =
        "0%";

    fraudScore.textContent =
        "--";

    behaviorScore.textContent =
        "--";

    graphScore.textContent =
        "--";

    temporalScore.textContent =
        "--";

    fraudProbability.textContent =
        "--";

    attackResult.textContent =
        "--";

}


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// ============================================================
// BACKEND HEALTH CHECK
// ============================================================

async function checkBackend() {

    try {

        const response =
            await fetch(`${API_BASE}/health`);

        if (!response.ok) {
            throw new Error("Backend unavailable");
        }

        const data =
            await response.json();

        console.log(
            "Sentinel-X backend:",
            data
        );

    }
    catch (error) {

        console.warn(
            "Sentinel-X backend is not currently running."
        );

    }

}


// ============================================================
// STARTUP
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        checkBackend();

    }
);