# 分析：编辑项目页面添加新硬件后 custom_name 为空的问题

## 一、Summary

用户反馈：在编辑项目页面选择硬件分类（如"35电机"），添加新硬件后点击保存，数据库中 `custom_name` 字段为空。

目标：分析完整数据流，找出原因并提出解决方案。

## 二、Current State Analysis（完整数据流追溯）

### 数据流图示

```
[点击"+ 35电机"] → addDeviceToEdit() → editingProject.device_configs 新增对象
    → custom_name: '' (空字符串初始化)
    
[点击编辑名称图标] → startEditName(index) → config.editingName = true
    → 用户输入名称 → v-model="config.custom_name" → config.custom_name = "xxx"
    → 失焦/回车 → saveDeviceName(index) → 仅设置 editingName = false
        → 对于新硬件(id 不存在): 不调用 API（正确，因为尚未保存到DB）

[点击"保存"] → saveEdit() → projectStore.updateProject()
    → JSON.parse(JSON.stringify(editingProject.device_configs)) 深拷贝
    → For configs 无 id: api.addDeviceConfig(pid, {..., custom_name: config.custom_name || ''})
    → For configs 有 id: api.updateDeviceConfig(cid, {..., custom_name: config.custom_name})
    → 后端 add_device_config: custom_name = data.get('custom_name', '')
    → 后端模型: custom_name = Column(String(200), default='')
    → 写入 SQLite 数据库
    → refreshAll() 重新从DB获取数据
```

### 当前代码正确性验证（已通过测试）

1. **[addDeviceToEdit 测试]** — 通过 ✓
   - `custom_name: ''` 被正确初始化
2. **[保存流程测试]** — 通过 ✓
   - 保存时 `custom_name: 'My Custom Device'` 被正确传递给 API
   - 未编辑时 `custom_name: ''` 被正确传递给 API
   - 已有设备的 `custom_name` 更新也被正确处理
3. **[saveDeviceName 测试]** — 通过 ✓
   - 已有设备（有 id）→ 调用 API 保存名称
   - 新设备（无 id）→ 不调用 API（正确）

### 当前行为的实质

**当前代码逻辑是正确的，没有任何bug。** `custom_name` 为空是因为：

| 场景 | 行为 | 是否合规 |
|------|------|---------|
| 添加硬件后不编辑名称，直接保存 | `custom_name` 为 `''` 写入数据库 | ✅ 正确 |
| 添加硬件后点击编辑图标，输入名称，再保存 | `custom_name` 为用户输入值写入数据库 | ✅ 正确 |
| 编辑已有硬件的名称后保存 | `custom_name` 被更新 | ✅ 正确 |

### 核心发现

**问题不是 Bug，而是 `custom_name` 没有默认值。** 

前端的 `addDeviceToEdit` 初始化为 `custom_name: ''`（空字符串），当用户没有点击编辑名称图标输入自定义名称时，空字符串就原样保存到数据库。

前端模板已有兜底显示逻辑：
```vue
<span class="device-edit-label">{{ config.custom_name || projectStore.getDeviceTypeLabel(config.device_type_id) }}</span>
```

当 `custom_name` 为空时，UI 显示设备类型标签（如"35电机"）作为显示名称。但数据库中存储的是空字符串。

## 三、问题定义

用户的核心疑问是：**为什么我添加硬件保存后，数据库里 `custom_name` 是空的？**

根本原因在于：`custom_name` 的初始值为空字符串 `''`，用户如果不主动编辑名称，空字符串就直接保存到数据库。数据库层面没有默认值从设备类型标签派生。

## 四、Proposed Changes（方案一：默认填充设备类型标签）

### Option A: 在 `addDeviceToEdit` 中默认填充设备类型标签

**文件**: `src/views/ProjectList.vue`

**修改内容**:
- 在 `addDeviceToEdit` 函数中，使用 `projectStore.getDeviceTypeLabel(typeId)` 获取设备类型标签并设置为 `custom_name` 的默认值

**代码变更**:
```javascript
// 修改前
custom_name: '',

// 修改后
custom_name: projectStore.getDeviceTypeLabel(typeId),
```

**优点**:
- 改动最小，只需修改一行
- 数据库中的 `custom_name` 不再是空字符串
- 用户编辑名称时可基于默认值修改

**缺点**:
- 用户没有编辑意图时，数据库中的数据有冗余存储（设备类型标签本来就存在于 device_types 表）
- 设备类型标签更改后，已保存的 `custom_name` 不会同步更新

### Option B: 在 `addDeviceToEdit` 中使用设备类型标签，但允许清空

**文件**: `src/views/ProjectList.vue`

**修改内容**:
- 同 Option A，但增加一个"恢复默认名称"功能

**代码变更**:
```javascript
custom_name: projectStore.getDeviceTypeLabel(typeId),
```

**优点**:
- 用户看到的是有意义的默认名称
- 数据库中有显式的名称值

### Option C: 保持现状，不加默认值

保持当前行为不变。`custom_name` 的作用是**自定义**名称，当用户没有自定义时，UI 自动回退到设备类型标签。

**优点**:
- 不存储冗余数据
- 设备类型标签更新后，显示自动同步

## 五、Assumptions & Decisions

需要用户决策的关键问题：

1. **`custom_name` 是否应该默认等于设备类型标签？**
   - 是 → 选择 Option A 或 B
   - 否 → 选择 Option C（保持现状）

2. **如果选择增加默认值，是否需要"恢复默认值"功能？**
   - 是 → Option B
   - 否 → Option A

## 六、Verification Steps

如果选择实施修改（Option A 或 B）：

### TDD 步骤

1. **RED** — 修改测试文件 `tests/test_add_device_custom_name.js`：
   - 第2个测试：验证 `custom_name` 默认等于 `getDeviceTypeLabel(typeId)` 的返回值
   - 运行测试，确认失败

2. **GREEN** — 修改 `src/views/ProjectList.vue` 中的 `addDeviceToEdit`：
   - 将 `custom_name: ''` 改为 `custom_name: projectStore.getDeviceTypeLabel(typeId)`

3. **验证** — 运行所有测试：
   ```bash
   node tests/test_add_device_custom_name.js
   node tests/test_save_custom_name.js
   node tests/test_save_device_name.js
   ```
   全部通过

4. **手动验证**：
   - 启动服务 `npm run python:dev`
   - 打开编辑项目页面
   - 添加"35电机"硬件
   - 右键检查元素 → 确认 `custom_name` 显示为"35电机"
   - 点击保存
   - 重新打开编辑 → 确认 `custom_name` 仍显示"35电机"
