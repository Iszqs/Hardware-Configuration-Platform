<template>
  <div class="hardware-library-page">
    <div class="page-header">
      <div>
        <h1>硬件库</h1>
      </div>
      <div class="header-actions">
        <button v-if="userStore.isAdmin" class="btn btn-primary" @click="openAddCategoryDialog">+ 新增分类</button>
        <button v-if="userStore.isAdmin" class="btn btn-danger" @click="deleteSelectedCategory" :disabled="!selectedCategory">删除分类</button>
      </div>
    </div>

    <div class="hardware-grid">
      <div
        v-for="category in projectStore.categories"
        :key="category.id"
        class="category-card card card-glass"
        :class="{ selected: selectedCategory?.id === category.id }"
        @click="selectCategory(category)"
      >
        <div class="category-header">
          <h3>{{ category.label }}</h3>
          <div v-if="userStore.isAdmin" class="category-edit-btn" @click.stop="editCategoryName(category)" aria-label="编辑分类" role="button" tabindex="0">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h13a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4Z"></path>
            </svg>
          </div>
        </div>
        <div class="device-types">
          <div
            v-for="subType in projectStore.subTypes[category.id]"
            :key="subType.id"
            class="device-type-item"
            :class="{ selected: selectedDevice?.id === subType.id }"
            @click.stop="selectDevice(subType, category.id)"
          >
            <span class="device-radio">{{ selectedDevice?.id === subType.id ? '✓' : '' }}</span>
            <span class="device-type-label">{{ subType.label }}</span>
          </div>
        </div>
        <div class="category-footer">
          <span class="device-count mono">{{ projectStore.subTypes[category.id]?.length || 0 }} 硬件</span>
          <div v-if="userStore.isAdmin" class="category-actions-bar">
            <button 
              class="btn btn-sm" 
              :class="selectedCategory?.id === category.id ? 'btn-primary' : 'btn-secondary'"
              @click.stop="openAddDialog(category.id)"
              :disabled="selectedCategory?.id !== category.id"
            >+ 新增</button>
            <button 
              class="btn btn-sm" 
              :class="selectedCategory?.id === category.id ? 'btn-success' : 'btn-secondary'"
              @click.stop="editSelectedDevice"
              :disabled="selectedCategory?.id !== category.id"
            >编辑</button>
            <button 
              class="btn btn-sm" 
              :class="selectedCategory?.id === category.id ? 'btn-danger' : 'btn-secondary'"
              @click.stop="deleteSelectedDevice"
              :disabled="selectedCategory?.id !== category.id"
            >删除</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeviceDialog" class="dialog-overlay" @click.self="closeDeviceDialog">
      <div class="dialog card">
        <h2>{{ editingDevice ? '编辑硬件' : '新增硬件' }}</h2>
        <div class="form">
          <div class="input-group">
            <label>硬件名称</label>
            <input class="input-field" v-model="deviceForm.label" placeholder="请输入硬件名称" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="closeDeviceDialog">取消</button>
          <button class="btn btn-primary" @click="saveDevice" :disabled="!deviceForm.label.trim()">保存</button>
        </div>
      </div>
    </div>

    <div v-if="showCategoryDialog" class="dialog-overlay" @click.self="showCategoryDialog = false">
      <div class="dialog dialog-sm card">
        <h2>{{ categoryForm.id ? '编辑分类' : '新增分类' }}</h2>
        <div class="form">
          <div class="input-group">
            <label>分类名称</label>
            <input class="input-field" v-model="categoryForm.label" placeholder="请输入分类名称" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showCategoryDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveCategory" :disabled="!categoryForm.label.trim()">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useProjectStore } from '../stores/projects'
import { useUserStore } from '../stores/user'

const projectStore = useProjectStore()
const userStore = useUserStore()

const showDeviceDialog = ref(false)
const showCategoryDialog = ref(false)
const editingDevice = ref(null)
const editingCategoryId = ref(null)

const deviceForm = reactive({
  label: '',
  categoryId: '',
  stationNumber: 1,
  baudRate: 9600
})

const categoryForm = reactive({
  id: '',
  label: ''
})

const selectedDevice = ref(null)
const selectedCategoryId = ref(null)
const selectedCategory = ref(null)

function openAddDialog(categoryId) {
  editingDevice.value = null
  editingCategoryId.value = null
  deviceForm.label = ''
  deviceForm.categoryId = categoryId || projectStore.categories[0]?.id || ''
  deviceForm.stationNumber = 1
  deviceForm.baudRate = 9600
  showDeviceDialog.value = true
}

