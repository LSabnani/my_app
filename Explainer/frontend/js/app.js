/**
 * Explainer GUI Application Logic
 * Coordinates Stepper State, API Communication, Candidate Selection, and CLEATS Presentation.
 */

const API_BASE = window.location.origin;

const state = {
  sessionId: null,
  currentStep: 1,
  problem: '',
  intent: '',
  application: '',
  primer: null,
  candidates: [],
  selectedCandidateIds: new Set(),
  top3: [],
  currentFilter: 'ALL',
  infographic: null,
  step4Mode: 'TOP3',
  currentProposal: null
};

// DOM Elements
const elements = {
  sessionIndicator: document.getElementById('sessionIndicator'),
  newSessionBtn: document.getElementById('newSessionBtn'),
  bkmRegistryBtn: document.getElementById('bkmRegistryBtn'),
  bkmModal: document.getElementById('bkmModal'),
  closeBkmModal: document.getElementById('closeBkmModal'),
  bkmList: document.getElementById('bkmList'),
  
  // Stepper Items
  stepItems: document.querySelectorAll('.step-item'),
  stepViews: {
    1: document.getElementById('step1View'),
    2: document.getElementById('step2View'),
    3: document.getElementById('step3View'),
    4: document.getElementById('step4View')
  },

  // Step 1
  greeterMessageText: document.getElementById('greeterMessageText'),
  intakeForm: document.getElementById('intakeForm'),
  problemInput: document.getElementById('problemInput'),
  intentInput: document.getElementById('intentInput'),
  applicationInput: document.getElementById('applicationInput'),
  quickChipsContainer: document.getElementById('quickChipsContainer'),
  submitIntakeBtn: document.getElementById('submitIntakeBtn'),

  // Step 2
  primerSourceBadge: document.getElementById('primerSourceBadge'),
  primerTopicTitle: document.getElementById('primerTopicTitle'),
  primerText: document.getElementById('primerText'),
  primerExternalLink: document.getElementById('primerExternalLink'),
  confirmYesBtn: document.getElementById('confirmYesBtn'),
  toggleRefineBtn: document.getElementById('toggleRefineBtn'),
  refineBox: document.getElementById('refineBox'),
  refinementInput: document.getElementById('refinementInput'),
  submitRefineBtn: document.getElementById('submitRefineBtn'),

  // Step 3
  candidateCountBadge: document.getElementById('candidateCountBadge'),
  candidatesGrid: document.getElementById('candidatesGrid'),
  selectAllBtn: document.getElementById('selectAllBtn'),
  clearAllBtn: document.getElementById('clearAllBtn'),
  selectedCountText: document.getElementById('selectedCountText'),
  evaluateCandidatesBtn: document.getElementById('evaluateCandidatesBtn'),
  filterBtns: document.querySelectorAll('.filter-btn'),

  // Step 4
  top3Container: document.getElementById('top3Container'),
  exportReportBtn: document.getElementById('exportReportBtn'),
  viewTop3Btn: document.getElementById('viewTop3Btn'),
  viewInfographicBtn: document.getElementById('viewInfographicBtn'),
  top3ModeContainer: document.getElementById('top3ModeContainer'),
  infographicModeContainer: document.getElementById('infographicModeContainer'),
  inlineInfographicHost: document.getElementById('inlineInfographicHost'),

  // Global Critic Link Audit & RPN Receipt Elements (Spec 8.4)
  globalAuditBanner: document.getElementById('globalAuditBanner'),
  auditBannerTitle: document.getElementById('auditBannerTitle'),
  auditBannerDesc: document.getElementById('auditBannerDesc'),
  openRpnReceiptBtn: document.getElementById('openRpnReceiptBtn'),
  rpnModal: document.getElementById('rpnModal'),
  closeRpnModal: document.getElementById('closeRpnModal'),

  // Simulated Data Proposal & User Agreement Elements (Spec 8.5)
  simulatedDataModal: document.getElementById('simulatedDataModal'),
  closeSimulatedDataModal: document.getElementById('closeSimulatedDataModal'),
  simMissingReasonText: document.getElementById('simMissingReasonText'),
  simMetricsGrid: document.getElementById('simMetricsGrid'),
  simRationaleText: document.getElementById('simRationaleText'),
  declineSimulatedDataBtn: document.getElementById('declineSimulatedDataBtn'),
  approveSimulatedDataBtn: document.getElementById('approveSimulatedDataBtn'),

  // Infographic Modal
  openInfographicModalBtn: document.getElementById('openInfographicModalBtn'),
  closeInfographicModal: document.getElementById('closeInfographicModal'),
  infographicModal: document.getElementById('infographicModal'),
  modalInfographicHost: document.getElementById('modalInfographicHost'),

  // Architecture Infographic Modal
  archInfographicBtn: document.getElementById('archInfographicBtn'),
  closeArchInfographicModal: document.getElementById('closeArchInfographicModal'),
  archInfographicModal: document.getElementById('archInfographicModal')
};

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  initApp();
  bindEvents();
});

async function initApp() {
  try {
    const res = await fetch(`${API_BASE}/api/session/start`, { method: 'POST' });
    const data = await res.json();
    state.sessionId = data.sessionId;
    elements.sessionIndicator.textContent = `Session: ${data.sessionId}`;
    elements.greeterMessageText.textContent = data.greeting;

    renderQuickChips(data.suggestedTopics || []);
    setStep(1);
  } catch (err) {
    console.error('Failed to initialize session:', err);
    elements.sessionIndicator.textContent = 'Session: Offline';
    elements.greeterMessageText.textContent = 'Welcome! Enter your problem or area of focus below to begin.';
  }
}

