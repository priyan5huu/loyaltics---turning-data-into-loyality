/* ═══════════════════════════════════════════════════════════════
   ChurnIQ — script.js
   Covers: Loader, Nav, Form Submission, Charts, History Logs
   ═══════════════════════════════════════════════════════════════ */

'use strict';

let API_BASE = window.location.origin + '/api';
if (window.location.hostname.includes('vercel.app')) {
  API_BASE = 'https://loyaltics-api.onrender.com/api';
}

// Loader Simulation
(function initLoader() {
  const loader = document.getElementById('loader');
  const bar = document.getElementById('loaderBar');
  const status = document.getElementById('loaderStatus');
  if (!loader) return;

  const messages = [
    'Initializing ChurnIQ model pipeline...',
    'Loading Scaler parameters...',
    'Fetching baseline statistics...',
    'Calibrating analytics dashboard...',
    'Ready.'
  ];
  let progress = 0;
  let msgIdx = 0;

  const tick = () => {
    progress += Math.floor(Math.random() * 15) + 5;
    if (progress > 100) progress = 100;
    
    if (bar) bar.style.width = progress + '%';
    
    if (status && msgIdx < messages.length && progress >= (msgIdx + 1) * 20) {
      status.textContent = messages[msgIdx];
      msgIdx++;
    }

    if (progress < 100) {
      setTimeout(tick, 100);
    } else {
      setTimeout(() => {
        loader.classList.add('hidden');
      }, 300);
    }
  };
  setTimeout(tick, 100);
})();

// Mobile Menu Navigation
(function initNav() {
  const hamburger = document.getElementById('navHamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('open');
  });

  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('open');
      mobileMenu.classList.remove('open');
    });
  });
})();

// History State
let historyData = [];
let histPage = 1;
const HIST_PER_PAGE = 10;
let searchQuery = '';

function renderHistoryPage() {
  const tbody = document.getElementById('historyTableBody');
  const pageLabel = document.getElementById('pageNumberLabel');
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');
  if (!tbody) return;

  // Filter history data
  const filtered = historyData.filter(item => {
    if (!searchQuery) return true;
    const risk = (item.result?.risk_level || '').toLowerCase();
    const contract = (item.input?.contract || '').toLowerCase();
    return risk.includes(searchQuery) || contract.includes(searchQuery);
  });

  const totalPages = Math.ceil(filtered.length / HIST_PER_PAGE) || 1;
  if (histPage > totalPages) histPage = totalPages;
  if (histPage < 1) histPage = 1;

  const start = (histPage - 1) * HIST_PER_PAGE;
  const end = start + HIST_PER_PAGE;
  const slice = filtered.slice(start, end);

  if (slice.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--muted); padding: 24px;">No matching records found</td></tr>`;
  } else {
    tbody.innerHTML = slice.map(h => {
      const date = new Date(h.timestamp).toLocaleString();
      const risk = h.result?.risk_level || 'Low Risk';
      const prob = h.result?.probability || 0;
      const contract = h.input?.contract || 'Month-to-month';
      const charges = parseFloat(h.input?.monthly_charges || 0).toFixed(2);
      
      let riskClass = 'history-risk--low';
      if (risk === 'High Risk') riskClass = 'history-risk--high';
      else if (risk === 'Moderate Risk') riskClass = 'history-risk--moderate';

      let predBadge = h.result?.prediction === 'Churn' ? 'history-prediction--churn' : 'history-prediction--safe';
      
      return `
        <tr>
          <td>${date}</td>
          <td style="text-transform: capitalize;">${contract}</td>
          <td>$${charges}</td>
          <td class="history-risk ${riskClass}">${risk}</td>
          <td><span class="history-prediction ${predBadge}">${prob}%</span></td>
        </tr>
      `;
    }).join('');
  }

  if (pageLabel) pageLabel.textContent = `Page ${histPage} of ${totalPages}`;
  if (prevBtn) prevBtn.disabled = (histPage === 1);
  if (nextBtn) nextBtn.disabled = (histPage === totalPages);
}

// Fetch History Logs
async function fetchHistory() {
  try {
    const res = await fetch(`${API_BASE}/history`);
    if (res.ok) {
      historyData = await res.json();
      renderHistoryPage();
    }
  } catch (err) {
    console.error('Failed to fetch prediction history:', err);
  }
}

