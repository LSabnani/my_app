import { runRedVsGreenSimulation, generateFinancialProjections } from './gtmPipeline.js';

// GTM Pipeline State
let activeGTMCompanyKey = 'apple-vs-samsung';
let activeGTMScenarioMode = 'balanced'; // 'balanced' | 'low-cost' | 'all-out'
let currentGTMResult = null;

// DOM Elements
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const themeIcon = document.getElementById('theme-icon');
const runGtmBtn = document.getElementById('run-gtm-btn');
const gtmPresetPills = document.querySelectorAll('#gtm-preset-pills .depth-tab');
const gtmScenarioPills = document.querySelectorAll('#gtm-scenario-pills .depth-tab');

const traceModalOverlay = document.getElementById('trace-modal-overlay');
const closeTraceModalBtn = document.getElementById('close-trace-modal-btn');
const traceTimelineContainer = document.getElementById('trace-timeline-container');
const traceConfidenceScore = document.getElementById('trace-confidence-score');
const viewGtmTraceBtn = document.getElementById('view-gtm-trace-btn');
const toastEl = document.getElementById('toast');

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  bindEvents();
  // Default run initial simulation (Apple vs Samsung)
  handleGTMSimulation(activeGTMCompanyKey, activeGTMScenarioMode);
});

function initTheme() {
  const savedTheme = localStorage.getItem('gtm_ai_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
  if (themeIcon) {
    themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
}

function bindEvents() {
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('gtm_ai_theme', next);
      updateThemeIcon(next);
    });
  }

  if (gtmPresetPills) {
    gtmPresetPills.forEach(pill => {
      pill.addEventListener('click', () => {
        gtmPresetPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeGTMCompanyKey = pill.getAttribute('data-company');
        handleGTMSimulation(activeGTMCompanyKey, activeGTMScenarioMode);
      });
    });
  }

  if (gtmScenarioPills) {
    gtmScenarioPills.forEach(pill => {
      pill.addEventListener('click', () => {
        gtmScenarioPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        activeGTMScenarioMode = pill.getAttribute('data-scenario');
        handleGTMSimulation(activeGTMCompanyKey, activeGTMScenarioMode);
      });
    });
  }

  if (runGtmBtn) {
    runGtmBtn.addEventListener('click', () => {
      handleGTMSimulation(activeGTMCompanyKey, activeGTMScenarioMode);
    });
  }

  if (viewGtmTraceBtn) {
    viewGtmTraceBtn.addEventListener('click', () => {
      if (!currentGTMResult) return;
      renderGTMTraceLog(currentGTMResult.traceLog, currentGTMResult.overallMetrics.confidenceScore);
    });
  }

  if (closeTraceModalBtn) {
    closeTraceModalBtn.addEventListener('click', closeTraceModal);
  }

  if (traceModalOverlay) {
    traceModalOverlay.addEventListener('click', (e) => {
      if (e.target === traceModalOverlay) closeTraceModal();
    });
  }
}

function handleGTMSimulation(companyKey = 'apple-vs-samsung', scenarioMode = 'balanced') {
  currentGTMResult = runRedVsGreenSimulation(companyKey, scenarioMode);
  renderGTMResults(currentGTMResult);
  showToast(`Ran Red vs Green Simulation (${scenarioMode.toUpperCase()}) for ${currentGTMResult.greenCompany} vs ${currentGTMResult.redCompany}!`);
}

