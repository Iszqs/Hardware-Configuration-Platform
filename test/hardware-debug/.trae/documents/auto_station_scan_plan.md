# 35电机和57电机配置/检测时自动扫描站号

## 需求

- **35电机**和**57电机**：点击配置和检测按钮时，自动扫描波特率(115200/9600)×站号(1-30)找到设备，然后执行后续操作
- 配置：写入波特率 + 写入数据库站号 + 断电保存
- 检测：读取寄存器验证

---

## 当前状态

当前 [modbus_service.py](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/backend/services/modbus_service.py) 的瓶颈：

1. `detect_baud_rate(station)` — 只能扫波特率，需要预先知道站号
2. `write_config(station, baud_rate)` — 使用传入的固定站号，如果设备实际站号不同则通信失败
3. `inspect(station)` — 也依赖传入的固定站号
4. 前端 `configSingle` 中 35电机写站号用站号1（假设设备当前在站号1），57电机更是直接固定站号1

**问题**：如果设备当前站号不是1，无论波特率是否匹配，通信都会失败。

---

## 修改方案

### 文件1：`backend/services/modbus_service.py`

#### 1.1 新增 `detect_device()` 方法

```python
def detect_device(self) -> tuple:
    """扫描所有波特率×站号组合，返回 (baud_rate, station_number)"""
    print('开始设备探测（波特率×站号）...')
    for baud in KNOWN_BAUD_RATES:
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
                print(f'设备探测成功: 波特率={baud}, 站号={station}')
                self._serial.timeout = 1
                return (baud, station)

    self._serial.timeout = 1
    raise RuntimeError('无法与设备通信，请检查串口连接和设备电源')
```

#### 1.2 修改 `write_config()` — 加入站号探测和站号写入流程

```python
def write_config(self, target_station: int, baud_rate: int) -> dict:
    """
    配置设备：
    1. 自动探测设备（波特率×站号）
    2. 写入目标波特率
    3. 如果目标站号与当前站号不同，写入目标站号
    4. 断电保存
    """
    baud_val = BAUD_RATE_MAP.get(baud_rate)
    if baud_val is None:
        return {'success': False, 'message': f'不支持的波特率: {baud_rate}'}

    if not self.ensure_connected():
        return {'success': False, 'message': '串口未连接，无法配置'}

    try:
        found_baud, found_station = self.detect_device()
    except RuntimeError as e:
        return {'success': False, 'message': str(e)}

    print(f'设备当前: 波特率={found_baud}, 站号={found_station}')
    print(f'目标: 波特率={baud_rate}, 站号={target_station}')

    # 写入目标波特率
    print(f'写入波特率 {baud_rate}...')
    result = self.write_register(found_station, 0x0009, baud_val)
    if not result:
        return {'success': False, 'message': '波特率写入失败'}
    
    # 切换串口波特率到目标值
    self._serial.baudrate = baud_rate
    self.baud_rate = baud_rate
    time.sleep(0.2)

    # 写入目标站号（如果与当前站号不同）
    current_station = self.read_register(found_station, 0x0066)
    if current_station != target_station:
        print(f'写入站号 {target_station}...')
        result = self.write_register(found_station, 0x0066, target_station)
        if not result:
            return {'success': False, 'message': '站号写入失败'}
        time.sleep(0.2)
        # 站号变更后，后续使用新站号通信
        save_station = target_station
    else:
        save_station = found_station

    # 断电保存
    self._serial.timeout = 0.05
    self._serial.reset_input_buffer()
    self._serial.timeout = 1

    print(f'发送断电保存指令（站号 {save_station}）...')
    saved = self.write_register(save_station, 0x00DC, 1)
    if not saved:
        time.sleep(0.5)
        saved = self.write_register(save_station, 0x00DC, 1)
    if not saved:
        return {'success': False, 'message': '配置成功，但断电保存失败，设备无响应'}

    return {'success': True, 'message': f'配置成功: 站号 {save_station}, 波特率 {baud_rate}'}
```

#### 1.3 修改 `inspect()` — 加入设备探测

