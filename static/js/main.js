document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    if (!token && window.location.pathname === "/dashboard") {
        window.location.href = "/login";
        return;
    }

    // ---------------- TAB SWITCHING ----------------
    const navLinks = document.querySelectorAll(".nav-link");
    const views = document.querySelectorAll(".dashboard-view");

    function switchView(viewId, linkId) {
        views.forEach(v => v.style.display = "none");
        document.getElementById(viewId).style.display = "block";

        navLinks.forEach(l => l.classList.remove("active"));

        const active = document.getElementById(linkId);
        if (active) active.classList.add("active");

        if (viewId === "historyView") loadHistory();
    }

    document.getElementById("newCaseLink")?.addEventListener("click", e => {
        e.preventDefault();
        switchView("newCaseView", "newCaseLink");
    });

    document.getElementById("historyLink")?.addEventListener("click", e => {
        e.preventDefault();
        switchView("historyView", "historyLink");
    });

    // ---------------- ANALYSIS FORM ----------------
    const form = document.getElementById("analysisForm");

    if (form) {
        form.addEventListener("submit", async e => {
            e.preventDefault();

            const btn = form.querySelector("button");
            btn.disabled = true;
            btn.innerText = "Analyzing...";

            const formData = new FormData(form);

            try {
                const res = await fetch("/api/analyze", {
                    method: "POST",
                    headers: {
                        "Authorization": "Bearer " + token
                    },
                    body: formData
                });

                const data = await res.json();

                renderResults(data);

            } catch (err) {
                alert("Analysis failed");
                console.error(err);
            }

            btn.disabled = false;
            btn.innerText = "Analyze Case";
        });
    }

    // ---------------- RENDER RESULTS ----------------
    function renderResults(data) {

        // ---- Classification ----
        const cls = document.getElementById("classificationResult");

        cls.innerHTML = `
            <div style="font-size:1.3rem;color:#3b82f6;font-weight:bold;">
                ${data.classification.primary}
            </div>
            <div style="color:#94a3b8;margin-top:4px;">
                Confidence: ${data.classification.confidence}
            </div>
            ${data.classification.secondary
                ? `<div style="margin-top:6px;font-size:0.85rem;color:#facc15;">
                    Secondary: ${data.classification.secondary}
                   </div>`
                : ""}
        `;

        // ---- AI Insights ----
        const insights = document.getElementById("insightsResult");

        let html = `
            <h4 style="margin-bottom:8px;">Legal Opinion</h4>
            <p style="line-height:1.6;">
                ${data.analysis.legal_opinion}
            </p>
        `;

        if (data.analysis.similar_precedents?.length) {
            html += `<h4 style="margin-top:16px;">Similar Precedents</h4>`;

            data.analysis.similar_precedents.forEach(p => {
                html += `
                    <div style="margin-top:10px;padding:10px;border:1px solid rgba(255,255,255,0.1);border-radius:6px;">
                        <div style="color:#3b82f6;font-weight:600;">
                            ${p.pdf_name}
                        </div>
                        <div style="font-size:0.8rem;color:#94a3b8;">
                            ${p.relevance}
                        </div>
                        <div style="margin-top:6px;font-size:0.9rem;">
                            ${p.summary}
                        </div>
                    </div>
                `;
            });
        }

        insights.innerHTML = html;
    }

    // ---------------- HISTORY ----------------
    async function loadHistory() {
        const list = document.getElementById("historyList");

        try {
            const res = await fetch("/api/history/", {
                headers: {
                    "Authorization": "Bearer " + token
                }
            });

            const data = await res.json();

            if (!data.length) {
                list.innerHTML = "No history found";
                return;
            }

            list.innerHTML = data.map(c => `
                <div class="glass-panel" style="padding:1rem;">
                    <div style="color:#3b82f6;font-weight:600;">
                        ${c.case_type}
                    </div>
                    <div style="font-size:0.8rem;color:#94a3b8;">
                        ${new Date(c.created_at).toLocaleDateString()}
                    </div>
                    <div style="margin-top:6px;">
                        ${c.description}
                    </div>
                </div>
            `).join("");

        } catch (e) {
            list.innerHTML = "Failed to load history";
        }
    }

    // ---------------- LOGOUT ----------------
    document.getElementById("logoutBtn")?.addEventListener("click", () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    });

});
