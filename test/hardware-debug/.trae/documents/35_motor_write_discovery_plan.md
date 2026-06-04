# 35电机配置按钮 - WRITE方式发现设备

## 需求变更

**当前行为**（READ方式发现）：
1. `find_device_35()` 使用 READ (0x03) 功能码尝试读取站号寄存器
2. 找到设备后，再 WRITE 波特率、站号、断电保存

**新需求**（WRITE方式发现）：
1. 直接使用 WRITE (0x06) 功能码写入站号寄存器 0x0066 尝试通信
2. 先试站号1（波特率115200→9600）
3. 无响应则试站号2-30（波特率115200→9600）
4. 写入成功后，继续写入波特率、断电保存

---

## 测试文件

### 文件：`tests/test_write_config_35.py`

```python
import sys
sys.path.insert(0, 'backend')

import unittest
import struct
from unittest.mock import MagicMock, patch
from services.modbus_service import ModbusService, BAUD_RATE_MAP, KNOWN_BAUD_RATES, build_frame

class TestWriteConfig35Discovery(unittest.TestCase):
    """35电机配置：使用WRITE方式发现设备"""

    def setUp(self):
        self.service = ModbusService()
        self.service._serial = MagicMock()
        self.service._serial.is_open = True
        self.service._serial.baudrate = 115200
        self.service.port = 'COM2'
        self.service.baud_rate = 115200
        self.service.is_connected = MagicMock(return_value=True)

    def test_write_config_35_tries_station_1_first(self):
        """优先尝试站号1"""
        # 记录所有尝试的 station
        tried_stations = []
        tried_bauds = []

        original_write_register = self.service.write_register
        call_count = [0]

        def mock_write_register(station, address, value):
            call_count[0] += 1
            if address == 0x0066:  # 站号寄存器
                tried_stations.append(station)
                tried_bauds.append(self.service.baud_rate)
            # 前3次调用返回失败（discovery阶段），后续返回成功
            if call_count[0] <= 3:
                return False
            return True

        self.service.write_register = mock_write_register

        # Mock read_response for write operations
        call_idx = [0]
        def mock_read(size):
            call_idx[0] += 1
            if call_idx[0] <= 3:
                return b''  # 无响应
            # Discovery成功后返回正常响应
            return struct.pack('>BBHH', 1, 0x06, 0x00DC, 0) + b'\x00\x00'

        self.service._serial.read = mock_read

        result = self.service.write_config_35(10, 115200)

        # 应该先尝试站号1
        self.assertIn(1, tried_stations, "应该先尝试站号1")

    def test_write_config_35_falls_back_to_station_2_30(self):
        """站号1失败后尝试站号2-30"""
        tried_stations = []

        original_write_register = self.service.write_register
        call_count = [0]

        def mock_write_register(station, address, value):
            if address == 0x0066:
                tried_stations.append(station)
            call_count[0] += 1
            # 所有discovery都失败
            return False

        self.service.write_register = mock_write_register

        def mock_read(size):
            return b''  # 无响应

        self.service._serial.read = mock_read

        result = self.service.write_config_35(10, 115200)

        # 应该尝试过站号2-30
        self.assertTrue(any(s > 1 for s in tried_stations), "站号1失败后应尝试站号2-30")

    def test_write_config_35_uses_both_baud_rates(self):
        """尝试两种波特率115200和9600"""
        tried_bauds = []

        original_write_register = self.service.write_register

        def mock_write_register(station, address, value):
            if address == 0x0066:
                tried_bauds.append(self.service.baud_rate)
            return False

        self.service.write_register = mock_write_register

        def mock_read(size):
            return b''

        self.service._serial.read = mock_read

        self.service.write_config_35(10, 115200)

        # 应该尝试过两种波特率
        self.assertTrue(len(set(tried_bauds)) > 1 or len(tried_bauds) >= 2,
                        f"应该尝试两种波特率，实际尝试: {tried_bauds}")

    def test_write_config_35_returns_error_when_no_device_found(self):
        """未找到设备时返回错误"""
        def mock_write_register(station, address, value):
            return False  # 所有写入都失败

        self.service.write_register = mock_write_register

        def mock_read(size):
            return b''

        self.service._serial.read = mock_read

        result = self.service.write_config_35(10, 115200)

        self.assertFalse(result['success'])
        self.assertIn('未找到', result['message'])

    def test_write_config_35_continues_config_after_discovery(self):
        """Discovery成功后继续写入波特率和保存"""
        write_calls = []

        def mock_write_register(station, address, value):
            write_calls.append((station, address, value))
            return True

        self.service.write_register = mock_write_register

        # Discovery成功后返回正常响应
        call_idx = [0]
        def mock_read(size):
            call_idx[0] += 1
            if call_idx[0] == 1:
                return struct.pack('>BBHH', 1, 0x06, 0x0066, 0) + b'\x00\x00'  # 站号写入响应
            return struct.pack('>BBHH', 1, 0x06, 0x0009, 0) + b'\x00\x00'  # 后续响应

        self.service._serial.read = mock_read

        with patch.object(self.service, 'connect', return_value=True):
            result = self.service.write_config_35(10, 115200)

        # 应该写入站号(0x0066)、波特率(0x0009)、断电保存(0x00DC)
        addresses = [call[1] for call in write_calls]
        self.assertIn(0x0066, addresses, "应该写入站号寄存器")
        self.assertIn(0x0009, addresses, "应该写入波特率寄存器")
        self.assertIn(0x00DC, addresses, "应该写入断电保存寄存器")


class TestWriteConfig35EndToEnd(unittest.TestCase):
    """35电机配置端到端测试：站号1直接成功"""

    def setUp(self):
        self.service = ModbusService()
        self.service._serial = MagicMock()
        self.service._serial.is_open = True
        self.service._serial.baudrate = 115200
        self.service.port = 'COM2'
        self.service.baud_rate = 115200
        self.service.is_connected = MagicMock(return_value=True)

    def test_station_1_success_completes_config(self):
        """站号1写入成功时，完整配置流程"""
        write_calls = []

        def mock_write_register(station, address, value):
            write_calls.append({'station': station, 'address': address, 'value': value})
            return True

        self.service.write_register = mock_write_register

        # 所有读取都返回成功
        def mock_read(size):
            return struct.pack('>BBHH', 1, 0x06, 0, 0) + b'\x00\x00'

        self.service._serial.read = mock_read

        with patch.object(self.service, 'connect', return_value=True):
            result = self.service.write_config_35(10, 115200)

        self.assertTrue(result['success'], msg=result.get('message', ''))

        # 验证写入顺序：discovery(站号) → 波特率 → 站号 → 保存
        addresses = [call['address'] for call in write_calls]
        self.assertEqual(addresses.count(0x0066), 2, "站号寄存器应写入2次：discovery + 正式写入")
        self.assertIn(0x0009, addresses, "应写入波特率")
        self.assertIn(0x00DC, addresses, "应写入断电保存")


if __name__ == '__main__':
    unittest.main()
```

