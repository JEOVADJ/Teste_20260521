const systemsEl = document.getElementById('systems')
const devicesEl = document.getElementById('devices')
const refreshBtn = document.getElementById('refresh')
const instantEl = document.getElementById('instant')

let chart

async function fetchSystems(){
  const res = await fetch('/api/systems')
  return res.json()
}

async function fetchDevices(system_id){
  const res = await fetch('/api/devices?system_id=' + system_id)
  return res.json()
}

async function fetchReadings(device_id){
  const res = await fetch('/api/readings?device_id=' + device_id + '&limit=500')
  return res.json()
}

function populateSelect(el, items, key='id', labelKey='name'){
  el.innerHTML = ''
  items.forEach(i => {
    const opt = document.createElement('option')
    opt.value = i[key]
    opt.textContent = i[labelKey] || i.identifier || i.name
    el.appendChild(opt)
  })
}

async function refresh(){
  const systems = await fetchSystems()
  populateSelect(systemsEl, systems, 'id', 'name')
  if(systems.length>0){
    const sysId = systemsEl.value
    const devices = await fetchDevices(sysId)
    populateSelect(devicesEl, devices, 'id', 'identifier')
    await loadChart()
  }
}

async function loadChart(){
  const deviceId = devicesEl.value
  if(!deviceId) return
  const data = await fetchReadings(deviceId)
  const labels = data.map(d => new Date(d.ts).toLocaleString()).reverse()
  const values = data.map(d => d.value).reverse()
  const ctx = document.getElementById('chart').getContext('2d')
  if(chart) chart.destroy()
  chart = new Chart(ctx, {
    type: 'line',
    data: {labels, datasets:[{label:'Valor',data:values,borderColor:'#0a5f7a',fill:false}]},
    options: {scales:{x:{display:true}}}
  })
}

refreshBtn.addEventListener('click', refresh)
systemsEl.addEventListener('change', refresh)
devicesEl.addEventListener('change', loadChart)

// realtime
const socket = io()
socket.on('connect', ()=>console.log('socket connected'))
socket.on('new_reading', payload =>{
  instantEl.textContent = `${payload.system} / ${payload.device_id} = ${payload.value} @ ${payload.timestamp||new Date().toISOString()}`
  // if the current selected device matches, refresh chart
  const selDeviceText = devicesEl.options[devicesEl.selectedIndex]?.text
  if(selDeviceText && selDeviceText === payload.device_id){
    loadChart()
  }
})

// init
refresh()
