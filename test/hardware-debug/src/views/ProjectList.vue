<template>
  <div class="project-list-page">
    <div class="page-header">
      <div>
        <h1>项目库</h1>
      </div>
      <div class="header-actions">
        <button v-if="userStore.isAdmin" class="btn btn-primary" @click="showCreateDialog = true">+ 新建项目</button>
      </div>
    </div>

    <div class="projects-grid">
      <div
        v-for="p in projectStore.projectList"
        :key="p.id"
        class="project-card card card-glass"
        :class="{ selected: selectedProject?.id === p.id }"
        @click="selectProject(p)"
      >
        <div class="card-header">
          <h3>{{ p.name }}</h3>
        </div>
        <p class="card-desc">{{ p.description }}</p>
        <div class="device-summary">
          <span v-for="cat in getDeviceSummary(p)" :key="cat.id" class="device-badge">
            {{ cat.label }} ×{{ cat.count }}
          </span>
        </div>
        <div class="card-footer">
          <span class="device-count mono">{{ p.device_configs.length }} 硬件</span>
          <div class="card-hover-actions">
            <template v-if="!userStore.isNormal">
              <button class="btn btn-sm btn-secondary" @click.stop="startEdit(p)">编辑</button>
              <button class="btn btn-sm btn-danger" @click.stop="confirmDelete(p.id, p.name)">删除</button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <div v-if="projectStore.projectList.length === 0" class="empty-hint">
      暂无项目
    </div>

    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog card">
        <h2>新建项目</h2>
        <div class="form">
          <div class="input-group">
            <label>项目名称</label>
            <input class="input-field" v-model="newProject.name" placeholder="如：2100" autocomplete="name" />
          </div>
          <div class="input-group">
            <label>描述</label>
            <input class="input-field" v-model="newProject.description" placeholder="简要描述" autocomplete="off" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showCreateDialog = false">取消</button>
          <button class="btn btn-primary" @click="createProject" :disabled="!newProject.name.trim()">创建</button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="dialog-overlay" @click.self="showDeleteConfirm = false">
      <div class="dialog dialog-sm card">
        <h2>确认删除</h2>
        <p>确定删除项目「{{ deletingName }}」？</p>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showDeleteConfirm = false">取消</button>
          <button class="btn btn-danger" @click="doDelete">删除</button>
        </div>
      </div>
    </div>

    <div v-if="showEditDialog" class="dialog-overlay" @click.self="showEditDialog = false">
      <div class="dialog card" style="width: 560px;">
        <h2>编辑项目</h2>
        <div class="form">
          <div class="input-group">
            <label>项目名称</label>
            <input class="input-field" v-model="editingProject.name" placeholder="如：2100" autocomplete="name" />
          </div>
          <div class="input-group">
            <label>描述</label>
            <input class="input-field" v-model="editingProject.description" placeholder="简要描述" autocomplete="off" />
          </div>
          
          <div class="input-group">
            <label>选择硬件分类</label>
            <div class="category-selection">
              <div class="category-tabs">
                <button
                  v-for="category in projectStore.categories"
                  :key="category.id"
                  class="category-tab"
                  :class="{ active: selectedCategory === category.id }"
                  @click="selectedCategory = category.id"
                >
                  {{ category.label }}
                </button>
              </div>
              <div v-if="selectedCategory" class="category-devices">
                <button
                  v-for="subType in projectStore.subTypes[selectedCategory]"
                  :key="subType.id"
                  class="device-add-btn"
                  @click="addDeviceToEdit(subType.id)"
                >
                  + {{ subType.label }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="editingProject.device_configs.length > 0" class="input-group">
            <label>硬件参数配置</label>
            <div class="device-edit-list">
              <div v-for="(config, index) in editingProject.device_configs" :key="index" class="device-edit-item">
                <div class="device-edit-top">
                  <div class="device-edit-info">
                    <div class="device-name-wrapper">
                      <input 
                        v-if="config.editingName" 
                        type="text" 
                        class="input-field device-name-input" 
                        v-model="config.custom_name" 
                        @blur="saveDeviceName(index)"
                        @keyup.enter="saveDeviceName(index)"
                        @keyup.escape="cancelEditName(index)"
                      />
                      <span v-else class="device-edit-label">{{ config.custom_name || projectStore.getDeviceTypeLabel(config.device_type_id) }}</span>
                    </div>
                  </div>
                  <button class="btn btn-sm btn-danger" @click="removeDeviceFromEdit(index)">删除</button>
                </div>
                <div class="device-edit-fields">
                  <div class="device-edit-field station-field">
                    <label class="device-field-label">站号</label>
                    <input type="number" class="input-field device-input" v-model.number="config.station_number" min="1" max="247" autocomplete="off" />
                  </div>
                  <div class="device-edit-field baud-field">
                    <label class="device-field-label">波特率</label>
                    <select class="input-field device-input" v-model="config.baud_rate">
                      <option v-for="rate in projectStore.DEFAULT_BAUD_RATES" :key="rate" :value="rate">{{ rate }}</option>
                    </select>
                  </div>
                  <div class="device-edit-field">
                    <label class="device-field-label">用途</label>
                    <input type="text" class="input-field device-input" v-model="config.purpose" autocomplete="off" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showEditDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveEdit" :disabled="!editingProject.name.trim()">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import { useUserStore } from '../stores/user'
import { api } from '../api'

const router = useRouter()
const projectStore = useProjectStore()
const userStore = useUserStore()
const showCreateDialog = ref(false)
const showDeleteConfirm = ref(false)
const showEditDialog = ref(false)
const deletingId = ref(null)
const deletingName = ref('')
const editingProject = reactive({ id: '', name: '', description: '', device_configs: [] })
const removedConfigIds = ref([])

const newProject = reactive({ name: '', description: '' })

const selectedProject = ref(null)
const selectedCategory = ref(null)

function selectProject(project) {
  // 任何用户点击有设备的项目卡片都跳转到配置页面
  if (project.device_configs.length > 0) {
    router.push('/configure/' + project.id)
    return
  }
  
  // 只有管理员才能选中没有设备的项目卡片进行编辑等操作
  if (userStore.isAdmin) {
    if (selectedProject.value?.id === project.id) {
      selectedProject.value = null
    } else {
      selectedProject.value = project
    }
  }
}

function getDeviceSummary(project) {
  const summary = []
  for (const cat of projectStore.categories) {
    const count = project.device_configs.filter(d => d.category_id === cat.id).length
    if (count > 0) {
      summary.push({ id: cat.id, label: cat.label, count })
    }
  }
  return summary
}

async function createProject() {
  await projectStore.addProject({
    name: newProject.name.trim(),
    description: newProject.description.trim(),
    device_configs: []
  })
  showCreateDialog.value = false
  Object.assign(newProject, { name: '', description: '' })
}

function confirmDelete(id, name) {
  deletingId.value = id
  deletingName.value = name
  showDeleteConfirm.value = true
}

async function doDelete() {
  await projectStore.deleteProject(deletingId.value)
  showDeleteConfirm.value = false
}

function startEdit(project) {
  editingProject.id = project.id
  editingProject.name = project.name
  editingProject.description = project.description
  // 深拷贝设备配置，避免直接修改原始数据
  editingProject.device_configs = JSON.parse(JSON.stringify(project.device_configs))
  showEditDialog.value = true
}

function addDeviceToEdit(typeId) {
  const categoryId = projectStore.getCategoryByType(typeId)
  const existing = editingProject.device_configs.filter(d => d.device_type_id === typeId)
  const newStationNumber = existing.length > 0
    ? Math.max(...existing.map(d => d.station_number)) + 1
    : 1
  
  editingProject.device_configs.push({
    category_id: categoryId,
    device_type_id: typeId,
    station_number: newStationNumber,
    baud_rate: 9600,
    data_bits: 8,
    stop_bits: 1,
    parity: 'none',
    custom_name: projectStore.getDeviceTypeLabel(typeId),
    purpose: ''
  })
}

function removeDeviceFromEdit(index) {
  const config = editingProject.device_configs[index]
  if (config.id) {
    removedConfigIds.value.push(config.id)
  }
  editingProject.device_configs.splice(index, 1)
}

function startEditName(index) {
  const config = editingProject.device_configs[index]
  config.editingName = true
}

function saveDeviceName(index) {
  const config = editingProject.device_configs[index]
  config.editingName = false
}

function cancelEditName(index) {
  const config = editingProject.device_configs[index]
  config.editingName = false
}

async function saveEdit() {
  if (editingProject.id && editingProject.name.trim()) {
    for (const configId of removedConfigIds.value) {
      await api.deleteDeviceConfig(configId)
    }
    removedConfigIds.value = []

    await projectStore.updateProject(editingProject.id, {
      name: editingProject.name.trim(),
      description: editingProject.description.trim(),
      device_configs: JSON.parse(JSON.stringify(editingProject.device_configs))
    })
    showEditDialog.value = false
    resetEdit()
  }
}

function resetEdit() {
  editingProject.id = ''
  editingProject.name = ''
  editingProject.description = ''
  editingProject.device_configs = []
  selectedCategory.value = null
  removedConfigIds.value = []
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
  grid-auto-rows: 1fr;
}

.project-card {
  display: flex;
  flex-direction: column;
  transition: all var(--transition-normal);
  cursor: pointer;
  border: 1px solid var(--border-default);
  padding: var(--spacing-lg);
  min-height: var(--card-min-height);
  position: relative;
  justify-content: space-between;
}

.project-card:hover {
  background: var(--bg-elevated);
  border-color: var(--color-border-strong);
  box-shadow: var(--elevation-md);
  transform: scale(1.02) translateY(-2px);
}

.project-card.selected {
  background: rgba(91, 107, 255, 0.1);
  border-color: var(--color-primary);
}

.project-card::after {
  content: '→';
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  font-size: 1.25rem;
  color: var(--text-dim);
  opacity: 0;
  transition: all var(--transition-fast);
}

.project-card:hover::after {
  opacity: 1;
  color: var(--color-primary);
}

.card-header {
  margin-bottom: var(--spacing-sm);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.project-radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  color: transparent;
  flex-shrink: 0;
}

.project-card.selected .project-radio {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #FFFFFF;
}

.card-header h3 {
  font-size: var(--card-title-font-size);
  font-weight: var(--card-title-font-weight);
  color: var(--text-primary);
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.card-desc {
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--spacing-lg);
}

.device-summary {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.device-badge {
  font-family: var(--font-headings);
  font-size: var(--card-label-font-size);
  font-weight: var(--card-label-font-weight);
  padding: 6px 16px;
  background: rgba(91, 107, 255, 0.12);
  color: var(--color-primary-hover);
  border-radius: var(--radius-full);
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--spacing-lg);
  border-top: 2px solid var(--border-default);
}

.device-count {
  font-size: var(--card-count-font-size);
  color: var(--text-secondary);
  font-weight: 600;
}

.card-hover-actions {
  display: flex;
  gap: var(--spacing-xs);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.project-card:hover .card-hover-actions,
.project-card.selected .card-hover-actions {
  opacity: 1;
}

.card-hover-actions .btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 配置按钮在卡片悬停或选中时更突出（绿色） */
.project-card:hover .card-hover-actions .btn-tertiary,
.project-card.selected .card-hover-actions .btn-tertiary {
  background: var(--color-success);
  border-color: var(--color-success);
  color: #FFFFFF;
}

.project-card:hover .card-hover-actions .btn-tertiary:hover,
.project-card.selected .card-hover-actions .btn-tertiary:hover {
  background: #22c778;
  border-color: #22c778;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.dialog {
  width: 480px;
  max-width: 90vw;
}

.dialog h2 {
  font-size: var(--text-md);
  margin-bottom: var(--spacing-lg);
}

.dialog p {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-lg);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  max-height: 65vh;
  overflow-y: auto;
  padding-right: 4px;
}

.category-selection {
  margin-top: var(--spacing-sm);
}

.category-tabs {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
}

.category-tab {
  padding: 6px 14px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-tab:hover {
  border-color: var(--color-border-strong);
}

.category-tab.active {
  background: rgba(91, 107, 255, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.category-devices {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.device-add-btn {
  padding: 6px 12px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.device-add-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--color-border-strong);
  color: var(--text-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.dialog-sm {
  width: 360px;
}

.device-edit-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.device-edit-item {
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
}

.device-edit-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.device-edit-info {
  margin-bottom: 0;
}

.device-edit-label {
  font-family: var(--font-headings);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-primary);
}

.device-edit-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.device-name-wrapper {
  display: flex;
  align-items: center;
}

.device-name-input {
  font-family: var(--font-headings);
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--text-primary);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  min-width: 150px;
}

.device-edit-fields {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-sm);
}

.device-edit-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.device-field-label {
  font-size: var(--text-xs);
  color: var(--text-dim);
}

.device-input {
  font-family: var(--font-mono);
  width: 100%;
}
</style>
