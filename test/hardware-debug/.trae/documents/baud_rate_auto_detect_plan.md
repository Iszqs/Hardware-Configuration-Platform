# 波特率自动探测方案

## 问题描述

串口默认波特率已改为 115200，但立三电机可能当前工作在 9600。此时点击"配置"按钮时，串口以 115200 打开但电机工作在 9600，双方波特率不匹配，Modbus 通信失败。

## 核心解决思路

在 `write_config` 执行真正的配置之前，**逐一尝试所有已知波特率**与设备建立通信，找到能成功通信的波特率，再执行后续流程。

## 修改内容

### 仅修改 1 个文件：`backend/services/modbus_service.py`

#### 3.1 新增 `detect_baud_rate` 方法

在 `ModbusService` 类中新增一个方法，在 `write_config` 之前调用：

```python
KNOWN_BAUD_RATES = [115200, 9600]

def detect_baud_rate(self, station: int) -> int:
    for baud in self.KNOWN_BAUD_RATES:
        if not self.is_connected() or self.baud_rate != baud:
            self.connect(self.port or 'COM2', baud)
            time.sleep(0.1)
        self._serial.timeout = 0.05
        self._serial.reset_input_buffer()
        self._serial.timeout = 0.5
        
        cmd = struct.pack('>BBHH', station, 0x03, 0x0066, 1)
        frame = build_frame(cmd)
        self.send_raw(frame)
        resp = self.read_response(8)
        
        if len(resp) >= 5 and resp[1] == 0x03:
            print(f'波特率探测成功: {baud}')
            self._serial.timeout = 1
            return baud
    
    self._serial.timeout = 1
    raise RuntimeError('无法与设备通信，请检查串口连接和设备电源')
```

#### 3.2 修改 `write_config` 方法

```python
def write_config(self, station: int, baud_rate: int) -> dict:
    baud_val = BAUD_RATE_MAP.get(baud_rate)
    if baud_val is None:
        return {'success': False, 'message': f'不支持的波特率: {baud_rate}'}

    if not self.ensure_connected():
        return {'success': False, 'message': '串口未连接，无法配置'}

    try:
        detected = self.detect_baud_rate(station)
    except RuntimeError as e:
        return {'success': False, 'message': str(e)}

    if detected != baud_rate:
        print(f'设备当前波特率为 {detected}，需要先切换至 {baud_rate}')

    result = self.write_register(station, 0x0009, baud_val)
    if not result:
        return {'success': False, 'message': '波特率写入失败'}

    if self._serial and self.baud_rate != baud_rate:
        self._serial.baudrate = baud_rate
        self.baud_rate = baud_rate
        time.sleep(0.2)
    else:
        time.sleep(0.2)

    self._serial.timeout = 0.05
    self._serial.reset_input_buffer()
    self._serial.timeout = 1

    saved = self.write_register(station, 0x00DC, 1)
    if not saved:
        time.sleep(0.5)
        saved = self.write_register(station, 0x00DC, 1)
    if not saved:
        return {'success': False, 'message': '波特率写入成功，但断电保存失败，设备无响应'}

    return {'success': True, 'message': f'站号 {station} 波特率 {baud_rate} 配置成功并已保存'}
```

## 验证方式

1. 电机波特率为 9600 时点击配置 → 探测到 9600 → 写入目标波特率 → 成功
2. 电机波特率为 115200 时点击配置 → 探测到 115200 → 写入目标波特率 → 成功
3. 电机断电或其他故障 → 探测失败 → 返回友好错误提示
