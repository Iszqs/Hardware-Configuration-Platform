<template>
  <div class="one-click-config" v-if="project">
    <div class="page-header">
      <div>
        <router-link to="/projects" class="back-link">← 项目库</router-link>
        <h1>硬件配置</h1>
      </div>
    </div>

    <div class="main-layout">
      <div class="left-section">
        <div v-if="project.device_configs.length" class="device-grid">
          <div
            v-for="(cfg, idx) in project.device_configs"
            :key="idx"
            class="device-card"
            :class="{
              'selected': selectedIndex === idx,
              'status-success': getDeviceStatus(idx) === 'success',
              'status-failed': getDeviceStatus(idx) === 'failed'
            }"
            @click="selectDevice(idx)"
          >
            <div class="device-header">
              <span class="category-tag">{{ projectStore.getCategoryLabel(cfg.category_id) }}</span>
            </div>
            <div class="device-main">
              <div class="device-name">{{ projectStore.getDeviceTypeLabel(cfg.device_type_id) }}</div>
              <div v-if="cfg.purpose" class="device-purpose">{{ cfg.purpose }}</div>
            </div>
            <div class="device-params">
              <div class="param">
                <span class="param-label">站号</span>
                <span class="param-value mono">{{ cfg.station_number }}</span>
              </div>
              <div class="param">
                <span class="param-label">波特率</span>
                <span class="param-value mono">{{ cfg.baud_rate }}</span>
              </div>
            </div>
            <div class="device-card-footer">
              <button
                class="btn btn-config"
                @click.stop="configSingle(idx)"
              >
                配置
              </button>
              <button
                class="btn btn-inspect"
                @click.stop="inspectSingle(idx)"
              >
                检测
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-devices">
          <p>暂无设备，请先添加设备</p>
        </div>
      </div>

      <div class="right-section">
        <!-- 结果 -->
        <div class="tab-content">
          <div v-if="lastResult" class="result-card" :class="'result-' + lastResult.status">
            <div class="result-type-title">📝 配置结果</div>
            <div class="result-header">
              <span v-if="lastResult.status === 'in_progress'" class="led led-scanning"></span>
              <span v-else class="led" :class="lastResult.status === 'success' ? 'led-success' : 'led-error'"></span>
              <span class="result-title">
                {{ projectStore.getCategoryLabel(lastResult.category_id) }} / {{ projectStore.getDeviceTypeLabel(lastResult.device_type_id) }}
              </span>
              <span v-if="lastResult.purpose" class="result-purpose">{{ lastResult.purpose }}</span>
            </div>
            <div class="check-items">
              <span class="check-tag" :class="lastResult.status === 'success' ? 'pass' : lastResult.status === 'in_progress' ? 'scanning' : 'fail'">
                {{ lastResult.message }}
              </span>
            </div>
            <div class="result-params" v-if="lastResult.status !== 'in_progress'">
              <span v-if="lastResult.device_type_id !== 2" class="result-param">站号: {{ lastResult.station_number }}</span>
              <span class="result-param">波特率: {{ lastResult.baud_rate }}</span>
            </div>
          </div>

          <div v-if="lastInspectResult" class="result-card" :class="lastInspectResult.passed ? 'result-success' : 'result-failed'">
            <div class="result-type-title">🔍 检测结果</div>
            <div class="result-header">
              <span class="led" :class="lastInspectResult.passed ? 'led-success' : 'led-error'"></span>
              <span class="result-title">
                {{ projectStore.getCategoryLabel(lastInspectResult.category_id) }} / {{ projectStore.getDeviceTypeLabel(lastInspectResult.device_type_id) }}
              </span>
              <span v-if="lastInspectResult.purpose" class="result-purpose">{{ lastInspectResult.purpose }}</span>
            </div>
            <div class="check-items">
              <span v-for="(item, j) in lastInspectResult.items" :key="j" class="check-tag" :class="item.passed ? 'pass' : 'fail'">
                {{ item.name }}
              </span>
            </div>
            <div class="result-params">
              <span v-if="lastInspectResult.device_type_id !== 2" class="result-param">站号: {{ lastInspectResult.station_number }}</span>
              <span class="result-param">波特率: {{ lastInspectResult.baud_rate }}</span>
            </div>
          </div>

          <div v-if="!lastResult && !lastInspectResult" class="empty-guide">
            <div class="guide-header">📋 使用说明</div>

            <div class="guide-card guide-step">
              <div class="guide-card-icon">①</div>
              <div class="guide-card-body">
                <span class="guide-step-text">先执行「<strong>配置</strong>」，再执行「<strong>检测</strong>」</span>
              </div>
            </div>

            <div class="guide-card">
              <div class="guide-card-icon">②</div>
              <div class="guide-card-body">
                <div class="guide-device-label">57 电机</div>
                <ul class="guide-list">
                  <li>仅支持波特率配置</li>
                  <li>站号需通过手动拨码设置</li>
                </ul>
              </div>
            </div>

            <div class="guide-card">
              <div class="guide-card-icon">③</div>
              <div class="guide-card-body">
                <div class="guide-device-label">35 电机</div>
                <ul class="guide-list">
                  <li>站号和波特率均支持配置</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="empty-hint">
    项目不存在 <router-link to="/projects">返回项目库</router-link>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import { useSerialStore } from '../stores/serial'
