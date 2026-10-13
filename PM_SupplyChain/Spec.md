# Specification: AI-Powered Power Quality Monitoring (PQM) Commodity Deep Dive & Executive Deck Generator

## 1. System Overview & Architecture
This project is an **AI-driven presentation pipeline** featuring a **Python Backend** with an automated **Critic Agent Verification loop** and an **interactive WebUI Frontend**. It automates the generation, factual verification, executive review, concise visual styling, iterative refinement, and final export (PDF/PPTX) of a **13-slide executive presentation deck** on **Power Quality Monitoring (PQM) solutions**.

```mermaid
graph TD
    subgraph Frontend ["WebUI Frontend (HTML/JS/CSS)"]
        UI0[User Problem / Scope Input Modal]
        UI1[Interactive Slide Viewer]
        UI2[Rating & Feedback Control (1-10 Scale)]
        UI3[Revision History & Diff Tracker]
        UI4[Export Trigger (PPTX / PDF)]
        UI5[Another Problem Trigger]
    end

    subgraph Backend ["Python Backend (FastAPI / AI Pipeline)"]
        API[REST & WebSocket API Endpoints]
        ProbEngine[Problem Ingestion & Scope Parser]
        Engine[AI Orchestrator / LLM Generator]
        Critic[Critic Agent & Fact Verifier]
        KDB[PQM Knowledge Base & Reference Links]
        RevEngine[Revision Engine & Diff Tracker]
        Archiver[Output Archiver & Cache Resetter]
        Exporter[PPTX / PDF Export Engine (python-pptx / ReportLab)]
    end

    UI0 --> API
    API --> ProbEngine
    ProbEngine --> Engine
    UI1 <--> API
    UI2 --> API
    API <--> Engine
    Engine --> Critic
    Critic <--> KDB
    Critic --> API
    API <--> RevEngine
    UI4 --> API
    API --> Exporter
    UI5 --> API
    API --> Archiver
    Archiver --> Exporter
    Archiver --> UI0
```

---

## 2. Core Features & Capabilities

### 2.1 Concise Narrative & Visual Design Standards
* **Punchy Executive Copy**: Replaces dense narrative paragraphs with concise **1–2 sentence executive summaries**.
* **High-Impact Metric Callout Cards**: Displays **3 quantitative metric cards** per slide (`99.9999% Uptime`, `$2.4M Risk/hr`, `16 Weeks`, `$450k Budget`, `$1.8M ROI`) with high contrast styling.
* **Sharp Takeaways**: Formats key takeaways into **6–12 word action-oriented bullet statements**.
* **Single-Line Footer Metadata**: Every slide includes author metadata, file name, date, slide number, and live verified reference sources:  
* **Single-Line Footer Metadata**: Every slide includes author metadata, dynamic scope prefix, date, slide number, and live verified reference sources:  
  `<SCOPE_TAG> #  •  <SCOPE_PREFIX>_Executive_Deck  •  Author: Lalit Sabnani  •  Date  •  Verified Sources`

### 2.2 User Input & New Problem Ingestion Architecture
* **Dynamic Problem Statement Capture**: Allows executive users to input new problem definitions, custom scopes, specialized industry domains (e.g., semiconductor fabs, hyperscale AI data centers, TIC electron microscopy), or target vendor lists via `POST /api/problem/ingest`.
* **Scope Parser & Complete Re-Synthesizer**: The AI pipeline parses the incoming user problem statement, extracts key requirements, updates presentation objectives, and completely re-synthesizes all 13 slide titles, subtitles, detailed content, takeaways, and metric callouts with zero remnants of prior studies.
* **Continuous Fact & Source Binding**: Automatically updates and attaches relevant technical standards and reference URLs for the new problem domain.
* **Multi-Problem Archival & Cache Reset ("Another Problem?")**:
  * When the user prompts for **"Another Problem?"** via `POST /api/problem/reset-next`:
    1. **Save Outputs**: Automatically compiles and archives current presentation decks as versioned **PPTX** and **PDF** files in `output/` (e.g., `<SCOPE_PREFIX>_Executive_Deck_YYYYMMDD_HHMMSS.pptx` & `.pdf`).
    2. **Clear Cache**: Clears the active slide approval cache, resets slide ratings to `Pending`, and clears transient feedback history in `PQM_Commodity_Study.json`.
    3. **Idle / Wait State**: Displays the **New Problem Input Modal** on the WebUI, awaiting executive inputs for the next problem statement.

