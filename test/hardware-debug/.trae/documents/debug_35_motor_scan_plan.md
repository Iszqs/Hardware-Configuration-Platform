# 排查35电机配置按钮未触发站号扫描问题

## 问题描述

35电机点击配置按钮后，没有触发1-30站号全量扫描。

## 可能原因

经过代码分析，`find_device_35()` 方法逻辑本身正确，但有几个潜在问题：

### 原因1：`ensure_connected()` 中串口连接状态丢失

`write_config_35` 先调用 `ensure_connected()`，如果串口未连接（如热重载后），`connect('COM2', 115200)` 可能失败返回 False，导致 `write_config_35` 提前返回，**永远不进入 `find_device_35`**。

### 原因2：站号1的第一步扫描耗时过长但无反馈

`find_device_35` 第一步（站号1×2个波特率）每次读超时0.3s，最快0.6s完成。第二步（30个站号×2个波特率）最多 30×2×0.3s = 18s。但前端没有进度提示，用户以为没触发。

### 原因3：前端没有进度提示，用户等不及

Vite 热更新可能未正确刷新前端代码，导致依旧调用了旧 API（如 `writeModbusConfig` 而非 `writeModbusConfig35`）。

---

## 修改方案

### 修改1：`modbus_service.py` — `write_config_35` 增强连接健壮性

在 `write_config_35` 中，如果 `ensure_connected()` 返回 False，不直接返回，改用 `connect('COM2', *baud)` 逐一尝试：

```python
def write_config_35(self, target_station: int, target_baud_rate: int) -> dict:
    baud_val = BAUD_RATE_MAP.get(target_baud_rate)
    if baud_val is None:
        return {'success': False, 'message': f'不支持的波特率: {target_baud_rate}'}

    # 确保串口已连接，遍历已知波特率重试
    if not self.is_connected():
        connected = False
        for baud in KNOWN_BAUD_RATES:
            if self.connect('COM2', baud):
                connected = True
                break
        if not connected:
            return {'success': False, 'message': '串口未连接，无法配置'}

    try:
        found_baud, found_station = self.find_device_35()
    except RuntimeError as e:
        return {'success': False, 'message': str(e)}
    # ... 其余不变
```

### 修改2：`find_device_35` 增加进度输出

当前已有 `print` 语句，但仅在终端可见。不修改（已在终端可查）。

### 修改3：前端增加扫描中的进度提示

**文件**：`src/views/OneClickConfig.vue`

在 `configSingle` 函数中，35电机调用 API 之前设置一个临时状态提示：

```javascript
if (config.device_type_id === 1) {
  // 先显示正在扫描的提示
  lastResult.value = {
    status: 'in_progress',
    message: '正在扫描设备（波特率+站号）...'
  }
  result = await api.writeModbusConfig35({...})
}
```

模板中增加 `in_progress` 状态显示：

```vue
<span v-if="lastResult?.status === 'in_progress'" class="status-scanning">扫描中...</span>
```

---

## 排查步骤（可先执行）

在修改代码之前，先通过后端日志确认问题：

1. 重启后端服务
2. 打开后端终端窗口观察日志
3. 点击35电机的配置按钮
4. 观察是否有以下输出：
   - `开始35电机设备查找...`
   - `第一步：尝试站号1...`
   - `第二步：站号1未找到，开始全量扫描(站号1-30)...`

如果没有上述日志 → 问题在代码路径（原因1或原因3）
如果有日志但扫描失败 → 问题在设备连接或扫描参数

---

## 修改汇总

| 文件 | 改动 |
|------|------|
| `modbus_service.py` | `write_config_35` 中增强 `ensure_connected` 为遍历波特率重连 |
| `OneClickConfig.vue` | `configSingle` 中35电机调用前显示"扫描中"状态提示 |
