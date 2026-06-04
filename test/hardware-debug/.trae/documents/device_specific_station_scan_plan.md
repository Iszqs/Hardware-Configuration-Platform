# 35电机/57电机配置与检测的站号处理方案

## 需求

| 设备 | 操作 | 行为 |
|------|------|------|
| **35电机** | 配置（写站号+波特率） | 先试站号1扫波特率(115200/9600) → 找不到则全扫(站号1-30×波特率) → 找到后写站号+波特率 |
| **35电机** | 检测 | 使用数据库站号检测站号+波特率是否与数据库一致 |
| **57电机** | 检测 | 使用数据库站号检测波特率是否与数据库一致 |
| **57电机** | 配置（写波特率） | 使用数据库站号直接写波特率 |

---

## 修改内容

### 文件1：`backend/services/modbus_service.py`

#### 1.1 新增 `find_device_35()` 方法

在 `detect_baud_rate` 方法之后新增：

```python
def find_device_35(self) -> tuple:
    """35电机设备查找：先试站号1，再全扫，返回 (found_baud, found_station)"""
    print('开始35电机设备查找...')
    
    # 第一步：尝试站号1
    print('第一步：尝试站号1...')
    for baud in KNOWN_BAUD_RATES:
        print(f'  尝试 站号=1, 波特率={baud}')
        if not self.is_connected() or self.baud_rate != baud:
            self.connect(self.port or 'COM2', baud)
            time.sleep(0.1)
        self._serial.timeout = 0.05
        self._serial.reset_input_buffer()
        self._serial.timeout = 0.3
        
        cmd = struct.pack('>BBHH', 1, 0x03, 0x0066, 1)
        frame = build_frame(cmd)
        self.send_raw(frame)
        resp = self.read_response(8)
        
        if len(resp) >= 5 and resp[1] == 0x03:
            print(f'站号1查找成功: 波特率={baud}')
            self._serial.timeout = 1
            return (baud, 1)
    
    # 第二步：全量扫描
    print('第二步：站号1未找到，开始全量扫描(站号1-30)...')
    for baud in KNOWN_BAUD_RATES:
        print(f'  尝试波特率 {baud}...')
        if not self.is_connected() or self.baud_rate != baud:
            self.connect(self.port or 'COM2', baud)
            time.sleep(0.1)
        self._serial.timeout = 0.05
        self._serial.reset_input_buffer()
        self._serial.timeout = 0.3
        
        for station in range(1, 31):
            cmd = struct.pack('>BBHH', station, 0x03, 0x0066, 1)
            frame = build_frame(cmd)
            self.send_raw(frame)
            resp = self.read_response(8)
            
            if len(resp) >= 5 and resp[1] == 0x03:
                print(f'全量扫描成功: 波特率={baud}, 站号={station}')
                self._serial.timeout = 1
                return (baud, station)
    
    self._serial.timeout = 1
    raise RuntimeError('未找到35电机设备，请检查串口连接和设备电源')
```

#### 1.2 新增 `write_config_35()` 方法

```python
def write_config_35(self, target_station: int, target_baud_rate: int) -> dict:
    """35电机配置：自动查找设备后写入站号+波特率"""
    baud_val = BAUD_RATE_MAP.get(target_baud_rate)
    if baud_val is None:
        return {'success': False, 'message': f'不支持的波特率: {target_baud_rate}'}

    if not self.ensure_connected():
        return {'success': False, 'message': '串口未连接，无法配置'}

    try:
        found_baud, found_station = self.find_device_35()
    except RuntimeError as e:
        return {'success': False, 'message': str(e)}

    print(f'设备当前: 波特率={found_baud}, 站号={found_station}')
    print(f'目标: 波特率={target_baud_rate}, 站号={target_station}')

    # 写入目标波特率
    result = self.write_register(found_station, 0x0009, baud_val)
    if not result:
        return {'success': False, 'message': '波特率写入失败'}

    # 切换串口波特率
    self._serial.baudrate = target_baud_rate
    self.baud_rate = target_baud_rate
    time.sleep(0.2)

    # 写入目标站号
    print(f'写入站号 {target_station}...')
    result = self.write_register(target_station if found_baud == target_baud_rate else found_station, 0x0066, target_station)
    if not result:
        return {'success': False, 'message': '站号写入失败'}
    time.sleep(0.2)

    # 断电保存（使用新站号）
    self._serial.timeout = 0.05
    self._serial.reset_input_buffer()
    self._serial.timeout = 1

    print(f'发送断电保存指令（站号 {target_station}）...')
    saved = self.write_register(target_station, 0x00DC, 1)
    if not saved:
        time.sleep(0.5)
        saved = self.write_register(target_station, 0x00DC, 1)
    if not saved:
        return {'success': False, 'message': '配置成功，但断电保存失败，设备无响应'}

    return {'success': True, 'message': f'35电机配置成功: 站号 {target_station}, 波特率 {target_baud_rate}'}
```