function closeDeviceDialog() {
  showDeviceDialog.value = false
  editingDevice.value = null
  editingCategoryId.value = null
  deviceForm.label = ''
  deviceForm.categoryId = ''
  deviceForm.stationNumber = 1
  deviceForm.baudRate = 9600
}

async function saveDevice() {
  if (!deviceForm.label.trim()) return
  
  if (editingDevice.value) {
    await projectStore.updateDeviceType(editingDevice.value.id, deviceForm.label.trim())
  } else {
    await projectStore.addDeviceType(deviceForm.categoryId, deviceForm.label.trim())
  }
  closeDeviceDialog()
}

function openAddCategoryDialog() {
  categoryForm.id = ''
  categoryForm.label = ''
  showCategoryDialog.value = true
}

function editCategoryName(category) {
  categoryForm.id = category.id
  categoryForm.label = category.label
  showCategoryDialog.value = true
}

async function saveCategory() {
  if (!categoryForm.label.trim()) return
  if (categoryForm.id) {
    await projectStore.updateCategory(categoryForm.id, categoryForm.label.trim())
  } else {
    await projectStore.addCategory(categoryForm.label.trim())
  }
  showCategoryDialog.value = false
}

function selectCategory(category) {
  if (selectedCategory.value?.id === category.id) {
    selectedCategory.value = null
  } else {
    selectedCategory.value = category
    selectedDevice.value = null
    selectedCategoryId.value = null
  }
}

async function deleteSelectedCategory() {
  if (!selectedCategory.value) return
  if (confirm(`确定要删除分类「${selectedCategory.value.label}」吗？此操作将同时删除该分类下的所有硬件类型。`)) {
    await projectStore.deleteCategory(selectedCategory.value.id)
    selectedCategory.value = null
  }
}

function selectDevice(device, categoryId) {
  if (selectedDevice.value?.id === device.id) {
    selectedDevice.value = null
    selectedCategoryId.value = null
    selectedCategory.value = null
  } else {
    selectedDevice.value = device
    selectedCategoryId.value = categoryId
    selectedCategory.value = projectStore.categories.find(cat => cat.id === categoryId)
  }
}

function editSelectedDevice() {
  if (selectedDevice.value && selectedCategoryId.value) {
    editingDevice.value = selectedDevice.value
    editingCategoryId.value = selectedCategoryId.value
    deviceForm.label = selectedDevice.value.label
    deviceForm.categoryId = selectedCategoryId.value
    showDeviceDialog.value = true
  }
}

async function deleteSelectedDevice() {
  if (selectedDevice.value && selectedCategoryId.value) {
    await projectStore.deleteDeviceType(selectedCategoryId.value, selectedDevice.value.id)
    selectedDevice.value = null
    selectedCategoryId.value = null
  }
}
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.hardware-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.category-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-default);
  min-height: var(--card-min-height);
}

.category-card:hover {
  background: var(--bg-elevated);
  border-color: var(--color-border-strong);
  box-shadow: var(--elevation-md);
  transform: scale(1.02) translateY(-2px);
}

.category-card.selected {
  background: rgba(91, 107, 255, 0.1);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px rgba(91, 107, 255, 0.3), var(--elevation-md);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.category-header h3 {
  font-size: var(--card-title-font-size);
  font-weight: var(--card-title-font-weight);
}

.category-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  color: var(--text-dim);
  cursor: pointer;
  transition: all var(--transition-fast);
  opacity: 0;
}

.category-card:hover .category-edit-btn {
  opacity: 1;
}

.category-edit-btn:hover {
  background: var(--bg-elevated);
  color: var(--color-primary);
}

.device-types {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  flex: 1;
}

.device-type-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-elevated);
  border-radius: var(--radius-sm);
  gap: var(--spacing-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.device-type-item:hover {
  background: rgba(91, 107, 255, 0.08);
}

.device-type-item.selected {
  background: rgba(91, 107, 255, 0.12);
  border-color: var(--color-primary);
}

.device-radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: transparent;
  flex-shrink: 0;
}

.device-type-item.selected .device-radio {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #FFFFFF;
}

.device-type-label {
  font-size: var(--card-label-font-size);
  font-weight: var(--card-label-font-weight);
  color: var(--text-secondary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.category-footer {
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-default);
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-actions-bar {
  display: flex;
  gap: var(--spacing-xs);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.category-card.selected .category-actions-bar {
  opacity: 1;
}

.category-actions-bar .btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.device-count {
  font-size: var(--card-count-font-size);
  color: var(--text-secondary);
  font-weight: 600;
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
  width: 400px;
  max-width: 90vw;
}

.dialog h2 {
  font-size: var(--text-md);
  margin-bottom: var(--spacing-lg);
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.dialog-sm {
  width: 360px;
}
</style>
