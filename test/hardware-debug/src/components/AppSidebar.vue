<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12,6 12,12 16,14"/>
        </svg>
      </div>
      <span class="brand-text">硬件配置平台</span>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in visibleNavItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span class="nav-label">{{ item.label }}</span>
        <span v-if="isActive(item.path)" class="nav-indicator"></span>
      </router-link>
    </nav>

    <!-- 底部：通信日志切换按钮 -->
    <div class="sidebar-footer">
      <button class="log-footer-btn" @click="toggleLogPanel">
        <span class="log-footer-icon">📋</span>
        <span class="log-footer-label">通信日志</span>
        <span class="log-footer-arrow">{{ logPanelExpanded ? '▼' : '▲' }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const route = useRoute()
const userStore = useUserStore()

const toggleLogPanel = inject('toggleLogPanel', () => {})
const logPanelExpanded = inject('logPanelExpanded', false)

const navItems = [
  {
    path: '/projects',
    label: '项目库',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>'
  }
]

const adminNavItems = [
  {
    path: '/hardware',
    label: '硬件库',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>'
  },
  {
    path: '/aging',
    label: '老化测试',
    icon: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>'
  }
]

const visibleNavItems = computed(() => {
  const items = [...navItems]
  if (userStore.isAdmin) {
    items.push(...adminNavItems)
  }
  return items
})

function isActive(path) {
  // 项目库下的子页面（硬件配置、质量检测）也高亮项目库
  if (path === '/projects' && (route.path.startsWith('/configure/') || route.path.startsWith('/inspect/'))) {
    return true
  }
  return route.path.startsWith(path)
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-surface);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  z-index: 20;
  overflow: hidden;
}

.sidebar-brand {
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: #FFFFFF;
  flex-shrink: 0;
}

.brand-text {
  font-family: var(--font-headings);
  font-size: var(--text-lg);
  font-weight: var(--fw-bold);
  color: var(--text-primary);
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 16px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  position: relative;
  min-height: 52px;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 24px;
  width: 3px;
  background: var(--color-primary);
  border-radius: 0 3px 3px 0;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.nav-item:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.nav-item.active {
  background: rgba(91, 107, 255, 0.18);
  color: var(--color-primary);
  font-weight: var(--fw-bold);
}

.nav-item.active::before {
  opacity: 1;
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-label {
  font-family: var(--font-headings);
  font-size: var(--text-base);
  font-weight: var(--fw-semibold);
  flex: 1;
}

.sidebar-footer {
  flex-shrink: 0;
  padding: 8px;
  border-top: 1px solid var(--border-default);
}

.log-footer-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-headings);
  font-size: var(--text-base);
  font-weight: var(--fw-semibold);
}

.log-footer-btn:hover {
  border-color: var(--color-border-strong);
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.04);
}

.log-footer-icon {
  font-size: 18px;
  line-height: 1;
}

.log-footer-label {
  flex: 1;
  text-align: left;
}

.log-footer-arrow {
  font-size: 11px;
  color: var(--text-tertiary);
}


</style>