function renderGTMResults(res) {
  document.getElementById('gtm-green-title').textContent = res.greenCompany;
  document.getElementById('gtm-green-overview').textContent = `Dominant high-margin market position in ${res.sector}.`;
  document.getElementById('gtm-red-title').textContent = res.redCompany;
  document.getElementById('gtm-red-overview').textContent = `Aggressive challenger deploying full-information attack vectors.`;

  document.getElementById('gtm-verdict-title').textContent = res.overallMetrics.winLikelihood;
  document.getElementById('gtm-defensibility-score').textContent = `${res.overallMetrics.greenDefensibilityScore}%`;
  document.getElementById('gtm-attack-score').textContent = `${res.overallMetrics.avgRedSuccessProbability}%`;

  // Financial War Chest & FCF Body
  const war = res.gtmAnalysis.financialWarChest;
  document.getElementById('gtm-warchest-body').innerHTML = `
    <p><strong>${res.greenCompany} Cash War Chest:</strong> <span style="color:#10b981; font-weight:700;">$${war.greenWarChest}B</span> (FCF: $${war.greenFCF}B)</p>
    <p><strong>${res.redCompany} Cash War Chest:</strong> <span style="color:#ef4444; font-weight:700;">$${war.redWarChest}B</span> (FCF: $${war.redFCF}B)</p>
    <p style="margin-top:0.5rem; color:var(--text-secondary);">${war.analysis}</p>
  `;

  // Product Head-to-Head Body
  const h2h = res.gtmAnalysis.headToHead;
  let specsHtml = '';
  if (h2h.greenSpecs && h2h.redSpecs) {
    specsHtml = `
      <div style="margin-top:0.75rem; background:rgba(0,0,0,0.25); border:1px solid var(--border-color); border-radius:10px; padding:0.75rem;">
        <div style="font-weight:700; font-size:0.85rem; color:var(--accent-secondary); margin-bottom:0.5rem;">📱 Detailed Hardware Specs Comparison</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:0.5rem; font-size:0.8rem;">
          <div style="border-right:1px solid var(--border-color); padding-right:0.5rem;">
            <div style="color:#10b981; font-weight:700; margin-bottom:0.2rem;">${h2h.greenProduct}</div>
            <div><strong>Display:</strong> ${h2h.greenSpecs.display}</div>
            <div><strong>Chipset:</strong> ${h2h.greenSpecs.chipset}</div>
            <div><strong>Memory:</strong> ${h2h.greenSpecs.memoryStorage}</div>
            <div><strong>Camera:</strong> ${h2h.greenSpecs.cameraSystem}</div>
            <div><strong>Battery:</strong> ${h2h.greenSpecs.batteryCharging}</div>
          </div>
          <div style="padding-left:0.5rem;">
            <div style="color:#ef4444; font-weight:700; margin-bottom:0.2rem;">${h2h.redProduct}</div>
            <div><strong>Display:</strong> ${h2h.redSpecs.display}</div>
            <div><strong>Chipset:</strong> ${h2h.redSpecs.chipset}</div>
            <div><strong>Memory:</strong> ${h2h.redSpecs.memoryStorage}</div>
            <div><strong>Camera:</strong> ${h2h.redSpecs.cameraSystem}</div>
            <div><strong>Battery:</strong> ${h2h.redSpecs.batteryCharging}</div>
          </div>
        </div>
      </div>
    `;
  }

  document.getElementById('gtm-headtohead-body').innerHTML = `
    <p><strong>Green Flagship Product:</strong> ${h2h.greenProduct} (${h2h.greenProductRevenue})</p>
    <p><strong>Red Flagship Product:</strong> ${h2h.redProduct} (${h2h.redProductRevenue})</p>
    <p><strong>Comparison Category:</strong> ${h2h.customerComparisonPair}</p>
    ${specsHtml}
    <p style="margin-top:0.5rem; color:var(--text-secondary);">${h2h.verdict}</p>
  `;

  // IP Portfolio Body
  const ip = res.gtmAnalysis.ipPortfolio;
  document.getElementById('gtm-ip-body').innerHTML = `
    <p><strong>Green Vetted IP:</strong> ${ip.greenStrengths.join(', ')}</p>
    <p><strong>Red Vetted IP:</strong> ${ip.redStrengths.join(', ')}</p>
    <p style="color:#f59e0b; margin-top:0.5rem;"><strong>Unvetted / Vulnerable IP Frontiers:</strong> ${ip.unvettedAreas.join('; ')}</p>
  `;

  // Loyalty Body
  const loy = res.gtmAnalysis.loyalty;
  document.getElementById('gtm-loyalty-body').innerHTML = `
    <p><strong>Green Retention Rate:</strong> <span style="color:#10b981; font-weight:700;">${loy.greenRetentionRate}</span></p>
    <p><strong>Red Retention Rate:</strong> <span style="color:#ef4444; font-weight:700;">${loy.redRetentionRate}</span></p>
    <p style="margin-top:0.5rem; color:var(--text-secondary);">${loy.greenBrandSentiment}</p>
  `;

  // Render Red Team Strategy Table
  const tbody = document.getElementById('gtm-strategies-table-body');
  tbody.innerHTML = res.redTeamStrategies.map(strat => {
    let probClass = strat.probabilityOfSuccess >= 80 ? 'high' : (strat.probabilityOfSuccess >= 70 ? 'med' : 'low');
    return `
      <tr>
        <td>
          <strong style="color:var(--text-primary);">${strat.title}</strong>
          <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.2rem;">${strat.summary}</div>
        </td>
        <td><span class="badge">${strat.feasibilityScore}/10</span></td>
        <td><strong>$${strat.costBillions}B</strong></td>
        <td>${strat.executionTimeMonths} mos</td>
        <td><span class="prob-badge ${probClass}">${strat.probabilityOfSuccess}%</span></td>
        <td style="font-size:0.82rem; color:#34d399;">${strat.greenCountermeasure}</td>
      </tr>
    `;
  }).join('');

  // Render Projections Table
  const proj = generateFinancialProjections(activeGTMCompanyKey);
  const projTbody = document.getElementById('gtm-projections-table-body');
  projTbody.innerHTML = `
    <tr>
      <td><strong>${res.greenCompany} Revenue ($B)</strong></td>
      <td>${proj.greenHistRev[0]}</td>
      <td>${proj.greenHistRev[1]}</td>
      <td>${proj.greenHistRev[2]}</td>
      <td style="color:#10b981;"><strong>${proj.greenFwdRev[0]}</strong></td>
      <td style="color:#10b981;"><strong>${proj.greenFwdRev[1]}</strong></td>
      <td style="color:#10b981;"><strong>${proj.greenFwdRev[2]}</strong></td>
    </tr>
    <tr>
      <td><strong>${res.redCompany} Revenue ($B)</strong></td>
      <td>${proj.redHistRev[0]}</td>
      <td>${proj.redHistRev[1]}</td>
      <td>${proj.redHistRev[2]}</td>
      <td style="color:#ef4444;"><strong>${proj.redFwdRev[0]}</strong></td>
      <td style="color:#ef4444;"><strong>${proj.redFwdRev[1]}</strong></td>
      <td style="color:#ef4444;"><strong>${proj.redFwdRev[2]}</strong></td>
    </tr>
    <tr>
      <td><strong>${res.greenCompany} Gross Margin %</strong></td>
      <td>${proj.greenHistGM[0]}%</td>
      <td>${proj.greenHistGM[1]}%</td>
      <td>${proj.greenHistGM[2]}%</td>
      <td style="color:#10b981;"><strong>${proj.greenFwdGM[0]}%</strong></td>
      <td style="color:#10b981;"><strong>${proj.greenFwdGM[1]}%</strong></td>
      <td style="color:#10b981;"><strong>${proj.greenFwdGM[2]}%</strong></td>
    </tr>
    <tr>
      <td><strong>${res.redCompany} Gross Margin %</strong></td>
      <td>${proj.redHistGM[0]}%</td>
      <td>${proj.redHistGM[1]}%</td>
      <td>${proj.redHistGM[2]}%</td>
      <td style="color:#ef4444;"><strong>${proj.redFwdGM[0]}%</strong></td>
      <td style="color:#ef4444;"><strong>${proj.redFwdGM[1]}%</strong></td>
      <td style="color:#ef4444;"><strong>${proj.redFwdGM[2]}%</strong></td>
    </tr>
  `;
}

function renderGTMTraceLog(traceLog, confidenceScore) {
  if (!traceTimelineContainer || !traceModalOverlay) return;
  traceConfidenceScore.textContent = `${confidenceScore}%`;
  traceTimelineContainer.innerHTML = traceLog.map(item => `
    <div class="trace-step">
      <div class="trace-step-number">${item.step}</div>
      <div style="flex:1;">
        <div class="trace-step-name">${item.name}</div>
        <div class="trace-step-detail">${item.detail}</div>
      </div>
    </div>
  `).join('');
  traceModalOverlay.style.display = 'flex';
  traceModalOverlay.classList.add('active');
}

function closeTraceModal() {
  if (traceModalOverlay) {
    traceModalOverlay.style.display = 'none';
    traceModalOverlay.classList.remove('active');
  }
}

function showToast(msg) {
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => {
    toastEl.classList.remove('show');
  }, 3000);
}
