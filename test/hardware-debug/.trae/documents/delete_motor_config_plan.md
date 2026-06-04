# 删除35电机和57电机配置检测后端功能

## 需求

删除35电机和57电机的配置和检测后端业务功能。

---

## 当前状态

### 后端路由 (`backend/routers/modbus.py`)
- `POST /api/modbus/write-config` - 57电机配置写入
- `POST /api/modbus/write-config-35` - 35电机配置写入
- `POST /api/modbus/inspect` - 设备检测
- `POST /api/modbus/read-config` - 读取配置
- `POST /api/modbus/save-config` - 断电保存
- `POST /api/modbus/write-station` - 写入站号

### 后端服务 (`backend/services/modbus_service.py`)
- `write_config()` - 57电机配置
- `write_config_35()` - 35电机配置
- `_find_device_35_by_write()` - 35电机发现
- `inspect()` - 设备检测
- `read_config()` - 读取配置
- `save_config_only()` - 断电保存
- `write_station_number()` - 写入站号

### 前端API (`src/api/index.js`)
- `writeModbusConfig()`
- `writeModbusConfig35()`
- `inspectModbus()`
- `readModbusConfig()`
- `writeModbusSaveOnly()`
- `writeModbusStationNumber()`

---

## 删除计划

### Step 1: 删除后端路由 (`backend/routers/modbus.py`)

删除以下路由：
- `POST /api/modbus/write-config`
- `POST /api/modbus/write-config-35`
- `POST /api/modbus/inspect`
- `POST /api/modbus/read-config`
- `POST /api/modbus/save-config`
- `POST /api/modbus/write-station`

### Step 2: 删除后端服务方法 (`backend/services/modbus_service.py`)

删除以下方法：
- `write_config()`
- `write_config_35()`
- `_find_device_35_by_write()`
- `inspect()`
- `read_config()`
- `save_config_only()`
- `write_station_number()`

同时删除相关导入和常量（如果仅用于这些方法）

### Step 3: 删除前端API (`src/api/index.js`)

删除：
- `writeModbusConfig()`
- `writeModbusConfig35()`
- `inspectModbus()`
- `readModbusConfig()`
- `writeModbusSaveOnly()`
- `writeModbusStationNumber()`

### Step 4: 修改前端组件 (`src/views/OneClickConfig.vue`)

删除或禁用：
- `configSingle()` 函数
- `inspectSingle()` 函数
- 配置按钮
- 检测按钮
- 相关的结果显示卡片

---

## 保留内容

- 串口连接相关功能（`/api/serial/*`）
- 项目和设备配置数据库相关功能
- 前端的串口配置页面

---

## 修改汇总

| 文件 | 删除内容 |
|------|----------|
| `backend/routers/modbus.py` | 所有Modbus通信相关路由 |
| `backend/services/modbus_service.py` | 所有配置写入和检测方法 |
| `src/api/index.js` | 所有Modbus相关API方法 |
| `src/views/OneClickConfig.vue` | 配置/检测按钮和相关逻辑 |

---

## 验证步骤

1. 重启后端服务，确认无路由错误
2. 访问前端，确认无API调用错误
3. 硬件配置页面不再显示配置和检测按钮