// Prediction Form Handler
(function initPrediction() {
  const form = document.getElementById('predictionForm');
  const submitBtn = document.getElementById('predictBtn');
  const idleState = document.getElementById('resultIdleState');
  const filledState = document.getElementById('resultFilled');
  const wrapper = document.getElementById('resultWrapper');
  if (!form || !submitBtn) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    // Map inputs to exact lowercase keys expected by backend preprocessing
    const payload = {
      gender: document.getElementById('gender').value,
      senior_citizen: parseInt(document.getElementById('senior_citizen').value),
      partner: parseInt(document.getElementById('partner').value),
      dependents: parseInt(document.getElementById('dependents').value),
      tenure: parseInt(document.getElementById('tenure').value),
      monthly_charges: parseFloat(document.getElementById('monthly_charges').value),
      paperless_billing: parseInt(document.getElementById('paperless_billing').value),
      phone_service: parseInt(document.getElementById('phone_service').value),
      
      // Select options
      contract: document.getElementById('contract').value === 'Month-to-month' ? 'monthly' :
                document.getElementById('contract').value === 'One year' ? 'one-year' : 'two-year',
                
      payment_method: document.getElementById('payment_method').value === 'Electronic check' ? 'electronic_check' :
                      document.getElementById('payment_method').value === 'Mailed check' ? 'mailed_check' :
                      document.getElementById('payment_method').value === 'Bank transfer (automatic)' ? 'bank_transfer' : 'credit_card',
                      
      internet_service: document.getElementById('internet_service').value === 'Fiber optic' ? 'fiber' :
                        document.getElementById('internet_service').value === 'DSL' ? 'dsl' : 'none',
      
      multiple_lines: document.getElementById('multiple_lines').value === 'Yes' ? 1 : 0,
      online_security: document.getElementById('online_security').value === 'Yes' ? 1 : 0,
      online_backup: document.getElementById('online_backup').value === 'Yes' ? 1 : 0,
      device_protection: document.getElementById('device_protection').value === 'Yes' ? 1 : 0,
      tech_support: document.getElementById('tech_support').value === 'Yes' ? 1 : 0,
      streaming_tv: document.getElementById('streaming_tv').value === 'Yes' ? 1 : 0,
      streaming_movies: document.getElementById('streaming_movies').value === 'Yes' ? 1 : 0
    };

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        
        // Hide idle state, show filled result
        if (idleState) idleState.style.display = 'none';
        if (filledState) filledState.style.display = 'block';

        // Populate verdict
        const badge = document.getElementById('verdictBadge');
        if (badge) {
          badge.textContent = data.prediction === 'Churn' ? 'At Risk' : 'Retained';
          badge.className = 'result-badge ' + (data.prediction === 'Churn' ? 'result-badge--churn' : 'result-badge--safe');
        }

        const probVal = document.getElementById('churnProbVal');
        if (probVal) probVal.textContent = `${data.probability}%`;

        // Update circular ring stroke-dashoffset (314 is circumference for radius 50)
        const ringFill = document.getElementById('riskRingFill');
        if (ringFill) {
          const pct = Math.min(Math.max(data.probability / 100, 0), 1);
          const offset = 314 - (314 * pct);
          ringFill.style.strokeDashoffset = offset;
          
          let color = '#22c55e'; // Green
          if (data.risk_level === 'High Risk') color = '#dc2626'; // Red
          else if (data.risk_level === 'Moderate Risk') color = '#d97706'; // Amber
          ringFill.style.setProperty('--ring-color', color);
        }

        const riskVal = document.getElementById('riskLevelVal');
        if (riskVal) {
          riskVal.textContent = data.risk_level;
          riskVal.className = 'result-risk-pill ' + 
            (data.risk_level === 'High Risk' ? 'high' : 
             data.risk_level === 'Moderate Risk' ? 'moderate' : 'low');
        }

        const meter = document.getElementById('riskMeterFill');
        const meterPct = document.getElementById('riskMeterPct');
        if (meterPct) meterPct.textContent = `${data.probability}%`;
        if (meter) {
          meter.style.width = `${data.probability}%`;
          meter.className = 'risk-meter-fill ' + 
            (data.risk_level === 'High Risk' ? 'risk-meter-fill--high' : 
             data.risk_level === 'Moderate Risk' ? 'risk-meter-fill--moderate' : 'risk-meter-fill--low');
        }

        // Render SHAP attribution bars
        const barsContainer = document.getElementById('xaiBarsContainer');
        if (barsContainer && data.xai?.impacts) {
          barsContainer.innerHTML = data.xai.impacts.map(impact => {
            const isNegative = impact.type === 'negative'; // negative matches retention force (safe/green)
            const typeClass = isNegative ? 'positive' : 'negative';
            const sign = isNegative ? '-' : '+';
            const scorePct = (impact.score * 100).toFixed(1);
            
            // Limit width for rendering nicely
            const widthPct = Math.min(Math.max(impact.score * 200, 10), 100);

            return `
              <div class="xai-bar-item">
                <div class="xai-bar-label">
                  <span>${impact.feature.replace(/_/g, ' ')}</span>
                  <span class="xai-bar-val ${typeClass}">${sign}${scorePct}%</span>
                </div>
                <div class="xai-bar-track">
                  <div class="xai-bar-fill ${typeClass}" style="width: ${widthPct}%"></div>
                </div>
              </div>
            `;
          }).join('');
        }

        // Render recommendations
        const recsList = document.getElementById('recsList');
        if (recsList && data.recommendations) {
          recsList.innerHTML = data.recommendations.map(rec => `
            <div class="rec-item">${rec}</div>
          `).join('');
        }

        // Refresh History
        await fetchHistory();
        
        // Smooth scroll to the result wrapper container on ALL screen sizes
        if (wrapper) {
          wrapper.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    } catch (err) {
      console.error('Inference error:', err);
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  });
})();

