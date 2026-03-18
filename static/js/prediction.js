document.addEventListener("DOMContentLoaded", function () {

    console.log("JS LOADED SUCCESSFULLY");

    const resultBtn   = document.getElementById("resultBtn");
    const fundusInput = document.getElementById("fundus");
    const scleraInput = document.getElementById("sclera");

    let fundusExtracted = false;
    let scleraExtracted = false;
    let isExtracting    = false;   // ← GUARD: prevents double-fire

    // ===============================
    // IMAGE PREVIEW + show extract btn
    // ===============================
    function setupImagePreview(input, previewId, placeholderId, extractWrapId) {
        input.addEventListener("change", () => {
            const file = input.files[0];
            if (!file) return;

            const preview     = document.getElementById(previewId);
            const placeholder = document.getElementById(placeholderId);
            const extractWrap = document.getElementById(extractWrapId);

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
            placeholder.style.display = "none";
            extractWrap.style.display = "block";

            // reset features when new image chosen
            if (input.id === "fundus") {
                fundusExtracted = false;
                document.getElementById("fundusFeatures").style.display = "none";
            } else {
                scleraExtracted = false;
                document.getElementById("scleraFeatures").style.display = "none";
            }

            checkReadyToPredict();
        });
    }

    setupImagePreview(fundusInput, "fundusPreview", "fundusPlaceholder", "fundusExtractWrap");
    setupImagePreview(scleraInput, "scleraPreview", "scleraPlaceholder", "scleraExtractWrap");

    // ===============================
    // CSRF TOKEN
    // ===============================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(c => {
                c = c.trim();
                if (c.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    // ===============================
    // ENABLE PREDICT BUTTON
    // ===============================
    function checkReadyToPredict() {
        resultBtn.disabled = !(fundusExtracted && scleraExtracted);
    }

    // ===============================
    // EXTRACT — BOTH IMAGES AT ONCE
    // ===============================
    function doExtractFeatures() {

        // GUARD: stop if already running — prevents double requests
        if (isExtracting) return;

        if (!fundusInput.files[0] || !scleraInput.files[0]) {
            alert("Please upload both Fundus and Sclera images first.");
            return;
        }

        // Lock immediately
        isExtracting = true;
        const fBtn = document.getElementById("fundusExtractBtn");
        const sBtn = document.getElementById("scleraExtractBtn");
        if (fBtn) { fBtn.disabled = true; fBtn.textContent = "Extracting..."; }
        if (sBtn) { sBtn.disabled = true; sBtn.textContent = "Extracting..."; }

        const data = new FormData();
        data.append("fundus", fundusInput.files[0]);
        data.append("sclera", scleraInput.files[0]);

        document.getElementById("features").innerHTML = `
            <p class="loading-msg">Extracting features...</p>
        `;
        resultBtn.disabled = true;

        fetch("/prediction/extract-features/", {
            method: "POST",
            headers: { "X-CSRFToken": csrftoken },
            body: data
        })
        .then(res => {
            if (!res.ok) throw new Error("Feature extraction failed");
            return res.json();
        })
        .then(d => {
            console.log("Features:", d);

            // Unlock
            isExtracting    = false;
            fundusExtracted = true;
            scleraExtracted = true;

            // Show per-card feature boxes
            renderFeatureCard("fundusFeaturesList", "fundusFeatures", d.fundus_features);
            renderFeatureCard("scleraFeaturesList", "scleraFeatures", d.sclera_features);

            // Hide per-card extract buttons after success
            document.getElementById("fundusExtractWrap").style.display = "none";
            document.getElementById("scleraExtractWrap").style.display = "none";

            // Clear the separate features div — no duplicate grid needed
            document.getElementById("features").innerHTML = "";

            checkReadyToPredict();
        })
        .catch(err => {
            console.error(err);
            isExtracting = false;

            // Re-enable buttons on error
            if (fBtn) { fBtn.disabled = false; fBtn.textContent = "Extract Features"; }
            if (sBtn) { sBtn.disabled = false; sBtn.textContent = "Extract Features"; }

            alert("Error extracting features. Please try again.");
            document.getElementById("features").innerHTML = "";
        });
    }

    function renderFeatureCard(listId, boxId, obj) {
        const box  = document.getElementById(boxId);
        const list = document.getElementById(listId);
        list.innerHTML = Object.entries(obj).map(([k, v]) => `
            <div class="feature-row">
                <span>${k}</span>
                <span>${Number(v).toFixed(4)}</span>
            </div>
        `).join("");
        box.style.display = "block";
    }

    // Wire both per-card buttons to the same guarded function
    document.getElementById("fundusExtractBtn").onclick = doExtractFeatures;
    document.getElementById("scleraExtractBtn").onclick = doExtractFeatures;

    // ===============================
    // FINAL RESULT
    // ===============================
    resultBtn.onclick = () => {

        document.getElementById("results").innerHTML = `
            <p class="loading-msg">Predicting blood group...</p>
        `;
        resultBtn.disabled = true;

        fetch("/prediction/final-result/")
        .then(res => {
            if (!res.ok) throw new Error("Prediction failed");
            return res.json();
        })
        .then(d => {
            console.log("Result:", d);

            if (!d.predicted_group) {
                alert("Prediction failed. Try again.");
                resultBtn.disabled = false;
                return;
            }

            // Probability grid cards
            const probCards = Object.entries(d.all_probabilities).map(([k, v]) => {
                const pct = parseFloat(v).toFixed(2);
                return `
                    <div class="prob-card">
                        <b>${k}</b>
                        <span>${pct}%</span>
                        <div class="prob-bar-wrap">
                            <div class="prob-bar" style="width:${Math.min(pct, 100)}%"></div>
                        </div>
                    </div>
                `;
            }).join("");

            // Combined features right panel
            const combinedRows = Object.entries(d.all_probabilities).map(([k, v]) => `
                <div class="row">
                    <span>${k}</span>
                    <span>${parseFloat(v).toFixed(2)}%</span>
                </div>
            `).join("");

            document.getElementById("results").innerHTML = `
                <div class="glass-card">

                    <div class="result-layout">

                        <!-- LEFT: badge + confidence + DOWNLOAD -->
                        <div class="result-main">
                            <p>Predicted Blood Group</p>
                            <div class="badge">${d.predicted_group}</div>
                            <p>Confidence:
                                <span class="confidence">${d.confidence}%</span>
                            </p>
                            <button id="downloadBtn" class="btn-primary">
                                Download Report
                            </button>
                        </div>

                        <!-- RIGHT: probability list -->
                        <div class="feature-card">
                            <h3>All Blood Group Probabilities</h3>
                            ${combinedRows}
                        </div>

                    </div>

                    <!-- PROBABILITY GRID -->
                    <div class="prob-grid">
                        ${probCards}
                    </div>

                    <!-- DISCLAIMER -->
                    <div class="disclaimer">
                        <span class="disclaimer-icon">&#9888;</span>
                        <div>
                            <strong>Important Disclaimer</strong>
                            This prediction is generated by a machine learning model for research purposes only.
                            It is NOT a replacement for laboratory blood tests. Please consult a medical
                            professional for accurate blood group determination.
                        </div>
                    </div>

                </div>
            `;

            // Wire download button
            document.getElementById("downloadBtn").onclick = () => {
                window.open(downloadURL, "_blank");
            };

        })
        .catch(err => {
            console.error(err);
            document.getElementById("results").innerHTML =
                "<p style='color:#f87171; text-align:center; padding:24px;'>Error fetching result. Please try again.</p>";
            resultBtn.disabled = false;
        });
    };

});