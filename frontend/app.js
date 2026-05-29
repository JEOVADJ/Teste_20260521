// ============ STATE & GLOBALS ============
const state = {
  currentSystem: null,
  currentDevice: null,
  chart: null,
  distributionChart: null,
  readings: [],
  autoRefreshInterval: null,
  darkMode: localStorage.getItem('darkMode') === 'true',
  autoRefresh: localStorage.getItem('autoRefresh') === 'true',
  refreshInterval: parseInt(localStorage.getItem('refreshInterval') || '30')
};

const socket = io();

// ============ DOM ELEMENTS ============
const elements = {
  sidebar: document.querySelector('.sidebar'),
  menuToggle: document.getElementById('menuToggle'),
  themeToggle: document.getElementById('themeToggle'),
  pageTitle: document.getElementById('pageTitle'),
  connectionStatus: document.getElementById('connectionStatus'),
  statusText: document.getElementById('statusText'),
  
  systemSelect: document.getElementById('systemSelect'),
  deviceSelect: document.getElementById('deviceSelect'),
  refreshBtn: document.getElementById('refreshBtn'),
  
  lastValue: document.getElementById('lastValue'),
  lastTime: document.getElementById('lastTime'),
  minValue: document.getElementById('minValue'),
  maxValue: document.getElementById('maxValue'),
  avgValue: document.getElementById('avgValue'),
  
  mainChart: document.getElementById('mainChart'),
  distributionChart: document.getElementById('distributionChart'),
  realtimeLog: document.getElementById('realtimeLog'),
  
  devicesList: document.getElementById('devicesList'),
  historyDevice: document.getElementById('historyDevice'),
  historyDate: document.getElementById('historyDate'),
  historyBody: document.getElementById('historyBody'),
  exportBtn: document.getElementById('exportBtn'),
  
  autoRefreshCheck: document.getElementById('autoRefresh'),
  refreshIntervalInput: document.getElementById('refreshInterval'),
  enableNotificationsCheck: document.getElementById('enableNotifications')
};

// ============ INITIALIZATION ============
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMenuNavigation();
  initEventListeners();
  initWebSocket();
  loadDashboard();
  setDefaultDate();
});

// ============ THEME ============
function initTheme() {
  if (state.darkMode) {
    document.body.classList.add('dark-theme');
    elements.themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  }
}

elements.themeToggle.addEventListener('click', () => {
  state.darkMode = !state.darkMode;
  document.body.classList.toggle('dark-theme');
  localStorage.setItem('darkMode', state.darkMode);
  elements.themeToggle.innerHTML = state.darkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

// ============ NAVIGATION ============
function initMenuNavigation() {
  const menuItems = document.querySelectorAll('.menu-item');
  const views = document.querySelectorAll('.view');

  menuItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = item.dataset.view;
      
      menuItems.forEach(m => m.classList.remove('active'));
      views.forEach(v => v.classList.remove('active'));
      
      item.classList.add('active');
      document.getElementById(viewName + 'View').classList.add('active');
      
      elements.pageTitle.textContent = item.textContent.trim();
      elements.sidebar.classList.remove('active');

      if (viewName === 'devices') loadDevices();
      if (viewName === 'history') loadHistoryDevices();
    });
  });

  elements.menuToggle.addEventListener('click', () => {
    elements.sidebar.classList.toggle('active');
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.sidebar') && !e.target.closest('.menu-toggle')) {
      elements.sidebar.classList.remove('active');
    }
  });
}

// ============ EVENT LISTENERS ============
function initEventListeners() {
  elements.systemSelect.addEventListener('change', () => {
    state.currentSystem = elements.systemSelect.value;
    loadDevices();
    loadChart();
  });

  elements.deviceSelect.addEventListener('change', () => {
    state.currentDevice = elements.deviceSelect.value;
    loadChart();
  });

  elements.refreshBtn.addEventListener('click', async () => {
    elements.refreshBtn.disabled = true;
    await loadSystems();
    if (state.currentDevice) await loadChart();
    elements.refreshBtn.disabled = false;
  });

  document.querySelectorAll('.btn-small').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.btn-small').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadChart();
    });
  });

  elements.autoRefreshCheck.addEventListener('change', () => {
    state.autoRefresh = elements.autoRefreshCheck.checked;
    localStorage.setItem('autoRefresh', state.autoRefresh);
    setupAutoRefresh();
  });

  elements.refreshIntervalInput.addEventListener('change', () => {
    state.refreshInterval = parseInt(elements.refreshIntervalInput.value);
    localStorage.setItem('refreshInterval', state.refreshInterval);
    setupAutoRefresh();
  });

  elements.exportBtn.addEventListener('click', exportHistory);
  
  elements.historyDate.addEventListener('change', loadHistory);
  elements.historyDevice.addEventListener('change', loadHistory);
}

