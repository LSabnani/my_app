# Agent with RAG Web Application

A Flask web application for managing an AI Agent with Retrieval-Augmented Generation (RAG) abilities, vector stores powered by local Ollama and ChromaDB, telemetry metrics, full audit payload logging, and dynamic skill execution.

## 🚀 Key Features

1. **Multi-Tab Glassmorphism UI**:
   - **Page 1: Chat & Knowledge Synthesis**: Interactive chat with Custom & Google ADK Agents, skill/tool execution loops, expandable step timers & logs, and retrieved context evidence breakdown.
   - **Page 2: Vector DB Ingestion**: Document and skill vector storage management, URL & directory vectorization, embedder model switching with warning confirmation, and document chunk inspection.
   - **Page 3: Telemetry**: Real-time System Throughput and Token Velocity charts (1m/15m/1h/1d intervals) with advanced performance metrics (TTFT, ITL, TPS, TPOT).
   - **Page 4: Audit Log & Event**: Comprehensive transparent event log viewer, user conversation inspection, API key redaction (`****`), and raw JSON payload modal viewer.

2. **Backend & Architecture**:
   - **Custom Agent**: Multi-turn planning, skill discovery, tool selection, procedural tool execution (Open-Meteo weather/time, person registry CSV lookup, stock market simulator, document search), and answer synthesis.
   - **Google ADK Agent**: Google ADK LlmAgent wrapper integration.
   - **Vector Stores**: ChromaDB vector databases (`skills_db` and `documents_db`) using local `ollama` embeddings (`nomic-embed-text` default).
   - **Environment & Configuration**: Configurable via `.env` or `--port` CLI argument.

---

## 🛠️ Prerequisites & Installation

1. **Activate Virtual Environment**:
   ```powershell
   .\.venv\Scripts\activate.ps1
   ```

2. **Install Required Packages**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure Environment (`.env`)**:
   Copy `.env.example` to `.env` and set your Google GenAI API key:
   ```env
   GEMINI_API_KEY=your_google_genai_api_key_here
   GEMINI_MODEL=gemma-4-26b-a4b-it
   PORT=5000
   ```

---

## 🚦 Running the Application

Start the web application orchestrator using:
```powershell
python app.py
```
Or specify a custom port:
```powershell
python app.py --port 8005
```

Open your browser and navigate to:
`http://localhost:5000` (or `http://localhost:8005`)

---

## 🛑 Shutting Down Services

- **Via GUI**: Click the light red **Shutdown** button in the top right corner of the web interface. Type `Shutdown the service` in the text field and click **Confirm Shutdown**. This gracefully terminates any background services (such as Ollama) started by the app.
- **Via Terminal**: Press `Ctrl + C` in the running PowerShell terminal.

---

## 📖 User Guide

### 1. Chat & Knowledge Synthesis Page
- Select your model from the dropdown. Selecting **Custom Model** reveals an input box to specify a custom OpenAI-compatible API endpoint (e.g. `http://127.0.0.1:8000/v1/chat/completions`). Standard Google AI Studio models route directly via the Google GenAI SDK.
- Configure temperature, max tokens, agent type (**Custom Agent** or **Google ADK Agent**), max turns (1–10), skill selector mode, and thresholds.
- Type your question in the chat bar (e.g., *"What is the weather and time in Tokyo?"* or *"Who is Lucas Dubois?"*).
  - *Time & Weather Tool*: Calculates the target city's exact local timezone (e.g. `Asia/Tokyo` / `JST`) and presents actual timestamps (`current_local_time`) without placeholder text.
- Click **Show Logs** on any agent message bubble to inspect step-by-step component execution and elapsed timers.
- Inspect matching vector chunks and skill scores in the **Retrieved Context Evidence** panel on the right.

### 2. Vector DB Ingestion Page
- View overall DB statistics (chunks, documents, DB size in MB).
- Ingest documents by providing a local folder path (e.g., `sample_docs`) or web URL, adjust chunk size and overlap, and click **Populate Vector Database**.
- Click sample preset buttons for rapid URL testing.
- Click **Update Skills Database** to scan `skills/` for new procedural tools.
- Delete individual documents or click **Reset DB** to clear vector storage.

### 3. Telemetry Page
- Monitor KPI metrics: Total Prompts, Responses, Errors, Input Tokens, and Output Tokens.
- Switch aggregation interval (1 min, 15 min, 1 hr, 1 day) and time range to visualize **System Throughput** and **Token Velocity** on dual line graphs.
- Track low-performance Metrics: Time to First Token (TTFT), Inter-Token Latency (ITL), Tokens Per Second (TPS), and Time Per Output Token (TPOT).

### 4. Audit Log & Event Page
- View top-level conversation summaries in the **User Conversations** table.
- Click any conversation row to view all associated events in chronological order.
- Click any event row to open a pop-up modal displaying the unredacted (keys sanitized) raw JSON payload.