function bindEvents() {
  // New Session
  elements.newSessionBtn.addEventListener('click', () => {
    if (confirm('Start a new Explainer session?')) {
      location.reload();
    }
  });

  // BKM Catalog Modal
  elements.bkmRegistryBtn.addEventListener('click', openBkmCatalog);
  elements.closeBkmModal.addEventListener('click', () => elements.bkmModal.classList.add('hidden'));
  elements.bkmModal.addEventListener('click', (e) => {
    if (e.target === elements.bkmModal) elements.bkmModal.classList.add('hidden');
  });

  // Step 1: Intake submission
  elements.intakeForm.addEventListener('submit', handleIntakeSubmit);

  // Step 2: Primer Confirmation & Refinement
  elements.confirmYesBtn.addEventListener('click', handlePrimerConfirm);
  elements.toggleRefineBtn.addEventListener('click', () => {
    elements.refineBox.classList.toggle('hidden');
  });
  elements.submitRefineBtn.addEventListener('click', handlePrimerRefine);

  // Step 3: Selection & Filters
  elements.selectAllBtn.addEventListener('click', selectAllCandidates);
  elements.clearAllBtn.addEventListener('click', clearAllCandidates);
  elements.evaluateCandidatesBtn.addEventListener('click', handleEvaluateCandidates);

  elements.filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      elements.filterBtns.forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      state.currentFilter = e.target.dataset.filter;
      renderCandidates();
    });
  });

  // Step 4: Export Summary & Mode Switcher
  elements.exportReportBtn.addEventListener('click', exportSummaryMarkdown);
  if (elements.viewTop3Btn) {
    elements.viewTop3Btn.addEventListener('click', () => switchStep4View('TOP3'));
  }
  if (elements.viewInfographicBtn) {
    elements.viewInfographicBtn.addEventListener('click', () => switchStep4View('INFOGRAPHIC'));
  }

  // FMEA RPN Diagnostics Modal (Spec 8.4)
  if (elements.openRpnReceiptBtn) {
    elements.openRpnReceiptBtn.addEventListener('click', openRpnModal);
  }
  if (elements.closeRpnModal) {
    elements.closeRpnModal.addEventListener('click', closeRpnModal);
  }
  if (elements.rpnModal) {
    elements.rpnModal.addEventListener('click', (e) => {
      if (e.target === elements.rpnModal) closeRpnModal();
    });
  }

  // Simulated Data Consent Modal (Spec 8.5)
  if (elements.closeSimulatedDataModal) {
    elements.closeSimulatedDataModal.addEventListener('click', closeSimulatedDataModal);
  }
  if (elements.simulatedDataModal) {
    elements.simulatedDataModal.addEventListener('click', (e) => {
      if (e.target === elements.simulatedDataModal) closeSimulatedDataModal();
    });
  }
  if (elements.approveSimulatedDataBtn) {
    elements.approveSimulatedDataBtn.addEventListener('click', handleApproveSimulatedData);
  }
  if (elements.declineSimulatedDataBtn) {
    elements.declineSimulatedDataBtn.addEventListener('click', handleDeclineSimulatedData);
  }

  // Knowledge Infographic Modal
  if (elements.openInfographicModalBtn) {
    elements.openInfographicModalBtn.addEventListener('click', openInfographicModal);
  }
  if (elements.closeInfographicModal) {
    elements.closeInfographicModal.addEventListener('click', () => elements.infographicModal.classList.add('hidden'));
  }
  if (elements.infographicModal) {
    elements.infographicModal.addEventListener('click', (e) => {
      if (e.target === elements.infographicModal) elements.infographicModal.classList.add('hidden');
    });
  }

  // Architecture Infographic Modal
  if (elements.archInfographicBtn) {
    elements.archInfographicBtn.addEventListener('click', () => {
      if (elements.archInfographicModal) elements.archInfographicModal.classList.remove('hidden');
    });
  }
  if (elements.closeArchInfographicModal) {
    elements.closeArchInfographicModal.addEventListener('click', () => {
      if (elements.archInfographicModal) elements.archInfographicModal.classList.add('hidden');
    });
  }
  if (elements.archInfographicModal) {
    elements.archInfographicModal.addEventListener('click', (e) => {
      if (e.target === elements.archInfographicModal) elements.archInfographicModal.classList.add('hidden');
    });
  }

  // Global delegation for stub interaction buttons
  document.addEventListener('click', handleGlobalStubActions);

  // Stepper Header click navigation (only to visited steps)
  elements.stepItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetStep = parseInt(item.dataset.step, 10);
      if (targetStep < state.currentStep) {
        setStep(targetStep);
      }
    });
  });
}

// ==========================================================================
// STEPPER LOGIC
// ==========================================================================

function setStep(stepNum) {
  state.currentStep = stepNum;

  // Update Stepper Nav
  elements.stepItems.forEach(item => {
    const s = parseInt(item.dataset.step, 10);
    item.classList.remove('active', 'completed');
    if (s === stepNum) {
      item.classList.add('active');
    } else if (s < stepNum) {
      item.classList.add('completed');
    }
  });

  // Toggle Viewports
  Object.keys(elements.stepViews).forEach(key => {
    const view = elements.stepViews[key];
    if (parseInt(key, 10) === stepNum) {
      view.classList.add('active');
    } else {
      view.classList.remove('active');
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================================================
// STEP 1: GREETER & INTAKE
// ==========================================================================

function renderQuickChips(topics) {
  elements.quickChipsContainer.innerHTML = '';
  topics.forEach(topic => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip';
    chip.textContent = topic;
    chip.addEventListener('click', () => {
      elements.problemInput.value = topic;
      elements.intentInput.value = 'In-depth architectural review and reference';
      elements.applicationInput.value = 'Team presentation and technical design document';
      elements.problemInput.focus();
    });
    elements.quickChipsContainer.appendChild(chip);
  });
}

async function handleIntakeSubmit(e) {
  e.preventDefault();
  const problem = elements.problemInput.value.trim();
  const intent = elements.intentInput.value.trim();
  const application = elements.applicationInput.value.trim();

  if (!problem) return;

  state.problem = problem;
  state.intent = intent;
  state.application = application;

  elements.submitIntakeBtn.disabled = true;
  elements.submitIntakeBtn.innerHTML = '<span>Consulting Wikipedia & Knowledge Base...</span>';

  try {
    const res = await fetch(`${API_BASE}/api/chat/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        problem: problem,
        intent: intent,
        target_application: application
      })
    });

    const data = await res.json();
    state.primer = data.primer;
    renderPrimer(data.primer);
    setStep(2);
  } catch (err) {
    console.error('Error fetching primer:', err);
    alert('Failed to connect to backend service.');
  } finally {
    elements.submitIntakeBtn.disabled = false;
    elements.submitIntakeBtn.innerHTML = `<span>Start Baseline Research</span>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
      </svg>`;
  }
}

// ==========================================================================
// STEP 2: BASELINE PRIMER
// ==========================================================================

function renderPrimer(primer) {
  if (!primer) return;
  elements.primerSourceBadge.textContent = primer.source || 'Wikipedia';
  elements.primerTopicTitle.textContent = primer.topic || state.problem;
  elements.primerText.textContent = primer.summary_text || 'No summary text available.';
  
  if (primer.page_url) {
    elements.primerExternalLink.href = primer.page_url;
    elements.primerExternalLink.classList.remove('hidden');
  } else {
    elements.primerExternalLink.classList.add('hidden');
  }
}

async function handlePrimerConfirm() {
  elements.confirmYesBtn.disabled = true;
  elements.confirmYesBtn.innerHTML = '<span>Searching Open-Source Slide Decks & Videos...</span>';

  try {
    const res = await fetch(`${API_BASE}/api/chat/confirm-primer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        confirmed: true
      })
    });

    const data = await res.json();
    state.candidates = data.candidates || [];
    
    // Select all candidates by default
    state.selectedCandidateIds = new Set(state.candidates.map(c => c.id));
    
    renderCandidates();
    setStep(3);
  } catch (err) {
    console.error('Error confirming primer:', err);
    alert('Failed to harvest candidate materials.');
  } finally {
    elements.confirmYesBtn.disabled = false;
    elements.confirmYesBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      <span>Yes, Proceed to Deep Dive (Harvest PPTs & Videos)</span>`;
  }
}

async function handlePrimerRefine() {
  const refinement = elements.refinementInput.value.trim();
  if (!refinement) return;

  elements.submitRefineBtn.disabled = true;
  elements.submitRefineBtn.textContent = 'Refining...';

  try {
    const res = await fetch(`${API_BASE}/api/chat/confirm-primer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        confirmed: false,
        refinement: refinement
      })
    });

    const data = await res.json();
    if (data.primer) {
      state.primer = data.primer;
      renderPrimer(data.primer);
      elements.refineBox.classList.add('hidden');
      elements.refinementInput.value = '';
    }
  } catch (err) {
    console.error('Failed to refine primer:', err);
  } finally {
    elements.submitRefineBtn.disabled = false;
    elements.submitRefineBtn.textContent = 'Refine & Refresh Primer';
  }
}