---

## 实施步骤

### Step 1: 创建测试文件
- 创建 `tests/test_write_config_35.py`

### Step 2: 运行测试验证RED
```bash
cd d:\Users\OL\Desktop\硬件配置平台\test\hardware-debug
python -m pytest tests/test_write_config_35.py -v
```
**期望**: 测试应该失败（因为当前实现使用READ方式发现设备）

### Step 3: 修改 `write_config_35` 方法
修改 `backend/services/modbus_service.py` 中的 `write_config_35` 方法：

```python
def write_config_35(self, target_station: int, target_baud_rate: int) -> dict:
    baud_val = BAUD_RATE_MAP.get(target_baud_rate)
    if baud_val is None:
        return {'success': False, 'message': f'不支持的波特率: {target_baud_rate}'}

    # 使用WRITE方式发现设备
    found_baud, found_station = self._find_device_35_by_write(target_station, target_baud_rate)

    if found_station is None:
        return {'success': False, 'message': '未找到35电机设备，请检查串口连接和设备电源'}

    # 写入目标波特率
    result = self.write_register(found_station, 0x0009, baud_val)
    if not result:
        return {'success': False, 'message': '波特率写入失败'}

    # 切换串口波特率
    self._serial.baudrate = target_baud_rate
    self.baud_rate = target_baud_rate
    time.sleep(0.2)

    # 写入目标站号
    result = self.write_register(target_station, 0x0066, target_station)
    if not result:
        return {'success': False, 'message': '站号写入失败'}
    time.sleep(0.2)

    # 断电保存
    self._serial.timeout = 0.05
    self._serial.reset_input_buffer()
    self._serial.timeout = 1

    saved = self.write_register(target_station, 0x00DC, 1)
    if not saved:
        time.sleep(0.5)
        saved = self.write_register(target_station, 0x00DC, 1)
    if not saved:
        return {'success': False, 'message': '配置成功，但断电保存失败，设备无响应'}

    return {'success': True, 'message': f'35电机配置成功: 站号 {target_station}, 波特率 {target_baud_rate}'}


def _find_device_35_by_write(self, target_station: int, target_baud_rate: int) -> tuple:
    """
    使用WRITE方式发现35电机设备。
    返回: (found_baud, found_station) 或 (None, None)
    """
    print('开始35电机设备查找(WRITE模式)...')

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

        # 使用WRITE功能码(0x06)写入站号寄存器
        cmd = struct.pack('>BBHH', 1, 0x06, 0x0066, 1)
        frame = build_frame(cmd)
        self.send_raw(frame)
        resp = self.read_response(8)

        if len(resp) >= 5 and resp[1] == 0x06:
            print(f'站号1写入成功: 波特率={baud}')
            self._serial.timeout = 1
            return (baud, 1)

    # 第二步：全量扫描站号2-30
    print('第二步：站号1未找到，开始全量扫描(站号2-30)...')
    for baud in KNOWN_BAUD_RATES:
        print(f'  尝试波特率 {baud}...')
        if not self.is_connected() or self.baud_rate != baud:
            self.connect(self.port or 'COM2', baud)
            time.sleep(0.1)
        self._serial.timeout = 0.05
        self._serial.reset_input_buffer()
        self._serial.timeout = 0.3

        for station in range(2, 31):
            cmd = struct.pack('>BBHH', station, 0x06, 0x0066, station)
            frame = build_frame(cmd)
            self.send_raw(frame)
            resp = self.read_response(8)

            if len(resp) >= 5 and resp[1] == 0x06:
                print(f'全量扫描成功: 波特率={baud}, 站号={station}')
                self._serial.timeout = 1
                return (baud, station)

    self._serial.timeout = 1
    return (None, None)
```

### Step 4: 运行测试验证GREEN
```bash
python -m pytest tests/test_write_config_35.py -v
```
**期望**: 所有测试通过

### Step 5: 验证其他测试仍然通过
```bash
python -m pytest tests/ -v
```

---

## 关键变更说明

| 项目 | 当前(READ) | 新(WRITE) |
|------|-----------|----------|
| 发现方式 | READ寄存器0x0066 | WRITE寄存器0x0066 |
| 功能码 | 0x03 (读) | 0x06 (写) |
| 站号1失败后 | 扫描站号1-30 | 扫描站号2-30 |
| 写入站号值 | 目标站号 | 临时站号(station值)用于discovery |

---

## 验证步骤

1. 运行 `pytest tests/test_write_config_35.py -v` 确认新测试失败（RED）
2. 实现 `_find_device_35_by_write` 方法
3. 运行测试确认通过（GREEN）
4. 运行所有测试确认无回归（REFACTOR）
5. 手动测试：连接35电机设备，点击配置按钮，观察日志输出
