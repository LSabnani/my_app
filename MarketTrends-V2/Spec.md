# Specification Document: Market Trends Analyzer V2

## 1. Overview
The **Market Trends Analyzer V2** is an AI-powered analytical system designed to research, analyze, and synthesize market intelligence into a professional multi-slide presentation deck based on user-provided industry and market segment inputs.

The system features an interactive **Competitor Approval Gateway** before deep market research, dynamically resolving top competitors by market cap and allowing user override via Finviz lookup.

---

## 2. Role & Persona
* **Role Title:** Experienced Marketing Professional
* **System Persona:** Acts as a seasoned marketing strategist capable of in-depth research across industry verticals, identifying growth drivers, competitive dynamics, product differentiators, and compliance frameworks.

---

## 3. User Workflow & Interactive Approval Flow

1. **Initial Input:**
   * User provides target `Industry` and `Market Segment` (or optional initial stock ticker).

2. **Top 5 Competitors Resolution & Approval Prompt:**
   * System resolves and presents the top 5 market-cap leading competitors in the specified space.
   * System prompts the user for approval ("Do you approve this competitor set?").

3. **Fallback Resolution (If User Does NOT Approve):**
   * If the user rejects the initial competitor set, the system asks the user to enter a **Stock Symbol** of one of the target competitor companies.
   * System queries **Finviz (`finviz.com`)** using the provided stock ticker to extract its exact **Sector** and **Industry**.
   * System maps to the sector/industry space on Finviz to extract the top 5 competitors in that space by market capitalization.
   * System presents the updated top 5 competitors and again requests user approval.

4. **Market Analysis Execution:**
   * **Only after the user explicitly approves** the competitor set does the system trigger the full market trends, sizing, differentiators, and compliance analysis study.

5. **Paginated Deck Presentation:**
   * Results are presented **one page (slide) at a time** with interactive navigation controls (Next/Previous page views).

---

## 4. Market Data Resolution & Finviz Scraping Strategy
* **Initial Resolution:** Regex phrase matching and curated/live sector resolution for top 5 competitors by market cap across major sectors:
  1. **Industrials / Aerospace & Defense:** General Dynamics (GD), RTX Corp (RTX), Lockheed Martin (LMT), Boeing (BA), Northrop Grumman (NOC) — incorporating low-cost combat drones, FPV kamikaze loitering munitions, EW jamming resilience, and real-world combat lessons from Ukraine and Iran conflicts.
  2. **Energy / Oil & Gas Integrated:** Exxon Mobil (XOM), Chevron (CVX), Shell (SHEL), TotalEnergies (TTE), BP (BP) — incorporating Middle East / Iran geopolitical conflict risks, supply security, and LNG long-term contracting.
  3. **Healthcare / Drug Manufacturers General:** Eli Lilly & Co (LLY), Johnson & Johnson (JNJ), AbbVie Inc (ABBV), Merck & Co (MRK), Novartis AG (NVS).
  4. **Consumer Cyclical / Auto Manufacturers:** Tesla (TSLA), Toyota (TM), General Motors (GM), Ferrari (RACE), Ford Motor (F).
  5. **Financial / Credit Services:** Visa Inc (V), Mastercard Inc (MA), American Express (AXP), Capital One (COF), PayPal (PYPL).
  6. **Technology / Semiconductor Equipment & Materials:** ASML Holding (ASML), Applied Materials (AMAT), Lam Research (LRCX), KLA Corp (KLAC).
  7. **Communication Services / Broadcasting & Media:** Fox Corporation (FOXA), Paramount Global (PARA), Nexstar Media Group (NXST), Tegna Inc (TGNA), Gray Television (GTN) — incorporating major broadcast TV networks (CBS, ABC, NBC, FOX), news networks (Fox News, CBS News, NewsNation, CNN), and FAST streaming platforms.
  8. **Communication Services / Entertainment:** The Walt Disney Company (DIS), Netflix (NFLX), Warner Bros. Discovery (WBD), Live Nation Entertainment (LYV), Fox Corporation (FOX) — spanning major broadcast/cable networks, live music & event ticketing, and direct-to-consumer streaming.
  9. **Consumer Defensive / Beverages - Non-Alcoholic:** The Coca-Cola Company (KO), PepsiCo Inc (PEP), Monster Beverage Corporation (MNST), Keurig Dr Pepper (KDP), Celsius Holdings (CELH) — spanning Direct-Store-Delivery (DSD) bottling networks, zero-sugar carbonated soft drinks, Gatorade/BodyArmor hydration, and functional thermogenic energy drinks.
  10. **Consumer Defensive / Beverages - Wineries & Distilleries:** Diageo plc (DEO), Constellation Brands (STZ), Brown-Forman (BF-B), Pernod Ricard (PRNDY), The Duckhorn Portfolio (NAPA) — spanning Three-Tier wholesale distribution, premium scotch/tequila/bourbon spirits, estate Napa Valley wine production, and canned RTD spirit cocktails.