```python
def inspect(self) -> dict:
    """自动探测设备后检测"""
    if not self.ensure_connected():
        return {'passed': False, 'items': [{'name': '串口连接', 'passed': False, 'detail': '串口未连接'}]}

    try:
        found_baud, found_station = self.detect_device()
        self._serial.baudrate = found_baud
        self.baud_rate = found_baud
    except RuntimeError as e:
        return {'passed': False, 'items': [{'name': '设备探测', 'passed': False, 'detail': str(e)}]}

    items = []
    station_val = self.read_register(found_station, 0x0066)
    items.append({
        'name': '站号验证',
        'passed': station_val >= 1 and station_val <= 247,
        'detail': f'当前站号: {station_val}'
    })

    baud_val = self.read_register(found_station, 0x0009)
    items.append({
        'name': '波特率验证',
        'passed': baud_val in BAUD_RATE_MAP.values(),
        'detail': f'当前波特率值: {baud_val}'
    })

    return {'passed': all(item['passed'] for item in items), 'items': items, 'station': found_station}
```

### 文件2：`backend/routers/modbus.py`

#### 2.1 修改 `inspect` 路由

```python
@router.post('/inspect')
async def inspect_device(data: dict):
    result = modbus_service.inspect()
    return result
```

不需要 `station_number` 参数了，由后端自动探测。

#### 2.2 `write-config` 路由（不变）

保持现有代码不变，因为 `target_station` 和 `baud_rate` 参数来自前端请求体。

### 文件3：`src/views/OneClickConfig.vue`

#### 3.1 修改 `configSingle` — 所有设备类型统一流程

```javascript
async function configSingle(idx) {
  if (!project.value || configInProgress.value) return
  selectedIndex.value = idx
  configInProgress.value = true
  const config = project.value.device_configs[idx]

  try {
    const result = await api.writeModbusConfig({
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      device_type_id: config.device_type_id
    })

    if (result.success) {
      serialStore.config.baudRate = config.baud_rate
    }

    lastResult.value = { /* ... 不变 ... */ }

    if (result.success && !configuredIndexes.value.includes(idx)) {
      configuredIndexes.value.push(idx)
    }
  } catch (error) { /* ... 不变 ... */ }

  configInProgress.value = false
}
```

**关键变化**：
- **移除**了 `if (config.device_type_id === 1)` 的特殊处理（不再需要前端写站号）
- 所有设备类型统一走 `writeModbusConfig`，站号探测由后端自动完成
- `station_number` 传递数据库中的目标站号

#### 3.2 `inspectSingle` 不变

`inspectSingle` 已经使用 `config.station_number`，但后端 `inspect` 路由会忽略该参数并自动探测。可以保持前端代码不变，或简化传参。

### 文件4：`src/views/QualityInspect.vue`

#### 4.1 `inspectSingle` 不变

同 OneClickConfig.vue 的 `inspectSingle` — 后端会忽略 `station_number` 参数并自动探测。

---

## 修改汇总

| 文件 | 改动 | 说明 |
|------|------|------|
| `modbus_service.py` | 新增 `detect_device()` | 扫描波特率×站号组合 |
| `modbus_service.py` | 重写 `write_config()` | 自动探测 → 写波特率 → 写站号 → 保存 |
| `modbus_service.py` | 重写 `inspect()` | 自动探测 → 读取验证 |
| `modbus.py` | 修改 `inspect` 路由 | 去掉 station 参数依赖 |
| `OneClickConfig.vue` | 简化 `configSingle` | 移除 device_type_id 分支，统一流程 |
| `OneClickConfig.vue` / `QualityInspect.vue` | `inspectSingle` 不变 | 后端自动探测 |

---

## 验证方式

1. 将设备站号手动改为 5（用串口工具或之前的配置功能）
2. 进入硬件配置页面，设置该设备数据库站号为 8，波特率 115200
3. 点击配置按钮 → 后端自动扫描1-30 → 发现站号5 → 写入波特率 → 写入站号8 → 保存
4. 点击检测按钮 → 自动扫描 → 发现站号8（刚写入的）→ 读取验证
5. 用串口工具验证设备当前站号确实为 8
