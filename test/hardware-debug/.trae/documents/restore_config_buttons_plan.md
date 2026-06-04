# 恢复硬件配置卡片中的配置和检测按钮

## 需求

重新添加硬件配置卡片中的"配置"和"检测"按钮，包括完整的前后端实现。

---

## 当前状态

| 文件 | 状态 |
|------|------|
| `backend/routers/modbus.py` | 仅保留空路由框架 |
| `backend/services/modbus_service.py` | 仅保留基础串口方法 |
| `src/api/index.js` | 已删除Modbus相关API |
| `src/views/OneClickConfig.vue` | 已删除配置/检测按钮和逻辑 |

---

## 恢复计划

### Step 1: 恢复后端路由 (`backend/routers/modbus.py`)

添加以下路由：
- `POST /api/modbus/write-config` - 57电机配置写入
- `POST /api/modbus/write-config-35` - 35电机配置写入
- `POST /api/modbus/inspect` - 设备检测

### Step 2: 恢复后端服务方法 (`backend/services/modbus_service.py`)

添加以下方法：
- `write_config()` - 57电机配置
- `write_config_35()` - 35电机配置（包含WRITE方式发现设备）
- `_find_device_35_by_write()` - 35电机发现
- `inspect()` - 设备检测
- `read_config()` - 读取配置
- `save_config_only()` - 断电保存
- `write_station_number()` - 写入站号
- `detect_baud_rate()` - 波特率检测

### Step 3: 恢复前端API (`src/api/index.js`)

添加：
- `writeModbusConfig()`
- `writeModbusConfig35()`
- `inspectModbus()`

### Step 4: 恢复前端组件 (`src/views/OneClickConfig.vue`)

恢复：
- 配置按钮
- 检测按钮
- `configSingle()` 函数
- `inspectSingle()` 函数
- 结果显示卡片

---

## 修改汇总

| 文件 | 改动 |
|------|------|
| `backend/routers/modbus.py` | 添加配置和检测路由 |
| `backend/services/modbus_service.py` | 添加配置和检测服务方法 |
| `src/api/index.js` | 添加Modbus API方法 |
| `src/views/OneClickConfig.vue` | 添加配置/检测按钮和逻辑 |

---

## 验证步骤

1. 后端会自动热更新（uvicorn --reload）
2. 前端会自动热更新（Vite HMR）
3. 打开硬件配置页面，确认配置和检测按钮显示
4. 点击按钮验证功能正常

---

## 参考实现

### 35电机配置流程
1. 使用WRITE方式（功能码0x06）尝试站号1，波特率115200→9600
2. 失败则扫描站号2-30，波特率115200→9600
3. 发现设备后写入目标波特率、站号、断电保存

### 57电机配置流程
1. 使用数据库站号直接写入波特率
2. 发送断电保存指令

### 检测流程
- 35电机：验证站号和波特率
- 57电机：验证设备响应和波特率
