/**
 * CHIPCHAIN - Semiconductor Equipment Commodity & Supplier Platform Frontend Application
 */

// Application State
let appState = {
  commodities: {},
  suppliers: [],
  filteredSuppliers: [],
  selectedCommodity: "All",
  selectedRegion: "All",
  selectedCountry: "All",
  searchQuery: "",
  approvalHistory: []
};

// Region to Countries mapping
const REGION_COUNTRIES = {
  "All": ["All", "Japan", "South Korea", "Taiwan", "USA", "Canada", "Netherlands", "Germany", "Switzerland", "Israel", "UK"],
  "Asia": ["All", "Japan", "South Korea", "Taiwan", "Singapore", "China"],
  "North America": ["All", "USA", "Canada", "Mexico"],
  "Europe": ["All", "Netherlands", "Switzerland", "Germany", "France", "UK"],
  "Middle East": ["All", "Israel", "UAE"]
};

// Standard Spec Deep-Dive Fallbacks for categories
const SPEC_DEEPDIVES = {
  "Advanced Ceramics": {
    title: "Advanced Ceramics",
    tam: "$4.2B",
    cagr: "+7.4%",
    description: "High-purity Alumina (Al2O3), Silicon Carbide (SiC), Quartz, and AlN engineered for plasma etch chambers, electrostatic chuck (E-Chuck) top plates, and wafer heaters.",
    leadingSuppliers: ["Kyocera Corporation", "CoorsTek", "Ferrotec Holdings", "Wonik QnC", "SCHOTT AG"],
    substrates: ["High-Purity Al2O3 (99.99%)", "CVD Silicon Carbide (SiC)", "Fused Quartz", "Aluminum Nitride (AlN)"],
    applications: "Plasma etch chamber liners, E-Chuck top plates, gas distribution plates, quartz diffusion tubes.",
    keyMetrics: {
      "Dielectric Strength": "> 15 kV/mm",
      "Plasma Erosion Rate": "< 0.1 nm/min",
      "Purity Grade": "99.9999% Synthetic Grade",
      "Thermal Conductivity": "180 W/m·K (AlN)"
    }
  },
  "Precision Machining": {
    title: "Precision Machining",
    tam: "$8.5B",
    cagr: "+6.8%",
    description: "5-axis ultra-precision CNC machined vacuum chamber bodies, gas showerheads, and optical alignment sub-assemblies.",
    leadingSuppliers: ["Ultra Clean Technology (UCT)", "Foxsemicon (FITI)", "Ferrotec Holdings", "Technic Inc."],
    substrates: ["Aluminum 6061-T6 / 7075", "Stainless Steel 316L VIM/VAR", "Titanium Grade 5", "Inconel 625"],
    applications: "UHP process chambers, gas distribution manifolds, showerheads, load lock chambers.",
    keyMetrics: {
      "Vacuum Tightness": "1x10^-9 Torr",
      "CMM Verification": "100% CMM Sub-micron",
      "Surface Roughness": "Ra < 0.2 µm",
      "Tolerance Envelope": "± 0.002 mm"
    }
  },
  "Specialized Welding": {
    title: "Specialized Welding & Frame Fabrication",
    tam: "$2.8B",
    cagr: "+5.9%",
    description: "Electron beam (EB), cleanroom orbital TIG, and laser welding for ultra-high purity (UHP) gas delivery sticks and heavy structural tool frames.",
    leadingSuppliers: ["Sanmina", "Benchmark Electronics", "Ultra Clean Technology (UCT)", "Dynamic Manufacturing", "Mott Corporation"],
    substrates: ["316L EP Stainless Steel", "Structural Steel Tubing", "Hastelloy C-22", "Nickel Alloy 200"],
    applications: "UHP gas stick assemblies, valve manifold boxes (VMB), heavy tool frames, sub-chassis structures.",
    keyMetrics: {
      "Purge Argon Grade": "6N (99.9999%)",
      "Helium Leak Rate": "< 1x10^-10 atm·cc/s",
      "Weld Penetration": "100% Full Penetration NDT",
      "Frame Planarity": "± 0.05 mm across 2m span"
    }
  },
  "Cable Harnesses": {
    title: "Cable Harnesses & Interconnects",
    tam: "$3.1B",
    cagr: "+8.1%",
    description: "Cleanroom ISO Class 1/10 cabling, high-flex robotics harnesses, RF feedthrough lines, and low-outgassing assemblies.",
    leadingSuppliers: ["BizLink Technology", "Volex", "Huber+Suhner", "Leoni", "Rosenberger"],
    substrates: ["PTFE / PEEK Insulation", "Silver-Plated Copper", "Silicone Jacket", "BeCu Contacts"],
    applications: "Wafer handling robotic arms, RF generator connections, motion control drag chains.",
    keyMetrics: {
      "Cleanroom Class": "ISO Class 1 / 10",
      "Outgassing TML": "< 0.5% (ASTM E595)",
      "Flex Cycles": "> 10,000,000 cycles",
      "Impedance Control": "50 Ω ± 2 Ω RF Cables"
    }
  },
  "Circuit Boards": {
    title: "Circuit Boards / PCBAs & EMS",
    tam: "$6.7B",
    cagr: "+9.2%",
    description: "High-density interconnect (HDI) rigid-flex PCBs, RF matching control boards, and complex cleanroom EMS system box builds.",
    leadingSuppliers: ["Plexus Corp", "Benchmark Electronics", "Celestica", "Sanmina", "Jabil"],
    substrates: ["Rogers 4350B RF Substrates", "FR-4 High TG", "Polyimide Rigid-Flex"],
    applications: "RF matching networks, generator controllers, optical sensor interface, tool power distribution.",
    keyMetrics: {
      "IPC Standard": "IPC Class 3 High Reliability",
      "Impedance Control": "± 5% high frequency",
      "Inspection Level": "3D AOI & 100% AXI X-Ray",
      "Cleanroom Assembly": "ISO Class 5-7 Assembly"
    }
  }
};