* **Finviz (`finviz.com`) Integration:**
  * Endpoint / Web Scraping: `https://finviz.com/quote.ashx?t={TICKER}`
  * Data Extracted: Sector (e.g. `Technology`), Industry (e.g. `Semiconductors`), and Country Filter (e.g. `geo_usa`).
  * Competitor Selection Window: Queries Finviz screener filtered by country, industry, and sector (`geo_usa,ind_semiconductors,sec_technology`) ordered by market cap (`o=-marketcap`). It positions a 5-company window centered on the target stock (2 companies above and 2 companies below its market cap rank). For example, entering `INTC` automatically extracts `geo_usa`, `Semiconductors`, and `Technology`, returning `MU`, `AMD`, `INTC`, `TXN`, and `MRVL`.
  * Extracted Top 5 competitors are fed into the approval pipeline.

---

## 5. Research Scope & Deliverables
Once competitor approval is granted, the system conducts research across five key areas:

1. **Market Trends & Customer Preferences:**
   * Macro and micro market trends shaping the segment.
   * Customer favorability factors and purchasing drivers.

2. **What Makes a Customer Choose the Product (Customer Choice Drivers):**
   * Primary decision criteria driving customer selection (e.g., ROI / Total Cost of Ownership, clinical efficacy & safety, brand trust, reliability SLAs, software ecosystem lock-in).
   * Key factors distinguishing winning products during customer evaluation.

3. **Market Sizing & Share:**
   * Total Market Segment Size in USD ($) for the previous year.
   * Market share breakdown for each of the approved **Top 5 Competitors**.

4. **Product Characteristics & Differentiators:**
   * Key features making leading products/services exciting.
   * Unique competitive differentiators (R&D scale, tech stack, patent moats, distribution).

5. **Regulatory & Compliance Specifications:**
   * Mandatory compliance requirements by government entities (FDA, EMA, NHTSA, BIS, etc.).
   * Industry standards (cGMP, ISO, SEMI, SOC 2, HIPAA/GDPR).
   * Segment-specific technical specs (Cold-chain logistics, electronic records compliance, data privacy).

---

## 6. Technology Stack & Environment
* **Backend:** Python (Flask + Requests + BeautifulSoup4 / Finviz Scraper)
* **Frontend:** Web Interface (HTML5, Vanilla CSS3, JavaScript ES6)
* **Output Format:** Interactive Web Slide Deck with Single Page View & PDF Export capability.

---

## 7. Output Presentation & Page-by-Page Specification
The output is structured as a paginated presentation deck displayed **one slide/page at a time**:

* **Page 1: Executive Summary & Market Sizing**
  * Overview of Industry & Market Segment.
  * Total Market Segment Size ($ Last Year) & YoY Growth.
