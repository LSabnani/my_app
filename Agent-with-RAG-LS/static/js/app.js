document.addEventListener('DOMContentLoaded', () => {
    // Current state variables
    let currentConversationId = 'conv_' + Date.now();
    let currentModelFilter = 'All Models';
    let currentInterval = '15 min';
    let currentTimeRange = '1 day';
    let throughputChart = null;
    let tokenChart = null;
    let selectedConversationId = null;

    // --- Tab Navigation Setup ---
    const tabLinks = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
    tabLinks.forEach(link => {
        link.addEventListener('shown.bs.tab', (e) => {
            const targetId = e.target.getAttribute('href');
            if (targetId === '#page-ingestion') {
                loadIngestionData();
            } else if (targetId === '#page-telemetry') {
                loadTelemetryData();
            } else if (targetId === '#page-audit') {
                loadAuditData();
            }
        });
    });

    // --- Periodic Backend Health Check ---
    async function checkHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            const badge = document.getElementById('agent-status-badge');
            if (badge) {
                badge.innerHTML = `<i class="bi bi-heart-pulse-fill me-1"></i> Backend: ${data.status.toUpperCase()} | Ollama: ${data.ollama ? 'ONLINE' : 'OFFLINE'}`;
            }
        } catch (e) {
            const badge = document.getElementById('agent-status-badge');
            if (badge) {
                badge.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1 text-danger"></i> Backend Offline`;
            }
        }
    }
    checkHealth();
    setInterval(checkHealth, 10000);

    // --- Shutdown Confirmation Modal ---
    const shutdownInput = document.getElementById('shutdown-confirm-input');
    const shutdownBtn = document.getElementById('confirm-shutdown-btn');
    if (shutdownInput && shutdownBtn) {
        shutdownInput.addEventListener('input', () => {
            shutdownBtn.disabled = (shutdownInput.value.trim() !== 'Shutdown the service');
        });
        shutdownBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/shutdown', { method: 'POST' });
                alert('Application and services are shutting down...');
                window.close();
            } catch (e) {
                alert('Shutdown signal sent.');
            }
        });
    }

    // --- PAGE 1: CHAT & KNOWLEDGE SYNTHESIS ---
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatInput = document.getElementById('chat-user-input');
    const chatContainer = document.getElementById('chat-container');
    const skillSelector = document.getElementById('skill-selector');
    const skillThresholdBox = document.getElementById('skill-threshold-container');

    const modelSelect = document.getElementById('model-select');
    const customEndpointContainer = document.getElementById('custom-endpoint-container');

    if (modelSelect && customEndpointContainer) {
        modelSelect.addEventListener('change', () => {
            if (modelSelect.value === 'Custom Model') {
                customEndpointContainer.style.display = 'block';
            } else {
                customEndpointContainer.style.display = 'none';
            }
        });
    }

    if (skillSelector && skillThresholdBox) {
        skillSelector.addEventListener('change', () => {
            if (skillSelector.value === 'Vector Store Selects') {
                skillThresholdBox.style.display = 'block';
            } else {
                skillThresholdBox.style.display = 'none';
            }
        });
    }

    async function sendChatMessage() {
        const query = chatInput.value.trim();
        if (!query) return;

        // Append User Message to UI
        appendUserMessage(query);
        chatInput.value = '';

        const model = document.getElementById('model-select').value;
        const temperature = parseFloat(document.getElementById('temp-input').value || 0.7);
        const maxTokens = parseInt(document.getElementById('max-tokens-input').value || 2048);
        const agentType = document.getElementById('agent-type-select').value;
        const maxTurns = parseInt(document.getElementById('max-turns-input').value || 3);
        const skillMode = document.getElementById('skill-selector').value;
        const skillThreshold = parseFloat(document.getElementById('skill-threshold-input').value || 0.2);
        const docThreshold = parseFloat(document.getElementById('doc-threshold-input').value || 0.3);
        const maxRagChunks = parseInt(document.getElementById('max-rag-chunks-select').value || 5);
        const customEndpoint = document.getElementById('custom-endpoint-input')?.value || '';

        currentConversationId = 'conv_' + Date.now();

        // Append Loading Indicator
        const loadingId = 'loading_' + Date.now();
        appendLoadingMessage(loadingId);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query,
                    conversation_id: currentConversationId,
                    model,
                    temperature,
                    max_tokens: maxTokens,
                    agent_type: agentType,
                    max_turns: maxTurns,
                    skill_selector_mode: skillMode,
                    skill_threshold: skillThreshold,
                    doc_threshold: docThreshold,
                    max_rag_chunks: maxRagChunks,
                    custom_endpoint: customEndpoint
                })
            });
            const data = await res.json();
            removeLoadingMessage(loadingId);

            if (data.status === 'success') {
                appendAgentMessage(data.agent_response, data.step_logs);
                renderRetrievedEvidence(data.evidence, data.skills_matched);
            } else {
                appendAgentMessage(`Error: ${data.message || 'Failed to process message.'}`, []);
            }
        } catch (e) {
            removeLoadingMessage(loadingId);
            appendAgentMessage(`Network error: ${e.message}`, []);
        }
    }

    if (sendChatBtn && chatInput) {
        sendChatBtn.addEventListener('click', sendChatMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    function appendUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'mb-3 text-end';
        div.innerHTML = `<div class="message-user d-inline-block text-start">${escapeHtml(text)}</div>`;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendLoadingMessage(id) {
        const div = document.createElement('div');
        div.id = id;
        div.className = 'mb-3 text-start';
        div.innerHTML = `
            <div class="message-agent d-inline-block">
                <span class="spinner-border spinner-border-sm me-2" role="status"></span> Thinking & executing tools...
            </div>`;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function removeLoadingMessage(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    function appendAgentMessage(responseHtml, stepLogs) {
        const div = document.createElement('div');
        div.className = 'mb-3 text-start';

        let logsHtml = '';
        if (stepLogs && stepLogs.length > 0) {
            const logsList = stepLogs.map(l => `
                <div class="log-bubble">
                    <i class="bi ${l.icon || 'bi-info-circle'} me-1 text-info"></i>
                    <strong>[${l.component}]</strong> <span class="badge bg-secondary ms-1">${l.elapsed}</span>
                    <div class="mt-1 text-mutedSmall">${escapeHtml(l.log)}</div>
                </div>
            `).join('');

            logsHtml = `
                <div class="logs-detail-box">
                    <button class="btn btn-outline-info btn-sm show-logs-btn" onclick="toggleLogs(this)">
                        <i class="bi bi-chevron-down me-1"></i> Show Logs
                    </button>
                    <div class="logs-content mt-3" style="display: none;">
                        ${logsList}
                    </div>
                </div>`;
        }

        div.innerHTML = `
            <div class="message-agent d-inline-block w-100">
                <div class="mb-2">${responseHtml.replace(/\n/g, '<br>')}</div>
                ${logsHtml}
            </div>`;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    window.toggleLogs = function(btn) {
        const content = btn.nextElementSibling;
        if (content.style.display === 'none') {
            content.style.display = 'block';
            btn.innerHTML = '<i class="bi bi-chevron-up me-1"></i> Hide Logs';
        } else {
            content.style.display = 'none';
            btn.innerHTML = '<i class="bi bi-chevron-down me-1"></i> Show Logs';
        }
    };

    function renderRetrievedEvidence(docEvidence, skillsMatched) {
        const evidenceContainer = document.getElementById('evidence-container');
        if (!evidenceContainer) return;

        let html = '';
        if (skillsMatched && skillsMatched.length > 0) {
            html += `<h6 class="text-info mb-2"><i class="bi bi-lightning-charge me-1"></i> Matched Skills</h6>`;
            skillsMatched.forEach(s => {
                html += `
                    <div class="card bg-dark border-secondary mb-2 p-2 fs-7">
                        <div class="d-flex justify-content-between">
                            <strong>${escapeHtml(s.name)}</strong>
                            <span class="badge bg-primary">Score: ${s.score}</span>
                        </div>
                        <div class="text-muted small">${escapeHtml(s.description)}</div>
                    </div>`;
            });
        }

        html += `<h6 class="text-info mt-3 mb-2"><i class="bi bi-file-earmark-text me-1"></i> Document Chunks</h6>`;
        if (docEvidence && docEvidence.grouped && Object.keys(docEvidence.grouped).length > 0) {
            for (const [docName, chunks] of Object.entries(docEvidence.grouped)) {
                html += `
                    <div class="mb-3">
                        <div class="fw-bold text-light small"><i class="bi bi-file-code me-1"></i> ${escapeHtml(docName)}</div>`;
                chunks.forEach(c => {
                    html += `
                        <div class="card bg-dark border-secondary mb-1 p-2 small">
                            <div class="d-flex justify-content-between text-muted fs-8 mb-1">
                                <span>Chunk #${c.chunk_index}</span>
                                <span class="badge bg-success">Match: ${c.score}</span>
                            </div>
                            <div class="text-light fs-7">${escapeHtml(c.chunk_text)}</div>
                        </div>`;
                });
                html += `</div>`;
            }
        } else {
            html += `<div class="text-muted small">No document chunks exceeded retrieval threshold.</div>`;
        }
        evidenceContainer.innerHTML = html;
    }

    // --- PAGE 2: VECTOR DB INGESTION ---
    async function loadIngestionData() {
        try {
            const res = await fetch('/api/ingestion/stats');
            const data = await res.json();
            document.getElementById('stat-chunks-count').innerText = data.chunk_count || 0;
            document.getElementById('stat-docs-count').innerText = data.document_count || 0;
            document.getElementById('stat-db-size').innerText = data.db_size_mb || '0.0';

            const docsRes = await fetch('/api/ingestion/documents');
            const docsData = await docsRes.json();
            renderIngestedDocsList(docsData.documents || []);

            const modelsRes = await fetch('/api/ingestion/embedding-models');
            const modelsData = await modelsRes.json();
            renderEmbeddingModelsTable(modelsData.models || []);
        } catch (e) {
            console.error('Failed to load ingestion stats:', e);
        }
    }

    const updateSkillsBtn = document.getElementById('update-skills-btn');
    if (updateSkillsBtn) {
        updateSkillsBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/ingestion/update-skills', { method: 'POST' });
                const data = await res.json();
                alert(`Skills Database Updated! ${data.new_skills_added} new skill(s) ingested.`);
                loadIngestionData();
            } catch (e) {
                alert('Error updating skills database.');
            }
        });
    }

    // Embedder model switcher warning popup modal
    const embedderSelect = document.getElementById('embedder-model-select');
    const embedderConfirmInput = document.getElementById('embedder-confirm-input');
    const deleteDataBtn = document.getElementById('confirm-delete-data-btn');
    let pendingEmbedderModel = null;

    if (embedderSelect) {
        embedderSelect.addEventListener('change', () => {
            pendingEmbedderModel = embedderSelect.value;
            const modal = new bootstrap.Modal(document.getElementById('embedderChangeModal'));
            modal.show();
        });
    }

    if (embedderConfirmInput && deleteDataBtn) {
        embedderConfirmInput.addEventListener('input', () => {
            deleteDataBtn.disabled = (embedderConfirmInput.value.trim() !== 'CHANGE MODEL AND DELETE DATA');
        });
        deleteDataBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/ingestion/change-embedder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model: pendingEmbedderModel })
                });
                alert(`Embedder changed to ${pendingEmbedderModel}. Data cleared and skills re-indexed.`);
                bootstrap.Modal.getInstance(document.getElementById('embedderChangeModal')).hide();
                loadIngestionData();
            } catch (e) {
                alert('Failed to change embedder model.');
            }
        });
    }

    // Sample URL preset buttons
    document.querySelectorAll('.sample-url-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const url = btn.getAttribute('data-url');
            document.getElementById('db-source-input').value = url;
        });
    });

    const populateDbBtn = document.getElementById('populate-db-btn');
    if (populateDbBtn) {
        populateDbBtn.addEventListener('click', async () => {
            const source = document.getElementById('db-source-input').value.trim();
            if (!source) {
                alert('Please enter a URL or local folder path.');
                return;
            }
            const chunkSize = parseInt(document.getElementById('chunk-size-input').value || 500);
            const chunkOverlap = parseInt(document.getElementById('chunk-overlap-input').value || 50);

            populateDbBtn.disabled = true;
            populateDbBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Ingesting...`;

            try {
                const res = await fetch('/api/ingestion/populate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ source, chunk_size: chunkSize, chunk_overlap: chunkOverlap })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    alert(`Ingestion Successful! Added ${data.chunks_added} chunks across ${data.documents_processed} document(s).`);
                } else {
                    alert(`Ingestion Error: ${data.message}`);
                }
                loadIngestionData();
            } catch (e) {
                alert('Network error during ingestion.');
            } finally {
                populateDbBtn.disabled = false;
                populateDbBtn.innerHTML = `<i class="bi bi-database-add me-1"></i> Populate Vector Database`;
            }
        });
    }

    function renderIngestedDocsList(docs) {
        const container = document.getElementById('ingested-docs-list');
        if (!container) return;
        if (!docs || docs.length === 0) {
            container.innerHTML = `<div class="text-muted small">No documents currently ingested in database.</div>`;
            return;
        }
        let html = '';
        docs.forEach(d => {
            html += `
                <div class="d-flex justify-content-between align-items-center bg-dark p-2 rounded mb-2 border border-secondary">
                    <div>
                        <div class="fw-bold text-light small"><i class="bi bi-file-earmark-code me-1"></i> ${escapeHtml(d.document)}</div>
                        <div class="text-muted fs-8">${d.chunk_count} chunks | ${d.total_characters} chars</div>
                    </div>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteDocument('${escapeHtml(d.document)}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>`;
        });
        container.innerHTML = html;
    }

    window.deleteDocument = async function(docName) {
        if (!confirm(`Are you sure you want to delete document '${docName}' from the database?`)) return;
        try {
            await fetch('/api/ingestion/document', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document_name: docName })
            });
            loadIngestionData();
        } catch (e) {
            alert('Failed to delete document.');
        }
    };

    const resetDbBtn = document.getElementById('reset-db-btn');
    if (resetDbBtn) {
        resetDbBtn.addEventListener('click', async () => {
            if (!confirm('WARNING: Resetting database will delete all document and skill vector data. Proceed?')) return;
            await fetch('/api/ingestion/reset', { method: 'POST' });
            loadIngestionData();
        });
    }

    function renderEmbeddingModelsTable(models) {
        const container = document.getElementById('embedding-models-table-body');
        if (!container) return;
        let html = '';
        models.forEach(m => {
            const badgeClass = m.status === 'Active' ? 'bg-success' : 'bg-secondary';
            html += `
                <tr>
                    <td class="fw-bold">${escapeHtml(m.name)}</td>
                    <td>${m.dimensions}</td>
                    <td>${m.context_window}</td>
                    <td>${m.size}</td>
                    <td class="text-muted small">${escapeHtml(m.description)}</td>
                    <td><span class="badge ${badgeClass}">${m.status}</span></td>
                </tr>`;
        });
        container.innerHTML = html;
    }

    // --- PAGE 3: TELEMETRY ---
    async function loadTelemetryData() {
        try {
            const modelFilter = document.getElementById('telemetry-model-filter')?.value || 'All Models';
            const interval = document.getElementById('telemetry-interval-select')?.value || '15 min';
            const timeRange = document.getElementById('telemetry-range-select')?.value || '1 day';

            const res = await fetch(`/api/telemetry/metrics?model=${encodeURIComponent(modelFilter)}&range=${encodeURIComponent(timeRange)}`);
            const data = await res.json();

            document.getElementById('t-prompts').innerText = data.summary.total_prompts;
            document.getElementById('t-responses').innerText = data.summary.total_responses;
            document.getElementById('t-errors').innerText = data.summary.total_errors;
            document.getElementById('t-in-tokens').innerText = data.summary.total_input_tokens;
            document.getElementById('t-out-tokens').innerText = data.summary.total_output_tokens;

            document.getElementById('metric-ttft').innerText = `${data.performance_metrics.ttft_sec} s`;
            document.getElementById('metric-itl').innerText = `${data.performance_metrics.itl_ms} ms`;
            document.getElementById('metric-tps').innerText = `${data.performance_metrics.tps} /s`;
            document.getElementById('metric-tpot').innerText = `${data.performance_metrics.tpot_ms} ms`;

            const chartRes = await fetch(`/api/telemetry/charts?model=${encodeURIComponent(modelFilter)}&interval=${encodeURIComponent(interval)}&range=${encodeURIComponent(timeRange)}`);
            const chartData = await chartRes.json();
            renderTelemetryCharts(chartData);
        } catch (e) {
            console.error('Failed to load telemetry data:', e);
        }
    }

    function renderTelemetryCharts(data) {
        const ctx1 = document.getElementById('throughputChart')?.getContext('2d');
        const ctx2 = document.getElementById('tokenVelocityChart')?.getContext('2d');
        if (!ctx1 || !ctx2) return;

        if (throughputChart) throughputChart.destroy();
        if (tokenChart) tokenChart.destroy();

        throughputChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Prompts', data: data.prompts, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', fill: true, tension: 0.3 },
                    { label: 'Responses', data: data.responses, borderColor: '#22c55e', backgroundColor: 'rgba(34, 197, 94, 0.1)', fill: true, tension: 0.3 },
                    { label: 'Errors', data: data.errors, borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', fill: true, tension: 0.3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }
        });

        tokenChart = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Input Tokens', data: data.input_tokens, borderColor: '#a855f7', backgroundColor: 'rgba(168, 85, 247, 0.1)', fill: true, tension: 0.3 },
                    { label: 'Output Tokens', data: data.output_tokens, borderColor: '#6366f1', backgroundColor: 'rgba(99, 102, 241, 0.1)', fill: true, tension: 0.3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#f8fafc' } } }, scales: { x: { ticks: { color: '#94a3b8' } }, y: { ticks: { color: '#94a3b8' } } } }
        });
    }

    const refreshTelemetryBtn = document.getElementById('refresh-telemetry-btn');
    if (refreshTelemetryBtn) {
        refreshTelemetryBtn.addEventListener('click', loadTelemetryData);
    }

    // --- PAGE 4: AUDIT LOG & EVENT ---
    async function loadAuditData() {
        try {
            const statsRes = await fetch('/api/audit/stats');
            const stats = await statsRes.json();
            document.getElementById('audit-total-prompts').innerText = stats.total_user_prompts;
            document.getElementById('audit-model-calls').innerText = stats.total_model_calls;
            document.getElementById('audit-embeds').innerText = stats.total_ollama_embeds;
            document.getElementById('audit-avg-latency').innerText = `${stats.avg_call_latency_sec} s`;

            const convRes = await fetch('/api/audit/conversations');
            const convData = await convRes.json();
            renderConversationsTable(convData.conversations || []);
        } catch (e) {
            console.error('Failed to load audit data:', e);
        }
    }

    function renderConversationsTable(conversations) {
        const tbody = document.getElementById('conversations-table-body');
        if (!tbody) return;
        if (!conversations || conversations.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No conversations logged yet.</td></tr>`;
            return;
        }

        let html = '';
        conversations.slice(0, 5).forEach((c, idx) => {
            html += `
                <tr onclick="selectConversationRow(this, '${c.conversation_id}')" class="${idx === 0 ? 'table-active' : ''}">
                    <td>${c.timestamp}</td>
                    <td><code>${c.conversation_id}</code></td>
                    <td>${escapeHtml(c.user_query).substring(0, 45)}...</td>
                    <td>${escapeHtml(c.agent_response).substring(0, 45)}...</td>
                    <td><span class="badge bg-info">${c.agent_type}</span></td>
                    <td><span class="badge bg-secondary">${c.event_count}</span></td>
                </tr>`;
        });
        tbody.innerHTML = html;

        if (conversations.length > 0) {
            loadEventsForConversation(conversations[0].conversation_id);
        }
    }

    window.selectConversationRow = function(row, cid) {
        document.querySelectorAll('#conversations-table-body tr').forEach(r => r.classList.remove('table-active'));
        row.classList.add('table-active');
        loadEventsForConversation(cid);
    };

    async function loadEventsForConversation(cid) {
        selectedConversationId = cid;
        document.getElementById('selected-conv-id-label').innerText = cid;
        try {
            const res = await fetch(`/api/audit/events?conversation_id=${encodeURIComponent(cid)}`);
            const data = await res.json();
            renderEventsTable(data.events || []);
        } catch (e) {
            console.error('Failed to load events:', e);
        }
    }

    function renderEventsTable(events) {
        const tbody = document.getElementById('events-table-body');
        if (!tbody) return;
        if (!events || events.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No events recorded for this conversation.</td></tr>`;
            return;
        }

        let html = '';
        events.forEach(e => {
            html += `
                <tr onclick='openPayloadModal(${JSON.stringify(e).replace(/'/g, "&apos;")})'>
                    <td>${e.timestamp}</td>
                    <td><span class="badge bg-primary">${e.event_type}</span></td>
                    <td>${escapeHtml(e.invoker)}</td>
                    <td>${escapeHtml(e.target)}</td>
                    <td>${escapeHtml(e.short_description)}</td>
                </tr>`;
        });
        tbody.innerHTML = html;
    }

    window.openPayloadModal = function(eventObj) {
        document.getElementById('modal-event-title').innerText = `${eventObj.event_type} Details`;
        document.getElementById('modal-json-content').innerText = JSON.stringify(eventObj.payload || {}, null, 2);
        const modal = new bootstrap.Modal(document.getElementById('payloadModal'));
        modal.show();
    };

    const clearLogsBtn = document.getElementById('clear-logs-btn');
    if (clearLogsBtn) {
        clearLogsBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all audit logs?')) return;
            await fetch('/api/audit/clear', { method: 'POST' });
            loadAuditData();
        });
    }

    const refreshAuditBtn = document.getElementById('refresh-audit-btn');
    if (refreshAuditBtn) {
        refreshAuditBtn.addEventListener('click', loadAuditData);
    }

    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