import { api } from '../api'

const route = useRoute()
const projectStore = useProjectStore()
const serialStore = useSerialStore()
const project = computed(() => {
  projectStore.categories
  projectStore.allDeviceTypes
  return projectStore.getProject(route.params.projectId)
})
const configInProgress = ref(false)
const selectedIndex = ref(null)
const lastResult = ref(null)

const inspectInProgress = ref(false)
const lastInspectResult = ref(null)
const deviceStatuses = ref({}) // { idx: { configSuccess: bool|null, inspectSuccess: bool|null } }

function getDeviceStatus(idx) {
  const status = deviceStatuses.value[idx]
  if (!status) return null
  if (status.configSuccess && status.inspectSuccess) return 'success'
  if (status.configSuccess === false || status.inspectSuccess === false) return 'failed'
  return null
}

function selectDevice(idx) {
  if (configInProgress.value || inspectInProgress.value) return
  selectedIndex.value = selectedIndex.value === idx ? null : idx
}

async function configSingle(idx) {
  if (!project.value || configInProgress.value) return
  selectedIndex.value = idx
  configInProgress.value = true
  const config = project.value.device_configs[idx]

  try {
    lastResult.value = {
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      status: 'in_progress',
      message: '正在配置...'
    }

    const is35Motor = projectStore.getDeviceTypeLabel(config.device_type_id).includes('35')
    let result

    if (is35Motor) {
      result = await api.writeModbusConfig35({
        current_station: 1,
        target_station: config.station_number,
        target_baud_rate: config.baud_rate
      })
    } else {
      result = await api.writeModbusConfig57({
        station_number: config.station_number,
        baud_rate: config.baud_rate
      })
    }

    if (result.current_baud_rate) {
      serialStore.config.baudRate = result.current_baud_rate
    }

    if (result.success) {
      serialStore.config.baudRate = config.baud_rate
    }

    lastResult.value = {
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      status: result.success ? 'success' : 'failed',
      message: result.message || (result.success ? '配置成功' : '配置失败')
    }

    // 更新设备状态
    if (!deviceStatuses.value[idx]) {
      deviceStatuses.value[idx] = { configSuccess: null, inspectSuccess: null }
    }
    deviceStatuses.value[idx].configSuccess = result.success
  } catch (error) {
    lastResult.value = {
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      status: 'failed',
      message: '配置失败：' + (error.message || '未知错误')
    }
    // 更新设备状态
    if (!deviceStatuses.value[idx]) {
      deviceStatuses.value[idx] = { configSuccess: null, inspectSuccess: null }
    }
    deviceStatuses.value[idx].configSuccess = false
  }

  configInProgress.value = false
}

async function inspectSingle(idx) {
  if (!project.value || inspectInProgress.value) return
  selectedIndex.value = idx
  inspectInProgress.value = true

  const config = project.value.device_configs[idx]

  try {
    const is35Motor = projectStore.getDeviceTypeLabel(config.device_type_id).includes('35')
    let result

    if (is35Motor) {
      result = await api.inspectModbus35({
        station_number: config.station_number,
        target_station: config.station_number,
        target_baud_rate: config.baud_rate
      })
    } else {
      result = await api.inspectModbus57({
        station_number: config.station_number,
        baud_rate: config.baud_rate
      })
    }

    if (result.current_baud_rate) {
      serialStore.config.baudRate = result.current_baud_rate
    }

    lastInspectResult.value = {
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      passed: result.passed,
      items: result.items || []
    }

    // 更新设备状态
    if (!deviceStatuses.value[idx]) {
      deviceStatuses.value[idx] = { configSuccess: null, inspectSuccess: null }
    }
    deviceStatuses.value[idx].inspectSuccess = result.passed
  } catch (error) {
    lastInspectResult.value = {
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      passed: false,
      items: [{ name: '检测失败', passed: false }]
    }
    // 更新设备状态
    if (!deviceStatuses.value[idx]) {
      deviceStatuses.value[idx] = { configSuccess: null, inspectSuccess: null }
    }
    deviceStatuses.value[idx].inspectSuccess = false
  }

  inspectInProgress.value = false
}
</script>

<style scoped>
.back-link {
  font-family: var(--font-headings);
  font-size: var(--text-sm);
  color: var(--text-dim);
  margin-bottom: var(--spacing-xs);
  display: inline-flex;
  align-items: center;
}

.back-link:hover {
  color: var(--color-primary);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: var(--spacing-lg);
  align-items: stretch;
}

.left-section {
  min-height: 500px;
}

.right-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  max-height: 650px;
  display: flex;
  flex-direction: column;
}

.result-tabs button.active {
  color: var(--color-primary);
  background: rgba(91, 107, 255, 0.12);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  border-bottom-color: var(--color-primary);
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.btn {
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.9rem;
  min-height: auto;
  height: auto;
}

.btn-secondary {
  background: var(--bg-elevated);
  border-color: var(--border-default);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-light);
}

.empty-guide {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px 0;
}

