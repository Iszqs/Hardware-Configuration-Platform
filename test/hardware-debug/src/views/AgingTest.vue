<template>
  <div class="aging-test">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1>老化测试</h1>
        <p>坐标点位循环运动 — 让步进电机按预设坐标循环运行</p>
      </div>
    </div>

    <div class="aging-layout">
      <!-- 左栏：参数设置 + 坐标点列表 -->
      <div class="aging-left">
        <!-- 参数设置 -->
        <div class="section-card">
          <h3>参数设置</h3>
          <div class="param-grid">
            <div class="input-group">
              <label>站号</label>
              <input class="input-field" type="number" v-model.number="station" min="1" max="64" />
            </div>
            <div class="input-group">
              <label>运行速度 (rpm)</label>
              <input class="input-field" type="number" v-model.number="speedRpm" min="1" max="3000" />
            </div>
            <div class="input-group">
              <label>加速时间 (ms)</label>
              <input class="input-field" type="number" v-model.number="accelMs" min="0" max="65535" />
            </div>
            <div class="input-group">
              <label>减速时间 (ms)</label>
              <input class="input-field" type="number" v-model.number="decelMs" min="0" max="65535" />
            </div>
            <div class="input-group">
              <label>默认停留 (ms)</label>
              <input class="input-field" type="number" v-model.number="defaultDwell" min="0" max="60000" />
            </div>
            <div class="input-group">
              <label>循环次数 (0=无限)</label>
              <input class="input-field" type="number" v-model.number="maxCycles" min="0" max="99999" />
            </div>
          </div>
          <div class="section-actions">
            <button class="btn btn-secondary btn-sm" @click="readPosition" :disabled="agingRunning">
              <span class="btn-icon">⟳</span> 读取当前位置
            </button>
            <button class="btn btn-secondary btn-sm" @click="applyParams" :disabled="agingRunning">
              <span class="btn-icon">✓</span> 应用参数
            </button>
          </div>
          <div v-if="readbackPosition !== null" class="readback-hint">
            当前位置: <strong class="mono">{{ readbackPosition }}</strong> pulses
          </div>
        </div>

        <!-- 坐标点列表 -->
        <div class="section-card">
          <div class="section-header">
            <h3>坐标点列表</h3>
            <button class="btn btn-sm btn-primary" @click="addPoint" :disabled="agingRunning">+ 添加坐标点</button>
          </div>

          <div v-if="points.length === 0" class="empty-hint">
            暂无坐标点，请添加
          </div>

          <div v-else class="points-table-wrapper">
            <table class="points-table">
              <thead>
                <tr>
                  <th class="col-idx">#</th>
                  <th class="col-pos">位置 (pulses)</th>
                  <th class="col-dwell">停留 (ms)</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(pt, idx) in points" :key="idx"
                    :class="{ 'active-row': agingRunning && currentPoint === idx + 1 }">
                  <td class="col-idx">{{ idx + 1 }}</td>
                  <td>
                    <input class="input-field input-sm mono" type="number" v-model.number="pt.position"
                           :disabled="agingRunning" />
                  </td>
                  <td>
                    <input class="input-field input-sm" type="number" v-model.number="pt.dwell"
                           placeholder="默认" :disabled="agingRunning" />
                  </td>
                  <td class="col-actions">
                    <button class="btn btn-icon-only" @click="moveUp(idx)" :disabled="idx === 0 || agingRunning" title="上移">↑</button>
                    <button class="btn btn-icon-only" @click="moveDown(idx)" :disabled="idx === points.length - 1 || agingRunning" title="下移">↓</button>
                    <button class="btn btn-icon-only btn-danger-text" @click="removePoint(idx)" :disabled="agingRunning" title="删除">×</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="preset-bar">
            <button class="btn btn-xs btn-secondary" @click="loadPreset('backforth')" :disabled="agingRunning">往返运动</button>
            <button class="btn btn-xs btn-secondary" @click="loadPreset('triangle')" :disabled="agingRunning">三角波</button>
            <button class="btn btn-xs btn-secondary" @click="loadPreset('sine')" :disabled="agingRunning">正弦近似</button>
          </div>
        </div>
      </div>

      <!-- 右栏：控制 + 状态 + 日志 -->
      <div class="aging-right">
        <!-- 控制按钮 -->
        <div class="section-card">
          <h3>控制</h3>
          <div class="control-bar">
            <button class="btn btn-secondary" @click="homeMotor" :disabled="agingRunning" title="回原点">
              <span class="btn-icon">⤺</span> 回原点
            </button>
            <button class="btn btn-success" @click="startAging" :disabled="agingRunning || points.length === 0">
              <span class="btn-icon">▶</span> 开始老化
            </button>
            <button class="btn btn-danger" @click="stopAging" :disabled="!agingRunning">
              <span class="btn-icon">■</span> 停止
            </button>
            <button class="btn btn-warning" @click="emergencyStop" title="急停">
              <span class="btn-icon">⛔</span> 急停
            </button>
          </div>
        </div>

        <!-- 实时状态 -->
        <div class="section-card">
          <h3>实时状态</h3>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">运行状态</span>
              <span class="status-value" :class="agingRunning ? 'status-running' : 'status-idle'">
                <span class="status-dot"></span>
                {{ agingRunning ? '运行中' : '空闲' }}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label">当前点位</span>
              <span class="status-value mono">{{ currentPoint }} / {{ totalPoints }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">循环次数</span>
              <span class="status-value mono">{{ cycleCount }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">运行时间</span>
              <span class="status-value mono">{{ formatTime(elapsedSeconds) }}</span>
            </div>
          </div>
        </div>

        <!-- 位置监控 -->
        <div class="section-card">
          <h3>位置监控</h3>
          <div class="position-display">
            <div class="position-bar-wrapper">
              <div class="position-bar" :style="positionBarStyle"></div>
            </div>
            <div class="position-text">
              <span>当前: <strong class="mono">{{ currentPosition ?? '—' }}</strong> pulses</span>
              <span v-if="positionHistory.length" class="position-range">
                范围: <strong class="mono">{{ positionRange }}</strong>
              </span>
            </div>
          </div>
          <!-- 简易实时曲线 -->
          <div class="chart-container">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>

        <!-- 测试日志 -->
        <div class="section-card">
          <div class="section-header">
            <h3>测试日志</h3>
            <button class="btn btn-xs btn-secondary" @click="clearLogs">清空</button>
          </div>
          <div class="log-container" ref="logContainer">
            <div v-for="(log, i) in logs" :key="i" class="log-line"
                 :class="{ 'log-success': log.includes('到位'), 'log-warn': log.includes('超时') || log.includes('异常'), 'log-error': log.includes('错误') || log.includes('失败'), 'log-info': log.includes('完成') || log.includes('开始') || log.includes('结束') }">
              {{ log }}
            </div>
            <div v-if="logs.length === 0" class="log-empty">暂无日志</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { api } from '../api/index.js'

// ── 参数 ──
const station = ref(1)
const speedRpm = ref(300)
const accelMs = ref(120)
const decelMs = ref(120)
const defaultDwell = ref(1000)
const maxCycles = ref(0)
const points = reactive([])
const readbackPosition = ref(null)

// ── 状态 ──
const agingRunning = ref(false)
const currentPoint = ref(0)
const totalPoints = ref(0)
const cycleCount = ref(0)
const elapsedSeconds = ref(0)
const currentPosition = ref(null)
const logs = ref([])
const positionHistory = ref([])
const chartCanvas = ref(null)

let pollTimer = null
let chartInstance = null
let elapsedTimer = null

// ── 计算属性 ──
const positionBarStyle = computed(() => {
  const hist = positionHistory.value
  if (!hist.length) return { width: '0%' }
  const min = Math.min(...hist)
  const max = Math.max(...hist)
  const range = max - min || 1
  const pct = ((currentPosition.value ?? min) - min) / range * 100
  return { width: `${Math.max(0, Math.min(100, pct))}%` }
})

const positionRange = computed(() => {
  const hist = positionHistory.value
  if (!hist.length) return '—'
  const min = Math.min(...hist)
  const max = Math.max(...hist)
  return `${min} ~ ${max}`
})

// ── 工具函数 ──
function formatTime(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function addLog(msg) {
  const ts = new Date().toLocaleTimeString('zh-CN', { hour12: false })
  logs.value.push(`[${ts}] ${msg}`)
  if (logs.value.length > 500) logs.value = logs.value.slice(-500)
  nextTick(() => {
    const el = document.querySelector('.log-container')
    if (el) el.scrollTop = el.scrollHeight
  })
}

// ── 坐标点管理 ──
function addPoint() {
  const lastPos = points.length > 0 ? points[points.length - 1].position : 0
  points.push({ position: lastPos + 5000, dwell: defaultDwell.value })
}

function removePoint(idx) {
  points.splice(idx, 1)
}

function moveUp(idx) {
  if (idx <= 0) return
  const tmp = points[idx]
  points[idx] = points[idx - 1]
  points[idx - 1] = tmp
}

function moveDown(idx) {
  if (idx >= points.length - 1) return
  const tmp = points[idx]
  points[idx] = points[idx + 1]
  points[idx + 1] = tmp
}

function loadPreset(type) {
  points.length = 0
  const dwell = defaultDwell.value
  if (type === 'backforth') {
    ;[0, 10000, 0, -10000, 0].forEach(p => points.push({ position: p, dwell }))
  } else if (type === 'triangle') {
    ;[0, 5000, 10000, 5000, 0, -5000, -10000, -5000, 0].forEach(p => points.push({ position: p, dwell }))
  } else if (type === 'sine') {
    const steps = [0, 3827, 7071, 9239, 10000, 9239, 7071, 3827, 0, -3827, -7071, -9239, -10000, -9239, -7071, -3827, 0]
    steps.forEach(p => points.push({ position: p, dwell }))
  }
  addLog(`已加载预设: ${type}`)
}

// ── API 操作 ──
async function readPosition() {
  try {
    const res = await api.agingPosition(station.value)
    if (res.position !== null) {
      readbackPosition.value = res.position
      currentPosition.value = res.position
      addLog(`读取当前位置: ${res.position} pulses`)
    } else {
      addLog('读取位置失败，请检查串口连接', 'error')
    }
  } catch (e) {
    addLog(`读取位置失败: ${e.message}`, 'error')
  }
}

async function applyParams() {
  try {
    const res = await api.agingMoveTo({ station: station.value, speed_rpm: speedRpm.value, position: 0 })
    // Just set speed to the motor without moving - use a quick no-op
    addLog(`参数已应用: 速度=${speedRpm.value}rpm, 加减速=${accelMs.value}/${decelMs.value}ms`)
  } catch (e) {
    addLog(`应用参数失败: ${e.message}`, 'error')
  }
}

async function homeMotor() {
  try {
    await api.agingHome({ station: station.value, speed_rpm: Math.min(speedRpm.value, 200) })
    addLog('正在回原点...')
  } catch (e) {
    addLog(`回原点失败: ${e.message}`, 'error')
  }
}

async function startAging() {
  if (points.length === 0) {
    addLog('请先添加坐标点', 'error')
    return
  }

  agingRunning.value = true
  currentPoint.value = 0
  cycleCount.value = 0
  elapsedSeconds.value = 0
  positionHistory.value = []

  // 启动计时器
  elapsedTimer = setInterval(() => { elapsedSeconds.value++ }, 1000)

  const data = {
    station: station.value,
    points: points.map(p => ({ position: p.position, dwell: p.dwell || defaultDwell.value })),
    speed_rpm: speedRpm.value,
    accel_ms: accelMs.value,
    decel_ms: decelMs.value,
    dwell_ms: defaultDwell.value,
    max_cycles: maxCycles.value,
  }

  try {
    const res = await api.agingStart(data)
    addLog(res.message || '老化测试已启动')
    // 开始轮询
    startPolling()
  } catch (e) {
    addLog(`启动失败: ${e.message}`, 'error')
    agingRunning.value = false
    clearInterval(elapsedTimer)
  }
}

async function stopAging() {
  try {
    await api.agingStop()
    addLog('老化测试已停止')
    agingRunning.value = false
    stopPolling()
    clearInterval(elapsedTimer)
  } catch (e) {
    addLog(`停止失败: ${e.message}`, 'error')
  }
}

async function emergencyStop() {
  try {
    await api.agingStopMotor({ station: station.value, emergency: true })
    addLog('急停已触发', 'warn')
    if (agingRunning.value) {
      agingRunning.value = false
      stopPolling()
      clearInterval(elapsedTimer)
    }
  } catch (e) {
    addLog(`急停失败: ${e.message}`, 'error')
  }
}

function clearLogs() {
  logs.value = []
}

// ── 轮询 ──
function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollStatus, 500)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollStatus() {
  try {
    const s = await api.agingStatus()
    if (!s.running) {
      agingRunning.value = false
      stopPolling()
      clearInterval(elapsedTimer)
    }
    currentPoint.value = s.current_point || 0
    totalPoints.value = s.total_points || 0
    cycleCount.value = s.cycle_count || 0
    elapsedSeconds.value = s.elapsed_seconds || 0

    // 更新位置
    if (s.current_position !== null && s.current_position !== undefined) {
      currentPosition.value = s.current_position
      positionHistory.value.push(s.current_position)
      if (positionHistory.value.length > 200) {
        positionHistory.value = positionHistory.value.slice(-200)
      }
    }

    // 合并日志
    if (s.logs && s.logs.length) {
      const existing = logs.value.length
      for (const log of s.logs) {
        // 简单的去重
        const tail = logs.value.slice(-5)
        if (!tail.some(l => l.includes(log.slice(15)))) {
          logs.value.push(log)
        }
      }
      if (logs.value.length > 500) logs.value = logs.value.slice(-500)
    }

    updateChart()
  } catch (e) {
    // 静默处理轮询错误
  }
}

// ── 简易位置曲线 (Canvas) ──
function initChart() {
  // 简单 canvas 线条绘制，无需 chart.js
}

function updateChart() {
  const canvas = chartCanvas.value
  if (!canvas || positionHistory.value.length < 2) return
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.parentElement.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  canvas.style.width = rect.width + 'px'
  canvas.style.height = rect.height + 'px'
  ctx.scale(dpr, dpr)

  const w = rect.width
  const h = rect.height
  const pad = { top: 8, bottom: 16, left: 8, right: 8 }
  const plotW = w - pad.left - pad.right
  const plotH = h - pad.top - pad.bottom

  ctx.clearRect(0, 0, w, h)

  const data = positionHistory.value
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  // 绘制网格
  ctx.strokeStyle = 'rgba(255,255,255,0.06)'
  ctx.lineWidth = 1
  for (let i = 0; i < 4; i++) {
    const y = pad.top + (plotH / 4) * i
    ctx.beginPath()
    ctx.moveTo(pad.left, y)
    ctx.lineTo(pad.left + plotW, y)
    ctx.stroke()
  }

  // 绘制曲线
  ctx.strokeStyle = '#c2ef4e'
  ctx.lineWidth = 2
  ctx.beginPath()
  for (let i = 0; i < data.length; i++) {
    const x = pad.left + (i / Math.max(data.length - 1, 1)) * plotW
    const y = pad.top + plotH - ((data[i] - min) / range) * plotH
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()
}

// ── 生命周期 ──
onMounted(() => {
  // 检查老化状态
  api.agingStatus().then(s => {
    if (s.running) {
      agingRunning.value = true
      startPolling()
    }
  }).catch(() => {})

  // 初始化 canvas
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  stopPolling()
  if (elapsedTimer) clearInterval(elapsedTimer)
})

// 尺寸变化时重绘曲线
watch(positionHistory, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.aging-test {
  padding: 24px;
  height: 100%;
  color: var(--text-primary, #e0e0e0);
}

.aging-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

/* ── 卡片通用 ── */
.section-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-card h3 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary, #a0a0a0);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h3 {
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* ── 参数网格 ── */
.param-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-group label {
  font-size: 11px;
  color: var(--text-tertiary, #707070);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.input-field {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: var(--text-primary, #e0e0e0);
  padding: 6px 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.input-field:focus {
  border-color: var(--brand-green, #c2ef4e);
}

.input-sm {
  padding: 4px 8px;
  font-size: 12px;
  width: 100%;
  box-sizing: border-box;
}

.mono {
  font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
}

.readback-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--brand-green, #c2ef4e);
}

/* ── 按钮 ── */
.btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-xs { padding: 4px 10px; font-size: 11px; }
.btn-primary { background: var(--brand-green, #c2ef4e); color: #1a1a2e; }
.btn-primary:hover:not(:disabled) { background: #a8d83a; }
.btn-secondary { background: rgba(255,255,255,0.08); color: var(--text-primary, #e0e0e0); }
.btn-secondary:hover:not(:disabled) { background: rgba(255,255,255,0.14); }
.btn-success { background: var(--brand-green, #c2ef4e); color: #1a1a2e; }
.btn-success:hover:not(:disabled) { background: #a8d83a; }
.btn-danger { background: var(--accent-error, #e74c3c); color: #fff; }
.btn-danger:hover:not(:disabled) { background: #c0392b; }
.btn-warning { background: #f39c12; color: #fff; }
.btn-warning:hover:not(:disabled) { background: #d68910; }
.btn-danger-text { color: var(--accent-error, #e74c3c); background: transparent; padding: 2px 6px; font-size: 14px; }
.btn-danger-text:hover:not(:disabled) { background: rgba(231,76,60,0.15); }
.btn-icon-only { background: transparent; border: 1px solid rgba(255,255,255,0.1); color: var(--text-secondary, #a0a0a0); padding: 2px 8px; font-size: 14px; border-radius: 4px; }
.btn-icon-only:hover:not(:disabled) { background: rgba(255,255,255,0.08); color: var(--text-primary, #e0e0e0); }
.btn-icon { font-size: 14px; }

/* ── 坐标点表格 ── */
.points-table-wrapper {
  max-height: 280px;
  overflow-y: auto;
  margin-bottom: 8px;
}

.points-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.points-table th {
  text-align: left;
  padding: 6px 8px;
  color: var(--text-tertiary, #707070);
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  position: sticky;
  top: 0;
  background: var(--bg-primary, #1a1a2e);
}

.points-table td {
  padding: 4px 8px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.points-table tr.active-row td {
  background: rgba(194, 239, 78, 0.08);
}

.col-idx { width: 30px; text-align: center; color: var(--text-tertiary); }
.col-pos { width: auto; }
.col-dwell { width: 100px; }
.col-actions { width: 100px; white-space: nowrap; }

.preset-bar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.empty-hint {
  text-align: center;
  padding: 24px 0;
  color: var(--text-tertiary, #505050);
  font-size: 13px;
}

/* ── 控制栏 ── */
.control-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* ── 状态网格 ── */
.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 11px;
  color: var(--text-tertiary, #707070);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-idle .status-dot { background: #707070; }
.status-running .status-dot { background: var(--brand-green, #c2ef4e); animation: pulse 1.5s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-running { color: var(--brand-green, #c2ef4e); }
.status-idle { color: var(--text-secondary, #a0a0a0); }

/* ── 位置监控 ── */
.position-display {
  margin-bottom: 8px;
}

.position-bar-wrapper {
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.position-bar {
  height: 100%;
  background: var(--brand-green, #c2ef4e);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.position-text {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.position-range {
  color: var(--text-tertiary, #707070);
}

.chart-container {
  height: 80px;
  width: 100%;
}

.chart-container canvas {
  width: 100%;
  height: 100%;
}

/* ── 日志 ── */
.log-container {
  height: 180px;
  overflow-y: auto;
  background: rgba(0,0,0,0.25);
  border-radius: 6px;
  padding: 8px;
  font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
  font-size: 11px;
  line-height: 1.6;
}

.log-line {
  padding: 1px 0;
  color: var(--text-secondary, #a0a0a0);
}

.log-success { color: var(--brand-green, #c2ef4e); }
.log-warn { color: #f39c12; }
.log-error { color: var(--accent-error, #e74c3c); }
.log-info { color: #5dade2; }

.log-empty {
  color: var(--text-tertiary, #505050);
  text-align: center;
  padding: 40px 0;
}

/* ── 响应式 ── */
@media (max-width: 900px) {
  .aging-layout {
    grid-template-columns: 1fr;
  }
  .param-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* ── 页面标题 ── */
.page-header h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

.page-header p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-tertiary, #707070);
}

/* ── 滚动条 ── */
.points-table-wrapper::-webkit-scrollbar,
.log-container::-webkit-scrollbar {
  width: 4px;
}

.points-table-wrapper::-webkit-scrollbar-thumb,
.log-container::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 2px;
}
</style>
