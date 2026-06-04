<template>
  <div class="log-panel" :class="{ expanded }">
    <!-- 面板标题栏 -->
    <div class="panel-header" @click="toggle">
      <div class="panel-header-left">
        <span class="panel-icon">📋</span>
        <span class="panel-title">通信日志</span>
        <span class="log-count mono" v-if="serialStore.logs.length">({{ serialStore.logs.length }})</span>
      </div>
      <div class="panel-header-right">
        <button class="btn btn-xs btn-secondary" @click.stop="serialStore.clearLogs" title="清空日志">清空</button>
        <button class="btn btn-xs toggle-btn" title="展开/收起">
          <span v-if="expanded">▼</span>
          <span v-else>▲</span>
        </button>
      </div>
    </div>

    <!-- 日志内容区 -->
    <div class="panel-body" ref="logBodyRef">
      <div v-for="(log, i) in serialStore.logs" :key="i" class="log-line" :class="'log-' + log.type">
        <span class="log-time mono">[{{ log.timestamp }}]</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      <div v-if="!serialStore.logs.length" class="log-empty">暂无通信日志</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useSerialStore } from '../stores/serial'

const serialStore = useSerialStore()
const logBodyRef = ref(null)
const expanded = ref(false)

let refreshTimer = null

function toggle() {
  expanded.value = !expanded.value
}

function startRefresh() {
  stopRefresh()
  refreshTimer = setInterval(() => {
    serialStore.fetchLogs()
  }, 2000)
}

function stopRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 展开时自动刷新，收起时停止（节省资源）
watch(expanded, (val) => {
  if (val) {
    serialStore.fetchLogs()
    startRefresh()
  } else {
    stopRefresh()
  }
})

// 日志更新时自动滚动到底部
watch(() => serialStore.logs.length, () => {
  if (!expanded.value) return
  nextTick(() => {
    if (logBodyRef.value) {
      logBodyRef.value.scrollTop = logBodyRef.value.scrollHeight
    }
  })
})

onUnmounted(() => {
  stopRefresh()
})

// 暴露 toggle 方法给父组件
defineExpose({ toggle })
</script>

<style scoped>
.log-panel {
  flex-shrink: 0;
  border-top: 1px solid var(--border-default);
  background: var(--bg-surface);
  overflow: hidden;
  transition: height 0.25s ease;
  height: 0;
}

.log-panel.expanded {
  height: 220px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 36px;
  padding: 0 16px;
  cursor: pointer;
  user-select: none;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-default);
}

.panel-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.panel-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-icon {
  font-size: 14px;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.log-count {
  font-size: 11px;
  color: var(--text-tertiary);
}

.panel-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 11px;
  padding: 2px 8px;
}

.toggle-btn:hover {
  color: var(--text-primary);
}

.panel-body {
  height: calc(220px - 36px);
  overflow-y: auto;
  padding: 8px 16px;
  font-family: var(--font-mono);
  font-size: var(--text-sm, 12px);
}

.log-line {
  padding: 2px 0;
  color: var(--text-secondary);
  display: flex;
  gap: 8px;
  line-height: 1.5;
}

.log-time {
  color: var(--text-dim);
  flex-shrink: 0;
}

.log-message {
  word-break: break-all;
}

.log-success {
  color: var(--color-success, #27ae60);
}

.log-error {
  color: var(--color-error, #e74c3c);
}

.log-warning {
  color: var(--color-warning, #f39c12);
}

.log-empty {
  text-align: center;
  padding: 40px 0;
  color: var(--text-dim);
}

.panel-body::-webkit-scrollbar {
  width: 4px;
}

.panel-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 2px;
}
</style>