// Initialize Application DOM Listeners
document.addEventListener("DOMContentLoaded", () => {
  initDOMListeners();
  fetchCleanAPIData();
});

// Setup DOM Event Listeners
function initDOMListeners() {
  const commoditySelect = document.getElementById("commodity-select");
  const regionSelect = document.getElementById("region-select");
  const countrySelect = document.getElementById("country-select");
  const quickSearch = document.getElementById("quick-search");

  const resetBtn = document.getElementById("reset-cache-btn");
  const exportPdfBtn = document.getElementById("export-pdf-btn");
  const exportCsvBtn = document.getElementById("export-csv-btn");
  const launchSlidesBtn = document.getElementById("launch-slides-btn");
  const modalCloseBtn = document.getElementById("modal-close-btn");

  const applyFilterBtn = document.getElementById("apply-filter-btn");

  // Commodity change listener: sets selection state
  commoditySelect.addEventListener("change", (e) => {
    appState.selectedCommodity = e.target.value;
  });

  // Region change listener: updates cascading country dropdown
  regionSelect.addEventListener("change", (e) => {
    appState.selectedRegion = e.target.value;
    updateCountryDropdown(appState.selectedRegion);
    appState.selectedCountry = countrySelect.value;
  });

  // Country change listener
  countrySelect.addEventListener("change", (e) => {
    appState.selectedCountry = e.target.value;
  });

  // Apply & Accept Filter button listener
  if (applyFilterBtn) {
    applyFilterBtn.addEventListener("click", () => {
      acceptFilterSelection();
    });
  }

  // Quick Search listener
  quickSearch.addEventListener("input", (e) => {
    appState.searchQuery = e.target.value.toLowerCase().trim();
    applyFiltersAndRender();
  });

  // Reset & Clear Cache Button handler
  resetBtn.addEventListener("click", () => {
    handleResetAndClearCache();
  });

  // Export PDF Button handler
  exportPdfBtn.addEventListener("click", () => {
    exportToPDF();
  });

  // Export CSV Button handler
  exportCsvBtn.addEventListener("click", () => {
    exportToCSV();
  });

  // Launch Executive Slide Deck handler
  launchSlidesBtn.addEventListener("click", () => {
    window.open("executive_slide_deck.html", "_blank");
  });

  // Close Modal handler
  modalCloseBtn.addEventListener("click", () => {
    document.getElementById("supplier-modal").classList.remove("active");
  });
}