// ============ WEBSOCKET ============
function initWebSocket() {
  socket.on('connect', () => {
    updateConnectionStatus(true);
    addRealtimeLog('✓ Conectado ao servidor');
  });

  socket.on('disconnect', () => {
    updateConnectionStatus(false);
    addRealtimeLog('✗ Desconectado do servidor');
  });

  socket.on('new_reading', (data) => {
    addRealtimeLog(`📊 ${data.system} / ${data.device_id}: ${data.value}`);
    if (state.currentDevice) {
      state.readings.unshift({
        ts: data.timestamp || new Date().toISOString(),
        value: data.value
      });
      if (state.readings.length > 500) state.readings.pop();
      updateStats();
      updateMainChart();
    }
  });
}

function updateConnectionStatus(connected) {
  elements.connectionStatus.classList.toggle('connected', connected);
  elements.statusText.textContent = connected ? 'Conectado' : 'Desconectado';
}

function addRealtimeLog(message) {
  const time = new Date().toLocaleTimeString();
  const item = document.createElement('div');
  item.className = 'log-item';
  item.textContent = `[${time}] ${message}`;
  
  elements.realtimeLog.insertBefore(item, elements.realtimeLog.firstChild);
  if (elements.realtimeLog.children.length > 50) {
    elements.realtimeLog.removeChild(elements.realtimeLog.lastChild);
  }
}

// ============ DATA LOADING ============
async function loadDashboard() {
  elements.autoRefreshCheck.checked = state.autoRefresh;
  elements.refreshIntervalInput.value = state.refreshInterval;
  
  await loadSystems();
  setupAutoRefresh();
}

async function loadSystems() {
  try {
    const res = await fetch('/api/systems');
    const systems = await res.json();
    
    populateSelect(elements.systemSelect, systems, 'id', 'name');
    
    if (systems.length > 0 && !state.currentSystem) {
      state.currentSystem = systems[0].id;
      elements.systemSelect.value = state.currentSystem;
      await loadDevices();
      await loadChart();
    }
  } catch (err) {
    console.error('Erro ao carregar sistemas:', err);
    addRealtimeLog('⚠️ Erro ao carregar sistemas');
  }
}

async function loadDevices() {
  if (!state.currentSystem) return;
  
  try {
    const res = await fetch(`/api/devices?system_id=${state.currentSystem}`);
    const devices = await res.json();
    
    populateSelect(elements.deviceSelect, devices, 'id', 'identifier');
    
    if (devices.length > 0 && !state.currentDevice) {
      state.currentDevice = devices[0].id;
      elements.deviceSelect.value = state.currentDevice;
      await loadChart();
    }
  } catch (err) {
    console.error('Erro ao carregar dispositivos:', err);
  }
}

async function loadChart() {
  if (!state.currentDevice) return;
  
  try {
    const period = document.querySelector('.btn-small.active')?.dataset.period || '24h';
    const res = await fetch(`/api/readings?device_id=${state.currentDevice}&limit=500`);
    state.readings = await res.json();
    
    updateStats();
    updateMainChart();
    updateDistributionChart();
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
  }
}

async function loadDevicesList() {
  try {
    const res = await fetch('/api/devices');
    const devices = await res.json();
    
    elements.devicesList.innerHTML = '';
    devices.forEach(device => {
      const card = document.createElement('div');
      card.className = 'device-card';
      card.innerHTML = `
        <h4><span class="device-status online"></span>${device.identifier}</h4>
        <p style="margin: 8px 0; color: #999; font-size: 12px;">ID: ${device.id}</p>
        <p style="margin: 8px 0; color: #999; font-size: 12px;">Sistema: ${device.system_id}</p>
      `;
      elements.devicesList.appendChild(card);
    });
  } catch (err) {
    console.error('Erro ao carregar lista de dispositivos:', err);
  }
}