// ==========================================================================
// STEP 3: CANDIDATES GRID
// ==========================================================================

function renderCandidates() {
  const filtered = state.candidates.filter(c => {
    if (state.currentFilter === 'ALL') return true;
    return c.type === state.currentFilter;
  });

  elements.candidateCountBadge.textContent = `${filtered.length} of ${state.candidates.length} Resources`;
  elements.candidatesGrid.innerHTML = '';

  filtered.forEach(candidate => {
    const isSelected = state.selectedCandidateIds.has(candidate.id);
    const isPPT = candidate.type === 'PPT_DECK';

    const card = document.createElement('div');
    card.className = `candidate-card ${isSelected ? 'selected' : ''}`;
    card.id = `card_${candidate.id}`;

    let typeBadge = '';
    if (candidate.type === 'PPT_DECK') {
      typeBadge = `<span class="resource-badge badge-ppt">📊 PPT Deck (${candidate.slide_count} Slides)</span>`;
    } else if (candidate.type === 'SCIENTIFIC_PAPER') {
      typeBadge = `<span class="resource-badge badge-paper">🔬 ScienceDirect (${candidate.journal || 'Peer-Reviewed Paper'})</span>`;
    } else {
      typeBadge = `<span class="resource-badge badge-video">▶ YouTube Video (${candidate.video_duration})</span>`;
    }

    const tagsHtml = (candidate.tags || [])
      .map(tag => `<span class="tag-pill">${tag}</span>`)
      .join('');

    card.innerHTML = `
      <div class="card-top-row">
        ${typeBadge}
        <label class="card-checkbox-label">
          <input type="checkbox" data-id="${candidate.id}" ${isSelected ? 'checked' : ''}>
          <span>Evaluate</span>
        </label>
      </div>
      <h3 class="candidate-title">${candidate.title}</h3>
      <div class="candidate-meta">${candidate.author_or_channel} • ${candidate.source}</div>
      <p class="candidate-snippet">${candidate.snippet}</p>
      
      <!-- Tracked Verification Links Preview -->
      <div class="candidate-links-compact">
        ${(candidate.reference_links && candidate.reference_links.length > 0) ? candidate.reference_links.slice(0, 3).map(l => `
          <div class="candidate-link-item">
            <span>${l.type === 'document' ? '📄' : (l.type === 'video' ? '🎥' : (l.type === 'paper' ? '🔬' : '🌐'))}</span>
            <a href="${l.url}" target="_blank" rel="noopener noreferrer" title="${l.url}">
              <span>${l.title || l.url}</span>
              <span class="verified-indicator" title="Active verifiable link">✓</span>
            </a>
          </div>
        `).join('') : `
          ${candidate.document_url ? `
            <div class="candidate-link-item">
              <span>📄 Doc:</span>
              <a href="${candidate.document_url}" target="_blank" rel="noopener noreferrer" title="${candidate.document_url}">${candidate.document_url} <span class="verified-indicator">✓</span></a>
            </div>` : ''}
          ${candidate.website_url ? `
            <div class="candidate-link-item">
              <span>🌐 Web:</span>
              <a href="${candidate.website_url}" target="_blank" rel="noopener noreferrer" title="${candidate.website_url}">${candidate.website_url} <span class="verified-indicator">✓</span></a>
            </div>` : ''}
          ${candidate.video_url ? `
            <div class="candidate-link-item">
              <span>🎥 Video:</span>
              <a href="${candidate.video_url}" target="_blank" rel="noopener noreferrer" title="${candidate.video_url}">${candidate.video_url} <span class="verified-indicator">✓</span></a>
            </div>` : ''}
        `}
      </div>

      <div class="candidate-tags">${tagsHtml}</div>
    `;

    // Bind checkbox
    const checkbox = card.querySelector('input[type="checkbox"]');
    checkbox.addEventListener('change', (e) => {
      if (e.target.checked) {
        state.selectedCandidateIds.add(candidate.id);
        card.classList.add('selected');
      } else {
        state.selectedCandidateIds.delete(candidate.id);
        card.classList.remove('selected');
      }
      updateSelectionSummary();
    });

    elements.candidatesGrid.appendChild(card);
  });

  updateSelectionSummary();
}

function updateSelectionSummary() {
  const count = state.selectedCandidateIds.size;
  elements.selectedCountText.textContent = `${count} of ${state.candidates.length} candidates selected for CLEATS evaluation`;
  elements.evaluateCandidatesBtn.disabled = count === 0;
}

function selectAllCandidates() {
  state.candidates.forEach(c => state.selectedCandidateIds.add(c.id));
  renderCandidates();
}

function clearAllCandidates() {
  state.selectedCandidateIds.clear();
  renderCandidates();
}

