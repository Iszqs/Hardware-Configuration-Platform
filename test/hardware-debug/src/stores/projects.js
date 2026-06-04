import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'

const STORAGE_KEY = 'hardware_projects_data'
const DEFAULT_BAUD_RATES = [115200, 9600]

export const useProjectStore = defineStore('projects', () => {
  const projects = ref([])
  const categories = ref([])
  const allDeviceTypes = ref([])
  const loaded = ref(false)

  const subTypes = computed(() => {
    const map = {}
    for (const device of allDeviceTypes.value) {
      if (!map[device.category_id]) {
        map[device.category_id] = []
      }
      map[device.category_id].push({ id: device.id, label: device.label })
    }
    return map
  })

  const projectList = computed(() => projects.value)

  async function init() {
    const hasData = await api.checkHasData()

    if (!hasData.has_data) {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
          const data = JSON.parse(saved)
          await api.importData({
            categories: data.categories || [],
            allDeviceTypes: data.allDeviceTypes || [],
            projects: data.projects || []
          })
          localStorage.removeItem(STORAGE_KEY)
        }
      } catch (e) {
        console.error('数据迁移失败:', e)
      }
    }

    await refreshAll()
    loaded.value = true
  }

  async function refreshAll() {
    const [cats, types, projs] = await Promise.all([
      api.getCategories(),
      api.getDeviceTypes(),
      api.getProjects(),
    ])
    categories.value = cats
    allDeviceTypes.value = types
    projects.value = projs
  }

  function getProject(id) {
    const pid = Number(id)
    return projects.value.find(p => p.id === pid)
  }

  async function addProject(project) {
    const created = await api.createProject({
      name: project.name,
      description: project.description || ''
    })
    projects.value.push(created)
    return created.id
  }

  async function updateProject(id, data) {
    const pid = Number(id)
    await api.updateProject(pid, {
      name: data.name,
      description: data.description
    })
    
    if (data.device_configs && Array.isArray(data.device_configs)) {
      for (const config of data.device_configs) {
        if (config.id) {
          await api.updateDeviceConfig(config.id, {
            station_number: config.station_number,
            baud_rate: config.baud_rate,
            data_bits: config.data_bits,
            stop_bits: config.stop_bits,
            parity: config.parity,
            custom_name: config.custom_name,
            purpose: config.purpose
          })
        } else {
          await api.addDeviceConfig(pid, {
            category_id: config.category_id,
            device_type_id: config.device_type_id,
            station_number: config.station_number,
            baud_rate: config.baud_rate,
            data_bits: config.data_bits,
            stop_bits: config.stop_bits,
            parity: config.parity,
            custom_name: config.custom_name || '',
            purpose: config.purpose || ''
          })
        }
      }
    }
    await refreshAll()
  }

  async function deleteProject(id) {
    const pid = Number(id)
    await api.deleteProject(pid)
    projects.value = projects.value.filter(p => p.id !== pid)
  }

  async function addDeviceConfig(projectId, deviceTypeId) {
    const dt = allDeviceTypes.value.find(d => d.id === deviceTypeId)
    if (!dt) return
    const config = await api.addDeviceConfig(Number(projectId), {
      category_id: dt.category_id,
      device_type_id: deviceTypeId,
      station_number: 1,
      baud_rate: 9600,
      data_bits: 8,
      stop_bits: 1,
      parity: 'none'
    })
    await refreshAll()
    return config
  }

  async function removeDeviceConfig(projectId, configIndex) {
    const project = getProject(projectId)
    if (!project || !project.device_configs[configIndex]) return
    const cfgId = project.device_configs[configIndex].id
    await api.deleteDeviceConfig(cfgId)
    await refreshAll()
  }

  async function updateDeviceConfig(projectId, configIndex, data) {
    const project = getProject(projectId)
    if (!project || !project.device_configs[configIndex]) return
    const cfgId = project.device_configs[configIndex].id
    const payload = {}
    if (data.stationNumber !== undefined) payload.station_number = data.stationNumber
    if (data.baudRate !== undefined) payload.baud_rate = data.baudRate
    if (data.dataBits !== undefined) payload.data_bits = data.dataBits
    if (data.stopBits !== undefined) payload.stop_bits = data.stopBits
    if (data.parity !== undefined) payload.parity = data.parity
    if (data.customName !== undefined) payload.custom_name = data.customName
    if (data.purpose !== undefined) payload.purpose = data.purpose
    await api.updateDeviceConfig(cfgId, payload)
    await refreshAll()
  }

  function getDevicesByCategory(projectId, categoryId) {
    const project = getProject(projectId)
    if (!project) return []
    const cid = Number(categoryId)
    return project.device_configs.filter(d => d.category_id === cid)
  }

  function getDeviceTypeLabel(deviceTypeId) {
    const device = allDeviceTypes.value.find(d => d.id === deviceTypeId)
    return device ? device.label : String(deviceTypeId)
  }

  function getCategoryLabel(categoryId) {
    const category = categories.value.find(c => c.id === categoryId)
    return category ? category.label : String(categoryId)
  }

  function getDeviceFullPath(deviceTypeId) {
    const device = allDeviceTypes.value.find(d => d.id === deviceTypeId)
    if (!device) return String(deviceTypeId)
    const category = categories.value.find(c => c.id === device.category_id)
    return `${category ? category.label : ''} / ${device.label}`
  }

  function getCategoryByType(deviceTypeId) {
    const device = allDeviceTypes.value.find(d => d.id === deviceTypeId)
    return device ? device.category_id : null
  }

  async function addDeviceType(categoryId, label) {
    await api.createDeviceType({ label, category_id: Number(categoryId) })
    await refreshAll()
  }

  async function updateDeviceType(typeId, label) {
    await api.updateDeviceType(Number(typeId), { label })
    await refreshAll()
  }

  async function deleteDeviceType(categoryId, typeId) {
    await api.deleteDeviceType(Number(typeId))
    await refreshAll()
  }

  async function addCategory(label) {
    await api.createCategory({ label })
    await refreshAll()
  }

  async function deleteCategory(categoryId) {
    await api.deleteCategory(Number(categoryId))
    await refreshAll()
  }

  async function updateCategory(categoryId, label) {
    await api.updateCategory(Number(categoryId), { label })
    await refreshAll()
  }

  return {
    DEFAULT_BAUD_RATES,
    projects, categories, allDeviceTypes, subTypes, projectList, loaded,
    init, refreshAll,
    getProject,
    addProject, updateProject, deleteProject,
    addDeviceConfig, removeDeviceConfig, updateDeviceConfig,
    getDevicesByCategory,
    getDeviceTypeLabel, getCategoryLabel, getDeviceFullPath, getCategoryByType,
    addDeviceType, updateDeviceType, deleteDeviceType,
    addCategory, deleteCategory, updateCategory,
  }
})
