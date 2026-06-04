<template>
  <div class="quality-inspect" v-if="project">
    <div class="page-header">
      <div>
        <router-link to="/projects" class="back-link">← 项目库</router-link>
        <h1>硬件检测</h1>
        <p>选择硬件进行检测</p>
      </div>
    </div>

    <div v-if="project.device_configs.length" class="device-grid">
      <div
        v-for="(cfg, idx) in project.device_configs"
        :key="idx"
        class="device-card"
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
          <div v-if="deviceResults[idx]" class="device-result-tag" :class="deviceResults[idx].passed ? 'pass' : 'fail'">
            {{ deviceResults[idx].passed ? '通过' : '未通过' }}
          </div>
          <button
            class="btn btn-primary"
            @click="inspectSingle(idx)"
            :disabled="inspectInProgress"
          >
            <span v-if="inspectInProgress" class="spinner"></span>
            {{ inspectInProgress ? '检测中...' : '检测' }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-devices">
      <p>暂无设备，请先添加设备</p>
    </div>

    <div v-if="inspectResults.length" class="inspect-results-section">
      <div class="inspect-overview">
        <span class="overview-text">
          检测结果：
          <strong :style="{ color: inspectPassCount === inspectResults.length ? 'var(--brand-green)' : 'var(--accent-error)' }">
            {{ inspectPassCount }}/{{ inspectResults.length }}
          </strong>
        </span>
        <button class="btn btn-secondary btn-sm" @click="clearInspectResults">清除结果</button>
      </div>
      <div class="inspect-results-list">
        <div
          v-for="(r, i) in inspectResults"
          :key="i"
          class="inspect-result-card"
          :class="r.passed ? 'pass' : 'fail'"
        >
          <div class="result-header">
            <span class="led" :class="r.passed ? 'led-success' : 'led-error'"></span>
            <span class="result-title">
              {{ projectStore.getCategoryLabel(r.category_id) }} / {{ projectStore.getDeviceTypeLabel(r.device_type_id) }}
            </span>
            <span v-if="r.purpose" class="result-purpose">{{ r.purpose }}</span>
          </div>
          <div class="check-items">
            <span v-for="(item, j) in r.items" :key="j" class="check-tag" :class="item.passed ? 'pass' : 'fail'">
              {{ item.name }}
            </span>
          </div>
          <div class="result-params">
            <span class="result-param">站号: {{ r.station_number }}</span>
            <span class="result-param">波特率: {{ r.baud_rate }}</span>
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
import { api } from '../api'

const route = useRoute()
const projectStore = useProjectStore()
const project = computed(() => projectStore.getProject(route.params.projectId))
const inspectInProgress = ref(false)
const inspectResults = ref([])
const deviceResults = ref({})

const inspectPassCount = computed(() => inspectResults.value.filter(r => r.passed).length)

async function inspectSingle(idx) {
  if (!project.value || inspectInProgress.value) return
  inspectInProgress.value = true
  
  const config = project.value.device_configs[idx]
  
  try {
    const result = await api.inspectModbus({
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      device_type_id: config.device_type_id
    })
    
    inspectResults.value.push({
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      passed: result.passed,
      items: result.items || []
    })
    
    deviceResults.value[idx] = { passed: result.passed }
  } catch (error) {
    inspectResults.value.push({
      device_type_id: config.device_type_id,
      category_id: config.category_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      purpose: config.purpose,
      passed: false,
      items: [{ name: '检测失败', passed: false }]
    })
    
    deviceResults.value[idx] = { passed: false }
  }
  
  inspectInProgress.value = false
}

function clearInspectResults() {
  inspectResults.value = []
  deviceResults.value = {}
}
</script>

<style scoped>
.back-link {
  font-family: var(--font-headings);
  font-size: 0.8125rem;
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

.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.device-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  min-height: 240px;
  justify-content: space-between;
}

.device-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
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

.device-header {
  margin-bottom: var(--spacing-md);
}

.category-tag {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  padding: 4px 12px;
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
  font-weight: var(--fw-bold);
  font-size: var(--text-md);
  color: var(--text-primary);
}

.device-purpose {
  font-family: var(--font-headings);
  font-size: var(--text-xl);
  font-weight: var(--fw-bold);
  color: var(--color-success);
  padding: 6px 14px;
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
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.param-value {
  font-size: var(--text-md);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
}

.empty-devices {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
  color: var(--text-dim);
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  border: 1px solid var(--border-default);
}

.device-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-default);
}

.device-card-footer .btn {
  flex: 1;
  font-size: var(--text-base);
  font-weight: var(--fw-semibold);
  padding: 10px 16px;
  min-height: 44px;
}

.device-result-tag {
  font-family: var(--font-headings);
  font-size: 0.9375rem;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.device-result-tag.pass {
  background: rgba(43, 224, 140, 0.12);
  color: var(--color-success);
}

.device-result-tag.fail {
  background: rgba(255, 58, 92, 0.12);
  color: var(--color-error);
}

.inspect-results-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-default);
}

.inspect-overview {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  font-size: var(--text-md);
  color: var(--text-secondary);
}

.overview-text strong {
  font-family: var(--font-headings);
  font-weight: 700;
  font-size: 1.25rem;
}

.inspect-results-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.inspect-result-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.inspect-result-card.pass {
  border-color: rgba(43, 224, 140, 0.2);
}

.inspect-result-card.fail {
  border-color: rgba(255, 58, 92, 0.2);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.result-title {
  font-family: var(--font-headings);
  font-weight: var(--fw-bold);
  font-size: var(--text-md);
}

.result-purpose {
  font-family: var(--font-headings);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-success);
  background: rgba(43, 224, 140, 0.15);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(43, 224, 140, 0.3);
}

.check-items {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.check-tag {
  font-family: var(--font-headings);
  font-size: 1rem;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: var(--radius-md);
}

.check-tag.pass {
  background: rgba(43, 224, 140, 0.1);
  color: var(--color-success);
}

.check-tag.fail {
  background: rgba(255, 58, 92, 0.1);
  color: var(--color-error);
}

.result-params {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-default);
  font-size: var(--text-base);
  color: var(--text-secondary);
}

.result-param {
  font-family: var(--font-mono);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin-right: var(--spacing-sm);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>