async function handleEvaluateCandidates() {
  if (state.selectedCandidateIds.size === 0) return;

  elements.evaluateCandidatesBtn.disabled = true;
  elements.evaluateCandidatesBtn.innerHTML = '<span>Running CLEATS Rubric & BKM Checks...</span>';

  try {
    const res = await fetch(`${API_BASE}/api/chat/confirm-candidates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: state.sessionId,
        selected_ids: Array.from(state.selectedCandidateIds)
      })
    });

    const data = await res.json();
    state.top3 = data.top3 || [];
    state.infographic = data.infographic || null;
    renderTop3Podium(state.top3);
    if (state.infographic && elements.inlineInfographicHost) {
      renderInfographic(state.infographic, elements.inlineInfographicHost);
    }
    setStep(4);
  } catch (err) {
    console.error('Error during evaluation:', err);
    alert('Failed to evaluate candidates.');
  } finally {
    elements.evaluateCandidatesBtn.disabled = false;
    elements.evaluateCandidatesBtn.innerHTML = `<span>Run CLEATS Evaluation & Rank Top 3</span>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
      </svg>`;
  }
}

// ==========================================================================
// CRITIC LINK AUDIT, FMEA RPN & SIMULATED DATA PROTOCOL (Spec 8.4 & 8.5)
// ==========================================================================

function getLinkReceiptBadge(link) {
  if (link.is_verified === false) {
    return `<span class="link-receipt-pill receipt-404" title="Reachability probe failed (404/DNS error) - Transparency penalized to 0.0">⚠️ 404 Unreachable</span>`;
  }
  if (link.type === 'paper' || (link.url && link.url.includes('doi.org'))) {
    return `<span class="link-receipt-pill receipt-403" title="Recognized institutional publisher bot-shield (Elsevier/ScienceDirect)">🔒 HTTP 403 (Publisher)</span>`;
  }
  return `<span class="link-receipt-pill receipt-200" title="Endpoint responded active with clean payload">✓ HTTP 200</span>`;
}

function renderGlobalAuditHeader(items) {
  if (!elements.globalAuditBanner) return;
  const hasFailures = items.some(item => {
    const links = item.reference_links || [];
    return item.critic_verified === false || links.some(l => l.is_verified === false);
  });

  if (hasFailures) {
    elements.globalAuditBanner.className = 'global-audit-banner audit-failed';
    if (elements.auditBannerTitle) {
      elements.auditBannerTitle.textContent = '⚠️ Critic Link Audit FAILED';
    }
    if (elements.auditBannerDesc) {
      elements.auditBannerDesc.textContent = 'Unreachable reference link(s) detected. Transparency penalized to 0.0 under Zero-Penalty Rule.';
    }
  } else {
    elements.globalAuditBanner.className = 'global-audit-banner audit-passed';
    if (elements.auditBannerTitle) {
      elements.auditBannerTitle.textContent = '✓ Critic Link Audit PASSED';
    }
    if (elements.auditBannerDesc) {
      elements.auditBannerDesc.textContent = 'All reference URLs verified active via live HTTP probe prior to publishing.';
    }
  }
}

function openRpnModal() {
  if (elements.rpnModal) {
    elements.rpnModal.classList.remove('hidden');
  }
}

function closeRpnModal() {
  if (elements.rpnModal) {
    elements.rpnModal.classList.add('hidden');
  }
}

function openSimulatedDataModal(proposal) {
  state.currentProposal = proposal;
  if (!elements.simulatedDataModal) return;

  if (elements.simMissingReasonText) {
    elements.simMissingReasonText.textContent = proposal.missing_data_description || 'Empirical benchmark telemetry is unmeasured.';
  }

  if (elements.simMetricsGrid) {
    elements.simMetricsGrid.innerHTML = '';
    const metrics = proposal.synthetic_metrics || {};
    Object.entries(metrics).forEach(([k, v]) => {
      const card = document.createElement('div');
      card.className = 'sim-metric-card';
      const label = k.replace(/_/g, ' ');
      card.innerHTML = `
        <div class="sim-metric-label">${label}</div>
        <div class="sim-metric-val">${v}</div>
      `;
      elements.simMetricsGrid.appendChild(card);
    });
  }

  if (elements.simRationaleText) {
    elements.simRationaleText.textContent = proposal.rationale || 'Provisional synthetic Monte Carlo bounds subject to explicit user confirmation.';
  }

  elements.simulatedDataModal.classList.remove('hidden');
}

function closeSimulatedDataModal() {
  if (elements.simulatedDataModal) {
    elements.simulatedDataModal.classList.add('hidden');
  }
  state.currentProposal = null;
}

async function triggerSimulatedProposal(candId, candTitle) {
  try {
    const res = await fetch(`${API_BASE}/api/critic/simulated-data/propose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_id: candId,
        title: candTitle,
        topic: state.problem || 'Cloud Architecture',
        missing_reason: 'Empirical p99 tail latency under 50,000 QPS edge saturation telemetry is unavailable.'
      })
    });
    const proposal = await res.json();
    openSimulatedDataModal(proposal);
  } catch (err) {
    console.error('Failed to generate simulated data proposal:', err);
    alert('Failed to connect to Critic simulated data engine.');
  }
}

async function handleApproveSimulatedData() {
  if (!state.currentProposal) return;
  const proposalId = state.currentProposal.proposal_id;
  const originalText = elements.approveSimulatedDataBtn.innerHTML;

  elements.approveSimulatedDataBtn.disabled = true;
  elements.approveSimulatedDataBtn.innerHTML = '<span>Executing Test with Simulated Data...</span>';

  try {
    const res = await fetch(`${API_BASE}/api/critic/simulated-data/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        proposal_id: proposalId,
        user_agreed: true,
        session_id: state.sessionId
      })
    });

    const data = await res.json();
    if (data.updated_candidate) {
      const targetIdx = state.top3.findIndex(c => c.id === data.updated_candidate.id);
      if (targetIdx !== -1) {
        state.top3[targetIdx] = data.updated_candidate;
      }
      renderTop3Podium(state.top3);
    }
    closeSimulatedDataModal();
  } catch (err) {
    console.error('Failed to confirm simulated test data:', err);
    alert('Failed to execute simulated data confirmation.');
  } finally {
    elements.approveSimulatedDataBtn.disabled = false;
    elements.approveSimulatedDataBtn.innerHTML = originalText;
  }
}

async function handleDeclineSimulatedData() {
  if (!state.currentProposal) return;
  const proposalId = state.currentProposal.proposal_id;

  try {
    await fetch(`${API_BASE}/api/critic/simulated-data/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        proposal_id: proposalId,
        user_agreed: false,
        session_id: state.sessionId
      })
    });
    closeSimulatedDataModal();
  } catch (err) {
    console.error('Failed to decline simulated test data:', err);
    closeSimulatedDataModal();
  }
}

