# 默认波特率改为115200 & 配置按钮站号固定为1

## 需求

1. 串口连接的默认波特率从 9600 改为 115200
2. 硬件配置页面中，配置按钮始终使用站号 1，检测按钮使用数据库中的站号

---

## 修改1：默认波特率 9600 → 115200

需要修改 6 个地方，覆盖前端 store、后端路由、后端 schema、后端 service 四个层级：

| # | 文件 | 行 | 当前值 | 改为 |
|---|------|----|--------|------|
| 1 | [serial.js](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/stores/serial.js) | L8 | `baudRate: 9600` | `baudRate: 115200` |
| 2 | [serial.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/routers/serial.py) | L17 | `data.get('baud_rate', 9600)` | `data.get('baud_rate', 115200)` |
| 3 | [schemas.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/schemas.py) | L34 | `baud_rate: int = 9600` | `baud_rate: int = 115200` |
| 4 | [schemas.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/schemas.py) | L73 | `baud_rate: int = 9600` | `baud_rate: int = 115200` |
| 5 | [modbus_service.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/services/modbus_service.py) | L62 | `def connect(self, port: str, baud_rate: int = 9600)` | `def connect(self, port: str, baud_rate: int = 115200)` |
| 6 | [modbus_service.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/services/modbus_service.py) | L160 | `baud = self.baud_rate or 9600` | `baud = self.baud_rate or 115200` |

### 影响范围
- 初始串口连接默认以 115200 打开
- 串口断开后自动重连默认以 115200 打开
- 无其他影响 — 用户仍可在串口面板中手动选择其他波特率

---

## 修改2：配置按钮站号固定为1，检测按钮使用数据库站号

### 2.1 OneClickConfig.vue — configSingle

**文件**：`src/views/OneClickConfig.vue`
**位置**：`configSingle` 函数 (L147-L200)

**改动 a** — `writeModbusStationNumber` 调用（L155-L158）：
```js
// 当前：使用数据库站号
old_station: config.station_number,
new_station: config.station_number
// 改为：固定站号 1
old_station: 1,
new_station: 1
```

**改动 b** — `writeModbusConfig` 调用（L164-L168）：
```js
// 当前：使用数据库站号
station_number: config.station_number,
// 改为：固定站号 1
station_number: 1,
```

### 2.2 OneClickConfig.vue — inspectSingle（无需修改）

`inspectSingle` 函数（L202 起）保持现状，仍然使用 `config.station_number`（数据库中的站号）。

### 2.3 QualityInspect.vue — inspectSingle（无需修改）

`inspectSingle` 函数（L112 起）已使用 `config.station_number`，无需修改。

---

## 修改汇总

| 文件 | 改动 | 行数 |
|------|------|------|
| `src/stores/serial.js` | 默认波特率 9600 → 115200 | 1 |
| `backend/routers/serial.py` | 默认波特率 9600 → 115200 | 1 |
| `backend/schemas.py` | 默认波特率 9600 → 115200 (2处) | 2 |
| `backend/services/modbus_service.py` | 默认波特率 9600 → 115200 (2处) | 2 |
| `src/views/OneClickConfig.vue` | configSingle 站号固定为 1 (2处) | 2 |

共修改 **5 个文件**，**8 处改动**。

---

## 验证方式

1. 打开 `http://localhost:5173/`，观察右上角串口状态栏显示 `COM2 @ 115200`
2. 打开串口配置弹窗，波特率下拉默认选中 115200
3. 点击配置按钮，发送的站号应为 1（后端日志可查）
4. 点击检测按钮，发送的站号应为数据库中的值（后端日志可查）
