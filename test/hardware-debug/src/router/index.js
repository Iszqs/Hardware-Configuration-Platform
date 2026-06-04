import { createRouter, createWebHistory } from 'vue-router'

const STORAGE_KEY = 'hardware_user_role'

function isAdmin() {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'admin'
  } catch (e) {
    return false
  }
}

const routes = [
  {
    path: '/',
    redirect: '/projects'
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: () => import('../views/ProjectList.vue'),
    meta: { title: '项目库', icon: 'projects' }
  },
  {
    path: '/hardware',
    name: 'HardwareLibrary',
    component: () => import('../views/HardwareLibrary.vue'),
    meta: { title: '硬件库', icon: 'hardware', requiresAdmin: true }
  },
  {
    path: '/serial',
    name: 'SerialConfig',
    component: () => import('../views/SerialConfig.vue'),
    meta: { title: '串口配置', icon: 'serial' }
  },
  {
    path: '/configure/:projectId',
    name: 'OneClickConfig',
    component: () => import('../views/OneClickConfig.vue'),
    meta: { title: '硬件配置', icon: 'configure' }
  },
  {
    path: '/inspect/:projectId',
    name: 'QualityInspect',
    component: () => import('../views/QualityInspect.vue'),
    meta: { title: '质量检测', icon: 'inspect' }
  },
  {
    path: '/aging',
    name: 'AgingTest',
    component: () => import('../views/AgingTest.vue'),
    meta: { title: '老化测试', icon: 'aging' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 注册一个全局前置守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !isAdmin()) {
    // 普通用户尝试访问管理员页面，重定向到项目库
    next('/projects')
  } else {
    next()
  }
})

export default router
