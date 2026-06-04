import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import { api } from '../api'

export const useSerialStore = defineStore('serial', () => {
  const config = ref({
    portName: 'COM1',
    baudRate: 115200,
    dataBits: 8,
    stopBits: 1,
    parity: 'none',
    flowControl: 'none'
  })

  const connected = ref(false)
  const connecting = ref(false)
  const logs = ref([])
  const availablePorts = ref([])

  // 后端真实状态（通过轮询同步）
  const actualPort = ref(null)
  const actualBaudRate = ref(null)

  let pollTimer = null

  const statusText = computed(() => {
    if (connecting.value) return '连接中...'
    if (connected.value) return '已连接'
    return '未连接'
  })

  const statusColor = computed(() => {
    if (connecting.value) return 'amber'
    if (connected.value) return 'green'
    return 'off'
  })

  const connectionInfo = computed(() => {
    if (connecting.value) return '连接中...'
    if (connected.value) {
      // 优先使用后端返回的真实端口信息
      const port = actualPort.value || config.value.portName
      const baud = actualBaudRate.value || config.value.baudRate
      return `${port} @ ${baud}`
    }
    return '未连接'
  })

  function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString()
    logs.value.push({ timestamp, message, type })
    if (logs.value.length > 200) {
      logs.value = logs.value.slice(-200)
    }
  }

  async function fetchLogs() {
    try {
      const backendLogs = await api.getSerialLogs()
      logs.value = backendLogs
    } catch (e) {
      console.error('获取日志失败:', e)
    }
  }

  async function fetchPorts() {
    try {
      const ports = await api.getPorts()
      availablePorts.value = ports.map(p => p.name)
      if (availablePorts.value.length > 0 && !availablePorts.value.includes(config.value.portName)) {
        config.value.portName = availablePorts.value[0]
      }
    } catch (e) {
      console.error('获取串口列表失败:', e)
    }
  }

  function startPolling() {
    stopPolling()
    pollTimer = setInterval(async () => {
      try {
        const status = await api.getSerialStatus()
        // 同步后端真实连接状态
        connected.value = status.connected
        actualPort.value = status.port || null
        actualBaudRate.value = status.baud_rate || null

        // 如果后端已断开，更新配置中的端口名
        if (!status.connected && status.port) {
          config.value.portName = status.port
        }
      } catch (e) {
        // 轮询失败时不更新状态，保留上次有效值
        console.debug('串口状态轮询失败:', e.message)
      }
    }, 2000)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  async function connect() {
    if (connecting.value || connected.value) return
    connecting.value = true
    addLog(`正在连接 ${config.value.portName}...`, 'info')

    try {
      const result = await api.connectSerial({
        port_name: config.value.portName,
        baud_rate: config.value.baudRate,
        data_bits: config.value.dataBits,
        stop_bits: config.value.stopBits,
        parity: config.value.parity
      })
      connected.value = true
      actualPort.value = result.port || config.value.portName
      actualBaudRate.value = result.baud_rate || config.value.baudRate
      addLog(`${config.value.portName} 连接成功 (${config.value.baudRate} bps)`, 'success')
    } catch (e) {
      addLog(`${config.value.portName} 连接失败：${e.message || '端口占用或不存在'}`, 'error')
    } finally {
      connecting.value = false
    }
  }

  function autoConnect(portName) {
    if (connecting.value || connected.value) return
    config.value.portName = portName
    connect()
  }

  async function disconnect() {
    try {
      await api.disconnectSerial()
    } catch (e) {
      // ignore
    }
    connected.value = false
    actualPort.value = null
    actualBaudRate.value = null
    addLog('串口已断开', 'info')
  }

  function sendData(data) {
    addLog(`发送: ${data}`, 'info')
  }

  async function clearLogs() {
    logs.value = []
    try {
      await api.clearSerialLogs()
    } catch (e) {
      // ignore
    }
  }

  return {
    config,
    connected,
    connecting,
    logs,
    availablePorts,
    actualPort,
    actualBaudRate,
    statusText,
    statusColor,
    connectionInfo,
    connect,
    autoConnect,
    disconnect,
    fetchPorts,
    fetchLogs,
    sendData,
    addLog,
    clearLogs,
    startPolling,
    stopPolling
  }
})
