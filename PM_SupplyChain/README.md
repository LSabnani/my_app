# Power Quality Monitoring (PQM) Commodity Deep Dive & AI Executive Presentation Generator

An **AI-driven presentation pipeline** featuring a **Python Backend (FastAPI)**, a **Multi-Problem Archival Engine ("Another Problem?")**, a **Critic Agent Verification Engine**, an **Interactive WebUI Frontend**, and automated **PPTX/PDF Document Exporters**.

---

## 🌟 Key Features

* **13-Slide Executive Study**: Complete commodity study covering PQM market dynamics, suppliers (Eaton, Schneider Electric, SEL, Janitza, Powerside), hardware/software architectures, evaluation criteria, TCO, strategic roadmaps, and **Next Steps & Implementation Execution Plan** (16 Weeks, $450k budget, $1.8M/yr ROI).
* **Concise Narrative & High-Impact Copy**: Replaces dense paragraphs with 1-2 sentence executive overviews, 3 quantitative metric cards per slide, and 6-12 word sharp bullet points.
* **User Problem Statement Ingestion**: Interactive UI modal and API (`POST /api/problem/ingest`) allowing users to enter custom problem statements or re-scope the presentation deck dynamically.
* **Multi-Problem Archival & Cache Reset ("Another Problem?")**:
  * Action button and API (`POST /api/problem/reset-next`) that automatically archives current outputs as versioned files (`output/PQM_Executive_Deck_YYYYMMDD_HHMMSS.pptx` & `.pdf`).
  * Clears transient approval cache and ratings in `PQM_Commodity_Study.json`.
  * Prompts the executive user for input on the **Next Problem**.
* **Critic Agent Fact & Link Verification**: Performs live HTTP GET/HEAD checks (`httpx`) to verify URL reachability (`HTTP 200 OK`) and cross-checks technical claims (IEC 61000-4-30 Class A, IEEE 1159, SEMI F47, IEC 62443, Modbus, IEC 61850).
* **Interactive Executive Review WebUI**:
  * 1–10 executive slide rating scale.
  * Conditional feedback prompts for scores `< 9` triggering dynamic AI slide revisions.
  * Real-time progress bar tracking slide approval status ($N/13$).
  * Automatic revision log recorded in `Revision_Log.md`.
* **Multi-Format Deck Exporters & Presentation Mode**:
  * **PPTX**: Native 16:9 widescreen PowerPoint presentation generated using `python-pptx` with a clean **white background (`#FFFFFF`)**, crisp dark slate typography, author metadata (*Lalit Sabnani*), date, dynamic scope file name, and slide number in footer.
  * **Fullscreen Presentation Mode**: In-browser presentation modal ("Start Presenting") with a **white canvas (`#FFFFFF`)**, high-contrast typography, metrics grid, and key takeaways.
  * **PDF**: Executive PDF brief generated using `reportlab`.

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup

Ensure Python 3.10+ is installed.

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

---

### 2. Launch the Application Server

Start the Python FastAPI server:

```powershell
python server.py
```

The server will launch at:
👉 **`http://127.0.0.1:8000`**

---

### 3. Using the Interactive WebUI

1. Open **`http://127.0.0.1:8000`** in your browser.
2. Click **New Problem Scope** in the top navigation bar to enter a custom problem statement or target domain scope.
3. Select any slide from the left sidebar navigation (`PQM 1` through `PQM 13`).
4. Click **Verify Links Live** to trigger on-demand Critic Agent HTTP verification on reference URLs.
5. Rate each slide on a scale of **1 to 10**:
   - If rated **9 or 10**: The slide status updates to **Approved** (green badge) and advances to the next slide.
   - If rated **below 9**: A feedback box appears requesting executive feedback. Upon submission, the AI engine refines the slide content and updates `Revision_Log.md`.
6. Click **Export PPTX** or **Export PDF** to download the current presentation deck.
7. Click **Another Problem?** when starting a new study cycle. This automatically archives the current PPTX/PDF files, clears the slide approval cache, and opens the prompt modal for your next problem statement.

---

## 📁 Repository Structure

```
PM_SupplyChain/
├── Spec.md                    # Detailed architectural & slide specification
├── README.md                  # Project overview & usage instructions
├── requirements.txt           # Python dependencies
├── server.py                  # FastAPI backend server & PPTX/PDF export engines
├── index.html                 # Interactive WebUI frontend (HTML5/CSS3/JS)
├── PQM_Commodity_Study.json   # Master dataset containing 13 structured slides
├── Revision_Log.md            # Markdown log tracking executive reviews & revisions
└── output/                    # Generated presentation artifacts & versioned archives
    ├── PQM_Executive_Deck.pptx
    ├── PQM_Executive_Deck.pdf
    ├── PQM_Executive_Deck_20261010_162008.pptx
    └── PQM_Executive_Deck_20261010_162008.pdf
```

---

## ⚡ API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/slides` | `GET` | Returns all 13 slides and current approval metadata |
| `GET /api/slides/{id}` | `GET` | Returns data for a specific slide ID |
| `POST /api/problem/ingest` | `POST` | Ingests a new user problem statement and re-scopes the presentation deck |
| `POST /api/problem/reset-next` | `POST` | Archives current PPTX/PDF outputs, clears slide review cache, and waits for next problem |
| `POST /api/slides/{id}/verify` | `POST` | Triggers Critic Agent live HTTP verification on slide reference links |
| `POST /api/slides/verify-all` | `POST` | Runs a Critic Agent live HTTP verification sweep across all slides |
| `POST /api/slides/{id}/rate` | `POST` | Submits executive rating (1-10) and feedback; triggers LLM slide revision when score < 9 |
| `POST /api/slides/{id}/revise` | `POST` | Triggers LLM regeneration for a specific slide incorporating executive feedback |
| `POST /api/slides/{id}/approve` | `POST` | Sets slide status to Approved (10/10), advancing executive approval progress |
| `POST /api/slides/revise-all-with-feedback` | `POST` | Batch executes LLM slide revisions across all slides containing executive feedback |
| `GET /api/export/pptx` | `GET` | Generates and downloads dynamically named Executive Deck PPTX |
| `GET /api/export/pdf` | `GET` | Generates and downloads dynamically named Executive Deck PDF |

---

## 🧪 Automated Testing & Cache Validation

To validate problem changes, scope re-scoping, and complete cache purging with zero remnant data leakage across studies, run:

```bash
.venv\Scripts\python.exe test_problem_scope_cache.py
```

### Verified Test Assertions:
1. **HTTP Anti-Caching**: Ensures `Cache-Control: no-cache, no-store, must-revalidate` is present.
2. **Complete Cache Purge**: Confirms `POST /api/problem/reset-next` archives existing output decks and resets all 13 slides to Pending/Unrated with zero residual content.
3. **Domain Synthesis (Scope A)**: Validates full synthesis for specialized scopes (e.g., 160kV 3mA X-Ray generators with Comet, Varex, and ASTM standards).
4. **Output Archiving**: Confirms archived files in `output/` match the sanitized scope prefix and timestamp.
5. **Zero-Pollution Scope Transition (Scope B)**: Validates ingestion of BESS infrastructure and proves zero Scope A tokens remain in cache.
6. **Procedural Commodity Synthesis (Scope C)**: Tests general procedural commodities with disk and memory cache synchronization.
7. **Dynamic Export Naming**: Ensures PPTX/PDF downloads dynamically reflect the active problem scope.

