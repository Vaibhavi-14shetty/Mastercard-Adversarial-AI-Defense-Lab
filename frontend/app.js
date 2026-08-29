// ============================================================
// SENTINEL-X FRONTEND
// Adaptive Red Team ↔ Blue Team Integration
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
// MAIN ADAPTIVE SIMULATION
// ============================================================

async function runSimulation() {

    const attack = document.getElementById("attack").value;

    const customer =
        document.getElementById("customer").value.trim();

    const amount =
        Number(document.getElementById("amount").value);

    const merchant =
        document.getElementById("merchant").value.trim();

    const device =
        document.getElementById("device").value.trim();

    const location =
        document.getElementById("location").value.trim();

    const beneficiary =
        document.getElementById("beneficiary").value.trim();

    const payment =
        document.getElementById("payment").value;


    // ========================================================
    // VALIDATION
    // ========================================================

    if (!customer || !merchant || !device || !location) {

        alert("Please fill all required transaction fields.");

        return;
    }

    if (!amount || amount <= 0) {

        alert("Transaction amount must be greater than zero.");

        return;
    }


    setLoading(true);


    try {

        // ====================================================
        // STEP 1 — BUILD ORIGINAL TRANSACTION
        // ====================================================

        const transaction = {

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

            is_fraud: false,

            attack_id: null
        };


        // ====================================================
        // STEP 2 — RED TEAM GENERATES V1
        // ====================================================

        console.log("RED TEAM → Generating attack V1...");

        const generateResponse = await fetch(
            `${API_BASE}/red-team/generate`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    transaction: transaction,

                    attack_id: attack

                })
            }
        );


        if (!generateResponse.ok) {

            throw new Error(
                await getErrorMessage(generateResponse)
            );
        }


        const v1 =
            await generateResponse.json();


        console.log(
            "RED TEAM V1:",
            v1.attack_id
        );


        // ====================================================
        // STEP 3 — BLUE TEAM ANALYZES V1
        // ====================================================

        console.log(
            "BLUE TEAM → Analyzing V1..."
        );


        const blueV1Response = await fetch(
            `${API_BASE}/simulate/adversarial`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(
                    v1.transaction
                )
            }
        );


        if (!blueV1Response.ok) {

            throw new Error(
                await getErrorMessage(blueV1Response)
            );
        }


        const blueV1 =
            await blueV1Response.json();


        console.log(
            "BLUE TEAM V1:",
            blueV1
        );


        // ====================================================
        // STEP 4 — ADAPT RED TEAM USING BLUE FEEDBACK
        // ====================================================

        console.log(
            "RED TEAM → Adapting attack..."
        );


        const adaptResponse = await fetch(
            `${API_BASE}/red-team/adapt-from-analysis`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    transaction: v1.transaction,

                    blue_team_analysis:
                        blueV1.blue_team_result

                })
            }
        );


        if (!adaptResponse.ok) {

            throw new Error(
                await getErrorMessage(adaptResponse)
            );
        }


        const v2 =
            await adaptResponse.json();


        console.log(
            "RED TEAM V2:",
            v2.evolved_attack_id
        );


        // ====================================================
        // STEP 5 — BLUE TEAM ANALYZES V2
        // ====================================================

        console.log(
            "BLUE TEAM → Analyzing evolved attack..."
        );


        const blueV2Response = await fetch(
            `${API_BASE}/simulate/adversarial`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(
                    v2.transaction
                )
            }
        );


        if (!blueV2Response.ok) {

            throw new Error(
                await getErrorMessage(blueV2Response)
            );
        }


        const blueV2 =
            await blueV2Response.json();


        console.log(
            "BLUE TEAM V2:",
            blueV2
        );


        // ====================================================
        // STEP 6 — DISPLAY FINAL V2 RESULT
        // ====================================================

        displaySecurityAnalysis(
            blueV2
        );

        displayTransaction(
            v2
        );


        // ====================================================
        // ADAPTIVE LOOP SUMMARY
        // ====================================================

        showAdaptiveSummary(
            v1,
            blueV1,
            v2,
            blueV2
        );


        console.log(
            "========== ADAPTIVE LOOP COMPLETE =========="
        );

        console.log(
            "V1:",
            v1.attack_id,
            "Risk:",
            blueV1.risk_score,
            "Decision:",
            blueV1.security_decision
        );

        console.log(
            "V2:",
            v2.evolved_attack_id,
            "Risk:",
            blueV2.risk_score,
            "Decision:",
            blueV2.security_decision
        );

        console.log(
            "Risk reduction:",
            (
                Number(blueV1.risk_score) -
                Number(blueV2.risk_score)
            ).toFixed(2)
        );

    }

    catch (error) {

        console.error(
            "Adaptive simulation error:",
            error
        );

        alert(
            "Sentinel-X simulation failed.\n\n" +
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
// BLUE TEAM DISPLAY
// ============================================================

function displaySecurityAnalysis(data) {

    const decision =
        data.security_decision || "WAITING";

    const risk =
        Number(data.risk_score || 0);

    const fraudProbabilityValue =
        Number(data.fraud_probability || 0);

    const behavior =
        Number(data.behavior_score || 0);

    const graph =
        Number(data.graph_risk_score || 0);


    // ========================================================
    // DECISION
    // ========================================================

    decisionBadge.textContent =
        decision;

    decisionBadge.className =
        "decision-badge " +
        decision.toLowerCase();


    // ========================================================
    // RISK
    // ========================================================

    riskScore.textContent =
        risk.toFixed(2);

    riskFill.style.width =
        `${Math.min(risk, 100)}%`;


    // ========================================================
    // SIGNALS
    // ========================================================

    fraudScore.textContent =
        `${(fraudProbabilityValue * 100).toFixed(1)}%`;

    behaviorScore.textContent =
        behavior.toFixed(1);

    graphScore.textContent =
        graph.toFixed(1);


    if (
        data.temporal_risk_score !== undefined
    ) {

        temporalScore.textContent =
            Number(
                data.temporal_risk_score
            ).toFixed(1);

    }
    else {

        temporalScore.textContent =
            "--";

    }


    // ========================================================
    // FRAUD PROBABILITY
    // ========================================================

    fraudProbability.textContent =
        `${(fraudProbabilityValue * 100).toFixed(1)}%`;


    // ========================================================
    // ATTACK ID
    // ========================================================

    attackResult.textContent =
        data.transaction?.attack_id ||
        "--";


    // ========================================================
    // REASONS
    // ========================================================

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
// TRANSACTION DISPLAY
// ============================================================

function displayTransaction(data) {

    const transaction =
        data.transaction;

    if (!transaction) {

        transactionSection.classList.add(
            "hidden"
        );

        return;
    }


    transactionSection.classList.remove(
        "hidden"
    );


    transactionDetails.innerHTML = `

        <div class="transaction-item">
            <span>Transaction ID</span>
            <strong>
                ${escapeHTML(transaction.transaction_id)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Customer</span>
            <strong>
                ${escapeHTML(transaction.customer_id)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Amount</span>
            <strong>
                ₹${Number(transaction.amount)
                    .toLocaleString("en-IN")}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Merchant</span>
            <strong>
                ${escapeHTML(transaction.merchant_id)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Device</span>
            <strong>
                ${escapeHTML(transaction.device_id)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Location</span>
            <strong>
                ${escapeHTML(transaction.location)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Payment Method</span>
            <strong>
                ${escapeHTML(transaction.payment_method)}
            </strong>
        </div>

        <div class="transaction-item">
            <span>Attack ID</span>
            <strong>
                ${escapeHTML(
                    transaction.attack_id || "N/A"
                )}
            </strong>
        </div>

    `;
}


// ============================================================
// ADAPTIVE LOOP SUMMARY
// ============================================================

function showAdaptiveSummary(
    v1,
    blueV1,
    v2,
    blueV2
) {

    const oldRisk =
        Number(blueV1.risk_score || 0);

    const newRisk =
        Number(blueV2.risk_score || 0);

    const reduction =
        oldRisk - newRisk;


    console.log(
        "=========================================="
    );

    console.log(
        "        SENTINEL-X ADAPTIVE LOOP"
    );

    console.log(
        "=========================================="
    );

    console.log(
        "Original Attack :",
        v1.attack_id
    );

    console.log(
        "V1 Risk         :",
        oldRisk.toFixed(2)
    );

    console.log(
        "V1 Decision     :",
        blueV1.security_decision
    );

    console.log(
        "Evolved Attack  :",
        v2.evolved_attack_id
    );

    console.log(
        "V2 Risk         :",
        newRisk.toFixed(2)
    );

    console.log(
        "V2 Decision     :",
        blueV2.security_decision
    );

    console.log(
        "Risk Reduction  :",
        reduction.toFixed(2)
    );

    console.log(
        "=========================================="
    );

}


// ============================================================
// LOADING
// ============================================================

function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove(
            "hidden"
        );

        simulateBtn.disabled = true;

        simulateBtn.innerHTML =
            "<span>⟳</span> RUNNING ADAPTIVE LOOP...";

    }
    else {

        loading.classList.add(
            "hidden"
        );

        simulateBtn.disabled = false;

        simulateBtn.innerHTML =
            "<span>⚡</span> GENERATE & ANALYZE ATTACK";

    }

}


// ============================================================
// RESET
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
// ERROR MESSAGE
// ============================================================

async function getErrorMessage(response) {

    try {

        const data = await response.json();

        console.error("Backend error response:", data);

        // FastAPI validation error
        if (Array.isArray(data.detail)) {

            return data.detail
                .map(error => {

                    if (typeof error === "string") {
                        return error;
                    }

                    const location =
                        error.loc
                            ? error.loc.join(" → ")
                            : "request";

                    return `${location}: ${error.msg || "Invalid value"}`;

                })
                .join("\n");

        }

        // Normal FastAPI error
        if (typeof data.detail === "string") {
            return data.detail;
        }

        // Object response
        if (data.detail) {
            return JSON.stringify(data.detail, null, 2);
        }

        return JSON.stringify(data, null, 2);

    }

    catch (error) {

        return `HTTP ${response.status}: ${response.statusText}`;

    }
}


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHTML(value) {

    return String(value ?? "")
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
            await fetch(
                `${API_BASE}/health`
            );

        if (!response.ok) {

            throw new Error(
                "Backend unavailable"
            );

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