import sys
sys.path.insert(0, 'backend')

import unittest
import struct
from unittest.mock import MagicMock
from services.modbus_service import ModbusService, BAUD_RATE_MAP, build_frame

class TestWriteConfig(unittest.TestCase):
    """write_config must adjust serial baudrate between writing register 0x0009 and 0x00DC."""

    def setUp(self):
        self.service = ModbusService()
        self.service._serial = MagicMock()
        self.service._serial.is_open = True
        self.service._serial.baudrate = 9600
        self.service.port = 'COM2'
        self.service.baud_rate = 9600

        # Mock a successful Modbus write response: station(1) + func(0x06) + addr(2) + val(2) + crc(2)
        def mock_read(length):
            return struct.pack('>BBHH', 1, 0x06, 0, 0) + b'\x00\x00'
        self.service._serial.read = mock_read

    def test_adjusts_baudrate_before_save_command(self):
        # Track write_register calls
        actual_registers = []

        def tracking_write_register(station, address, value):
            actual_registers.append((station, address, value))
            return True

        self.service.write_register = tracking_write_register

        result = self.service.write_config(1, 115200)

        # Verify: register 0x0009 (baud) written first, then 0x00DC (save)
        self.assertTrue(result['success'], msg=result.get('message', ''))
        self.assertEqual(len(actual_registers), 2,
            'write_config must write 2 registers (baud + save)')
        self.assertEqual(actual_registers[0][1], 0x0009,
            'First register must be baud rate (0x0009)')
        self.assertEqual(actual_registers[1][1], 0x00DC,
            'Second register must be save (0x00DC)')
        self.assertEqual(actual_registers[1][2], 1,
            'Save register value should be 1')

    def test_serial_baudrate_updated_to_new_value(self):
        result = self.service.write_config(1, 115200)

        self.assertTrue(result['success'], msg=result.get('message', ''))
        # The serial baudrate must be updated to the target baud rate
        self.assertEqual(self.service._serial.baudrate, 115200,
            'Serial baudrate must be updated to target baud rate')

    def test_serial_baudrate_not_updated_for_same_baudrate(self):
        self.service._serial.baudrate = 9600

        result = self.service.write_config(1, 9600)

        self.assertTrue(result['success'], msg=result.get('message', ''))
        self.assertEqual(self.service._serial.baudrate, 9600,
            'Serial baudrate stays same when target matches')

if __name__ == '__main__':
    unittest.main()
