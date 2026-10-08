/**
 * Front-end Client Controller for Point & Figure Technical Analysis.
 * Fetches analysis from Python FastAPI backend and renders P&F charts & status metrics.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Register Quick Benchmark Button Listeners
    const presetBtns = document.querySelectorAll(".preset-btn");
    presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            presetBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const symbolInput = document.getElementById("symbol");
            symbolInput.value = btn.dataset.symbol;
            runAnalysis();
        });
    });

    // Run Initial Analysis
    runAnalysis();
});

async function runAnalysis() {
    const symbol = document.getElementById("symbol").value.trim().toUpperCase() || "AMAT";
    const boxSizePct = parseFloat(document.getElementById("box_size").value) || 1.0;
    const reversal = parseInt(document.getElementById("reversal").value, 10) || 3;
    const period = document.getElementById("period").value || "6m";
    const useMock = document.getElementById("use_mock").checked;

    const analyzeBtn = document.getElementById("analyze-btn");
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Analyzing...`;
    if (window.lucide) lucide.createIcons();

    try {
        const url = `/api/pnf/analyze?symbol=${encodeURIComponent(symbol)}&box_size_pct=${boxSizePct}&reversal=${reversal}&period=${period}&use_mock=${useMock}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        renderDashboard(data);
    } catch (err) {
        console.error("Analysis Error:", err);
        alert(`Failed to fetch P&F analysis: ${err.message}`);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `<i data-lucide="play"></i> Analyze P&F Chart`;
        if (window.lucide) lucide.createIcons();
    }
}

function renderDashboard(data) {
    // 1. Status Chip & Data Source Tag
    const chip = document.getElementById("status-reading-chip");
    chip.textContent = data.status_reading;

    // Apply color depending on active column type
    if (data.status_reading.startsWith("X")) {
        chip.style.background = "linear-gradient(135deg, #10b981, #059669)";
        chip.style.boxShadow = "0 0 16px rgba(16, 185, 129, 0.4)";
    } else {
        chip.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";
        chip.style.boxShadow = "0 0 16px rgba(239, 68, 68, 0.4)";
    }

    const dataSourceTag = document.getElementById("data-source-tag");
    dataSourceTag.textContent = `${data.symbol} • ${data.data_source} (${data.data_points} points)`;

    // 2. Trend Badge
    const trendVal = document.getElementById("trend-val");
    if (data.trend.toLowerCase() === "bullish") {
        trendVal.innerHTML = `<span class="badge bullish"><i data-lucide="trending-up"></i> Bullish</span>`;
    } else {
        trendVal.innerHTML = `<span class="badge bearish"><i data-lucide="trending-down"></i> Bearish</span>`;
    }

    // 3. Signal
    document.getElementById("signal-val").textContent = data.signal;

    // 4. Support & Resistance
    document.getElementById("sup-val").textContent = `$${data.levels.support.toFixed(2)}`;
    document.getElementById("res-val").textContent = `$${data.levels.resistance.toFixed(2)}`;

    // 5. Near-Term & Long-Term Targets
    document.getElementById("near-target-val").textContent = `$${data.targets.near_term.toFixed(2)}`;
    document.getElementById("long-target-val").textContent = `$${data.targets.long_term.toFixed(2)}`;

    // 6. Box Pill Info
    document.getElementById("box-val-pill").textContent = `Box Size: $${data.parameters.box_size_val} (${data.parameters.box_size_pct}%) | Reversal: ${data.parameters.reversal}`;

    // 7. Render P&F Columns Grid
    renderChartGrid(data.columns);

    if (window.lucide) lucide.createIcons();
}

function renderChartGrid(columns) {
    const gridContainer = document.getElementById("chart-grid");
    gridContainer.innerHTML = "";

    if (!columns || columns.length === 0) {
        gridContainer.innerHTML = `<p style="color: var(--text-muted); padding: 20px;">No P&F columns available.</p>`;
        return;
    }

    // Find global min and max prices across all boxes to align vertical box levels
    let allBoxPrices = [];
    columns.forEach(col => {
        allBoxPrices.push(...col.boxes);
    });

    if (allBoxPrices.length === 0) return;

    allBoxPrices.sort((a, b) => a - b);

    // Build each column element
    columns.forEach((col, colIdx) => {
        const colDiv = document.createElement("div");
        colDiv.className = "pnf-col";

        // Add boxes
        col.boxes.forEach(boxPrice => {
            const boxDiv = document.createElement("div");
            const isX = col.type === "X";
            boxDiv.className = `pnf-box ${isX ? "box-x" : "box-o"}`;
            boxDiv.textContent = isX ? "X" : "O";
            boxDiv.title = `Col ${colIdx + 1} (${col.type}) | Price: $${boxPrice.toFixed(2)} | Box count: ${col.box_count}`;
            colDiv.appendChild(boxDiv);
        });

        // Add Column Label Footer
        const footerDiv = document.createElement("div");
        footerDiv.className = "pnf-col-header";
        footerDiv.textContent = `C${colIdx + 1}`;
        colDiv.appendChild(footerDiv);

        gridContainer.appendChild(colDiv);
    });
}
