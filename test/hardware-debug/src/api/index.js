const BASE_URL = 'http://localhost:5175'

async function request(path, options = {}, timeout = 90000) {
  const url = `${BASE_URL}${path}`
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)
  const config = {
    headers: { 'Content-Type': 'application/json' },
    signal: controller.signal,
    ...options,
  }
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }
  let res
  try {
    res = await fetch(url, config)
  } catch (e) {
    clearTimeout(timeoutId)
    if (e.name === 'AbortError') {
      throw new Error('请求超时，请检查串口连接')
    }
    throw e
  }
  clearTimeout(timeoutId)
  if (!res.ok) {
    throw new Error(`API 错误: ${res.status} ${res.statusText}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getCategories() { return request('/api/categories') },
  createCategory(data) { return request('/api/categories', { method: 'POST', body: data }) },
  updateCategory(id, data) { return request(`/api/categories/${id}`, { method: 'PUT', body: data }) },
  deleteCategory(id) { return request(`/api/categories/${id}`, { method: 'DELETE' }) },

  getDeviceTypes() { return request('/api/device-types') },
  getDeviceTypesByCategory(categoryId) { return request(`/api/device-types/by-category/${categoryId}`) },
  createDeviceType(data) { return request('/api/device-types', { method: 'POST', body: data }) },
  updateDeviceType(id, data) { return request(`/api/device-types/${id}`, { method: 'PUT', body: data }) },
  deleteDeviceType(id) { return request(`/api/device-types/${id}`, { method: 'DELETE' }) },

  getProjects() { return request('/api/projects') },
  getProject(id) { return request(`/api/projects/${id}`) },
  createProject(data) { return request('/api/projects', { method: 'POST', body: data }) },
  updateProject(id, data) { return request(`/api/projects/${id}`, { method: 'PUT', body: data }) },
  deleteProject(id) { return request(`/api/projects/${id}`, { method: 'DELETE' }) },

  addDeviceConfig(projectId, data) { return request(`/api/projects/${projectId}/configs`, { method: 'POST', body: data }) },
  updateDeviceConfig(configId, data) { return request(`/api/projects/configs/${configId}`, { method: 'PUT', body: data }) },
  deleteDeviceConfig(configId) { return request(`/api/projects/configs/${configId}`, { method: 'DELETE' }) },

  getPorts() { return request('/api/serial/ports') },
  connectSerial(data) { return request('/api/serial/connect', { method: 'POST', body: data }) },
  disconnectSerial() { return request('/api/serial/disconnect', { method: 'POST' }) },
  getSerialStatus() { return request('/api/serial/status') },
  getSerialLogs() { return request('/api/serial/logs') },
  clearSerialLogs() { return request('/api/serial/logs', { method: 'DELETE' }) },
  saveSerialLog(data) { return request('/api/serial/logs', { method: 'POST', body: data }) },

  writeModbusConfig57(data) { return request('/api/modbus/write-config-57', { method: 'POST', body: data }) },
  inspectModbus57(data) { return request('/api/modbus/inspect-57', { method: 'POST', body: data }) },
  writeModbusConfig35(data) { return request('/api/modbus/write-config-35', { method: 'POST', body: data }) },
  inspectModbus35(data) { return request('/api/modbus/inspect-35', { method: 'POST', body: data }) },

  checkHasData() { return request('/api/migrate/has-data') },
  importData(data) { return request('/api/migrate/import', { method: 'POST', body: data }) },

  // ── 老化测试 API ──
  agingStart(data) { return request('/api/aging/start', { method: 'POST', body: data }) },
  agingStop() { return request('/api/aging/stop', { method: 'POST' }) },
  agingStatus() { return request('/api/aging/status') },
  agingMoveTo(data) { return request('/api/aging/move-to', { method: 'POST', body: data }) },
  agingHome(data) { return request('/api/aging/home', { method: 'POST', body: data }) },
  agingStopMotor(data) { return request('/api/aging/stop-motor', { method: 'POST', body: data }) },
  agingEnable(data) { return request('/api/aging/enable', { method: 'POST', body: data }) },
  agingPosition(station) { return request(`/api/aging/position?station=${station}`) },
}
