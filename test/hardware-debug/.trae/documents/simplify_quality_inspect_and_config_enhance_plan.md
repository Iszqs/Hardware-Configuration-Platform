# 计划：简化质检页面为单设备操作，配置按钮增强

## 一、Summary

用户需求：
1. **QualityInspect.vue** — 去掉多选、全选、批量检测功能，改为每台设备独立"检测"按钮（与 OneClickConfig.vue 风格一致）
2. **配置按钮增强** — 35电机同时写入站号和波特率，57电机只写波特率

## 二、Current State Analysis

### 2.1 质量检测页面 (QualityInspect.vue)

**当前**：多选/全选/批量模式
- 设备卡片可勾选（checkbox）
- 顶部有"全选/取消全选"按钮
- 右上角有"开始检测"按钮，批量检测选中的设备
- 检测完成后结果统一展示

**目标**：单设备操作模式
- 每台设备卡片底部有独立的"检测"按钮
- 点击立即检测该设备，结果展示在对应卡片下方

### 2.2 配置按钮 (OneClickConfig.vue)

**当前行为**：
- `configSingle` 调用 `api.writeModbusConfig({station_number, baud_rate, device_type_id})`
- 后端 `write_config` 只写波特率寄存器 `0x0009` + 保存 `0x00DC`

**目标行为**：
- 35电机 (`device_type_id=1`)：先写站号寄存器 `0x0066`（使用 `write_station_number`），再写波特率
- 57电机 (`device_type_id=2`)：只写波特率（保持当前行为）

### 2.3 后端 API 现状

| API | 路径 | 功能 |
|-----|------|------|
| `write_config` | `POST /api/modbus/write-config` | 写波特率+保存 |
| `write_station_number` | **不存在**（后端有方法但无路由） | 后端有 `ModbusService.write_station_number` 方法，但**没有对应的 API 路由** |
| `inspect` | `POST /api/modbus/inspect` | 读取站号和波特率验证 |

## 三、Proposed Changes

### 文件1: `src/views/QualityInspect.vue` — 简化为单设备操作

**改动内容**：
- 移除：`selection-bar`（全选/取消全选/已选择计数）
- 移除：设备卡片上的 `checkbox` 和 `selected` 状态
- 移除：顶部"开始检测"按钮
- 移除：`selectedIndexes`、`selectedAll`、`passCount`、`allPassed`、`selectDevice`、`toggleSelectAll`、`resetResults`
- 移除：`overview-bar`（"通过 X/Y"统计条）
- 新增：每张设备卡片底部加"检测"按钮（参照 OneClickConfig.vue 风格）
- 新增：每台设备独立的检测逻辑，结果展示在卡片内部或下方

**详细的模板变更**：

```vue
<template>
  <div class="quality-inspect" v-if="project">
    <div class="page-header">
      <div>
        <router-link to="/projects" class="back-link">← 项目库</router-link>
        <h1>硬件检测</h1>
        <p>选择硬件进行检测</p>
      </div>
    </div>

    <div v-if="project.device_configs.length" class="device-grid">
      <div v-for="(cfg, idx) in project.device_configs" :key="idx" class="device-card">
        <div class="device-header">
          <span class="category-tag">{{ projectStore.getCategoryLabel(cfg.category_id) }}</span>
        </div>
        <div class="device-main">
          <div class="device-name">{{ projectStore.getDeviceTypeLabel(cfg.device_type_id) }}</div>
          <div v-if="cfg.purpose" class="device-purpose">{{ cfg.purpose }}</div>
        </div>
        <div class="device-params">
          <div class="param">
            <span class="param-label">站号</span>
            <span class="param-value mono">{{ cfg.station_number }}</span>
          </div>
          <div class="param">
            <span class="param-label">波特率</span>
            <span class="param-value mono">{{ cfg.baud_rate }}</span>
          </div>
        </div>
        <div class="device-card-footer">
          <button class="btn btn-primary" @click="inspectSingle(idx)" :disabled="inspectInProgress">
            {{ inspectInProgress ? '检测中...' : '检测' }}
          </button>
        </div>
      </div>
    </div>
    <!-- ... -->
  </div>
</template>
```

**详细的 script 变更**：
```javascript
const inspectInProgress = ref(false)
const inspectResults = ref([])  // 保留，用于展示结果

async function inspectSingle(idx) {
  // ...保持不变，但不再遍历 selectedIndexes
}

function clearInspectResults() {
  inspectResults.value = []
}
```

### 文件2: `src/views/OneClickConfig.vue` — 配置按钮增强

**改动内容**：
修改 `configSingle` 函数，根据设备类型调用不同的后端 API：
- 35电机：先写站号，再写波特率
- 57电机：只写波特率

```javascript
async function configSingle(idx) {
  if (!project.value || configInProgress.value) return
  configInProgress.value = true
  const config = project.value.device_configs[idx]
  
  try {
    if (config.device_type_id === 1) {
      // 35电机：写站号 + 写波特率
      await api.writeModbusStationNumber({
        old_station: config.station_number,
        new_station: config.station_number
      })
    }
    
    const result = await api.writeModbusConfig({
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      device_type_id: config.device_type_id
    })
    
    // ... 后续处理同上
  }
}
```

### 文件3: `src/api/index.js` — 新增 API

新增 `writeModbusStationNumber` API：

```javascript
writeModbusStationNumber(data) { return request('/api/modbus/write-station', { method: 'POST', body: data }) },
```

### 文件4: `backend/routers/modbus.py` — 新增写站号路由

新增 API 端点：

```python
@router.post('/write-station')
async def write_station(data: dict):
    old_station = data.get('old_station', 1)
    new_station = data.get('new_station', 1)
    result = modbus_service.write_station_number(old_station, new_station)
    return result
```

## 四、Assumptions & Decisions

| 决策 | 选项 | 选择 |
|------|------|------|
| 35电机站号写什么值？ | 写入当前数据库中的 `station_number` | 写入数据库配置的值（已在前端 `configSingle` 中作为参数） |
| 35电机写站号失败后的行为 | 继续/中止 | 站号写入成功后继续写波特率，失败则返回错误 |
| 检测结果展示方式 | 单个卡片下方/统一结果区 | 使用当前已存在的 `inspectResults` 列表区展示 |

## 五、Verification Steps

1. **构建验证**：`npm run build` 确保无编译错误
2. **启动服务**：`npm run python:dev`
3. **手动验证**：
   - 进入质量检测页面 → 每台设备有"检测"按钮，无 checkbox/全选
   - 点击检测 → 结果展示在下方
   - 进入硬件配置页面 → 35电机点击配置同时写站号和波特率
   - 57电机点击配置只写波特率
