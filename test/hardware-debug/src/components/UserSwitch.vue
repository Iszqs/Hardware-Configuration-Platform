<template>
  <div class="user-switch">
    <button class="user-button" @click="toggleDropdown" aria-label="用户切换">
      <div class="user-avatar" :class="{ admin: userStore.isAdmin }">
        <svg v-if="userStore.isAdmin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM12 14a7 7 0 0 0-7 7h14a7 7 0 0 0-7-7z"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <span class="user-label">{{ userStore.roleLabel }}</span>
      <span class="arrow-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline :points="showDropdown ? '6 18 12 12 18 18' : '6 6 12 12 18 6'"/>
        </svg>
      </span>
    </button>
    <div v-if="showDropdown" class="dropdown-menu">
      <button
        class="dropdown-item"
        :class="{ active: userStore.isNormal }"
        @click="selectRole('normal')"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>普通用户</span>
      </button>
      <button
        class="dropdown-item"
        :class="{ active: userStore.isAdmin }"
        @click="selectRole('admin')"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zM12 14a7 7 0 0 0-7 7h14a7 7 0 0 0-7-7z"/>
        </svg>
        <span>管理员</span>
      </button>
    </div>
    <div v-if="showDropdown" class="dropdown-overlay" @click="showDropdown = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const router = useRouter()
const showDropdown = ref(false)

const adminOnlyPaths = ['/hardware']

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function selectRole(role) {
  userStore.setRole(role)
  showDropdown.value = false
  
  // 如果切换到普通用户并且在管理员专用页面，跳转到项目库
  if (role === 'normal' && adminOnlyPaths.includes(router.currentRoute.value.path)) {
    router.push('/projects')
  }
  // App.vue中的userKey会自动处理组件重新渲染
}
</script>

<style scoped>
.user-switch {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 8px 18px;
  height: 40px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: var(--font-headings);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.user-button:hover {
  border-color: var(--color-border-strong);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.user-avatar {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  border-radius: 50%;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.user-avatar.admin {
  background: rgba(91, 107, 255, 0.12);
  color: var(--color-primary);
}

.user-label {
  color: var(--text-secondary);
  white-space: nowrap;
}

.arrow-icon {
  color: var(--text-dim);
  transition: all var(--transition-fast);
  width: 18px;
  height: 18px;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 200px;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  z-index: 1000;
  overflow: hidden;
  animation: dropdown-appear 0.15s ease-out;
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-headings);
  font-size: 1rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  min-height: 48px;
}

.dropdown-item:hover {
  background: var(--bg-elevated);
}

.dropdown-item.active {
  background: rgba(91, 107, 255, 0.15);
  color: var(--color-primary);
  font-weight: 700;
}

.dropdown-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
}
</style>