async function loadHistoryDevices() {
  try {
    const res = await fetch('/api/devices');
    const devices = await res.json();
    populateSelect(elements.historyDevice, devices, 'id', 'identifier');
  } catch (err) {
    console.error('Erro ao carregar dispositivos do histórico:', err);
  }
}

async function loadHistory() {
  const deviceId = elements.historyDevice.value;
  const date = elements.historyDate.value;
  
  if (!deviceId || !date) return;
  
  try {
    const startDate = date + 'T00:00:00';
    const endDate = date + 'T23:59:59';
    const res = await fetch(`/api/readings?device_id=${deviceId}&start=${startDate}&end=${endDate}&limit=10000`);
    const readings = await res.json();
    
    elements.historyBody.innerHTML = '';
    if (readings.length === 0) {
      elements.historyBody.innerHTML = '<tr><td colspan="3" class="text-center">Nenhum dado</td></tr>';
      return;
    }
    
    readings.reverse().forEach(reading => {
      const row = document.createElement('tr');
      const dateObj = new Date(reading.ts);
      row.innerHTML = `
        <td>${dateObj.toLocaleString('pt-BR')}</td>
        <td>${reading.value.toFixed(2)}</td>
        <td>${elements.historyDevice.options[elements.historyDevice.selectedIndex].text}</td>
      `;
      elements.historyBody.appendChild(row);
    });
  } catch (err) {
    console.error('Erro ao carregar histórico:', err);
  }
}

// ============ STATS ============
function updateStats() {
  if (state.readings.length === 0) return;
  
  const values = state.readings.map(r => r.value);
  const latest = values[0];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
  
  elements.lastValue.textContent = latest.toFixed(2);
  elements.lastTime.textContent = new Date(state.readings[0].ts).toLocaleString('pt-BR');
  elements.minValue.textContent = min.toFixed(2);
  elements.maxValue.textContent = max.toFixed(2);
  elements.avgValue.textContent = avg;
}

// ============ CHARTS ============
function updateMainChart() {
  const labels = state.readings.map(r => new Date(r.ts).toLocaleTimeString('pt-BR')).reverse();
  const data = state.readings.map(r => r.value).reverse();
  
  const ctx = elements.mainChart.getContext('2d');
  
  if (state.chart) state.chart.destroy();
  
  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Valor',
        data,
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#667eea',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: {
            drawBorder: false,
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

function updateDistributionChart() {
  const values = state.readings.map(r => r.value);
  if (values.length === 0) return;
  
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = (max - min) / 10 || 1;
  
  const bins = Array(10).fill(0);
  values.forEach(v => {
    const index = Math.floor((v - min) / range);
    if (index >= 0 && index < 10) bins[index]++;
  });
  
  const labels = bins.map((_, i) => {
    const binMin = (min + i * range).toFixed(1);
    const binMax = (min + (i + 1) * range).toFixed(1);
    return `${binMin}-${binMax}`;
  });
  
  const ctx = elements.distributionChart.getContext('2d');
  
  if (state.distributionChart) state.distributionChart.destroy();
  
  state.distributionChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Frequência',
        data: bins,
        backgroundColor: 'rgba(118, 75, 162, 0.7)',
        borderColor: '#764ba2',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            drawBorder: false
          }
        },
        y: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// ============ AUTO REFRESH ============
function setupAutoRefresh() {
  if (state.autoRefreshInterval) clearInterval(state.autoRefreshInterval);
  
  if (state.autoRefresh) {
    state.autoRefreshInterval = setInterval(() => {
      if (state.currentDevice) loadChart();
    }, state.refreshInterval * 1000);
  }
}

// ============ EXPORT ============
function exportHistory() {
  const rows = elements.historyBody.querySelectorAll('tr');
  if (rows.length === 0) {
    alert('Nenhum dado para exportar');
    return;
  }
  
  let csv = 'Data/Hora,Valor,Dispositivo\n';
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length === 3) {
      csv += `${cells[0].textContent},${cells[1].textContent},${cells[2].textContent}\n`;
    }
  });
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `historico_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
}

// ============ UTILITIES ============
function populateSelect(el, items, valueKey = 'id', labelKey = 'name') {
  el.innerHTML = '';
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item[valueKey];
    opt.textContent = item[labelKey] || item.identifier || item.name;
    el.appendChild(opt);
  });
}

function setDefaultDate() {
  const today = new Date();
  elements.historyDate.valueAsDate = today;
}