### 文件2：`backend/routers/modbus.py`

新增路由：

```python
@router.post('/write-config-35')
async def write_config_35(data: dict):
    station_number = data.get('station_number', 1)
    baud_rate = data.get('baud_rate', 9600)
    result = modbus_service.write_config_35(station_number, baud_rate)
    return result
```

### 文件3：`src/api/index.js`

新增 API 方法：

```javascript
writeModbusConfig35(data) { return request('/api/modbus/write-config-35', { method: 'POST', body: data }) },
```

### 文件4：`src/views/OneClickConfig.vue`

#### 4.1 `configSingle` 函数

```javascript
async function configSingle(idx) {
  if (!project.value || configInProgress.value) return
  selectedIndex.value = idx
  configInProgress.value = true
  const config = project.value.device_configs[idx]
  
  try {
    let result
    if (config.device_type_id === 1) {
      // 35电机：自动扫描设备后写站号+波特率
      result = await api.writeModbusConfig35({
        station_number: config.station_number,
        baud_rate: config.baud_rate
      })
    } else {
      // 其他设备（57电机等）：使用数据库站号写波特率
      result = await api.writeModbusConfig({
        station_number: config.station_number,
        baud_rate: config.baud_rate
      })
    }
    
    if (result.success) {
      serialStore.config.baudRate = config.baud_rate
    }
    
    lastResult.value = { /* 不变 */ }
    
    if (result.success && !configuredIndexes.value.includes(idx)) {
      configuredIndexes.value.push(idx)
    }
  } catch (error) { /* 不变 */ }
  
  configInProgress.value = false
}
```

**关键变化**：
- 35电机：调用 `writeModbusConfig35`（自动扫描站号），只传 `baud_rate`
- 57电机：调用 `writeModbusConfig`，传 `station_number: config.station_number`（不再硬编码1）
- 移除原来 35电机的站号写入逻辑

#### 4.2 `inspectSingle` 函数（不变）

`inspectSingle` 已经使用 `config.station_number` 调用 `api.inspectModbus`，符合需求（所有设备都用数据库站号检测），无需修改。

---

## 修改汇总

| 文件 | 改动 |
|------|------|
| `modbus_service.py` | 新增 `find_device_35()` 和 `write_config_35()` 方法 |
| `modbus.py` | 新增 `POST /api/modbus/write-config-35` 路由 |
| `api/index.js` | 新增 `writeModbusConfig35()` API 方法 |
| `OneClickConfig.vue` | `configSingle` 中按设备类型分流：35电机走扫描API，57电机走常规API传数据库站号 |

共修改 **4 个文件**，新增 **3 处**（后端方法、路由、前端API），修改 **1 处**（前端configSingle逻辑）。

---

## 验证方式

**场景1：35电机配置**
1. 将35电机设备站号设为 5（用串口工具）
2. 在项目库中设置该设备数据库站号为 5，波特率 115200
3. 点击配置按钮
4. 期望：先扫站号1失败 → 全扫发现站号5 → 写入115200波特率 → 成功

**场景2：57电机配置**
1. 57电机设备站号与数据库一致（如站号3）
2. 点击配置按钮
3. 期望：直接用站号3通信 → 写入目标波特率 → 成功

**场景3：检测**
1. 35电机和57电机点击检测按钮
2. 期望：使用数据库站号直接检测
