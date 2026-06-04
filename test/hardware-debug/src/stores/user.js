import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const ROLES = {
  NORMAL: 'normal',
  ADMIN: 'admin'
}

const STORAGE_KEY = 'hardware_user_role'

function loadRole() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && Object.values(ROLES).includes(saved)) {
      return saved
    }
  } catch (e) {
    console.error('Failed to load role:', e)
  }
  return ROLES.NORMAL
}

function saveRole(role) {
  try {
    localStorage.setItem(STORAGE_KEY, role)
  } catch (e) {
    console.error('Failed to save role:', e)
  }
}

export const useUserStore = defineStore('user', () => {
  const currentRole = ref(loadRole())

  const isAdmin = computed(() => currentRole.value === ROLES.ADMIN)
  const isNormal = computed(() => currentRole.value === ROLES.NORMAL)
  const roleLabel = computed(() => {
    return currentRole.value === ROLES.ADMIN ? '管理员' : '普通用户'
  })

  function toggleRole() {
    currentRole.value = currentRole.value === ROLES.ADMIN ? ROLES.NORMAL : ROLES.ADMIN
    saveRole(currentRole.value)
  }

  function setRole(role) {
    if (Object.values(ROLES).includes(role)) {
      currentRole.value = role
      saveRole(currentRole.value)
    }
  }

  return {
    currentRole,
    isAdmin,
    isNormal,
    roleLabel,
    toggleRole,
    setRole,
    ROLES
  }
})
