# 📈 Sector Industry Leaders Agent App (v2)

A Python-based interactive web application and research agent that systematically identifies, captures, and exports top stock constituent symbols across market sectors and industries from **Finviz.com**.

---

## ✨ Features

- **Automated Finviz Research Agent**: Extracts top 5 to 10 market-cap ranked stock symbols for each industry within every sector.
- **Sector-by-Sector Iteration**: Aggregates records iteratively across industries.
- **Human-in-the-Loop Review**: Pauses after each sector to allow live UI editing and verification.
- **PDF Report Generation**: Exports sector leader tables into clean PDF documents using ReportLab.
- **Master Combined Export**: Allows downloading all approved sector data as a unified combined CSV file.
- **Cache Management**: Clears session cache after sector approval before advancing to the next sector.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure Python 3.10 or higher is installed.

### 2. Set Up Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Launch Application

```powershell
streamlit run app.py
```
Or directly via `.venv`:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
sector_industry_leaders/
├── app.py              # Main Streamlit web application
├── data_manager.py     # Sector & industry data scraping & mapping module
├── scraper.py          # Finviz web scraper & PDF report generator
├── requirements.txt    # Python package dependencies
├── spec.md             # Functional application specifications
└── README.md           # Documentation & instructions
```
