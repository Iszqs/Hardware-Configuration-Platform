# 57电机配置/检测时同步前端串口波特率

## 需求

在操作57电机的"配置"或"检测"按钮时，若系统切换通信波特率，串口连接也会同步切换至相同的新波特率。

---

## 当前问题

- 后端 `write_config_57` 和 `inspect_57` 在波特率切换时会调用 `self.connect(baud)` 切换后端串口波特率
- 但前端 `serialStore.config.baudRate` 没有被更新
- 导致前端显示的波特率与实际后端使用的波特率不一致

---

## 解决方案

### 修改后端返回结果

在 `write_config_57` 和 `inspect_57` 返回结果中，添加当前使用的波特率：

```python
# write_config_57 返回值
{
    'success': True,
    'message': '...',
    'current_baud_rate': 115200  # 新增
}

# inspect_57 返回值
{
    'passed': True,
    'items': [...],
    'station': 1,
    'current_baud_rate': 115200  # 新增
}
```

### 修改前端更新serialStore

在 `configSingle` 和 `inspectSingle` 中，收到结果后更新 `serialStore.config.baudRate`：

```javascript
// configSingle
if (result.current_baud_rate) {
    serialStore.config.baudRate = result.current_baud_rate
}

// inspectSingle
if (result.current_baud_rate) {
    serialStore.config.baudRate = result.current_baud_rate
}
```

---

## 修改文件

| 文件 | 改动 |
|------|------|
| `backend/services/modbus_service.py` | 在 `write_config_57` 和 `inspect_57` 返回值中添加 `current_baud_rate` |
| `src/views/OneClickConfig.vue` | 在 `configSingle` 和 `inspectSingle` 中更新 `serialStore.config.baudRate` |

---

## 实施步骤

1. 修改 `write_config_57`：在所有返回语句中添加 `current_baud_rate` 字段
2. 修改 `inspect_57`：在所有返回语句中添加 `current_baud_rate` 字段
3. 修改 `configSingle` 函数：根据返回的 `current_baud_rate` 更新 `serialStore.config.baudRate`
4. 修改 `inspectSingle` 函数：根据返回的 `current_baud_rate` 更新 `serialStore.config.baudRate`

---

## 验证

1. 连接串口后，在配置或检测过程中切换波特率
2. 观察 `serialStore.config.baudRate` 是否被更新为当前使用的波特率