// Dashboard Analytics Charts
async function initDashboard() {
  const chartEl = document.getElementById('chartChurnDist');
  if (!chartEl) return;

  try {
    const res = await fetch(`${API_BASE}/analytics`);
    if (!res.ok) return;
    const data = await res.json();

    // Global Font Settings for light beige contrast
    Chart.defaults.color = '#1F1F1F';
    Chart.defaults.font.family = '"Inter", sans-serif';
    Chart.defaults.font.size = 11;
    const gridColor = 'rgba(26, 26, 26, 0.08)';

    // Upgraded Premium Theme Palette
    const palette = {
      churnRed: '#FF4757',       // Vibrant coral red
      retainedGreen: '#2ED573',  // Cool, vivid emerald green
      
      // Contract Types
      monthToMonth: '#57606F',  // Sleek charcoal
      oneYear: '#FFA502',       // Golden amber
      twoYear: '#1E90FF',       // Dodger blue
      
      // Internet Service Types
      fiberOptic: '#70A1FF',    // Light steel blue
      dsl: '#FF7F50',           // Warm coral orange
      noInternet: '#A4B0BE',    // Soft warm gray
      
      // Primary accent colors
      indigo: '#6C5CE7',        // Rich violet/indigo
      teal: '#00CEC9',          // Bright turquoise/teal
      orange: '#E17055'         // Sunset orange
    };

    // 1. Churn Distribution (Doughnut)
    new Chart(document.getElementById('chartChurnDist'), {
      type: 'doughnut',
      data: {
        labels: Object.keys(data.churn_distribution),
        datasets: [{
          data: Object.values(data.churn_distribution),
          backgroundColor: [palette.churnRed, palette.retainedGreen],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        cutout: '70%',
        plugins: { legend: { position: 'bottom' } }
      }
    });

    // 2. Contract Type (Pie)
    new Chart(document.getElementById('chartContract'), {
      type: 'pie',
      data: {
        labels: Object.keys(data.contract_distribution),
        datasets: [{
          data: Object.values(data.contract_distribution),
          backgroundColor: [palette.monthToMonth, palette.twoYear, palette.oneYear],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        plugins: { legend: { position: 'bottom' } }
      }
    });

    // 3. Monthly Charges (Bar)
    const chargesCtx = document.getElementById('chartCharges').getContext('2d');
    const chargesGrad = chargesCtx.createLinearGradient(0, 0, 0, 200);
    chargesGrad.addColorStop(0, '#6C5CE7');
    chargesGrad.addColorStop(1, 'rgba(108, 92, 231, 0.1)');

    new Chart(document.getElementById('chartCharges'), {
      type: 'bar',
      data: {
        labels: Object.keys(data.monthly_charges_distribution),
        datasets: [{
          label: 'Subscribers',
          data: Object.values(data.monthly_charges_distribution),
          backgroundColor: chargesGrad,
          borderRadius: 4
        }]
      },
      options: {
        scales: {
          y: { grid: { color: gridColor } },
          x: { grid: { display: false } }
        },
        plugins: { legend: { display: false } }
      }
    });

    // 4. Tenure (Bar)
    const tenureCtx = document.getElementById('chartTenure').getContext('2d');
    const tenureGrad = tenureCtx.createLinearGradient(0, 0, 0, 200);
    tenureGrad.addColorStop(0, '#00CEC9');
    tenureGrad.addColorStop(1, 'rgba(0, 206, 201, 0.1)');

    new Chart(document.getElementById('chartTenure'), {
      type: 'bar',
      data: {
        labels: Object.keys(data.tenure_distribution),
        datasets: [{
          label: 'Subscribers',
          data: Object.values(data.tenure_distribution),
          backgroundColor: tenureGrad,
          borderRadius: 4
        }]
      },
      options: {
        scales: {
          y: { grid: { color: gridColor } },
          x: { grid: { display: false } }
        },
        plugins: { legend: { display: false } }
      }
    });

    // 5. Internet Service (Doughnut)
    new Chart(document.getElementById('chartInternet'), {
      type: 'doughnut',
      data: {
        labels: Object.keys(data.internet_service_distribution),
        datasets: [{
          data: Object.values(data.internet_service_distribution),
          backgroundColor: [palette.fiberOptic, palette.dsl, palette.noInternet],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        cutout: '70%',
        plugins: { legend: { position: 'bottom' } }
      }
    });

    // 6. Model Performance (Radar)
    const m = data.model_performance;
    new Chart(document.getElementById('chartModelPerf'), {
      type: 'radar',
      data: {
        labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC'],
        datasets: [{
          label: m.model_name || 'Ensemble Model',
          data: [m.accuracy, m.precision, m.recall, m.f1_score, m.roc_auc],
          backgroundColor: 'rgba(108, 92, 231, 0.15)',
          borderColor: '#6C5CE7',
          borderWidth: 2,
          pointBackgroundColor: '#00CEC9'
        }]
      },
      options: {
        scales: {
          r: {
            angleLines: { color: gridColor },
            grid: { color: gridColor },
            ticks: { display: false }
          }
        },
        plugins: { legend: { position: 'bottom' } }
      }
    });

    // 7. Feature Importance (Horizontal Bar)
    const fi = data.feature_importance;
    const fiCtx = document.getElementById('chartFeatureImp').getContext('2d');
    const fiGrad = fiCtx.createLinearGradient(0, 0, 400, 0);
    fiGrad.addColorStop(0, 'rgba(225, 112, 85, 0.2)');
    fiGrad.addColorStop(1, '#E17055');

    new Chart(document.getElementById('chartFeatureImp'), {
      type: 'bar',
      indexAxis: 'y',
      data: {
        labels: fi.map(f => f.feature.replace(/_/g, ' ')),
        datasets: [{
          label: 'Importance Weight',
          data: fi.map(f => f.importance),
          backgroundColor: fiGrad,
          borderRadius: 4
        }]
      },
      options: {
        scales: {
          x: { grid: { color: gridColor } },
          y: { grid: { display: false } }
        },
        plugins: { legend: { display: false } }
      }
    });

    // 8. Recent Predictions Trend (Line)
    const pt = [...data.prediction_trend].reverse();
    if (pt.length > 0) {
      const ptCtx = document.getElementById('chartPredTrend').getContext('2d');
      const ptGrad = ptCtx.createLinearGradient(0, 0, 0, 150);
      ptGrad.addColorStop(0, 'rgba(255, 71, 87, 0.4)');
      ptGrad.addColorStop(1, 'rgba(255, 71, 87, 0.01)');

      new Chart(document.getElementById('chartPredTrend'), {
        type: 'line',
        data: {
          labels: pt.map(p => new Date(p.timestamp).toLocaleTimeString()),
          datasets: [{
            label: 'Risk %',
            data: pt.map(p => p.probability),
            borderColor: palette.churnRed,
            backgroundColor: ptGrad,
            fill: true,
            tension: 0.3,
            borderWidth: 2
          }]
        },
        options: {
          scales: {
            y: { min: 0, max: 100, grid: { color: gridColor } },
            x: { grid: { display: false } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

    // 9. Tenure vs No of Customers (Loyal vs Churned)
    if (data.tenure_vs_churn) {
      new Chart(document.getElementById('chartTenureVsChurn'), {
        type: 'bar',
        data: {
          labels: data.tenure_vs_churn.labels,
          datasets: [
            {
              label: 'Loyal',
              data: data.tenure_vs_churn.loyal,
              backgroundColor: palette.retainedGreen,
              borderRadius: 4
            },
            {
              label: 'Churned',
              data: data.tenure_vs_churn.churned,
              backgroundColor: palette.churnRed,
              borderRadius: 4
            }
          ]
        },
        options: {
          scales: {
            y: { 
              grid: { color: gridColor },
              title: { display: true, text: 'No of customers', color: '#1F1F1F' }
            },
            x: { 
              grid: { display: false },
              title: { display: true, text: 'Tenure (months)', color: '#1F1F1F' }
            }
          },
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }
  } catch (err) {
    console.error('Failed to init dashboard charts:', err);
  }
}

// Setup Page Listeners
document.addEventListener('DOMContentLoaded', () => {
  fetchHistory();
  initDashboard();

  // Search logic
  const searchInput = document.getElementById('historySearch');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      histPage = 1;
      renderHistoryPage();
    });
  }

  // Pagination logic
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (histPage > 1) {
        histPage--;
        renderHistoryPage();
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      histPage++;
      renderHistoryPage();
    });
  }
});
