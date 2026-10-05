/**
 * SONAR // Main Application Controller
 * Manages dataset state, reactive filtering, pagination, exports, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Data Initialization (with serverless & web-server fallback)
  let rawConcerts = window.CONCERT_DATA || [];
  let summaryMetrics = window.SUMMARY_DATA || null;

  if (!rawConcerts.length) {
    // Attempt local fetch if opened via http server
    fetch('data/cleaned_concert_turnout.json')
      .then(res => res.json())
      .then(data => {
        rawConcerts = data;
        return fetch('data/analysis_summary.json');
      })
      .then(res => res.json())
      .then(sumData => {
        summaryMetrics = sumData;
        initApp(rawConcerts, summaryMetrics);
      })
      .catch(err => {
        console.warn('Local fetch error:', err);
      });
  } else {
    initApp(rawConcerts, summaryMetrics);
  }
});

function initApp(concerts, summary) {
  console.log(`Scanalytical loaded: ${concerts.length} concerts.`);

  // 1. Initialize Engines
  if (window.ChartEngine && summary) {
    window.ChartEngine.initAllCharts(summary);
  }
  if (window.MapEngine) {
    window.MapEngine.initMap(concerts);
  }
  if (window.SimulatorEngine) {
    window.SimulatorEngine.initSimulator();
  }

  // 2. Setup Factor Tabs
  setupTabs();

  // 3. Setup Interactive Data Table
  setupTable(concerts);

  // 4. Setup Chart Zoom Modal
  setupModal();

  // 5. Populate Artist Filter Dropdowns dynamically
  populateDropdowns(concerts);
}

function setupTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

function populateDropdowns(concerts) {
  const artistMapSelect = document.getElementById('map-filter-artist');
  if (!artistMapSelect) return;

  const artists = Array.from(new Set(concerts.map(c => c.artist))).sort();
  artists.forEach(a => {
    const opt = document.createElement('option');
    opt.value = a;
    opt.textContent = a;
    artistMapSelect.appendChild(opt);
  });
}

// -------------------------------------------------------------
// Interactive Data Table Component
// -------------------------------------------------------------
let currentPage = 1;
const pageSize = 15;
let filteredData = [];
let sortCol = 'date';
let sortAsc = false;

function setupTable(concerts) {
  filteredData = [...concerts];
  const searchInput = document.getElementById('table-search');
  const exportCsvBtn = document.getElementById('btn-export-csv');
  const exportJsonBtn = document.getElementById('btn-export-json');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      filteredData = concerts.filter(c => 
        c.artist.toLowerCase().includes(q) ||
        c.city.toLowerCase().includes(q) ||
        c.country.toLowerCase().includes(q) ||
        c.venue.toLowerCase().includes(q) ||
        c.tour.toLowerCase().includes(q)
      );
      currentPage = 1;
      renderTable();
    });
  }

  // Sorting
  document.querySelectorAll('.styled-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.getAttribute('data-sort');
      if (sortCol === col) {
        sortAsc = !sortAsc;
      } else {
        sortCol = col;
        sortAsc = true;
      }
      sortData();
      renderTable();
    });
  });

  // Export buttons
  if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', () => exportCSV(filteredData));
  }
  if (exportJsonBtn) {
    exportJsonBtn.addEventListener('click', () => exportJSON(filteredData));
  }

  renderTable();
}

function sortData() {
  filteredData.sort((a, b) => {
    let valA = a[sortCol];
    let valB = b[sortCol];
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });
}

function renderTable() {
  const tbody = document.getElementById('table-body');
  const pageInfo = document.getElementById('page-info');
  const prevBtn = document.getElementById('btn-prev');
  const nextBtn = document.getElementById('btn-next');
  if (!tbody) return;

  const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
  const startIdx = (currentPage - 1) * pageSize;
  const pageRows = filteredData.slice(startIdx, startIdx + pageSize);

  tbody.innerHTML = pageRows.map(r => `
    <tr>
      <td><strong>${r.artist}</strong></td>
      <td style="color:#94A3B8;">${r.tour}</td>
      <td>${r.city}, <span style="color:#64748B;">${r.country}</span></td>
      <td>${r.venue}</td>
      <td><span class="table-tag ${r.venue_type === 'Stadium' ? 'tag-standard' : ''}">${r.venue_type}</span></td>
      <td style="font-family:var(--font-mono); font-weight:600;">${r.attendance.toLocaleString()}</td>
      <td style="font-family:var(--font-mono); color:#94A3B8;">${r.capacity.toLocaleString()}</td>
      <td>
        <span class="table-tag ${r.is_sellout ? 'tag-sellout' : 'tag-standard'}">
          ${r.occupancy_rate}%
        </span>
      </td>
      <td style="font-family:var(--font-mono); color:#10B981;">$${(r.gross_usd / 1e6).toFixed(2)}M</td>
      <td style="font-family:var(--font-mono);">$${r.avg_ticket_price.toFixed(2)}</td>
      <td style="color:#64748B; font-size:0.8rem;">${r.date}</td>
    </tr>
  `).join('');

  if (pageInfo) {
    pageInfo.textContent = `Showing ${Math.min(filteredData.length, startIdx + 1)} - ${Math.min(filteredData.length, startIdx + pageSize)} of ${filteredData.length.toLocaleString()} concerts`;
  }

  if (prevBtn) {
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
      if (currentPage > 1) {
        currentPage--;
        renderTable();
      }
    };
  }

  if (nextBtn) {
    nextBtn.disabled = currentPage >= totalPages;
    nextBtn.onclick = () => {
      if (currentPage < totalPages) {
        currentPage++;
        renderTable();
      }
    };
  }
}

function exportCSV(data) {
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const rows = data.map(obj => headers.map(h => `"${String(obj[h] || '').replace(/"/g, '""')}"`).join(','));
  const csvContent = [headers.join(','), ...rows].join('\n');
  downloadBlob(csvContent, 'cleaned_concert_turnout.csv', 'text/csv;charset=utf-8;');
}

function exportJSON(data) {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadBlob(jsonContent, 'cleaned_concert_turnout.json', 'application/json');
}

function downloadBlob(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// -------------------------------------------------------------
// Chart Zoom Modal Component
// -------------------------------------------------------------
function setupModal() {
  const modal = document.getElementById('chart-modal');
  const modalImg = document.getElementById('modal-img');
  const modalClose = document.getElementById('modal-close');

  document.querySelectorAll('[data-zoom-chart]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const chartPath = btn.getAttribute('data-zoom-chart');
      if (modal && modalImg) {
        modalImg.src = chartPath;
        modal.classList.add('active');
      }
    });
  });

  if (modalClose) {
    modalClose.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }
}