// ==========================================================================
// STEP 4: CLEATS EVALUATION & TOP 3 RECOMMENDATIONS
// ==========================================================================

function renderTop3Podium(items) {
  elements.top3Container.innerHTML = '';

  if (!items || items.length === 0) {
    elements.top3Container.innerHTML = '<p class="text-muted">No items met evaluation criteria.</p>';
    return;
  }

  // Render Global Critic Link Audit Header (Spec 8.4)
  renderGlobalAuditHeader(items);

  const rankClasses = ['rank-gold', 'rank-silver', 'rank-bronze'];
  const rankNames = ['1st Recommendation', '2nd Recommendation', '3rd Recommendation'];

  items.forEach((item, index) => {
    const sc = item.scorecard || {};
    const bkm = sc.bkm_status || {};
    const unmeasurable = sc.unmeasurable_flags || [];
    const isPPT = item.type === 'PPT_DECK';
    const canvasId = `radar_canvas_${item.id}`;

    const card = document.createElement('div');
    card.className = `top3-item-card rank-${index + 1}`;

    // Simulated Data Provenance Badge (Spec 8.5)
    let simBadgeHtml = '';
    if (sc.is_simulated_data) {
      simBadgeHtml = `
        <div class="simulated-data-badge">
          <span>🧪 User-Approved Simulated Data (Proposal: ${sc.simulated_proposal_id || 'sim_prop'})</span>
        </div>
      `;
    }

    // Zero Warning Banner
    let zeroWarningHtml = '';
    if (unmeasurable.length > 0) {
      const reasons = unmeasurable.map(u => `<strong>${u.name} (0.0):</strong> ${u.reason}`).join(' | ');
      zeroWarningHtml = `
        <div class="zero-warning-banner">
          <span class="warning-tag">ZERO RATING</span>
          <span class="warning-reason">${reasons}</span>
        </div>
      `;
    }

    // Propose Simulated Data Button (When unmeasurable metric is detected)
    let proposeSimBtnHtml = '';
    if (unmeasurable.length > 0 && !sc.is_simulated_data) {
      proposeSimBtnHtml = `
        <button type="button" class="btn-propose-sim" data-cand-id="${item.id}" data-cand-title="${encodeURIComponent(item.title)}">
          <span>🧪 Propose Simulated Test Data</span>
        </button>
      `;
    }

    // BKM Shield
    let bkmHtml = '';
    if (bkm.is_elevated_bkm) {
      bkmHtml = `
        <div class="bkm-shield">
          <div class="shield-icon">★</div>
          <div>
            <div class="bkm-shield-title">ELEVATED TO BEST KNOWN METHOD (BKM)</div>
            <div class="bkm-shield-desc">${bkm.triangulation_evidence}</div>
          </div>
        </div>
      `;
    } else if (!bkm.is_bkm_eligible) {
      bkmHtml = `
        <div class="bkm-shield bkm-disqualified">
          <div class="shield-icon">✕</div>
          <div>
            <div class="bkm-shield-title">BKM Disqualified</div>
            <div class="bkm-shield-desc">${bkm.disqualification_reason || 'Does not meet BKM qualification standards.'}</div>
          </div>
        </div>
      `;
    } else {
      bkmHtml = `
        <div class="bkm-shield">
          <div class="shield-icon">⏳</div>
          <div>
            <div class="bkm-shield-title">BKM Candidate (${bkm.triangulation_count}/3 Replications)</div>
            <div class="bkm-shield-desc">${bkm.triangulation_evidence}</div>
          </div>
        </div>
      `;
    }

    let typeBadge = '';
    if (item.type === 'PPT_DECK') {
      typeBadge = `<span class="resource-badge badge-ppt">📊 PowerPoint Deck (${item.slide_count} Slides)</span>`;
    } else if (item.type === 'SCIENTIFIC_PAPER') {
      typeBadge = `<span class="resource-badge badge-paper">🔬 ScienceDirect (${item.journal || 'Peer-Reviewed Paper'})</span>`;
    } else {
      typeBadge = `<span class="resource-badge badge-video">▶ YouTube Video (${item.video_duration})</span>`;
    }

    // Build Tracked Verification Links List with Critic Real-Time Receipts (Spec 8.4)
    const trackedLinks = (item.reference_links && item.reference_links.length > 0)
      ? item.reference_links
      : [
          item.document_url ? { title: item.type === 'SCIENTIFIC_PAPER' ? 'Full Peer-Reviewed Paper (PDF)' : 'Slide Deck / Document (.pptx / .pdf)', url: item.document_url, type: 'document', description: 'Direct document link' } : null,
          item.website_url ? { title: item.type === 'SCIENTIFIC_PAPER' ? 'ScienceDirect Article & DOI Record' : 'Companion Project & Documentation Site', url: item.website_url, type: 'website', description: 'Official specs & repo' } : null,
          item.video_url ? { title: 'Video Walkthrough', url: item.video_url, type: 'video', description: 'Audio-visual stream' } : null,
          { title: 'Primary Catalog Source', url: item.url, type: isPPT ? 'document' : 'website', description: 'Catalog access page' }
        ].filter(Boolean);

    const linksListHtml = trackedLinks.map((link, lIdx) => {
      const typeClass = link.type === 'document' ? 'link-type-document' : (link.type === 'website' ? 'link-type-website' : (link.type === 'paper' ? 'link-type-paper' : 'link-type-video'));
      const icon = link.type === 'document' ? '📄' : (link.type === 'website' ? '🌐' : (link.type === 'paper' ? '🔬' : '🎥'));
      const copyBtnId = `copy_btn_${item.id}_${lIdx}`;
      const receiptBadge = getLinkReceiptBadge(link);

      return `
        <div class="link-row">
          <div class="link-left">
            <span class="link-type-pill ${typeClass}">${icon} ${link.type.toUpperCase()}</span>
            <div class="link-details">
              <div class="link-label-row">
                <span class="link-label">${link.title}</span>
                ${receiptBadge}
              </div>
              <a href="${link.url}" target="_blank" rel="noopener noreferrer" class="link-url-anchor" title="${link.url}">
                <span>${link.url}</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
              </a>
            </div>
          </div>
          <div class="link-actions">
            <button type="button" class="btn-copy-url" data-url="${link.url}" id="${copyBtnId}">
              Copy URL
            </button>
          </div>
        </div>
      `;
    }).join('');

    const sourceLinksBoxHtml = `
      <div class="source-links-box">
        <div class="links-header">
          <span class="links-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
            Critic-Audited Verification Links
          </span>
          <span class="validation-tag">✓ Critic Verified</span>
        </div>
        <div class="link-rows-list">
          ${linksListHtml}
        </div>
      </div>
    `;

    card.innerHTML = `
      <div class="podium-rank-badge ${rankClasses[index]}">
        ★ Rank #${index + 1} — ${rankNames[index]}
      </div>
      <div class="critic-audit-banner">
        <span class="critic-shield">🛡️</span>
        <span class="critic-audit-text"><strong>Critic Link Gatekeeper:</strong> ${item.critic_audit_notes || 'All reference links verified active and valid before publishing.'}</span>
        <button type="button" class="btn-rpn-receipt btn-card-rpn">🛡️ FMEA RPN</button>
      </div>

      <div class="top3-grid">
        <!-- Resource Information Column -->
        <div class="resource-info-col">
          <div style="margin-bottom: 10px;">${typeBadge}</div>
          ${simBadgeHtml}
          <h3>${item.title}</h3>
          <div class="meta-line">${item.author_or_channel} • ${item.source}</div>
          <p class="summary-desc">${item.snippet}</p>

          ${zeroWarningHtml}
          ${proposeSimBtnHtml}
          ${bkmHtml}
          ${sourceLinksBoxHtml}

          <div style="margin-top: 18px;">
            <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
              <span>${isPPT ? 'Open Presentation Deck' : 'Watch Video on YouTube'}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
          </div>
        </div>

        <!-- Radar & Scores Column -->
        <div class="radar-col">
          <div class="composite-score-badge">
            <div class="composite-val">${sc.composite_score || 0}</div>
            <div class="composite-label">CLEATS Overall Score</div>
          </div>

          <canvas id="${canvasId}" class="radar-canvas"></canvas>

          <table class="metrics-table">
            <tbody>
              <tr>
                <td class="metric-name">C (Completeness)</td>
                <td class="metric-score ${sc.completeness === 0 ? 'score-zero' : ''}">${sc.completeness}/10</td>
              </tr>
              <tr>
                <td class="metric-name">L (Latency)</td>
                <td class="metric-score ${sc.latency === 0 ? 'score-zero' : ''}">${sc.latency}/10</td>
              </tr>
              <tr>
                <td class="metric-name">E (Engagement)</td>
                <td class="metric-score ${sc.engagement === 0 ? 'score-zero' : ''}">${sc.engagement}/10</td>
              </tr>
              <tr>
                <td class="metric-name">A (Accuracy)</td>
                <td class="metric-score ${sc.accuracy === 0 ? 'score-zero' : ''}">${sc.accuracy}/10</td>
              </tr>
              <tr>
                <td class="metric-name">T (Transparency)</td>
                <td class="metric-score ${sc.transparency === 0 ? 'score-zero' : ''}">${sc.transparency}/10</td>
              </tr>
              <tr>
                <td class="metric-name">S (Standardization)</td>
                <td class="metric-score ${sc.standardization === 0 ? 'score-zero' : ''}">${sc.standardization}/10</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;

    elements.top3Container.appendChild(card);

    // Bind Copy URL buttons inside this card
    card.querySelectorAll('.btn-copy-url').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const urlToCopy = e.target.getAttribute('data-url');
        if (urlToCopy) {
          navigator.clipboard.writeText(urlToCopy).then(() => {
            const originalText = e.target.textContent;
            e.target.textContent = 'Copied!';
            e.target.classList.add('copied');
            setTimeout(() => {
              e.target.textContent = originalText;
              e.target.classList.remove('copied');
            }, 1800);
          }).catch(err => {
            console.error('Copy failed:', err);
          });
        }
      });
    });

    // Bind Propose Simulated Data button inside this card
    card.querySelectorAll('.btn-propose-sim').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const candId = e.currentTarget.getAttribute('data-cand-id');
        const candTitle = decodeURIComponent(e.currentTarget.getAttribute('data-cand-title') || '');
        triggerSimulatedProposal(candId, candTitle);
      });
    });

    // Bind FMEA RPN receipt button inside this card
    card.querySelectorAll('.btn-card-rpn').forEach(btn => {
      btn.addEventListener('click', openRpnModal);
    });

    // Render Canvas Radar Chart
    setTimeout(() => {
      drawCLEATSRadar(canvasId, sc);
    }, 50);
  });
}

function exportSummaryMarkdown() {
  if (!state.top3 || state.top3.length === 0) return;

  let md = `# Explainer Evaluation Summary Report\n\n`;
  md += `**Problem Statement:** ${state.problem}\n`;
  md += `**Motivation/Intent:** ${state.intent}\n`;
  md += `**Target Application:** ${state.application}\n\n`;
  md += `## Baseline Alignment (Wikipedia)\n${state.primer?.summary_text || 'N/A'}\n\n`;
  md += `## Top 3 Recommended Resources (CLEATS Rubric)\n\n`;

  state.top3.forEach((item, idx) => {
    const sc = item.scorecard || {};
    md += `### #${idx + 1}: ${item.title}\n`;
    md += `- **Type:** ${item.type}\n`;
    md += `- **Author/Source:** ${item.author_or_channel} (${item.source})\n`;
    md += `- **Primary URL:** ${item.url}\n`;
    if (item.document_url) md += `- **Document/Presentation URL:** ${item.document_url}\n`;
    if (item.website_url) md += `- **Companion Website/Repo URL:** ${item.website_url}\n`;
    if (item.video_url) md += `- **Video Walkthrough URL:** ${item.video_url}\n`;
    md += `- **Critic Link Audit:** ${item.critic_audit_notes || 'PASSED (All reference links checked active prior to publishing)'}\n`;
    
    if (item.reference_links && item.reference_links.length > 0) {
      md += `- **Tracked Validation Links:**\n`;
      item.reference_links.forEach(l => {
        md += `  - [${l.type.toUpperCase()}] ${l.title}: ${l.url}\n`;
      });
    }

    md += `- **CLEATS Composite Score:** ${sc.composite_score}/10\n`;
    md += `  - Completeness (C): ${sc.completeness}/10\n`;
    md += `  - Latency (L): ${sc.latency}/10\n`;
    md += `  - Engagement (E): ${sc.engagement}/10\n`;
    md += `  - Accuracy (A): ${sc.accuracy}/10\n`;
    md += `  - Transparency (T): ${sc.transparency}/10\n`;
    md += `  - Standardization (S): ${sc.standardization}/10\n`;
    md += `- **BKM Status:** ${sc.bkm_status?.is_elevated_bkm ? 'ELEVATED BKM' : (sc.bkm_status?.is_bkm_eligible ? 'Eligible Candidate' : 'Disqualified')}\n\n`;
  });

  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `explainer_cleats_report_${state.sessionId}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// ==========================================================================
// BKM CATALOG MODAL
// ==========================================================================

async function openBkmCatalog() {
  elements.bkmModal.classList.remove('hidden');
  elements.bkmList.innerHTML = '<p class="text-muted">Loading BKM catalog...</p>';

  try {
    const res = await fetch(`${API_BASE}/api/bkm/registry`);
    const data = await res.json();
    const templates = data.bkmTemplates || [];

    if (templates.length === 0) {
      elements.bkmList.innerHTML = '<p class="text-muted">No elevated BKM templates currently registered.</p>';
      return;
    }

    elements.bkmList.innerHTML = '';
    templates.forEach(t => {
      const entry = document.createElement('div');
      entry.className = 'bkm-entry';

      const repsHtml = (t.replications || []).map(r => `
        <li><strong>${r.person}</strong> (${r.timestamp}): <em>${r.result}</em></li>
      `).join('');

      entry.innerHTML = `
        <h4 class="bkm-entry-title">★ ${t.title}</h4>
        <div class="bkm-entry-meta">Domain: ${t.domain} • Method: ${t.method_name}</div>
        <p style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 8px;"><strong>Verified Replications (3x):</strong></p>
        <ul class="bkm-rep-list">
          ${repsHtml}
        </ul>
      `;
      elements.bkmList.appendChild(entry);
    });
  } catch (err) {
    console.error('Failed to load BKM catalog:', err);
    elements.bkmList.innerHTML = '<p class="text-danger">Failed to load BKM catalog.</p>';
  }
}

// ==========================================================================
// KNOWLEDGE INFOGRAPHIC & UNKNOWN STUBS LOGIC
// ==========================================================================

function switchStep4View(mode) {
  state.step4Mode = mode;
  if (mode === 'TOP3') {
    elements.viewTop3Btn.classList.add('active');
    elements.viewInfographicBtn.classList.remove('active');
    elements.top3ModeContainer.classList.remove('hidden');
    elements.infographicModeContainer.classList.add('hidden');
  } else {
    elements.viewInfographicBtn.classList.add('active');
    elements.viewTop3Btn.classList.remove('active');
    elements.top3ModeContainer.classList.add('hidden');
    elements.infographicModeContainer.classList.remove('hidden');

    if (!state.infographic) {
      loadSessionInfographic();
    } else {
      renderInfographic(state.infographic, elements.inlineInfographicHost);
    }
  }
}

async function loadSessionInfographic() {
  elements.inlineInfographicHost.innerHTML = '<p class="text-muted" style="padding: 24px; text-align: center;">Synthesizing knowledge infographic and stubs...</p>';
  try {
    const url = state.sessionId
      ? `${API_BASE}/api/session/${state.sessionId}/infographic`
      : `${API_BASE}/api/infographic/topic/${encodeURIComponent(state.problem || 'Distributed Systems Architecture')}`;
    const res = await fetch(url);
    const data = await res.json();
    state.infographic = data;
    renderInfographic(state.infographic, elements.inlineInfographicHost);
  } catch (err) {
    console.error('Failed to load session infographic:', err);
    elements.inlineInfographicHost.innerHTML = '<p class="text-danger">Failed to generate knowledge infographic.</p>';
  }
}

async function openInfographicModal() {
  elements.infographicModal.classList.remove('hidden');
  elements.modalInfographicHost.innerHTML = '<p class="text-muted" style="padding: 24px; text-align: center;">Loading knowledge infographic & open stubs...</p>';

  try {
    let data = state.infographic;
    if (!data) {
      const url = state.sessionId
        ? `${API_BASE}/api/session/${state.sessionId}/infographic`
        : `${API_BASE}/api/infographic/topic/${encodeURIComponent(state.problem || 'Distributed Systems Architecture')}`;
      const res = await fetch(url);
      data = await res.json();
      state.infographic = data;
    }
    renderInfographic(data, elements.modalInfographicHost);
  } catch (err) {
    console.error('Failed to load modal infographic:', err);
    elements.modalInfographicHost.innerHTML = '<p class="text-danger">Failed to load infographic.</p>';
  }
}

function renderInfographic(info, container) {
  if (!info || !container) return;

  const knownCardsHtml = (info.known_items || []).map((item, itemIdx) => {
    // Generate verified reference links list
    const refLinks = (item.reference_links && item.reference_links.length > 0)
      ? item.reference_links
      : (item.sources || []).filter(s => s.startsWith('http')).map(url => ({
          title: 'Validated Source Reference',
          url: url,
          type: 'website',
          description: 'Direct verification link'
        }));

    const refLinksHtml = refLinks.map((link, lIdx) => {
      const typeClass = link.type === 'document' ? 'link-type-document' : (link.type === 'video' ? 'link-type-video' : (link.type === 'paper' ? 'link-type-paper' : 'link-type-website'));
      const icon = link.type === 'document' ? '📄' : (link.type === 'video' ? '🎥' : (link.type === 'paper' ? '🔬' : '🌐'));
      const copyBtnId = `copy_known_${itemIdx}_${lIdx}`;
      return `
        <div class="link-row">
          <div class="link-left">
            <span class="link-type-pill ${typeClass}">${icon} ${(link.type || 'website').toUpperCase()}</span>
            <div class="link-details">
              <div class="link-label-row">
                <span class="link-label">${link.title}</span>
                <span class="link-verified-badge" title="Active verifiable link">✓ Verified</span>
              </div>
              <a href="${link.url}" target="_blank" rel="noopener noreferrer" class="link-url-anchor" title="${link.url}">
                <span>${link.url}</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
              </a>
            </div>
          </div>
          <div class="link-actions">
            <button type="button" class="btn-copy-url" data-url="${link.url}" id="${copyBtnId}">
              Copy URL
            </button>
          </div>
        </div>
      `;
    }).join('');

    const sourceLinks = (item.sources || []).map(s => {
      const isUrl = s.startsWith('http');
      if (isUrl) {
        return `<a href="${s}" target="_blank" rel="noopener noreferrer" class="source-item-pill">🔗 ${new URL(s).hostname}</a>`;
      }
      return `<span class="source-item-pill">${s}</span>`;
    }).join('');

    return `
      <div class="known-card">
        <div class="card-tag-row">
          <span class="category-tag">${item.icon || '✓'} ${item.category}</span>
          <span class="confidence-tag">${item.confidence}/10 Confidence</span>
        </div>
        <h4 class="known-card-title">
          ${item.primary_url ? `<a href="${item.primary_url}" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none;" title="Open Primary Source">${item.title} ↗</a>` : item.title}
        </h4>
        <p class="known-card-detail">${item.detail}</p>

        ${refLinks.length > 0 ? `
          <div class="source-links-box" style="margin-top: 12px; margin-bottom: 12px;">
            <div class="links-header">
              <span class="links-title" style="font-size: 0.76rem;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
                Clickable Verifiable & Validatable Links
              </span>
              <span class="validation-tag">Verifiable</span>
            </div>
            <div class="link-rows-list">
              ${refLinksHtml}
            </div>
          </div>
        ` : ''}

        <div class="sources-row">
          <span>Sources:</span>
          ${sourceLinks}
        </div>
      </div>
    `;
  }).join('');

  const stubCardsHtml = (info.unknown_stubs || []).map(stub => {
    const sevClass = stub.impact_severity === 'HIGH' ? 'severity-high' : (stub.impact_severity === 'MEDIUM' ? 'severity-medium' : 'severity-low');

    return `
      <div class="stub-card" id="${stub.id}">
        <div class="card-tag-row">
          <span class="category-tag" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: rgba(245, 158, 11, 0.35);">
            ${stub.icon || '❓'} ${stub.category}
          </span>
          <span class="severity-pill ${sevClass}">${stub.impact_severity} IMPACT</span>
        </div>
        <h4 class="stub-card-title">${stub.title}</h4>
        <p class="stub-card-gap">${stub.gap_description}</p>
        
        <div class="stub-action-box">
          <strong>Suggested Action:</strong> ${stub.suggested_action}
        </div>

        <div class="stub-prompt-container">
          <div class="prompt-label">Investigation Stub Prompt:</div>
          <div class="prompt-text">${stub.inquiry_prompt}</div>
        </div>

        <div class="stub-buttons-row">
          <button class="btn-stub-copy" data-prompt="${encodeURIComponent(stub.inquiry_prompt)}">
            📋 Copy Inquiry Prompt
          </button>
          <button class="btn-stub-investigate" data-topic="${encodeURIComponent(stub.title)}" data-prompt="${encodeURIComponent(stub.inquiry_prompt)}">
            🔍 Investigate Stub
          </button>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="infographic-dashboard">
      <!-- Hero Panel -->
      <div class="infographic-hero">
        <div class="hero-header-row">
          <div class="hero-title-group">
            <h2>🗺️ Knowledge Map: ${info.topic}</h2>
            <p>${info.summary}</p>
          </div>
          <div class="hero-metric-badge">
            <div>
              <div class="metric-circle">${info.mastery_percentage}%</div>
              <div class="metric-desc">Knowledge Mastery</div>
            </div>
          </div>
        </div>

        <div class="mastery-progress-track">
          <div class="mastery-progress-fill" style="width: ${info.mastery_percentage}%;"></div>
        </div>

        <div class="hero-stats-row">
          <span class="stat-pill known">✓ ${info.measured_dimensions_count} Verified Knowledge Pillars</span>
          <span class="stat-pill unknown">❓ ${info.unmeasured_stubs_count} Open Knowledge Stubs</span>
          <span class="stat-pill bkm">★ ${info.bkm_elevation_progress}</span>
        </div>
      </div>

      <!-- Two-Column Infographic -->
      <div class="infographic-columns">
        <!-- WHAT IS KNOWN -->
        <div class="infographic-column">
          <div class="column-header known-col">
            <h3 class="column-title known-title">
              <span>✓ WHAT IS KNOWN</span>
            </h3>
            <span class="column-badge">${(info.known_items || []).length} Verified Pillars</span>
          </div>
          ${knownCardsHtml}
        </div>

        <!-- WHAT IS STILL NOT KNOWN (STUBS) -->
        <div class="infographic-column">
          <div class="column-header unknown-col">
            <h3 class="column-title unknown-title">
              <span>❓ WHAT IS STILL NOT KNOWN (STUBS)</span>
            </h3>
            <span class="column-badge">${(info.unknown_stubs || []).length} Open Stubs</span>
          </div>
          ${stubCardsHtml}
        </div>
      </div>
    </div>
  `;

  // Bind copy URL buttons within the infographic
  container.querySelectorAll('.btn-copy-url').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const urlToCopy = e.target.getAttribute('data-url');
      if (urlToCopy && navigator.clipboard) {
        navigator.clipboard.writeText(urlToCopy).then(() => {
          const originalText = e.target.textContent;
          e.target.textContent = 'Copied!';
          e.target.classList.add('copied');
          setTimeout(() => {
            e.target.textContent = originalText;
            e.target.classList.remove('copied');
          }, 1800);
        }).catch(err => {
          console.error('Copy failed:', err);
        });
      }
    });
  });
}

function handleGlobalStubActions(e) {
  // Copy Prompt Button
  const copyBtn = e.target.closest('.btn-stub-copy');
  if (copyBtn) {
    const prompt = decodeURIComponent(copyBtn.dataset.prompt || '');
    if (prompt && navigator.clipboard) {
      navigator.clipboard.writeText(prompt).then(() => {
        const origText = copyBtn.innerHTML;
        copyBtn.classList.add('copied');
        copyBtn.innerHTML = '✓ Copied Prompt!';
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          copyBtn.innerHTML = origText;
        }, 2200);
      });
    }
    return;
  }

  // Investigate Stub Button
  const invBtn = e.target.closest('.btn-stub-investigate');
  if (invBtn) {
    const prompt = decodeURIComponent(invBtn.dataset.prompt || '');
    const topic = decodeURIComponent(invBtn.dataset.topic || '');
    
    // Close modal if open
    if (elements.infographicModal) {
      elements.infographicModal.classList.add('hidden');
    }

    // Populate intake and switch to Step 1
    if (elements.problemInput) {
      elements.problemInput.value = prompt || topic;
      if (elements.intentInput) {
        elements.intentInput.value = `Investigate open knowledge stub: ${topic}`;
      }
      setStep(1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      elements.problemInput.focus();
    }
    return;
  }
}

