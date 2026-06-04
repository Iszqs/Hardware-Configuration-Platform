# 计划：编辑页面添加硬件后 custom_name 默认为分类名，且仅点击保存才写库

## 一、Summary

用户要求两项变更：
1. 添加新硬件后，`custom_name` 的默认值应为选中硬件分类的名称（如"35电机"）→ **已在上一轮修复中完成**
2. 编辑过程中所有修改（编辑名称、删除硬件等）只操作本地状态，**只有点击"保存"按钮才执行数据库操作**

## 二、Current State Analysis

### 已完成（无需再改）

**Requirement 1 ✅** — `addDeviceToEdit` 已使用 `custom_name: projectStore.getDeviceTypeLabel(typeId)`：

```javascript
// src/views/ProjectList.vue:262-272
editingProject.device_configs.push({
  ...
  custom_name: projectStore.getDeviceTypeLabel(typeId),  // 已修复
  purpose: ''
})
```

### 需要修改

**当前的问题：编辑过程中存在多处即时数据库操作**

| 操作 | 文件 | 当前行为 | 问题 |
|------|------|---------|------|
| 编辑硬件名失焦/回车 | `saveDeviceName` (ProjectList.vue:288-296) | 对于有 id 的设备，**立即调用 API** `updateDeviceConfig` | 应只更新本地状态 |
| 删除硬件 | `removeDeviceFromEdit` (ProjectList.vue:275-281) | 对于有 id 的设备，**立即调用 API** `removeDeviceConfig` | 应只从本地移除，删除操作推迟到"保存"时 |

### 数据流设计

```
当前（有问题的）：
  addDeviceToEdit → 仅本地 ✓
  saveDeviceName → 本地 + API 即时写库 ✗
  removeDeviceFromEdit → 本地 + API 即时写库 ✗
  saveEdit → 本地 + API 写库（完整保存）

目标（正确的）：
  addDeviceToEdit → 仅本地 ✓
  saveDeviceName → 仅本地 ✓
  removeDeviceFromEdit → 仅本地，记录被删的 config id
  saveEdit → 批量处理：删除已移除的配置 → 添加/更新配置 → API 写库
```

## 三、Proposed Changes

### 文件1: `src/views/ProjectList.vue` — 编辑操作仅改本地状态

#### 1.1 `saveDeviceName` — 移除 API 调用

```javascript
// 修改前
async function saveDeviceName(index) {
  const config = editingProject.device_configs[index]
  config.editingName = false
  if (config.id) {
    await projectStore.updateDeviceConfig(editingProject.id, index, {
      customName: config.custom_name
    })
  }
}

// 修改后
function saveDeviceName(index) {
  const config = editingProject.device_configs[index]
  config.editingName = false
}
```

**说明**：编辑名称只更新本地 `editingProject` 中的 `custom_name`，不触发 API 调用。实际的读写将在 `saveEdit` 点击"保存"时统一处理。

#### 1.2 `removeDeviceFromEdit` — 移除即时 API 调用，记录待删 ID

```javascript
// 修改前
function removeDeviceFromEdit(index) {
  const config = editingProject.device_configs[index]
  if (config.id) {
    projectStore.removeDeviceConfig(editingProject.id, index)
  }
  editingProject.device_configs.splice(index, 1)
}

// 修改后
function removeDeviceFromEdit(index) {
  const config = editingProject.device_configs[index]
  if (config.id) {
    removedConfigIds.push(config.id)
  }
  editingProject.device_configs.splice(index, 1)
}
```

**说明**：不再即时调用 API 删除，而是将 config id 记录到 `removedConfigIds` 数组中，待 `saveEdit` 时统一处理。新增设备的删除（无 id）只需从本地数组移除即可。

#### 1.3 新增 `removedConfigIds` 响应式变量

在 `<script setup>` 中添加：
```javascript
const removedConfigIds = ref([])
```

#### 1.4 `saveEdit` — 先删除已移除的配置，再统一保存

```javascript
// 修改前
function saveEdit() {
  if (editingProject.id && editingProject.name.trim()) {
    projectStore.updateProject(editingProject.id, {
      name: editingProject.name.trim(),
      description: editingProject.description.trim(),
      device_configs: JSON.parse(JSON.stringify(editingProject.device_configs))
    })
    showEditDialog.value = false
    resetEdit()
  }
}

在 `<script setup>` 顶部新增 import：
```javascript
import { api } from '../api'
```

```javascript
// 修改后
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
```

**说明**：
- 遍历 `removedConfigIds` 逐一调用 `api.deleteDeviceConfig`（这些是已有 id 的设备）
- 清空记录数组
- 调用 `updateProject` 进行新增/更新操作

#### 1.5 `resetEdit` — 清空待删记录

```javascript
function resetEdit() {
  editingProject.id = ''
  editingProject.name = ''
  editingProject.description = ''
  editingProject.device_configs = []
  selectedCategory.value = null
  removedConfigIds.value = []  // 新增
}
```

### 文件2: `tests/test_save_device_name.js` — 更新测试用例

修改两个测试：

1. **第1个测试**：验证 `saveDeviceName` 不再调用 API（改为只改本地状态）
2. **第2个测试**：验证不调用 API 的行为（与修改前一致，但确保没有 API 调用）

### 文件3: `tests/test_save_custom_name.js` — 无需修改

这个文件测试 `updateProject` 保存流程，逻辑不变。

### 文件4: `tests/test_add_device_custom_name.js` — 无需修改

已验证 `custom_name` 默认为设备类型标签。

## 四、Refactor Consideration

`saveEdit` 中直接调用了 `api.deleteDeviceConfig`，而之前是通过 `projectStore.removeDeviceConfig` 间接调用。观察 `removeDeviceConfig` 的实现：

```javascript
async function removeDeviceConfig(projectId, configIndex) {
    const project = getProject(projectId)
    if (!project || !project.device_configs[configIndex]) return
    const cfgId = project.device_configs[configIndex].id
    await api.deleteDeviceConfig(cfgId)
    await refreshAll()
  }
```

该方法通过 `configIndex` 在 store 的 project 中查找 config，与 editingProject 的索引可能不同步，不适合直接使用。因此在 `saveEdit` 中直接调用 `api.deleteDeviceConfig(configId)` 是正确的做法。

## 五、Verification Steps

### TDD 步骤

1. **RED** — 修改 `test_save_device_name.js`：
   - 第一个测试：验证 `saveDeviceName` 不再调用 API（只改本地状态）
   - 运行测试，确认失败（旧代码会调用 API）

2. **GREEN** — 修改 `src/views/ProjectList.vue` 相应逻辑

3. **验证** — 运行所有测试：
   ```bash
   node tests/test_add_device_custom_name.js
   node tests/test_save_custom_name.js
   node tests/test_save_device_name.js
   ```

4. **构建验证** — `npm run build` 确保无编译错误

5. **手动验证** — 启动服务，编辑项目页面：
   - 添加"35电机"硬件 → `custom_name` 显示"35电机" ✅（已有）
   - 编辑名称后点击其他地方 → 不调用 API ✅（新行为）
   - 删除已有设备 → 不调用 API ✅（新行为）
   - 点击保存 → 一次保存所有修改 ✅（新行为）
