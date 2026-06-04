# 硬件配置按钮指令发送失败问题修复计划（TDD）

## 问题描述
点击硬件配置页面的"配置"或"检测"按钮时，没有实际发送 Modbus 指令到硬件设备。

## 根因分析

**关键发现：两个独立的 ModbusService 实例**

| 文件 | 行为 |
|------|------|
| `backend/routers/serial.py` | 创建 `modbus_service = ModbusService()`，处理连接请求 |
| `backend/routers/modbus.py` | 创建**另一个** `modbus_service = ModbusService()`，处理配置/检测请求 |

当用户点击"连接"按钮：
1. `serial.py` 中的实例调用 `connect()` → 串口连接成功
2. `modbus.py` 中的实例仍保持 `self._serial = None`

当用户点击"配置"/"检测"按钮：
1. `modbus.py` 中的实例调用 `write_config()` / `inspect()`
2. `is_connected()` 返回 `False`，所有指令被跳过

**根本原因：缺少共享的串口服务实例**

## 修复方案

创建单例模式的 ModbusService，确保整个后端共享同一个串口连接：

### 方案 A：模块级共享（推荐）
在 `backend/services/__init__.py` 中创建全局实例，所有路由从这里导入

### 方案 B：依赖注入
通过 FastAPI 的依赖注入系统共享实例

选择**方案 A**，更简单直接，改动最小。

## TDD 实施步骤

### 第一阶段：RED（写失败测试）

#### Step 1: 创建测试文件 `tests/modbus-singleton.test.js`
测试内容：
1. 验证 `serial.py` 和 `modbus.py` 使用同一个 `ModbusService` 实例
2. 验证连接后 `is_connected()` 返回 `True`
3. 验证配置指令在连接状态下能正常发送

**预期：测试 1 和 3 失败**（因为当前是两个独立实例）

### 第二阶段：GREEN（修复代码）

#### Step 2: 修改 `backend/services/__init__.py`
```python
from .modbus_service import ModbusService

modbus_service = ModbusService()
```

#### Step 3: 修改 `backend/routers/serial.py`
```python
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
import serial.tools.list_ports

# 从 services 模块导入共享实例
from ..services import modbus_service

router = APIRouter(prefix='/api/serial', tags=['串口'])
# 移除本地创建的实例：modbus_service = ModbusService()
```

#### Step 4: 修改 `backend/routers/modbus.py`
```python
from fastapi import APIRouter, HTTPException
# 从 services 模块导入共享实例
from ..services import modbus_service

router = APIRouter(prefix='/api/modbus', tags=['Modbus通信'])
# 移除本地创建的实例：modbus_service = ModbusService()
```

### 第三阶段：REFACTOR（验证）

#### Step 5: 运行全部测试，确认全部 PASS
- `node tests/modbus-singleton.test.js`
- `node tests/input-field-sizing.test.js`
- `node tests/typography-tokens.test.js`
- `node tests/card-tokens.test.js`
- `node tests/test_add_device_custom_name.js`
- `node tests/test_save_device_name.js`

#### Step 6: 构建验证
- `npm run build`

---

## 影响范围分析

| 影响项 | 说明 |
|--------|------|
| 串口连接 | 连接状态在 `serial.py` 和 `modbus.py` 之间共享 |
| Modbus 指令 | 配置/检测指令现在能正确发送到串口 |
| 前端交互 | 用户连接串口后，配置和检测按钮将实际生效 |

## 验证清单

- [ ] RED 测试正确失败（两个实例不共享）
- [ ] GREEN 修复后测试通过（单例共享）
- [ ] 全部 6 组测试通过
- [ ] `npm run build` 成功
- [ ] 连接串口后，配置/检测按钮能发送指令