* **Page 2: Market Trends & Customer Choice Drivers**
  * Generalized 8-part structured market intelligence grid applicable to every sector/industry query, featuring verified inline clickable source links (`[Source](url)`):
    1. **Trends:** Current market trends and shift drivers shaping the sector.
    2. **Market Size and Growth:** Current market valuation ($) and long-term CAGR projection metrics.
    3. **Spending Patterns:** Discretionary vs. non-discretionary consumer and enterprise spending allocations.
    4. **Shifts or Changes:** Structural macroeconomic, demographic, interest rate, and regulatory pivots.
    5. **Technology and Consumer Behavior:** Digital app adoption, AI integration, smart tech tools, and consumer expectations.
    6. **Retail and Competitive Landscape:** Market share distribution, big-box/DTC distribution channels, and private label growth.
    7. **Challenges:** Industry headwinds, raw material inflation, labor shortages, and supply chain risks.
    8. **Bottom Line:** Strategic summary takeaway and winning positioning recommendations for stakeholders.
* **Page 3: Competitive Landscape & Market Share**
  * Approved Top 5 market cap leading competitors with tickers and market share percentages.
  * **Differentiating Value Proposition:** Dedicated section per competitor detailing its unique core offering, strategic value proposition, and competitive advantage.
  * **Top 3 Key Products per Competitor:** Granular breakdown of the top 3 flagship products or services for each of the 5 leaders.
  * **Leading Product Highlight:** Prominent callout summarizing the market leader's dominant product positioning and key differentiator.
* **Page 4: Product Excitement & Differentiating Factors**
  * Characteristics making top products/services exciting.
  * Key differentiating pillars across R&D, tech stack, and scale.
  * **Competitor Differentiating Capability Ratings Matrix (1-5 Scale):** Interactive rating table evaluating all 5 approved competitors on a 1-5 scale across 4 core differentiating dimensions (*Product Innovation & Tech Stack*, *Market Reach & Brand Loyalty*, *Cost Efficiency & Pricing Power*, and *Ecosystem Integration & Scale Moat*), featuring an aggregate overall benchmark score.
* **Page 5: Compliance Framework & Industry Specifications**
  * Mandatory government compliance requirements.
  * Industry and segment-specific standards & specs.
* **Page 6: Product Specification Roadmap**
  * **Minimum Viable Product (MVP) Specifications:** Baseline functional features, essential SLA reliability, standard API interoperability, and low-friction entry pricing.
  * **Winning Product Specifications:** Market-leading performance/speed, advanced AI/ML automated workflows, 99.999% high-availability SLA, and strong ecosystem moats.

---

## 8. UI & Interaction Features
* **Competitor Approval Modal / Card:** Interactive prompt to confirm or revise competitor selection before running full analysis.
* **Stock Symbol Finviz Search Form:** Displayed when user clicks "No / Modify Competitors" to look up ticker, sector, and industry via `finviz.com`.
* **Dynamic Industry & Segment Header Injection:** Every slide title, subtitle, and breakdown explicitly references the active Industry Vertical and Market Segment.
* **Information Sources & Citations Footer:** Every slide features a dedicated footer displaying verified clickable links (`🔗 Information Sources & Citations`) referencing SEC EDGAR 10-K filings, Finviz screener data, Gartner/Forrester research, McKinsey industry studies, regulatory databases (FCC/FDA/ISO/NIST), and market intelligence sources.
* **Per-Slide Review & Approval Gateway:** Once competitors are approved, the presentation presents each slide sequentially with an explicit **Slide Review Gateway Bar** (`✓ Approve Slide & Next` or `✎ Flag for Revision`). The system tracks individual slide approvals and notifies the user upon full deck approval.
* **Page-by-Page Viewer:** Navigation controls (Next Slide / Previous Slide / Slide Progress Dots) displaying one page at a time.
* **Reset Button:**
  1. Exports current deck as **PDF** if desired.
  2. Clears backend/frontend session state and competitor selections.
  3. Resets input fields and starts fresh session.
