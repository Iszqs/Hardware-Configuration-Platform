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
        self.service._serial.timeout = 1
        self.service._serial.reset_input_buffer = MagicMock()

    def test_write_config_35_tries_station_1_first(self):
        """优先尝试站号1"""
        sent_stations = []

        def mock_send_raw(frame):
            if frame[1] == 0x06:  # WRITE command
                station = frame[0]
                sent_stations.append(station)

        self.service.send_raw = mock_send_raw

        def mock_read_response(size):
            return b''  # 无响应

        self.service.read_response = mock_read_response
        self.service.is_connected = MagicMock(return_value=True)

        result = self.service.write_config_35(10, 115200)

        self.assertIn(1, sent_stations, "应该先尝试站号1")

    def test_write_config_35_falls_back_to_station_2_30(self):
        """站号1失败后尝试站号2-30"""
        sent_stations = []

        def mock_send_raw(frame):
            if frame[1] == 0x06:
                station = frame[0]
                sent_stations.append(station)

        self.service.send_raw = mock_send_raw

        def mock_read_response(size):
            return b''  # 无响应

        self.service.read_response = mock_read_response
        self.service.is_connected = MagicMock(return_value=True)

        result = self.service.write_config_35(10, 115200)

        self.assertTrue(any(s > 1 for s in sent_stations), f"站号1失败后应尝试站号2-30，实际: {sent_stations}")

    def test_write_config_35_uses_both_baud_rates(self):
        """尝试两种波特率115200和9600"""
        attempted_bauds = []
        original_connect = self.service.connect

        def mock_connect(port, baud):
            attempted_bauds.append(baud)
            return True

        self.service.connect = mock_connect
        self.service.is_connected = MagicMock(return_value=False)

        def mock_send_raw(frame):
            pass

        self.service.send_raw = mock_send_raw

        def mock_read_response(size):
            return b''  # 无响应

        self.service.read_response = mock_read_response

        self.service.write_config_35(10, 115200)

        baud_set = set(attempted_bauds)
        self.assertTrue(len(baud_set) >= 2 or len(attempted_bauds) >= 2,
                        f"应该尝试两种波特率，实际: {attempted_bauds}")

    def test_write_config_35_returns_error_when_no_device_found(self):
        """未找到设备时返回错误"""
        self.service.is_connected = MagicMock(return_value=True)

        def mock_send_raw(frame):
            pass

        self.service.send_raw = mock_send_raw

        def mock_read(size):
            return b''  # 无响应

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

        # Discovery阶段：站号1 WRITE成功
        discovery_done = [False]
        call_count = [0]

        def mock_send_raw(frame):
            pass

        self.service.send_raw = mock_send_raw

        def mock_read(size):
            call_count[0] += 1
            if call_count[0] == 1:
                return struct.pack('>BBHH', 1, 0x06, 0x0066, 0) + b'\x00\x00'
            return struct.pack('>BBHH', 1, 0x06, 0x0009, 0) + b'\x00\x00'

        self.service._serial.read = mock_read
        self.service.is_connected = MagicMock(return_value=True)

        with patch.object(self.service, 'connect', return_value=True):
            result = self.service.write_config_35(10, 115200)

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
        self.service._serial.timeout = 1
        self.service._serial.reset_input_buffer = MagicMock()
        self.service.is_connected = MagicMock(return_value=True)

    def test_station_1_success_completes_config(self):
        """站号1写入成功时，完整配置流程"""
        write_calls = []

        def mock_write_register(station, address, value):
            write_calls.append({'station': station, 'address': address, 'value': value})
            return True

        self.service.write_register = mock_write_register

        def mock_send_raw(frame):
            pass

        self.service.send_raw = mock_send_raw

        def mock_read(size):
            return struct.pack('>BBHH', 1, 0x06, 0, 0) + b'\x00\x00'

        self.service._serial.read = mock_read

        with patch.object(self.service, 'connect', return_value=True):
            result = self.service.write_config_35(10, 115200)

        self.assertTrue(result['success'], msg=result.get('message', ''))

        addresses = [call['address'] for call in write_calls]
        self.assertIn(0x0009, addresses, "应写入波特率")
        self.assertIn(0x0066, addresses, "应写入站号")
        self.assertIn(0x00DC, addresses, "应写入断电保存")


if __name__ == '__main__':
    unittest.main()
