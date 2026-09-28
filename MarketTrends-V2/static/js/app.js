function renderMarkdownLinks(text) {
  if (!text) return '';
  return text.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="trend-source-link">$1 🔗</a>');
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('market-form');
  const industryInput = document.getElementById('industry');
  const segmentInput = document.getElementById('market_segment');
  const analyzeBtn = document.getElementById('btn-analyze');
  const resetBtn = document.getElementById('btn-reset');
  const exportBtn = document.getElementById('btn-export');
  
  const placeholderState = document.getElementById('placeholder-state');
  const approvalSection = document.getElementById('approval-section');
  const approvalSubtitle = document.getElementById('approval-subtitle');
  const approvalCompetitorList = document.getElementById('approval-competitor-list');
  const tickerFormBox = document.getElementById('ticker-form-box');
  const tickerInput = document.getElementById('ticker-input');
  const fetchTickerBtn = document.getElementById('btn-fetch-ticker');
  const tickerStatusMsg = document.getElementById('ticker-status-msg');
  const approveCompetitorsBtn = document.getElementById('btn-approve-competitors');
  const disapproveCompetitorsBtn = document.getElementById('btn-disapprove-competitors');

  const presentationSection = document.getElementById('presentation-section');
  const slideCardsContainer = document.getElementById('slide-cards-container');
  const currentSlideSpan = document.getElementById('current-slide-num');
  const totalSlidesSpan = document.getElementById('total-slides-num');
  const prevBtn = document.getElementById('prev-slide');
  const nextBtn = document.getElementById('next-slide');
  const deckTitleMeta = document.getElementById('deck-title-meta');

  let currentSlideIndex = 0;
  let slidesData = [];
  let currentResolvedCompetitors = [];
  let activeIndustry = '';
  let activeSegment = '';

  // Quick Chips
  document.querySelectorAll('.tag-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const ind = chip.dataset.industry;
      const seg = chip.dataset.segment;
      if (ind && seg) {
        industryInput.value = ind;
        segmentInput.value = seg;
        fetchInitialCompetitors();
      }
    });
  });

  // Form submit -> Step 1: Fetch Competitors for Approval
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    fetchInitialCompetitors();
  });

  async function fetchInitialCompetitors() {
    activeIndustry = industryInput.value.trim();
    activeSegment = segmentInput.value.trim();

    if (!activeIndustry || !activeSegment) {
      alert("Please provide both Industry and Market Segment inputs.");
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span>Resolving Competitors...</span>`;

    try {
      const resp = await fetch('/api/get-competitors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry: activeIndustry, market_segment: activeSegment })
      });

      const res = await resp.json();
      if (res.status === 'success') {
        currentResolvedCompetitors = res.competitors;
        renderCompetitorApproval(res.industry, res.market_segment, currentResolvedCompetitors);
      } else {
        alert(res.message || "Failed to resolve competitors.");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred while resolving top competitors.");
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = `<span>Generate 5-Slide Deck</span>`;
    }
  }

  function renderCompetitorApproval(industry, segment, competitors) {
    placeholderState.style.display = 'none';
    presentationSection.classList.remove('active');
    tickerFormBox.style.display = 'none';
    tickerStatusMsg.innerHTML = '';
    tickerStatusMsg.className = 'ticker-status';

    approvalSubtitle.innerHTML = `Resolved Top 5 Market-Cap Leaders for <strong>${segment}</strong> (${industry}):`;
    
    approvalCompetitorList.innerHTML = competitors.map((comp, idx) => `
      <div class="approval-comp-card">
        <div class="approval-comp-rank">Rank #${idx + 1}</div>
        <div class="approval-comp-name">${comp.name}</div>
        <div class="approval-comp-share">${comp.share} Est. Share</div>
        <div class="approval-comp-offering">${comp.key_offering}</div>
        ${comp.top_products && comp.top_products.length > 0 ? `
          <div style="margin-top: 0.4rem; padding-top: 0.4rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 0.7rem; font-weight: 700; color: #93c5fd; margin-bottom: 0.2rem; text-transform: uppercase;">📦 Key Products:</div>
            <div style="font-size: 0.78rem; color: #d1d5db; line-height: 1.3;">${comp.top_products.slice(0, 3).join(" • ")}</div>
          </div>
        ` : ''}
      </div>
    `).join('');

    approvalSection.style.display = 'block';
  }

  // Handle "No / Enter Stock Symbol" button click
  disapproveCompetitorsBtn.addEventListener('click', () => {
    tickerFormBox.style.display = tickerFormBox.style.display === 'none' ? 'block' : 'none';
    if (tickerFormBox.style.display === 'block') {
      tickerInput.focus();
    }
  });

  // Handle Finviz Ticker Lookup
  fetchTickerBtn.addEventListener('click', () => {
    lookupTickerViaFinviz();
  });

  tickerInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      lookupTickerViaFinviz();
    }
  });

  async function lookupTickerViaFinviz() {
    const symbol = tickerInput.value.trim();
    if (!symbol) {
      alert("Please enter a stock ticker symbol (e.g., TSLA, LLY).");
      return;
    }

    fetchTickerBtn.disabled = true;
    fetchTickerBtn.innerHTML = `<span>Querying Finviz...</span>`;
    tickerStatusMsg.innerHTML = `Querying finviz.com for ${symbol.toUpperCase()} sector & industry...`;
    tickerStatusMsg.className = 'ticker-status';

    try {
      const resp = await fetch('/api/lookup-ticker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: symbol })
      });

      const res = await resp.json();
      if (res.status === 'success' && res.competitors && res.competitors.length > 0) {
        currentResolvedCompetitors = res.competitors;
        activeIndustry = res.sector;
        activeSegment = res.industry;
        
        industryInput.value = res.sector;
        segmentInput.value = res.industry;

        tickerStatusMsg.innerHTML = `✓ Mapped ticker <strong>${res.ticker}</strong> to Sector: <strong>${res.sector}</strong> | Industry: <strong>${res.industry}</strong>`;
        tickerStatusMsg.className = 'ticker-status success';

        renderCompetitorApproval(res.sector, res.industry, currentResolvedCompetitors);
        tickerFormBox.style.display = 'block';
      } else {
        tickerStatusMsg.innerHTML = `⚠ Unable to map ticker ${symbol.toUpperCase()} via Finviz. Showing fallback competitors.`;
        tickerStatusMsg.className = 'ticker-status error';
      }
    } catch (err) {
      console.error(err);
      tickerStatusMsg.innerHTML = `⚠ Error connecting to Finviz service.`;
      tickerStatusMsg.className = 'ticker-status error';
    } finally {
      fetchTickerBtn.disabled = false;
      fetchTickerBtn.innerHTML = `<span>Map & Fetch via Finviz</span>`;
    }
  }

  // Handle Approve Competitors -> Trigger Full Market Analysis
  approveCompetitorsBtn.addEventListener('click', () => {
    triggerFullMarketAnalysis();
  });

  async function triggerFullMarketAnalysis() {
    if (!currentResolvedCompetitors || currentResolvedCompetitors.length === 0) {
      alert("No approved competitor list found.");
      return;
    }

    approveCompetitorsBtn.disabled = true;
    approveCompetitorsBtn.innerHTML = `<span>Running Study...</span>`;

    try {
      const resp = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          industry: activeIndustry,
          market_segment: activeSegment,
          approved_competitors: currentResolvedCompetitors
        })
      });

      const res = await resp.json();
      if (res.status === 'success') {
        slidesData = res.slides;
        approvalSection.style.display = 'none';
        renderPresentation(res.industry, res.segment, slidesData);
      } else {
        alert(res.message || "Failed to generate market analysis study.");
      }
    } catch (err) {
      console.error(err);
      alert("An error occurred while generating full analysis study.");
    } finally {
      approveCompetitorsBtn.disabled = false;
      approveCompetitorsBtn.innerHTML = `
        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <span>Approve & Continue Study</span>
      `;
    }
  }

  function renderPresentation(industry, segment, slides) {
    deckTitleMeta.textContent = `${segment} (${industry})`;
    totalSlidesSpan.textContent = slides.length;
    currentSlideIndex = 0;

    slideCardsContainer.innerHTML = '';

    slides.forEach((slide, idx) => {
      const card = document.createElement('div');
      card.className = `slide-card ${idx === 0 ? 'active' : ''}`;
      card.dataset.index = idx;

      let contentHTML = '';

      if (slide.type === 'summary') {
        contentHTML = `
          <div class="summary-grid">
            <div class="stat-box">
              <div class="stat-lbl">Market Size (Last Year)</div>
              <div class="stat-val">${slide.data.market_size_last_year}</div>
              <div class="stat-lbl" style="color: var(--accent-cyan);">YoY Growth: ${slide.data.yoy_growth_rate}</div>
            </div>
            <div class="summary-text-box">
              <h4 style="color: #93c5fd; font-size: 1rem; font-weight: 600;">Executive Strategic Overview</h4>
              <p class="summary-paragraph">${slide.data.executive_takeaway}</p>
            </div>
          </div>
        `;
      } else if (slide.type === 'trends') {
        if (slide.data.structured_trends) {
          const st = slide.data.structured_trends;
          const order = [
            'trends',
            'market_size_growth',
            'spending_patterns',
            'shifts_changes',
            'tech_consumer_behavior',
            'retail_competitive_landscape',
            'challenges',
            'bottom_line'
          ];
          contentHTML = `
            <div class="structured-trends-grid">
              ${order.map(key => {
                const sec = st[key];
                if (!sec) return '';
                return `
                  <div class="trend-section-card">
                    <div class="trend-card-header">
                      <span class="trend-card-icon">${sec.icon}</span>
                      <span class="trend-card-title">${sec.title}</span>
                    </div>
                    <div class="trend-card-body">
                      ${renderMarkdownLinks(sec.text)}
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          `;
        } else {
          const choiceDrivers = slide.data.customer_choice_drivers || slide.data.customer_preferences || [];
          contentHTML = `
            <div class="two-col-grid">
              <div class="info-card">
                <div class="info-card-header">🚀 Key Market Trends</div>
                <ul class="bullet-list">
                  ${slide.data.trends.map(t => `<li>${renderMarkdownLinks(t)}</li>`).join('')}
                </ul>
              </div>
              <div class="info-card">
                <div class="info-card-header">💡 What Makes a Customer Choose the Product</div>
                <ul class="bullet-list">
                  ${choiceDrivers.map(cp => `<li>${renderMarkdownLinks(cp)}</li>`).join('')}
                </ul>
              </div>
            </div>
          `;
        }
      } else if (slide.type === 'competitors') {
        contentHTML = `
          <div class="info-card" style="margin-bottom: 1rem; border-left: 4px solid var(--accent-blue); background: rgba(56, 189, 248, 0.08);">
            <div class="info-card-header" style="color: #38bdf8;">🏆 Leading Product & Key Differentiator</div>
            <p style="font-size: 0.98rem; color: #f3f4f6; font-weight: 500; margin: 0;">${slide.data.leading_product_summary || `Leading Product Highlight: ${slide.data.market_share_providers[0].name} commands the market lead, differentiated by its ${slide.data.market_share_providers[0].key_offering}.`}</p>
          </div>
          <div class="provider-cards">
            ${slide.data.market_share_providers.map((p, pIdx) => `
              <div class="provider-card">
                <div class="provider-rank">Rank #${pIdx + 1}</div>
                <div class="provider-name">${p.name}</div>
                <div class="provider-share-text">${p.share} Share</div>
                <div class="provider-share-bar">
                  <div class="share-fill" style="width: ${p.share};"></div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.75rem; font-weight: 700; color: #a7f3d0; text-transform: uppercase; letter-spacing: 0.05em;">💡 Differentiating Value Proposition</div>
                <div class="provider-desc" style="margin-top: 0.2rem; font-weight: 500;">${p.key_offering}</div>
                ${p.top_products && p.top_products.length > 0 ? `
                  <div class="top-products-box" style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #93c5fd; margin-bottom: 0.35rem; text-transform: uppercase; letter-spacing: 0.05em;">📦 Top 3 Key Products</div>
                    <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.25rem;">
                      ${p.top_products.slice(0, 3).map(prod => `
                        <li style="font-size: 0.8rem; color: #e5e7eb; display: flex; align-items: flex-start; gap: 0.35rem;">
                          <span style="color: #38bdf8; font-size: 0.7rem; margin-top: 0.15rem;">🔹</span>
                          <span>${prod}</span>
                        </li>
                      `).join('')}
                    </ul>
                  </div>
                ` : ''}
              </div>
            `).join('')}
          </div>
          <div class="info-card">
            <div class="info-card-header">📊 Market Share Dynamics</div>
            <p style="font-size: 0.95rem; color: #d1d5db;">${slide.data.market_dynamics}</p>
          </div>
        `;
      } else if (slide.type === 'product_features') {
        const criteria = slide.data.matrix_criteria || [
          "Product Innovation & Tech Stack",
          "Market Reach & Brand Loyalty",
          "Cost Efficiency & Pricing Power",
          "Ecosystem Integration & Scale Moat"
        ];
        const matrix = slide.data.ratings_matrix || [];

        contentHTML = `
          <div class="two-col-grid" style="margin-bottom: 1.5rem;">
            <div class="info-card">
              <div class="info-card-header">⚡ Exciting Product Characteristics</div>
              <ul class="bullet-list">
                ${slide.data.exciting_characteristics.map(ec => `<li>${ec}</li>`).join('')}
              </ul>
            </div>
            <div class="info-card">
              <div class="info-card-header">🛡️ Key Differentiating Pillars</div>
              <ul class="bullet-list">
                ${slide.data.differentiating_characteristics.map(dc => `<li>${dc}</li>`).join('')}
              </ul>
            </div>
          </div>

          ${matrix.length > 0 ? `
            <div class="info-card" style="border-top: 3px solid var(--accent-cyan);">
              <div class="info-card-header" style="justify-content: space-between;">
                <span>📊 Competitor Differentiating Capability Ratings (1-5 Scale)</span>
                <span style="font-size: 0.75rem; font-weight: 500; color: #9ca3af;">5 = Market Leader | 1 = Basic Capability</span>
              </div>
              <div style="overflow-x: auto; margin-top: 0.75rem;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
                  <thead>
                    <tr style="border-bottom: 2px solid rgba(255, 255, 255, 0.12); background: rgba(15, 23, 42, 0.6);">
                      <th style="padding: 0.75rem 0.5rem; color: #38bdf8; font-weight: 700;">Competitor</th>
                      ${criteria.map(c => `<th style="padding: 0.75rem 0.5rem; color: #93c5fd; font-weight: 600; text-align: center;">${c}</th>`).join('')}
                      <th style="padding: 0.75rem 0.5rem; color: #a7f3d0; font-weight: 700; text-align: center;">Overall Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${matrix.map((r, rIdx) => `
                      <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.06); ${rIdx % 2 === 1 ? 'background: rgba(255, 255, 255, 0.02);' : ''}">
                        <td style="padding: 0.75rem 0.5rem; font-weight: 600; color: #f3f4f6;">
                          ${r.competitor} <span style="font-size: 0.75rem; color: #9ca3af; font-weight: 400;">(${r.share})</span>
                        </td>
                        ${r.scores.map(score => `
                          <td style="padding: 0.75rem 0.5rem; text-align: center;">
                            <span style="
                              display: inline-block;
                              padding: 0.2rem 0.65rem;
                              border-radius: 6px;
                              font-weight: 700;
                              font-size: 0.82rem;
                              background: ${score === 5 ? 'rgba(34, 197, 94, 0.2)' : score === 4 ? 'rgba(56, 189, 248, 0.2)' : 'rgba(234, 179, 8, 0.2)'};
                              color: ${score === 5 ? '#4ade80' : score === 4 ? '#38bdf8' : '#facc15'};
                              border: 1px solid ${score === 5 ? 'rgba(34, 197, 94, 0.4)' : score === 4 ? 'rgba(56, 189, 248, 0.4)' : 'rgba(234, 179, 8, 0.4)'};
                            ">
                              ${score} / 5
                            </span>
                          </td>
                        `).join('')}
                        <td style="padding: 0.75rem 0.5rem; text-align: center; font-weight: 800; color: #34d399; font-size: 0.95rem;">
                          ⭐ ${r.overall_score}
                        </td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            </div>
          ` : ''}
        `;
      } else if (slide.type === 'compliance') {
        contentHTML = `
          <div class="three-col-grid">
            <div class="info-card">
              <div class="info-card-header">🏛️ Government Specs</div>
              <ul class="bullet-list">
                ${slide.data.government_regulations.map(gr => `<li>${gr}</li>`).join('')}
              </ul>
            </div>
            <div class="info-card">
              <div class="info-card-header">📜 Industry Standards</div>
              <ul class="bullet-list">
                ${slide.data.industry_standards.map(is => `<li>${is}</li>`).join('')}
              </ul>
            </div>
            <div class="info-card">
              <div class="info-card-header">🎯 Segment Specs</div>
              <ul class="bullet-list">
                ${slide.data.segment_specs.map(ss => `<li>${ss}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      } else if (slide.type === 'product_specs') {
        contentHTML = `
          <div class="two-col-grid">
            <div class="info-card" style="border-top: 4px solid var(--accent-amber);">
              <div class="info-card-header" style="color: #f59e0b;">📦 Minimum Viable Product (MVP) Specifications</div>
              <ul class="bullet-list">
                ${slide.data.mvp_specifications.map(ms => `<li>${ms}</li>`).join('')}
              </ul>
            </div>
            <div class="info-card" style="border-top: 4px solid var(--accent-cyan);">
              <div class="info-card-header" style="color: #38bdf8;">🏆 Winning Product Specifications</div>
              <ul class="bullet-list">
                ${slide.data.winning_specifications.map(ws => `<li>${ws}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      }

      const sourcesHTML = slide.sources && slide.sources.length > 0 ? `
        <div class="slide-sources-footer" style="margin-top: 1.25rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.78rem; color: #9ca3af; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
          <div style="font-weight: 600; color: #93c5fd; display: flex; align-items: center; gap: 0.35rem;">
            <span>🔗 Information Sources & Citations:</span>
          </div>
          <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
            ${slide.sources.map(src => `
              <a href="${src.url}" target="_blank" rel="noopener noreferrer" style="color: #38bdf8; text-decoration: none; display: inline-flex; align-items: center; gap: 0.25rem; background: rgba(56, 189, 248, 0.08); padding: 0.2rem 0.6rem; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.2); transition: all 0.2s ease;" onmouseover="this.style.borderColor='#38bdf8'" onmouseout="this.style.borderColor='rgba(56, 189, 248, 0.2)'">
                <span>${src.label}</span>
                <span style="font-size: 0.65rem;">↗</span>
              </a>
            `).join('')}
          </div>
        </div>
      ` : '';

      card.innerHTML = `
        <div class="slide-header">
          <div class="slide-title-wrap">
            <div class="slide-title">${slide.title}</div>
            <div class="slide-subtitle">${slide.subtitle}</div>
          </div>
          <div class="slide-num-badge">Page ${slide.slide_number} of ${slides.length}</div>
        </div>
        ${contentHTML}
        ${sourcesHTML}
      `;

      slideCardsContainer.appendChild(card);
    });

    placeholderState.style.display = 'none';
    presentationSection.classList.add('active');
    
    // Initialize slide approval statuses
    slideApprovals = new Array(slides.length).fill(false);
    updateCarouselState();
  }

  let slideApprovals = [];

  const slideApprovalTitle = document.getElementById('slide-approval-title');
  const slideApprovalSubtitle = document.getElementById('slide-approval-subtitle');
  const slideApprovalIcon = document.getElementById('slide-approval-icon');
  const btnApproveSlide = document.getElementById('btn-approve-slide');
  const btnReviseSlide = document.getElementById('btn-revise-slide');

  function updateCarouselState() {
    const cards = document.querySelectorAll('.slide-card');
    cards.forEach((card, idx) => {
      card.classList.toggle('active', idx === currentSlideIndex);
    });

    currentSlideSpan.textContent = currentSlideIndex + 1;
    prevBtn.disabled = currentSlideIndex === 0;
    nextBtn.disabled = currentSlideIndex === slidesData.length - 1;

    // Update Slide Approval Gateway UI
    const isApproved = slideApprovals[currentSlideIndex];
    if (isApproved) {
      slideApprovalIcon.textContent = '✅';
      slideApprovalTitle.innerHTML = `<span style="color: #4ade80;">Slide ${currentSlideIndex + 1} Approved</span> (${activeSegment})`;
      slideApprovalSubtitle.textContent = `You have approved the content for Page ${currentSlideIndex + 1}. Click next to continue review.`;
      btnApproveSlide.innerHTML = `<span>✓ Approved</span>`;
      btnApproveSlide.style.background = 'rgba(34, 197, 94, 0.25)';
      btnApproveSlide.style.border = '1px solid #4ade80';
    } else {
      slideApprovalIcon.textContent = '❓';
      slideApprovalTitle.innerHTML = `Slide ${currentSlideIndex + 1} Review Gateway (${activeSegment})`;
      slideApprovalSubtitle.textContent = `Do you approve the detailed ${activeSegment} analysis for Slide ${currentSlideIndex + 1}?`;
      btnApproveSlide.innerHTML = `<span>✓ Approve Slide & Next</span>`;
      btnApproveSlide.style.background = 'linear-gradient(135deg, #10b981, #059669)';
      btnApproveSlide.style.border = 'none';
    }
  }

  btnApproveSlide.addEventListener('click', () => {
    slideApprovals[currentSlideIndex] = true;
    updateCarouselState();

    if (currentSlideIndex < slidesData.length - 1) {
      currentSlideIndex++;
      updateCarouselState();
    } else {
      alert(`🎉 Excellent! You have reviewed and approved all ${slidesData.length} slides for ${activeSegment} (${activeIndustry}). The presentation deck is complete!`);
    }
  });

  btnReviseSlide.addEventListener('click', () => {
    slideApprovals[currentSlideIndex] = false;
    updateCarouselState();
    alert(`Slide ${currentSlideIndex + 1} flagged for review. You can adjust the competitor selection or re-run analysis.`);
  });

  prevBtn.addEventListener('click', () => {
    if (currentSlideIndex > 0) {
      currentSlideIndex--;
      updateCarouselState();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentSlideIndex < slidesData.length - 1) {
      currentSlideIndex++;
      updateCarouselState();
    }
  });

  // Export PDF functionality
  exportBtn.addEventListener('click', () => {
    exportDeckToPDF();
  });

  function exportDeckToPDF() {
    if (!slidesData || slidesData.length === 0) {
      alert("No slides to export.");
      return;
    }

    const element = document.createElement('div');
    element.style.padding = '20px';
    element.style.fontFamily = 'Arial, sans-serif';
    element.style.color = '#111827';
    element.style.background = '#ffffff';

    let html = `<h1 style="color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px;">Market Trends Specification Deck - ${deckTitleMeta.textContent}</h1>`;

    slidesData.forEach(slide => {
      html += `
        <div style="page-break-after: always; margin-bottom: 30px; padding: 20px; border: 1px solid #cbd5e1; border-radius: 8px;">
          <h2 style="color: #2563eb; margin-top: 0;">Page ${slide.slide_number}: ${slide.title}</h2>
          <p style="color: #64748b; font-style: italic;">${slide.subtitle}</p>
          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">
      `;

      if (slide.type === 'summary') {
        html += `
          <p><strong>Market Size (Last Year):</strong> ${slide.data.market_size_last_year} (YoY Growth: ${slide.data.yoy_growth_rate})</p>
          <p><strong>Executive Takeaway:</strong> ${slide.data.executive_takeaway}</p>
        `;
      } else if (slide.type === 'trends') {
        if (slide.data.structured_trends) {
          const st = slide.data.structured_trends;
          const keys = ['trends', 'market_size_growth', 'spending_patterns', 'shifts_changes', 'tech_consumer_behavior', 'retail_competitive_landscape', 'challenges', 'bottom_line'];
          html += `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;">`;
          keys.forEach(k => {
            const sec = st[k];
            if (sec) {
              html += `
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px;">
                  <h4 style="margin: 0 0 4px 0; color: #1e40af; font-size: 0.95rem;">${sec.icon} ${sec.title}</h4>
                  <p style="margin: 0; font-size: 0.85rem; color: #334155; line-height: 1.4;">${renderMarkdownLinks(sec.text)}</p>
                </div>
              `;
            }
          });
          html += `</div>`;
        } else {
          const choiceDrivers = slide.data.customer_choice_drivers || slide.data.customer_preferences || [];
          html += `
            <h3>Market Trends</h3>
            <ul>${slide.data.trends.map(t => `<li>${renderMarkdownLinks(t)}</li>`).join('')}</ul>
            <h3>Customer Preferences</h3>
            <ul>${choiceDrivers.map(cp => `<li>${renderMarkdownLinks(cp)}</li>`).join('')}</ul>
          `;
        }
      } else if (slide.type === 'competitors') {
        html += `
          <h3>Top Providers & Market Share</h3>
          <ul>${slide.data.market_share_providers.map(p => `<li><strong>${p.name}:</strong> ${p.share} - ${p.key_offering}</li>`).join('')}</ul>
          <p><strong>Market Share Dynamics:</strong> ${slide.data.market_dynamics}</p>
        `;
      } else if (slide.type === 'product_features') {
        html += `
          <h3>Exciting Characteristics</h3>
          <ul>${slide.data.exciting_characteristics.map(ec => `<li>${ec}</li>`).join('')}</ul>
          <h3>Differentiating Characteristics</h3>
          <ul>${slide.data.differentiating_characteristics.map(dc => `<li>${dc}</li>`).join('')}</ul>
        `;
      } else if (slide.type === 'compliance') {
        html += `
          <h3>Government Regulations</h3>
          <ul>${slide.data.government_regulations.map(gr => `<li>${gr}</li>`).join('')}</ul>
          <h3>Industry Standards</h3>
          <ul>${slide.data.industry_standards.map(is => `<li>${is}</li>`).join('')}</ul>
          <h3>Segment Specifications</h3>
          <ul>${slide.data.segment_specs.map(ss => `<li>${ss}</li>`).join('')}</ul>
        `;
      }

      html += `</div>`;
    });

    element.innerHTML = html;

    const opt = {
      margin:       0.5,
      filename:     `Market_Trends_${industryInput.value}_${segmentInput.value}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2 },
      jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
    };

    if (window.html2pdf) {
      window.html2pdf().set(opt).from(element).save();
    } else {
      window.print();
    }
  }

  // Reset Button logic (Captures PDF, clears cache, resets screen and presentation materials)
  resetBtn.addEventListener('click', async () => {
    if (confirm("Reset will capture current slides to PDF, clear application cache, and reset the screen. Proceed?")) {
      // 1. Capture output slides PDF if slides exist
      if (slidesData && slidesData.length > 0) {
        exportDeckToPDF();
      }

      // 2. Clear backend cache
      try {
        await fetch('/api/reset', {
          method: 'POST',
          headers: { 'Cache-Control': 'no-cache' }
        });
      } catch (e) {
        console.error("Cache reset request failed", e);
      }

      // 3. Clear ALL input fields & ticker lookup materials
      industryInput.value = '';
      segmentInput.value = '';
      tickerInput.value = '';
      tickerStatusMsg.innerHTML = '';
      tickerStatusMsg.className = 'ticker-status';
      tickerFormBox.style.display = 'none';

      // 4. Purge presentation deck and competitor approval DOM contents
      approvalCompetitorList.innerHTML = '';
      slideCardsContainer.innerHTML = '';
      deckTitleMeta.textContent = '-';
      currentSlideSpan.textContent = '1';
      totalSlidesSpan.textContent = '5';

      // 5. Reset memory & state variables
      slidesData = [];
      currentResolvedCompetitors = [];
      activeIndustry = '';
      activeSegment = '';
      currentSlideIndex = 0;

      // 6. Reset UI section views
      approvalSection.style.display = 'none';
      presentationSection.classList.remove('active');
      placeholderState.style.display = 'block';
    }
  });
});

