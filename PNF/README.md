# Point & Figure (PNF) Technical Analysis Suite

A modern Python & Web-based technical analysis application for generating **Point & Figure (P&F / PNF)** charts, computing John J. Murphy status readings (e.g., `X4@433.341`, `X15@240.130`), detecting technical breakout/breakdown signals, calculating target price objectives, and generating comparative stock ranking reports (e.g., Magnificent 7 analysis).

---

## 🌟 Key Features

- **P&F Algorithm Engine ([pnf_engine.py](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/pnf_engine.py))**: Supports dynamic percentage box sizing (`1%` default) or fixed dollar sizes, alongside configurable reversal box counts (`3-box reversal` default).
- **Status Reading Notation**: Computes real-time status strings (e.g., `X4@433.341`) tracking column state (`X` or `O`), box count, and current market price.
- **Pattern & Signal Recognition**: Automatically identifies classic P&F technical patterns:
  - **Double Top Buy** (Bullish Breakout)
  - **Double Bottom Sell** (Bearish Breakdown)
  - **Consolidation / Trend Bias**
- **Target Price Projections**:
  - **Near-Term Target**: Calculated via column base count shift ($\frac{\text{Base Count} \times \text{Reversal}}{2}$ boxes).
  - **Long-Term Objective**: Base extension price projection.
  - **Support & Resistance**: Dynamic key horizontal price levels.
  - **Reward % Calculation**: Long-term price upside relative to current price.
- **FastAPI REST API ([main.py](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/main.py))**: Endpoint at `/api/pnf/analyze` fetching live market data via `yfinance` with fallback synthetic benchmark generation.
- **Modern Dark Glassmorphism UI ([static/index.html](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/static/index.html))**: Interactive web interface featuring live interactive P&F column visualization grids, tooltip price details, preset benchmark shortcuts (`AMAT`, `NVDA`, `TSLA`, `GOOGL`, `AAPL`, `MSFT`, `AMZN`, `META`), and customizable parameter controls.
- **Magnificent 7 Screening Output ([OUTPUT.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/OUTPUT.md))**: Comparative CSV and formatted Markdown output table for Mag 7 stocks sorted by Reward % descending.

---

## 📁 Repository Structure

```
PNF/
├── SPEC.md             # Complete Technical Specification Document
├── PNF.docx            # Original Requirements Document
├── OUTPUT.md           # Magnificent 7 PNF Screening & Ranking Report
├── pnf_engine.py       # Core P&F Calculation Engine & Indicator Module
├── main.py             # FastAPI REST Server & Static File Host
├── requirements.txt    # Python Project Dependencies
└── static/             # Web Application Frontend Assets
    ├── index.html      # Dark Glassmorphism Dashboard HTML
    ├── styles.css      # UI Design Tokens & Layout CSS
    └── app.js          # Client Controller & Grid Column Visualizer
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Activate Virtual Environment & Install Dependencies

```powershell
# On Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch Backend & UI Server

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

### 4. Open Application in Browser
Navigate to: 👉 **`http://127.0.0.1:8080`**

---

## 📊 REST API Reference

### `GET /api/pnf/analyze`

**Query Parameters:**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `symbol` | `string` | `AMAT` | Ticker symbol (e.g. `NVDA`, `TSLA`, `AAPL`, `AMAT`) |
| `box_size_pct` | `float` | `1.0` | Percentage box size (e.g. `1.0` for 1%) |
| `reversal` | `integer` | `3` | Reversal box count |
| `period` | `string` | `6m` | Historical price lookback (`1m`, `3m`, `6m`, `1y`, `2y`) |
| `use_mock` | `boolean` | `false` | Force synthetic benchmark data mode |

**Sample Response:**
```json
{
  "symbol": "NVDA",
  "data_source": "Live Market Data (yfinance)",
  "data_points": 120,
  "parameters": {
    "box_size_pct": 1.0,
    "box_size_val": 2.4013,
    "reversal": 3
  },
  "status_reading": "X15@240.130",
  "trend": "Bullish",
  "signal": "Double Top Buy (Bullish Breakout)",
  "levels": {
    "support": 210.50,
    "resistance": 245.00
  },
  "targets": {
    "near_term": 279.14,
    "long_term": 338.96
  },
  "columns": [...]
}
```

---

## 📈 Magnificent 7 Screening Report

The suite includes pre-calculated PNF analysis for the **Magnificent 7** stocks (`NVDA`, `TSLA`, `GOOGL`, `AMZN`, `MSFT`, `META`, `AAPL`) using 1% box size and 3-box reversal, sorted by **Reward %** in descending order.

See the full report at [OUTPUT.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/OUTPUT.md).

---

## 📜 Technical Specification

For complete mathematical definitions, status reading notations, and benchmark verification details, refer to [SPEC.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/SPEC.md).
