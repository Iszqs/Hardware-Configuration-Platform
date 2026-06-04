<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      <div class="modal">
        <div class="modal-header">
          <h2>串口配置</h2>
          <button class="close-btn" @click="handleClose" aria-label="关闭">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="config-panel">
            <div class="section-title">连接参数</div>
            <div class="form-grid">
              <div class="input-group">
                <label>串口号</label>
                <select class="input-field" v-model="serialStore.config.portName">
                  <option v-for="p in serialStore.availablePorts" :key="p" :value="p">{{ p }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>波特率</label>
                <select class="input-field" v-model="serialStore.config.baudRate">
                  <option v-for="r in [9600, 19200, 38400, 57600, 115200]" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>数据位</label>
                <select class="input-field" v-model="serialStore.config.dataBits">
                  <option v-for="d in [8,7,6,5]" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>校验</label>
                <select class="input-field" v-model="serialStore.config.parity">
                  <option value="none">无</option>
                  <option value="even">偶校验</option>
                  <option value="odd">奇校验</option>
                </select>
              </div>
            </div>

            <div class="status-section">
              <div class="status-row">
                <span class="led" :class="'led-' + serialStore.statusColor"></span>
                <span class="status-text">{{ serialStore.statusText }}</span>
              </div>
              <button
                v-if="!serialStore.connected"
                class="btn btn-primary"
                @click="serialStore.connect"
                :disabled="serialStore.connecting"
              >
                {{ serialStore.connecting ? '连接中...' : '连接' }}
              </button>
              <button v-else class="btn btn-danger" @click="serialStore.disconnect">断开</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useSerialStore } from '../stores/serial'

const props = defineProps({
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])
const serialStore = useSerialStore()

watch(() => props.visible, (val) => {
  if (val) {
    serialStore.fetchPorts()
  }
})

function handleClose() {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  width: 90%;
  max-width: 360px;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--elevation-lg);
  overflow: hidden;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-default);
}

.modal-header h2 {
  font-family: var(--font-headings);
  font-size: 1.2rem;
  font-weight: 600;
}

.close-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 16px;
  max-height: 70vh;
  overflow-y: auto;
}

@media (max-width: 700px) {
  .modal-body {
    max-height: 80vh;
  }
}

.config-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-family: var(--font-headings);
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-group label {
  font-family: var(--font-headings);
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-field {
  background: var(--bg-input);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 1rem;
}

.input-field:hover {
  border-color: var(--border-light);
}

.input-field:focus {
  border-color: var(--color-primary);
  box-shadow: var(--elevation-focus);
}

.status-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-default);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  color: var(--text-secondary);
}

:deep(.led) {
  width: 16px;
  height: 16px;
}

.modal .btn {
  height: 40px;
  font-size: 1rem;
}

.modal button, .modal select {
  touch-action: manipulation;
}
</style>