.guide-header {
  font-family: var(--font-headings);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.guide-card {
  display: flex;
  gap: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  align-items: flex-start;
}

.guide-card-icon {
  font-size: 1.3rem;
  line-height: 1;
  flex-shrink: 0;
  width: 28px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guide-card-body {
  flex: 1;
  min-width: 0;
}

.guide-step-text {
  font-size: 0.95rem;
  color: var(--text-primary);
  line-height: 1.5;
}

.guide-step-text strong {
  color: var(--color-primary);
}

.guide-device-label {
  font-family: var(--font-headings);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.guide-list {
  margin: 0;
  padding-left: 16px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.7;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.device-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  min-height: var(--card-min-height);
  justify-content: space-between;
}

.device-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--color-primary), var(--color-secondary), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.device-card:hover::before {
  opacity: 1;
}

.device-card:hover {
  border-color: var(--color-border-strong);
  background: var(--bg-elevated);
  box-shadow: var(--elevation-md);
  transform: scale(1.02) translateY(-2px);
}

.device-card.selected {
  border-color: var(--color-primary);
  background: rgba(91, 107, 255, 0.1);
}

.device-card.status-success {
  border-color: var(--color-success);
}

.device-card.status-failed {
  border-color: var(--color-error);
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.category-tag {
  font-size: var(--card-label-font-size);
  font-weight: var(--card-label-font-weight);
  color: var(--text-secondary);
  background: var(--bg-elevated);
  padding: 6px 14px;
  border-radius: var(--radius-full);
}

.device-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.device-name {
  font-family: var(--font-headings);
  font-weight: var(--card-title-font-weight);
  font-size: var(--card-title-font-size);
  color: var(--text-primary);
}

.device-purpose {
  font-family: var(--font-headings);
  font-size: var(--text-xl);
  font-weight: var(--fw-bold);
  color: var(--color-success);
  padding: 8px 16px;
  background: rgba(43, 224, 140, 0.15);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(43, 224, 140, 0.3);
}

.device-params {
  display: flex;
  gap: var(--spacing-md);
}

.param {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.param-label {
  font-size: var(--card-label-font-size);
  font-weight: var(--card-label-font-weight);
  color: var(--text-secondary);
}

.param-value {
  font-size: var(--text-md);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
}

.empty-devices {
  text-align: center;
  padding: var(--spacing-2xl) var(--spacing-lg);
  color: var(--text-dim);
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-default);
}

.result-card {
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-md);
  border: 2px solid;
}

.result-type-title {
  font-family: var(--font-headings);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--border-light);
}

.result-success {
  background: rgba(43, 224, 140, 0.1);
  border-color: rgba(43, 224, 140, 0.4);
}

.result-failed {
  background: rgba(255, 58, 92, 0.1);
  border-color: rgba(255, 58, 92, 0.4);
}

.result-in_progress {
  background: rgba(255, 193, 7, 0.1);
  border-color: rgba(255, 193, 7, 0.4);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.led {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}

.led-success {
  background: var(--color-success);
  box-shadow: 0 0 12px rgba(43, 224, 140, 0.6);
}

.led-error {
  background: var(--color-error);
  box-shadow: 0 0 12px rgba(255, 58, 92, 0.6);
}

.led-scanning {
  background: var(--color-warning);
  box-shadow: 0 0 12px rgba(255, 193, 7, 0.6);
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.9); }
}

.result-title {
  font-family: var(--font-headings);
  font-weight: var(--fw-bold);
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.result-purpose {
  font-family: var(--font-headings);
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-success);
  background: rgba(43, 224, 140, 0.15);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(43, 224, 140, 0.3);
}

.result-param {
  display: flex;
  gap: var(--spacing-xs);
}

.check-items {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
}

.check-tag {
  font-family: var(--font-headings);
  font-size: 1.0625rem;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: var(--radius-md);
}

.check-tag.pass {
  background: rgba(43, 224, 140, 0.15);
  color: var(--color-success);
}

.check-tag.fail {
  background: rgba(255, 58, 92, 0.15);
  color: var(--color-error);
}

.check-tag.scanning {
  background: rgba(255, 193, 7, 0.15);
  color: var(--color-warning);
}

.result-params {
  display: flex;
  gap: var(--spacing-xl);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-default);
  font-size: 1.0625rem;
  color: var(--text-secondary);
}

.device-card-footer {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-default);
}

.device-card-footer .btn {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 16px;
  min-height: 48px;
}

.btn-config {
  background: var(--color-success);
  border-color: var(--color-success);
  color: #FFFFFF;
}

.btn-config:hover:not(:disabled) {
  background: #22c778;
  border-color: #22c778;
}

.btn-config:disabled {
  background: rgba(43, 224, 140, 0.4);
  border-color: rgba(43, 224, 140, 0.4);
  color: rgba(255, 255, 255, 0.6);
}

.btn-inspect {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #FFFFFF;
}

.btn-inspect:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-inspect:disabled {
  background: rgba(91, 107, 255, 0.4);
  border-color: rgba(91, 107, 255, 0.4);
  color: rgba(255, 255, 255, 0.6);
}
</style>
