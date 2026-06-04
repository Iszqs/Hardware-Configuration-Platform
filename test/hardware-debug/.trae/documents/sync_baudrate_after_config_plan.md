# 配置按钮点击后同步串口波特率

## 问题描述

点击硬件配置页面的"配置"按钮，成功写入波特率和断电保存后，前端串口状态面板中显示的波特率（`serialStore.config.baudRate`）仍然是旧值（9600），与后端实际波特率不一致。

## 当前状态分析

### 后端状态（已正确更新）
- `ModbusService._serial.baudrate` → `write_config` 第191行已修改为波特率
- `ModbusService.baud_rate` → `write_config` 第192行已修改为波特率

### 前端状态（未同步）
- `serialStore.config.baudRate` → 始终为初始值 `9600`，从未被更新
- `configSingle` 函数从未引用 `serialStore`

### 代码路径

```
[OneClickConfig.vue] configSingle(idx)
  → api.writeModbusConfig({ station_number, baud_rate })
    → [backend] write_config() → 成功写入设备并更新后端baud_rate
  → 仅更新 lastResult + configuredIndexes
  → ❌ 缺失 serialStore.config.baudRate 同步
```

### 次要问题
`ensure_connected()` 硬编码波特率为 9600，应使用当前 `self.baud_rate`。

## 修改方案

### 修改1：OneClickConfig.vue — 配置成功后同步 serialStore

**文件**：`src/views/OneClickConfig.vue`
**位置**：`configSingle` 函数内，`api.writeModbusConfig` 成功后（第180-182行）

在 `if (result.success && !configuredIndexes.value.includes(idx))` 之前增加：
```js
if (result.success) {
  serialStore.config.baudRate = config.baud_rate
}
```

**效果**：
- 配置成功后，前端串口面板的波特率立即同步为目标波特率
- 串口状态栏显示 `COM2 @ {baud_rate}` 而不是 `COM2 @ 9600`

### 修改2：modbus_service.py — ensure_connected 使用缓存的波特率

**文件**：`backend/services/modbus_service.py`
**位置**：`ensure_connected` 方法（第157-161行）

将：
```python
def ensure_connected(self) -> bool:
    if self.is_connected():
        return True
    print('串口未连接，尝试自动连接 COM2...')
    return self.connect('COM2', 9600)
```

改为：
```python
def ensure_connected(self) -> bool:
    if self.is_connected():
        return True
    baud = self.baud_rate or 9600
    print(f'串口未连接，尝试自动连接 COM2 ({baud} bps)...')
    return self.connect('COM2', baud)
```

**效果**：
- 如果之前已成功配置过波特率，重连时会使用正确的波特率
- 首次连接或缓存为空时，仍默认使用 9600

## 验证方式

不涉及新的测试用例。手动验证即可：
1. 打开 `http://localhost:5173/`，确保串口已连接 COM2
2. 进入硬件配置页面，点击某设备的"配置"按钮
3. 观察页面右上角串口状态栏，波特率应更新为目标波特率
4. 查看后端日志，确认 `serialStore` 中的波特率已同步
