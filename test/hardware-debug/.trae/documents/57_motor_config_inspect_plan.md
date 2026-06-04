# 57电机配置和检测按钮功能

## 需求说明

### 配置按钮
1. 根据数据库中的站号，向设备写入设定的波特率
2. 若设备无响应，则自动切换至其他波特率并重新尝试写入
3. 一旦收到响应，判断返回报文中的波特率是否与当前写入的波特率一致
4. 验证通过后，发送断电保存指令，确保参数生效

### 检测按钮
1. 依据数据库中的站号和波特率，向设备发起读取请求
2. 若设备无响应，则自动切换波特率并重新尝试读取
3. 一旦收到响应，判断返回报文中的站号和波特率是否与数据库中的记录一致

---

## 实施计划

### Step 1: 添加后端服务方法 (`backend/services/modbus_service.py`)

添加常量：
```python
BAUD_RATE_MAP = {9600: 6, 115200: 12}
KNOWN_BAUD_RATES = [115200, 9600]
```

添加方法：
- `write_config_57(station, target_baud_rate)` - 57电机配置
- `inspect_57(station, target_baud_rate)` - 57电机检测

### Step 2: 添加后端路由 (`backend/routers/modbus.py`)

```python
@router.post('/write-config-57')
async def write_config_57(data: dict):
    station = data.get('station_number', 1)
    baud_rate = data.get('baud_rate', 115200)
    return modbus_service.write_config_57(station, baud_rate)

@router.post('/inspect-57')
async def inspect_57(data: dict):
    station = data.get('station_number', 1)
    baud_rate = data.get('baud_rate', 115200)
    return modbus_service.inspect_57(station, baud_rate)
```

### Step 3: 添加前端API (`src/api/index.js`)

```javascript
writeModbusConfig57(data) { return request('/api/modbus/write-config-57', { method: 'POST', body: data }) },
inspectModbus57(data) { return request('/api/modbus/inspect-57', { method: 'POST', body: data }) },
```

### Step 4: 修改前端组件 (`src/views/OneClickConfig.vue`)

添加配置和检测按钮，调用对应的API。

---

## 核心逻辑

### 57电机配置流程

```
1. 获取数据库站号和目标波特率
2. 尝试以当前串口波特率写入目标波特率
3. 若无响应，切换波特率重试（115200 ↔ 9600）
4. 收到响应后，读取设备波特率验证
5. 验证通过，发送断电保存指令
```

### 57电机检测流程

```
1. 获取数据库站号和波特率
2. 尝试以当前波特率读取设备站号和波特率
3. 若无响应，切换波特率重试
4. 收到响应后，对比读取值与数据库值
5. 返回检测结果
```

---

## 修改文件

| 文件 | 改动 |
|------|------|
| `backend/services/modbus_service.py` | 添加 `write_config_57`、`inspect_57` 方法 |
| `backend/routers/modbus.py` | 添加 `/write-config-57`、`/inspect-57` 路由 |
| `src/api/index.js` | 添加 `writeModbusConfig57`、`inspectModbus57` API |
| `src/views/OneClickConfig.vue` | 添加配置/检测按钮和逻辑 |

---

## 验证

1. 打开硬件配置页面
2. 点击57电机的"配置"按钮，观察日志输出
3. 点击57电机的"检测"按钮，查看检测结果