### 2.3 Python AI Pipeline Backend & Critic Agent
* **AI Generator**: Synthesizes slide content using domain knowledge for PQM solutions, TIC Electron Microscopy (TEM, SEM, FIB-SEM), suppliers, evaluation criteria, and execution roadmaps.
* **Critic Agent & Verification Loop**: 
  * Every generated slide includes **detailed primary reference links** (industry standards, vendor product specs, technical whitepapers, IEEE/IEC standards, market reports).
  * The **Critic Agent** performs live HTTP checks (`httpx`) to verify URL reachability (`HTTP 200 OK`) and cross-checks technical claims.
* **Iterative Revision Engine**: Processes executive ratings (1–10 scale) and textual feedback. When a slide receives a score lower than 9, the pipeline dynamically refines the content and re-verifies via the Critic Agent.
* **Revision Tracking & Logging**: Maintains full revision history in `Revision_Log.md` / JSON store to log slide state before/after feedback.
* **Document Exporter**:
  * **PPTX Generator**: Uses `python-pptx` to build native, highly polished PowerPoint decks with a clean **solid white background (`#FFFFFF`)**, crisp dark slate typography (`#0F172A` / `#334155`), high-contrast accent highlights, author metadata (*Lalit Sabnani*), date, dynamic scope file name, and slide number in the footer.
  * **PDF Generator**: Uses `reportlab` to build executive PDF briefs with dynamic scope titles.

### 2.4 Interactive WebUI Frontend
* **"Another Problem?" Action Center**: Header trigger allowing users to save current outputs, clear state, and open the new problem prompt modal.
* **Executive Slide Carousel / Viewer**: Displays rendered slides along with metric cards, visual diagrams, and **clickable Critic Verification Reference Links with live HTTP status badges**.
* **Fullscreen Presentation Mode ("Start Presenting")**: Clean, presentation-ready full-screen overlay mode styled with a **white canvas (`#FFFFFF`)**, dark typography, metric callout cards, and key executive takeaways.
* **Footer Info Line**: Displays `<SCOPE_TAG> #  •  <SCOPE_PREFIX>_Executive_Deck  •  Author: Lalit Sabnani  •  Date  •  Verified Sources`.
* **Feedback Modal / Controller**:
  * Rating buttons / slider (1 to 10 scale).
  * Conditional feedback input (required when rating < 9).
  * One-click "Approve & Next" vs. "Regenerate with Feedback".
* **Live Progress & Revision Dashboard**: Displays approval status across all 13 slides and historical feedback logs.
* **Export Action Center**: Trigger PDF / PPTX download once all slides are approved (score $\ge$ 9).

---

## 3. 13-Slide Executive Deck Structure & Critic Verification Links

