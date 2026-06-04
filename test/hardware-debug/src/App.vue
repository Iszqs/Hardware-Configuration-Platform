<template>
  <div class="app-shell">
    <AppSidebar />
    <main class="main-content">
      <header class="top-bar">
        <div class="top-bar-actions">
          <UserSwitch />
          <div class="serial-status-badge" @click="showSerialModal = true" aria-label="串口状态" role="button" tabindex="0">
            <span class="led" :class="'led-' + serialStore.statusColor"></span>
            <span class="serial-status-text">{{ serialStore.connectionInfo }}</span>
          </div>
        </div>
      </header>
      <div class="page-container" :class="{ 'with-log-panel': logPanelExpanded }">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="userKey" />
          </transition>
        </router-view>
      </div>
      <LogPanel ref="logPanelRef" />
    </main>
    <SerialModal :visible="showSerialModal" @close="showSerialModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, provide } from 'vue'
import { useSerialStore } from './stores/serial'
import { useUserStore } from './stores/user'
import { useProjectStore } from './stores/projects'
import AppSidebar from './components/AppSidebar.vue'
import SerialModal from './components/SerialModal.vue'
import UserSwitch from './components/UserSwitch.vue'
import LogPanel from './components/LogPanel.vue'

const serialStore = useSerialStore()
const userStore = useUserStore()
const projectStore = useProjectStore()
const showSerialModal = ref(false)
const logPanelRef = ref(null)
const logPanelExpanded = ref(false)

function toggleLogPanel() {
  if (logPanelRef.value) {
    logPanelRef.value.toggle()
    logPanelExpanded.value = !logPanelExpanded.value
  }
}

// 提供给侧边栏使用
provide('toggleLogPanel', toggleLogPanel)
provide('logPanelExpanded', logPanelExpanded)

onMounted(async () => {
  await projectStore.init()
  serialStore.autoConnect('COM2')
  // 尝试恢复串口状态同步（后端可能已连接）
  serialStore.startPolling()
})

// 使用userStore.role作为key，角色变化时重新渲染所有组件
const userKey = computed(() => userStore.role)
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}

.top-bar {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
  z-index: 10;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.serial-status-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 8px 18px;
  height: 40px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.serial-status-badge:hover {
  border-color: var(--color-border-strong);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.serial-status-text {
  font-family: var(--font-headings);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.page-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  transition: flex var(--transition-normal);
}

@media (max-width: 768px) {
  .page-container {
    padding: 20px 16px;
  }

  .top-bar {
    padding: 0 16px;
  }
}
</style>
