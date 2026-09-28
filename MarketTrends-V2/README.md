# Market Trends Analyzer V2 📊

An AI-driven market intelligence platform and professional presentation deck generator built with Python (Flask) featuring an **Interactive Competitor Approval Gateway**, **Finviz Sector Lookup**, and **Page-by-Page Deck Viewing**.

---

## 🌟 Key Features

* **Competitor Approval Gateway:** Displays the top 5 competitors by market cap and requires user approval before starting market analysis.
* **Finviz Stock Symbol Lookup & Centered Market-Cap Selection:** If initial competitors are rejected, users can enter a company's stock ticker (e.g. `INTC`). The system scrapes `finviz.com` to extract country (`geo_usa`), sector, and industry, and automatically selects **2 companies above and 2 companies below** the target company's market cap rank (e.g., returning `MU`, `AMD`, `INTC`, `TXN`, and `MRVL` for `INTC`).
* **Real-World Market-Cap Resolution:** Dynamically fetches and ranks industry leaders according to stock market capitalization.
* **Gated Market Analysis Study:** Detailed market trends research, sizing, differentiators, and compliance analysis only executes after user approval.
* **Paginated Deck Viewing (One Page at a Time):**
  1. **Page 1:** Executive Summary & Market Sizing ($ Last Year & YoY Growth)
  2. **Page 2:** Market Trends & What Makes a Customer Choose the Product (Decision drivers & selection criteria)
  3. **Page 3:** Leading Products & Market Share (Approved Top 5 leaders with stock tickers, market share %, **Top 3 Key Products for each competitor**, and **Leading Product & Key Differentiating Characteristic line**)
  4. **Page 4:** Product Excitement & Differentiators (Unique characteristics & competitive moats)
  5. **Page 5:** Mandatory Compliance & Industry Specs (FDA, cGMP, NHTSA, ISO 26262, SEMI)
  6. **Page 6:** Product Specification Roadmap (**Minimum Viable Product (MVP) vs. Winning Product Specifications**)
* **Instant PDF Export:** Client-side vector PDF generation of the presentation deck.
* **State Reset:** One-click Reset button clears backend/frontend state and competitor approvals for a fresh research session.

---

## 📁 Project Structure

```text
MarketTrends-V2/
├── app.py                      # Flask application server & market research engine
├── Spec.md                     # Markdown specification document
├── MarketTrends-V2.yaml        # YAML system schema & configuration spec
├── .env                        # Environment configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & setup guide
├── templates/
│   └── index.html              # Modern web app UI template
└── static/
    ├── css/
    │   └── styles.css          # Glassmorphic dark styling & print layout rules
    └── js/
        └── app.js              # Slide carousel controller & PDF exporter
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Python 3.9+** installed on your system.

### 2. Environment Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run Application

```powershell
python app.py
```

Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 💡 Usage Workflow

1. **Step 1 - Target Input:** Enter target `Industry` and `Market Segment`.
2. **Step 2 - Review Competitors:** Review the presented Top 5 competitors by market cap.
   * Click **Approve** to proceed directly to full market analysis.
   * Click **Modify / Disapprove** if you want to specify a target competitor ticker.
3. **Step 3 - Finviz Lookup (If Disapproved):** Enter stock symbol (e.g., `GD`, `LMT`, `RTX`, `INTC`, `XOM`, `MA`, `V`, `TSLA`, or `LLY`). System maps `finviz.com` country, sector & industry (e.g., `Industrials` / `Aerospace & Defense`), presents updated top 5 competitors centered around market cap, and asks for approval.
4. **Step 4 - Market Analysis Study:** Once approved, system generates the 5-page intelligence report.
5. **Step 5 - Page-by-Page View:** Navigate through the deck one page at a time.

---

## 🛠️ Technology Stack & Dependencies

* **Backend:** Python 3, Flask, Requests, BeautifulSoup4 (Finviz Scraper), Jinja2, Werkzeug, python-dotenv
* **Frontend:** HTML5, CSS3 (Vanilla Glassmorphism), JavaScript (ES6)
* **PDF Engine:** `html2pdf.js` / `jsPDF`
* **Data Source:** Finviz Web Scraper & Live Market Cap Leaderboard

