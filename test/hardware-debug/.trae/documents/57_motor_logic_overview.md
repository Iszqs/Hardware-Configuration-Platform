# 57电机配置与检测逻辑说明

## 设备类型

- **35电机**：`device_type_id === 1`（标签: "35电机"）
- **57电机**：`device_type_id === 2`（标签: "57电机"）

---

## 57电机配置按钮

### 流程

1. **前端** `OneClickConfig.vue` - `configSingle(idx)` 函数
   - 判断 `config.device_type_id !== 1`（即57电机）
   - 调用 `api.writeModbusConfig({ station_number, baud_rate })`

2. **后端** `modbus_service.py` - `write_config(station, baud_rate)` 函数
   ```python
   def write_config(self, station: int, baud_rate: int) -> dict:
       # 1. 校验波特率是否支持 (9600 或 115200)
       baud_val = BAUD_RATE_MAP.get(baud_rate)  # {9600: 6, 115200: 12}

       # 2. 确保串口连接
       if not self.ensure_connected():
           return {'success': False, 'message': '串口未连接，无法配置'}

       # 3. 自动检测设备当前波特率（尝试115200→9600）
       detected = self.detect_baud_rate(station)

       # 4. 写入目标波特率到寄存器 0x0009
       result = self.write_register(station, 0x0009, baud_val)

       # 5. 切换串口波特率
       self._serial.baudrate = baud_rate
       self.baud_rate = baud_rate
       time.sleep(0.2)

       # 6. 发送断电保存指令到寄存器 0x00DC
       saved = self.write_register(station, 0x00DC, 1)
       if not saved:
           time.sleep(0.5)
           saved = self.write_register(station, 0x00DC, 1)  # 重试
   ```

### 关键点

- **使用数据库站号直接通信**：传入的 `station` 参数直接用于写操作
- **自动波特率检测**：`detect_baud_rate(station)` 会在写入前先尝试与设备通信（尝试 115200 → 9600），因为设备当前波特率可能与串口不同
- **只写波特率，不写站号**：寄存器 0x0066（站号）不会被写入
- **断电保存**：写入完成后发送寄存器 0x00DC = 1 保存到设备

---

## 57电机检测按钮

### 流程

1. **前端** `OneClickConfig.vue` - `inspectSingle(idx)` 函数
   - 调用 `api.inspectModbus({ station_number, baud_rate, device_type_id })`

2. **后端** `modbus_service.py` - `inspect(station, target_baud_rate, device_type_id)` 函数
   ```python
   def inspect(self, station: int, target_baud_rate: int = 9600, device_type_id: int = 1) -> dict:
       items = []

       if device_type_id == 1:
           # 35电机：验证站号是否与数据库一致
           station_val = self.read_register(station, 0x0066)
           items.append({
               'name': '站号验证',
               'passed': station_val == station,
               'detail': f'读取站号: {station_val}, 期望: {station}'
           })
       else:
           # 57电机：只验证设备有响应，不验证站号
           station_val = self.read_register(station, 0x0066)
           items.append({
               'name': '设备响应',
               'passed': station_val >= 1,
               'detail': f'当前站号: {station_val if station_val >= 0 else "无响应"}'
           })

       # 57电机检测：读取并验证波特率
       baud_val = self.read_register(station, 0x0009)
       target_baud_val = BAUD_RATE_MAP.get(target_baud_rate, -1)
       baud_passed = baud_val == target_baud_val if target_baud_val > 0 else baud_val in BAUD_RATE_MAP.values()
       items.append({
           'name': '波特率验证',
           'passed': baud_passed,
           'detail': f'读取波特率值: {baud_val}, 期望: {target_baud_rate}'
       })

       return {'passed': all(item['passed'] for item in items), 'items': items, 'station': station}
   ```

### 关键点

- **57电机不验证站号**：设备响应检查只要求 `station_val >= 1`（设备有响应即可）
- **只验证波特率**：检查寄存器 0x0009 的值是否与数据库中的目标波特率一致
- **返回检查项列表**：前端根据 `items` 数组显示详细的验证结果

---

## 35电机 vs 57电机 对比

| 项目 | 35电机 (device_type_id=1) | 57电机 (device_type_id=2) |
|------|-------------------------|--------------------------|
| 配置方式 | 专用 `write_config_35`，先扫描站号1→全扫1-30，再写站号+波特率 | 使用通用 `write_config`，用数据库站号直接写波特率 |
| 检测站号 | 验证站号与数据库一致 | 只验证设备有响应 |
| 检测波特率 | 验证波特率与数据库一致 | 验证波特率与数据库一致 |
| 断电保存 | 写入 0x00DC = 1 | 写入 0x00DC = 1 |

---

## 相关寄存器

| 寄存器 | 功能 | 说明 |
|--------|------|------|
| 0x0009 | 波特率 | 值 6=9600, 12=115200 |
| 0x0066 | 站号 | 设备地址 |
| 0x00DC | 断电保存 | 写入 1 保存配置 |

---

## 当前实现状态

✅ **57电机配置**：已按需求实现，使用数据库站号直接写波特率
✅ **57电机检测**：已按需求实现，只验证波特率（不验证站号）