| Slide # | Slide Title | Technical & Commodity Content Focus | Critic Agent Verification Reference Links |
| :--- | :--- | :--- | :--- |
| **Slide 1** | **Title & Executive Summary** | Project Context, Technology Landscape (TEM, SEM, FIB-SEM), Scope, and Strategic Takeaways | • [ISO/IEC 17025 Testing Accreditation](https://www.iso.org/standard/66912.html)<br>• [IEEE Industry Applications Standard](https://www.ieee-pes.org/) |
| **Slide 2** | **Commodity Definition & Industry Relevance** | Modality Specs (ARM200F TEM, Quanta 450 SEM, Scios 2 / Helios 5 FIB-SEM), Failure Analysis & Microstructure | • [ISO 9001 Quality Management Standards](https://www.iso.org/iso-9001-quality-management.html)<br>• [NIST Engineering Infrastructure Framework](https://www.nist.gov/cyberframework) |
| **Slide 3** | **Market Dynamics & Macro Drivers** | Market Size ($1.61B to $2.22B MarketsandMarkets; $5.28B to $7.82B Mordor), CAGR, Semiconductor 2nm Scaling | • [IEA Industry & Technology Outlook](https://www.iea.org/reports/electricity-2024)<br>• [McKinsey Market Dynamics Study](https://www.mckinsey.com/capabilities/operations/our-insights) |
| **Slide 4** | **Competitive Landscape & Market Share** | Equipment Market Shares (Hitachi 30.77% SEM, Thermo Fisher 86.17% TEM & 58.42% FIB-SEM), Supplier Tiers | • [Gartner Vendor Magic Quadrant](https://www.gartner.com/en/supply-chain)<br>• [IEEE Vendor Evaluation Matrix](https://www.ieee-pes.org/) |
| **Slide 5** | **Supplier Differentiation & USPs** | Equipment Makers (Thermo Fisher, ZEISS, JEOL, TESCAN) vs. TIC Labs (SGS, Intertek, Eurofins EAG, Exponent) | • [ISA Technical Vendor Comparison](https://www.isa.org/standards-and-publications)<br>• [CIGRE Equipment Assessment](https://www.cigre.org/) |
| **Slide 6** | **Product & Hardware Architecture** | Dual-Beam Ion Column, Electron Optics, Detector Suites, Telemetry Gateways | • [IEC 61850 Communication Standard](https://www.iec.ch/grid/smartgrid/smartgrid_61850.htm)<br>• [Modbus Organization Specs](https://modbus.org/specs.php) |
| **Slide 7** | **Software Platforms & Power Analytics** | Image Acquisition Automation, 3D Serial Reconstruction, Real-Time EPMS & Predictive Analytics | • [Schneider EcoStruxure Power Monitoring Expert](https://www.se.com/ww/en/product-range/61347-ecostruxure-power-monitoring-expert/)<br>• [Eaton Foreseer EPMS Software](https://www.eaton.com/us/en-us/catalog/backup-power-ups-surge-it-power-distribution/eaton-foreseer-epms.html) |
| **Slide 8** | **Service Offerings & Lifecycle Management** | ISO/IEC 17025 Accreditation, Annual Calibration, Maintenance Contracts, Skilled Staffing | • [ISO/IEC 17025 Laboratory Accreditation](https://www.iso.org/standard/66912.html)<br>• [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) |
| **Slide 9** | **Vendor Evaluation & Selection Criteria** | Scoring Matrix: Resolution & Accuracy (30%), TCO (25%), Interoperability (20%), Cyber (15%), Support (10%) | • [IEC 61850 Communication Networks](https://www.iec.ch/grid/smartgrid/smartgrid_61850.htm)<br>• [Modbus Organization Specifications](https://modbus.org/specs.php) |
| **Slide 10** | **Total Cost of Ownership (TCO) & Sourcing Risk** | CapEx (35%) vs. OpEx (65%), Equipment Lead Times, In-House Lab Substitution Risk | • [Gartner IT/Facilities Procurement Best Practices](https://www.gartner.com/en/supply-chain)<br>• [McKinsey Supply Chain Resilience Framework](https://www.mckinsey.com/capabilities/operations/our-insights) |
| **Slide 11** | **Implementation & Operational Roadmap** | Phased Deployment (Audits, Staging, Rollout), CTB Staging & FRACAS Governance | • [ASQ FRACAS Quality Standard](https://asq.org/quality-resources/fracas)<br>• [PMI Standard for Program Management](https://www.pmi.org/pmbok-guide-standards) |
| **Slide 12** | **Strategic Recommendations & Sourcing Plan** | Sourcing Framework: Equipment Acquisition vs. Outsourced TIC Services, Dual-Vendor Contracts | • [IEEE Power & Energy Society Procurement Guidelines](https://www.ieee-pes.org/)<br>• [CIGRE Power Quality Working Group Reports](https://www.cigre.org/) |
| **Slide 13** | **Next Steps & Implementation Execution Plan** | Key Deliverables, 16-Week Execution Timeline, $450k Budget, $1.8M/yr ROI Risk Mitigation | • [PMI Project Budgeting & Governance Standard](https://www.pmi.org/pmbok-guide-standards)<br>• [Gartner IT & Facilities Execution Framework](https://www.gartner.com/en/supply-chain) |

---

## 4. Deliverables

1. [Spec.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PM_SupplyChain/Spec.md) *(This file)*: Master specification.
2. [README.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PM_SupplyChain/README.md): Quickstart guide & project overview.
3. `server.py`: FastAPI backend application with dynamic file exports & `POST /api/problem/reset-next` archiver.
4. `index.html`: Interactive WebUI frontend with dynamic scope footers & "Another Problem?" modal.
5. `PQM_Commodity_Study.json`: Master presentation dataset (13 concise slides for active TIC study).
6. `Revision_Log.md`: Executive revision log.
7. `output/TIC_Electron_Microscopy_Services_Equipment_Market_Executive_Deck.pptx` & `output/TIC_Electron_Microscopy_Services_Equipment_Market_Executive_Deck.pdf`: Exported deck artifacts.
