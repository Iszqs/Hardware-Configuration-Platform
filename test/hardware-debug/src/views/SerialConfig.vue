<template>
  <div class="serial-config-page">
    <div class="page-header">
      <div>
        <h1>串口配置</h1>
        <p>Modbus RTU 串口通信参数</p>
      </div>
    </div>

    <div class="config-section card">
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

      <div class="connect-row">
        <div class="status-display">
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
</template>

<script setup>
import { onMounted } from 'vue'
import { useSerialStore } from '../stores/serial'

const serialStore = useSerialStore()

onMounted(() => {
  serialStore.fetchPorts()
})
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}

.connect-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-default);
}

.status-display {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.933rem;
  color: var(--text-secondary);
}

.status-text {
  font-family: var(--font-headings);
  font-weight: 500;
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