// Fetch Clean API Data with cache-busting timestamp query
async function fetchCleanAPIData() {
  try {
    const timestamp = new Date().getTime();
    const response = await fetch(`/api/data?_t=${timestamp}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    appState.commodities = data.commodities || {};
    
    // Sort suppliers by Region -> Country -> City (Spec Default)
    appState.suppliers = sortSuppliers(data.suppliers || []);
    
    // Update timestamp tag
    const now = new Date();
    document.getElementById("report-timestamp").textContent = now.toLocaleString();

    // Populate commodity & country dropdown initial state
    populateCommodityDropdown();
    updateCountryDropdown(appState.selectedRegion);

    // Filter and render
    applyFiltersAndRender();
    showToast("Clean API data fetched successfully", "success");

  } catch (err) {
    console.error("API Fetch Error:", err);
    showToast("Server offline. Using local database fallback.", "warning");
    // Fallback attempt to fetch direct database.json static file
    fetchStaticDatabaseFallback();
  }
}

// Fallback if REST server endpoint fails
async function fetchStaticDatabaseFallback() {
  try {
    const timestamp = new Date().getTime();
    const response = await fetch(`database.json?_t=${timestamp}`);
    const data = await response.json();
    appState.commodities = data.commodities || {};
    appState.suppliers = sortSuppliers(data.suppliers || []);
    populateCommodityDropdown();
    updateCountryDropdown("All");
    applyFiltersAndRender();
  } catch (e) {
    console.error("Static Database Load Error:", e);
  }
}

// Populate Commodity Dropdown dynamically from Database & Suppliers
function populateCommodityDropdown() {
  const commoditySelect = document.getElementById("commodity-select");
  if (!commoditySelect) return;

  const currentSelection = appState.selectedCommodity || "All";

  // Gather unique commodity list
  const commSet = new Set(Object.keys(appState.commodities || {}));
  (appState.suppliers || []).forEach(s => {
    if (s.commodity) commSet.add(s.commodity);
  });

  // Helper to parse TAM string like "$8.5B" or "$500M" into a numeric value for sorting
  const parseTam = (commName) => {
    const info = appState.commodities[commName] || {};
    const tamStr = info.tam || "$0";
    const num = parseFloat(tamStr.replace(/[^0-9.]/g, '')) || 0;
    if (tamStr.toUpperCase().includes('B')) return num * 1000;
    return num;
  };

  const sortedList = Array.from(commSet).sort((a, b) => parseTam(b) - parseTam(a));

  commoditySelect.innerHTML = "";
  
  // All Commodities default option
  const allOpt = document.createElement("option");
  allOpt.value = "All";
  allOpt.textContent = "All Commodities";
  if (currentSelection === "All") allOpt.selected = true;
  commoditySelect.appendChild(allOpt);

  sortedList.forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    if (name === currentSelection) opt.selected = true;
    commoditySelect.appendChild(opt);
  });

  renderCommodityCards(sortedList);
}

// Render Interactive Commodity Selector Cards
function renderCommodityCards(commodityList) {
  const grid = document.getElementById("commodity-cards-grid");
  if (!grid) return;
  grid.innerHTML = "";

  // Add "All Commodities" Card
  const allCard = document.createElement("div");
  allCard.className = `commodity-card ${appState.selectedCommodity === 'All' ? 'active' : ''}`;
  allCard.onclick = () => selectCommodityCard('All');
  allCard.innerHTML = `
    <div class="commodity-card-title"><i class="fa-solid fa-layer-group" style="color: var(--primary);"></i> All Commodities</div>
    <div class="commodity-card-meta">
      <span>58 Suppliers</span>
      <span style="color: var(--accent-green);">$25.3B TAM</span>
    </div>
  `;
  grid.appendChild(allCard);

  commodityList.forEach(name => {
    const card = document.createElement("div");
    const isActive = appState.selectedCommodity === name;
    card.className = `commodity-card ${isActive ? 'active' : ''}`;
    card.onclick = () => selectCommodityCard(name);

    const info = appState.commodities[name] || {};
    const tam = info.tam || '$3.5B+';
    const cagr = info.cagr || '+7.0%';
    const count = appState.suppliers.filter(s => (s.commodity || '').toLowerCase().includes(name.toLowerCase())).length;

    card.innerHTML = `
      <div class="commodity-card-title"><i class="fa-solid fa-microchip" style="color: var(--primary);"></i> ${name}</div>
      <div class="commodity-card-meta">
        <span>${count} Suppliers</span>
        <span style="color: var(--accent-gold);">${tam} (${cagr})</span>
      </div>
    `;
    grid.appendChild(card);
  });
}

// Select Commodity Card handler
function selectCommodityCard(name) {
  appState.selectedCommodity = name;
  const select = document.getElementById("commodity-select");
  if (select) select.value = name;

  acceptFilterSelection();
}

// Accept Filter Selection & Update Analysis Flow
function acceptFilterSelection() {
  showToast(`Filters accepted for: ${appState.selectedCommodity} (${appState.selectedRegion} / ${appState.selectedCountry}). Updating analysis...`, "info");

  // 1. Purge browser localStorage & sessionStorage
  localStorage.clear();
  sessionStorage.clear();
  appState.approvalHistory = [];

  // 2. Fetch clean API data & re-render
  fetchCleanAPIData().then(() => {
    showToast("Analysis updated! Click 'Export Executive PDF' when ready to export.", "success");
  });
}

// Sort suppliers by Region -> Country -> City (Spec Default)
function sortSuppliers(suppliers) {
  return suppliers.sort((a, b) => {
    const regionA = (a.region || "").toLowerCase();
    const regionB = (b.region || "").toLowerCase();
    if (regionA !== regionB) return regionA.localeCompare(regionB);

    const countryA = (a.country || "").toLowerCase();
    const countryB = (b.country || "").toLowerCase();
    if (countryA !== countryB) return countryA.localeCompare(countryB);

    const cityA = (a.city || "").toLowerCase();
    const cityB = (b.city || "").toLowerCase();
    return cityA.localeCompare(cityB);
  });
}

// Cascading Country Dropdown
function updateCountryDropdown(region) {
  const countrySelect = document.getElementById("country-select");
  countrySelect.innerHTML = "";

  const countries = REGION_COUNTRIES[region] || REGION_COUNTRIES["All"];
  countries.forEach(country => {
    const opt = document.createElement("option");
    opt.value = country;
    opt.textContent = country === "All" ? "All Countries" : country;
    if (country === appState.selectedCountry) opt.selected = true;
    countrySelect.appendChild(opt);
  });

  if (!countries.includes(appState.selectedCountry)) {
    appState.selectedCountry = "All";
    countrySelect.value = "All";
  }
}

// Apply Filters & Update Dashboard Render
function applyFiltersAndRender() {
  let list = [...appState.suppliers];

  // Commodity Filter
  if (appState.selectedCommodity && appState.selectedCommodity !== "All") {
    const term = appState.selectedCommodity.toLowerCase();
    list = list.filter(s => {
      const c = (s.commodity || "").toLowerCase();
      return c.includes(term) || term.includes(c) ||
        (term.includes("ceramic") && c.includes("ceramic")) ||
        (term.includes("machining") && c.includes("machining")) ||
        (term.includes("welding") && c.includes("welding")) ||
        (term.includes("harness") && c.includes("harness")) ||
        (term.includes("circuit") && c.includes("pcba"));
    });
  }

  // Region Filter
  if (appState.selectedRegion && appState.selectedRegion !== "All") {
    list = list.filter(s => (s.region || "").toLowerCase() === appState.selectedRegion.toLowerCase());
  }

  // Country Filter
  if (appState.selectedCountry && appState.selectedCountry !== "All") {
    list = list.filter(s => (s.country || "").toLowerCase() === appState.selectedCountry.toLowerCase());
  }

  // Quick Search Filter
  if (appState.searchQuery) {
    const q = appState.searchQuery;
    list = list.filter(s => 
      (s.name || "").toLowerCase().includes(q) ||
      (s.city || "").toLowerCase().includes(q) ||
      (s.country || "").toLowerCase().includes(q) ||
      (s.commodity || "").toLowerCase().includes(q) ||
      (s.cadFormats || []).join(" ").toLowerCase().includes(q)
    );
  }

  appState.filteredSuppliers = list;

  // Render Sub-components
  renderMetaBanner();
  renderKPIBanner();
  renderCommodityDeepDive();
  renderSuppliersTable();
}

// Render Executive Header Meta Banner
function renderMetaBanner() {
  document.getElementById("meta-commodity-tag").innerHTML = `<i class="fa-solid fa-boxes-stacked"></i> Commodity: ${appState.selectedCommodity}`;
  document.getElementById("meta-region-tag").innerHTML = `<i class="fa-solid fa-earth-americas"></i> Region: ${appState.selectedRegion}`;
  document.getElementById("meta-country-tag").innerHTML = `<i class="fa-solid fa-location-dot"></i> Country: ${appState.selectedCountry}`;
  
  const titleElem = document.getElementById("exec-study-title");
  if (appState.selectedCommodity !== "All") {
    titleElem.textContent = `${appState.selectedCommodity} — Executive Sourcing & Supplier Study`;
  } else {
    titleElem.textContent = "Semiconductor Equipment Sourcing & Supplier Study Report";
  }
}

// Render KPI Summary Banner
function renderKPIBanner() {
  const count = appState.filteredSuppliers.length;
  document.getElementById("kpi-suppliers-count").textContent = count;

  if (count === 0) {
    document.getElementById("kpi-avg-otd").textContent = "N/A";
    document.getElementById("kpi-rnd-spend").textContent = "$0M";
    document.getElementById("kpi-free-cash").textContent = "$0M";
    return;
  }

  // OTD Avg
  const sumOtd = appState.filteredSuppliers.reduce((acc, s) => acc + (s.performance?.otdPct || 0), 0);
  const avgOtd = (sumOtd / count).toFixed(1);
  document.getElementById("kpi-avg-otd").textContent = `${avgOtd}%`;

  // R&D Spend Sum (2025)
  const sumRnd = appState.filteredSuppliers.reduce((acc, s) => {
    const rnd2025 = s.financials?.rndInvestment?.["2025"] || s.financials?.rndInvestment?.["2024"] || 0;
    return acc + rnd2025;
  }, 0);
  document.getElementById("kpi-rnd-spend").textContent = `$${sumRnd.toFixed(1)}M`;

  // Free Cash Flow Sum
  const sumFcf = appState.filteredSuppliers.reduce((acc, s) => acc + (s.financials?.freeCashFlow || 0), 0);
  document.getElementById("kpi-free-cash").textContent = `$${sumFcf.toFixed(1)}M`;
}

// Render Commodity Deep Dive Section
function renderCommodityDeepDive() {
  const categoryName = appState.selectedCommodity !== "All" ? appState.selectedCommodity : "Precision Machining";
  
  // Find match in dataset or fallback
  let deepData = null;

  // Search exact or partial key in database commodities
  for (const key in appState.commodities) {
    if (key.toLowerCase().includes(categoryName.toLowerCase()) || categoryName.toLowerCase().includes(key.toLowerCase())) {
      deepData = appState.commodities[key];
      break;
    }
  }

  if (!deepData) {
    deepData = SPEC_DEEPDIVES[categoryName] || SPEC_DEEPDIVES["Advanced Ceramics"] || SPEC_DEEPDIVES["Precision Machining"];
  }

  document.getElementById("deepdive-category-name").textContent = `${deepData.title || categoryName} Deep-Dive Metrics (${deepData.tam || '$5.0B'} TAM | CAGR ${deepData.cagr || '+7.0%'})`;
  document.getElementById("deepdive-description").textContent = deepData.description || "High-integrity semiconductor commodity specifications.";

  // Substrates
  const subsContainer = document.getElementById("deepdive-substrates");
  subsContainer.innerHTML = "";
  (deepData.substrates || []).forEach(sub => {
    const badge = document.createElement("span");
    badge.className = "badge-item";
    badge.textContent = sub;
    subsContainer.appendChild(badge);
  });

  // Applications
  document.getElementById("deepdive-applications").textContent = deepData.applications || "Semiconductor vacuum & process equipment.";

  // Key Metrics
  const metricsContainer = document.getElementById("deepdive-key-metrics");
  metricsContainer.innerHTML = "";
  const metrics = deepData.keyMetrics || {};
  for (const k in metrics) {
    const row = document.createElement("div");
    row.className = "metric-row";
    row.innerHTML = `<span class="metric-key">${formatMetricName(k)}:</span><span class="metric-val">${metrics[k]}</span>`;
    metricsContainer.appendChild(row);
  }

  // Leading Suppliers
  const leadsContainer = document.getElementById("deepdive-leading-suppliers");
  leadsContainer.innerHTML = "";
  (deepData.leadingSuppliers || []).forEach(sup => {
    const badge = document.createElement("span");
    badge.className = "badge-item";
    badge.style.borderColor = "var(--primary)";
    badge.style.color = "var(--primary)";
    badge.textContent = sup;
    leadsContainer.appendChild(badge);
  });
}

function formatMetricName(key) {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
}

// Render Global Suppliers Matrix Table
function renderSuppliersTable() {
  const tbody = document.getElementById("suppliers-table-body");
  tbody.innerHTML = "";

  if (appState.filteredSuppliers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching suppliers found for selected criteria.</td></tr>`;
    return;
  }

  appState.filteredSuppliers.forEach(s => {
    const tr = document.createElement("tr");

    const otd = s.performance?.otdPct || 0;
    const otdClass = otd >= 96 ? "otd-high" : "otd-medium";

    const fcf = s.financials?.freeCashFlow ? `$${s.financials.freeCashFlow}M FCF` : 'N/A';
    const rev2025 = s.financials?.revenueHistory?.["2025"] ? `$${s.financials.revenueHistory["2025"]}M Rev` : '';

    const directLabor = s.costStructure?.directLaborRate ? `$${s.costStructure.directLaborRate}/hr` : 'N/A';
    const burden = s.costStructure?.burdenRate ? `$${s.costStructure.burdenRate}/hr` : 'N/A';
    const margin = s.costStructure?.targetProfitMargin ? `${s.costStructure.targetProfitMargin}% Margin` : '';

    const cleanroom = s.contaminationControl?.cleanroomClass || 'ISO Class 5';
    const cads = (s.cadFormats || []).slice(0, 2).join(", ");

    tr.innerHTML = `
      <td>
        <div class="supplier-name">${s.name}</div>
        <div class="supplier-location"><i class="fa-solid fa-location-dot"></i> ${s.city}, ${s.country} (${s.region})</div>
      </td>
      <td><span class="badge-item" style="color: var(--primary);">${s.commodity}</span></td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem;">
        Est. ${s.establishedYear || 'N/A'}<br>
        <span style="color: var(--text-muted);">${(s.employees || 0).toLocaleString()} Staff</span>
      </td>
      <td>
        <span class="otd-badge ${otdClass}">
          <i class="fa-solid fa-circle-check"></i> ${otd}%
        </span>
      </td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem;">
        Proto: ${s.performance?.prototypeLeadTimeDays || 14}d<br>
        Vol: ${s.performance?.volumeLeadTimeWeeks || 6}w
      </td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem;">
        <span style="color: var(--accent-green); font-weight: 600;">${fcf}</span><br>
        <span style="color: var(--text-muted);">${rev2025}</span>
      </td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem;">
        Labor: ${directLabor}<br>
        Burden: ${burden}<br>
        <span style="color: var(--accent-gold);">${margin}</span>
      </td>
      <td>
        <span class="badge-item" style="background: rgba(6, 214, 160, 0.1); color: var(--accent-green); border-color: rgba(6, 214, 160, 0.3);">
          ${cleanroom}
        </span>
      </td>
      <td style="font-size: 0.78rem; color: var(--text-muted);">
        CAD: ${cads}<br>
        <span style="color: var(--primary);">${s.dataSharing?.edi || 'REST API'}</span>
      </td>
      <td>
        <button class="btn btn-secondary" style="padding: 0.35rem 0.65rem; font-size: 0.75rem;" onclick="viewSupplierDetails('${s.id}')">
          <i class="fa-solid fa-eye"></i> Profile
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}

// Supplier Detail Profile Modal
window.viewSupplierDetails = function(supplierId) {
  const s = appState.suppliers.find(sup => sup.id === supplierId);
  if (!s) return;

  const modalBody = document.getElementById("modal-body-content");
  modalBody.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <div>
        <h2 style="font-size: 1.5rem; font-weight: 800; color: #fff;">${s.name}</h2>
        <div style="color: var(--primary); font-weight: 600; font-size: 0.9rem; margin-top: 0.2rem;">
          <i class="fa-solid fa-microchip"></i> ${s.commodity} &bull; ${s.city}, ${s.country} (${s.region})
        </div>
      </div>
      <div class="otd-badge otd-high" style="font-size: 1rem; padding: 0.5rem 1rem;">
        OTD: ${s.performance?.otdPct || 0}%
      </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
      <div class="detail-block">
        <h4><i class="fa-solid fa-building"></i> Overview Metadata</h4>
        <div class="metrics-list">
          <div class="metric-row"><span class="metric-key">Est. Year:</span><span class="metric-val">${s.establishedYear}</span></div>
          <div class="metric-row"><span class="metric-key">Headcount:</span><span class="metric-val">${s.employees?.toLocaleString()}</span></div>
          <div class="metric-row"><span class="metric-key">Commodity Revenue Share:</span><span class="metric-val">${s.commodityConcentration}%</span></div>
        </div>
      </div>

      <div class="detail-block">
        <h4><i class="fa-solid fa-vault"></i> Financial Solvency</h4>
        <div class="metrics-list">
          <div class="metric-row"><span class="metric-key">Free Cash Flow:</span><span class="metric-val">$${s.financials?.freeCashFlow}M</span></div>
          <div class="metric-row"><span class="metric-key">2025 Revenue:</span><span class="metric-val">$${s.financials?.revenueHistory?.["2025"]}M</span></div>
          <div class="metric-row"><span class="metric-key">2025 R&D Investment:</span><span class="metric-val">$${s.financials?.rndInvestment?.["2025"]}M</span></div>
        </div>
      </div>

      <div class="detail-block">
        <h4><i class="fa-solid fa-calculator"></i> Cost & Rate Structure</h4>
        <div class="metrics-list">
          <div class="metric-row"><span class="metric-key">Direct Labor:</span><span class="metric-val">$${s.costStructure?.directLaborRate}/hr</span></div>
          <div class="metric-row"><span class="metric-key">Burden Rate:</span><span class="metric-val">$${s.costStructure?.burdenRate}/hr</span></div>
          <div class="metric-row"><span class="metric-key">Target Margin:</span><span class="metric-val">${s.costStructure?.targetProfitMargin}%</span></div>
        </div>
      </div>

      <div class="detail-block">
        <h4><i class="fa-solid fa-shield-virus"></i> Contamination & BCP</h4>
        <div class="metrics-list">
          <div class="metric-row"><span class="metric-key">Cleanroom Rating:</span><span class="metric-val">${s.contaminationControl?.cleanroomClass}</span></div>
          <div class="metric-row"><span class="metric-key">UPW Resistivity:</span><span class="metric-val">${s.contaminationControl?.upwResistivity || '18.2 MΩ·cm'}</span></div>
          <div class="metric-row"><span class="metric-key">Dual-Site Redundancy:</span><span class="metric-val">${s.bcp?.dualSiteRedundancy ? 'Yes' : 'No'}</span></div>
          <div class="metric-row"><span class="metric-key">RTO Recovery Time:</span><span class="metric-val">${s.bcp?.rtoHours} hours</span></div>
        </div>
      </div>
    </div>
  `;

  document.getElementById("supplier-modal").classList.add("active");
};

// Commodity Change Analysis & Cache Refresh Handler
function handleCommodityChangeAutoPublish() {
  showToast(`Commodity analysis updated to: ${appState.selectedCommodity}`, "info");

  // 1. Purge browser localStorage & sessionStorage
  localStorage.clear();
  sessionStorage.clear();

  // 2. Reset approval step history
  appState.approvalHistory = [];

  // 3. Fetch clean data from Python API server with timestamp query
  fetchCleanAPIData();
}

// Reset & Clear Cache Button Handler
function handleResetAndClearCache() {
  // 1. Purge local & session storage
  localStorage.clear();
  sessionStorage.clear();
  appState.approvalHistory = [];

  // 2. Reset all user inputs to defaults
  appState.selectedCommodity = "All";
  appState.selectedRegion = "All";
  appState.selectedCountry = "All";
  appState.searchQuery = "";

  document.getElementById("commodity-select").value = "All";
  document.getElementById("region-select").value = "All";
  document.getElementById("quick-search").value = "";

  updateCountryDropdown("All");

  // 3. Re-fetch clean data with timestamp query
  fetchCleanAPIData();

  showToast("Cache cleared, inputs reset & clean API data refreshed!", "success");
}

// Export Executive Study Package to PDF
function exportToPDF() {
  const container = document.getElementById("report-container");
  
  if (window.html2pdf) {
    const opt = {
      margin:       0.3,
      filename:     `CHIPCHAIN_Executive_Study_${appState.selectedCommodity}_${new Date().toISOString().slice(0,10)}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#0a0d14' },
      jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };
    
    html2pdf().set(opt).from(container).save().then(() => {
      showToast("Executive Study PDF downloaded successfully", "success");
    }).catch(err => {
      console.warn("html2pdf error, falling back to window.print():", err);
      window.print();
    });
  } else {
    window.print();
  }
}

// Export Supplier Matrix to CSV
function exportToCSV() {
  if (appState.filteredSuppliers.length === 0) {
    showToast("No data to export", "warning");
    return;
  }

  const headers = ["ID", "Name", "Commodity", "Region", "Country", "City", "Established", "Employees", "OTD %", "Proto Lead Days", "Volume Lead Weeks", "Free Cash Flow ($M)", "Direct Labor ($/hr)", "Burden Rate ($/hr)", "Cleanroom Class"];
  
  const rows = appState.filteredSuppliers.map(s => [
    `"${s.id || ''}"`,
    `"${s.name || ''}"`,
    `"${s.commodity || ''}"`,
    `"${s.region || ''}"`,
    `"${s.country || ''}"`,
    `"${s.city || ''}"`,
    s.establishedYear || '',
    s.employees || '',
    s.performance?.otdPct || '',
    s.performance?.prototypeLeadTimeDays || '',
    s.performance?.volumeLeadTimeWeeks || '',
    s.financials?.freeCashFlow || '',
    s.costStructure?.directLaborRate || '',
    s.costStructure?.burdenRate || '',
    `"${s.contaminationControl?.cleanroomClass || ''}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `CHIPCHAIN_Suppliers_${appState.selectedCommodity}_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast("CSV file exported successfully", "success");
}

// Toast Notification System
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";

  let icon = "fa-circle-info";
  if (type === "success") icon = "fa-circle-check";
  if (type === "warning") icon = "fa-triangle-exclamation";
  if (type === "error") icon = "fa-circle-xmark";

  toast.innerHTML = `<i class="fa-solid ${icon}" style="color: var(--primary);"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
