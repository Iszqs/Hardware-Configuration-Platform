import serial
import serial.tools.list_ports
import struct
import time
from backend.services.log_service import add_log

# 波特率映射：实际波特率 -> 寄存器值
BAUD_RATE_MAP = {9600: 6, 115200: 12}
# 已知波特率列表（用于自动检测）
KNOWN_BAUD_RATES = [115200, 9600]

CRC16TABLE = [
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040,
]


def calc_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ CRC16TABLE[(crc ^ byte) & 0xFF]
    return crc


def build_frame(cmd: bytes) -> bytes:
    crc = calc_crc16(cmd)
    return cmd + struct.pack('<H', crc)


class ModbusService:
    def __init__(self):
        self._serial = None
        self.port = None
        self.baud_rate = None

    def connect(self, port: str, baud_rate: int = 9600) -> bool:
        try:
            if self._serial and self._serial.is_open:
                self._serial.close()
            self._serial = serial.Serial(
                port=port,
                baudrate=baud_rate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.port = port
            self.baud_rate = baud_rate
            return True
        except Exception as e:
            add_log(f'串口连接失败: {e}', 'error')
            self._serial = None
            return False

    def disconnect(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self.port = None
        self.baud_rate = None

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def send_raw(self, data: bytes) -> bool:
        if not self.is_connected():
            add_log('发送失败: 串口未连接', 'error')
            return False
        try:
            bytes_written = self._serial.write(data)
            add_log(f'发送: {data.hex().upper()}', 'info')
            return True
        except Exception as e:
            add_log(f'写入失败: {e}', 'error')
            return False

    def read_response(self, length: int = 8) -> bytes:
        if not self.is_connected():
            add_log('读取失败: 串口未连接', 'error')
            return b''
        try:
            data = self._serial.read(length)
            if len(data) > 0:
                add_log(f'接收: {data.hex().upper()}', 'success')
            else:
                add_log('读取超时，未收到响应', 'warning')
            return data
        except Exception as e:
            add_log(f'读取失败: {e}', 'error')
            return b''

    def write_register(self, station: int, address: int, value: int) -> bool:
        cmd = struct.pack('>BBHH', station, 0x06, address, value)
        frame = build_frame(cmd)
        if not self.send_raw(frame):
            return False
        resp = self.read_response(8)
        # Modbus 06 响应会回显写入的地址和值，直接验证
        if len(resp) >= 6 and resp[1] == 0x06:
            resp_addr = struct.unpack('>H', resp[2:4])[0]
            resp_value = struct.unpack('>H', resp[4:6])[0]
            if resp_addr == address and resp_value == value:
                return True
            add_log(f'写入回显不匹配: 地址={resp_addr:X}, 值={resp_value}', 'warning')
        return False

    def clear_buffer(self):
        if self._serial and self._serial.is_open:
            self._serial.timeout = 0.05
            leftover = self._serial.read(100)
            if leftover:
                add_log(f'清除缓冲区残留 {len(leftover)} 字节: {leftover.hex().upper()}', 'warning')
            self._serial.timeout = 1

    def read_register(self, station: int, address: int) -> int:
        cmd = struct.pack('>BBHH', station, 0x03, address, 1)
        frame = build_frame(cmd)
        if not self.send_raw(frame):
            return -1
        resp = self.read_response(8)
        if len(resp) >= 5 and resp[1] == 0x03:
            # 站号和波特率寄存器统一用大端序
            return struct.unpack('>H', resp[3:5])[0]
        return -1

    def ensure_connected(self) -> bool:
        if self.is_connected():
            return True
        baud = self.baud_rate or 115200
        add_log(f'串口未连接，尝试自动连接 COM2 ({baud} bps)...', 'warning')
        return self.connect('COM2', baud)

    def write_config_57(self, station: int, target_baud_rate: int) -> dict:
        """
        57电机配置：根据数据库站号写入波特率
        1. 尝试以当前波特率写入
        2. 无响应则切换波特率重试
        3. 验证写入结果
        4. 发送断电保存
        """
        baud_val = BAUD_RATE_MAP.get(target_baud_rate)
        if baud_val is None:
            return {'success': False, 'message': f'不支持的波特率: {target_baud_rate}'}

        add_log(f'57电机配置: 站号={station}, 目标波特率={target_baud_rate}', 'info')

        # 确保串口连接
        if not self.is_connected():
            for baud in KNOWN_BAUD_RATES:
                if self.connect(self.port or 'COM2', baud):
                    break
            if not self.is_connected():
                return {'success': False, 'message': '串口未连接'}

        # 尝试写入波特率（自动切换波特率重试）
        write_success = False
        current_baud = self.baud_rate
        for baud in KNOWN_BAUD_RATES:
            add_log(f'尝试以波特率 {baud} 写入...', 'info')
            if self.baud_rate != baud:
                self.connect(self.port or 'COM2', baud)
                time.sleep(0.1)

            if self.write_register(station, 0x0009, baud_val):
                write_success = True
                current_baud = baud
                add_log(f'波特率写入成功 (波特率={baud})', 'success')
                break

        if not write_success:
            return {'success': False, 'message': '波特率写入失败，设备无响应', 'current_baud_rate': current_baud}

        add_log('波特率写入成功，执行断电保存...', 'info')

        # 切换到目标波特率
        time.sleep(0.2)
        self._serial.baudrate = target_baud_rate
        self.baud_rate = target_baud_rate
        current_baud = target_baud_rate
        time.sleep(0.1)

        # 断电保存
        time.sleep(0.2)
        saved = self.write_register(station, 0x00DC, 1)
        if not saved:
            time.sleep(0.5)
            saved = self.write_register(station, 0x00DC, 1)

        if saved:
            return {'success': True, 'message': f'57电机配置成功: 波特率={target_baud_rate}', 'current_baud_rate': current_baud}
        else:
            return {'success': False, 'message': '配置成功但断电保存失败', 'current_baud_rate': current_baud}

    def inspect_57(self, station: int, target_baud_rate: int) -> dict:
        """
        57电机检测：读取设备站号和波特率，与数据库对比
        1. 尝试以当前波特率读取
        2. 无响应则切换波特率重试
        3. 对比读取值与数据库值
        """
        target_baud_val = BAUD_RATE_MAP.get(target_baud_rate, -1)

        add_log(f'57电机检测: 站号={station}, 目标波特率={target_baud_rate}', 'info')

        # 确保串口连接
        if not self.is_connected():
            for baud in KNOWN_BAUD_RATES:
                if self.connect(self.port or 'COM2', baud):
                    break
            if not self.is_connected():
                return {'passed': False, 'items': [{'name': '串口连接', 'passed': False}], 'current_baud_rate': None}

        items = []
        current_baud = self.baud_rate

        # 尝试读取波特率（自动切换波特率重试）
        baud_val = -1
        for baud in KNOWN_BAUD_RATES:
            add_log(f'尝试以波特率 {baud} 读取波特率...', 'info')
            if self.baud_rate != baud:
                self.connect(self.port or 'COM2', baud)
                time.sleep(0.1)

            baud_val = self.read_register(station, 0x0009)
            if baud_val >= 0:
                current_baud = baud
                add_log(f'波特率读取成功: {baud_val}', 'success')
                break

        # 波特率检测
        if baud_val >= 0:
            baud_passed = baud_val == target_baud_val
            items.append({
                'name': '波特率验证',
                'passed': baud_passed,
                'detail': f'读取波特率值={baud_val}, 期望={target_baud_val}'
            })
        else:
            items.append({
                'name': '波特率验证',
                'passed': False,
                'detail': '设备无响应'
            })

        return {
            'passed': all(item['passed'] for item in items),
            'items': items,
            'station': station,
            'current_baud_rate': current_baud
        }

    def write_config_35(self, current_station: int, target_station: int, target_baud_rate: int) -> dict:
        """
        35电机配置：写入站号和波特率
        1. 使用当前站号和波特率(115200/9600)尝试写入目标站号和目标波特率
        2. 验证返回的站号和波特率是否与写入值一致
        3. 若一致，执行断电保存
        4. 若失败，切换站号2-30重试
        """
        baud_val = BAUD_RATE_MAP.get(target_baud_rate)
        if baud_val is None:
            return {'success': False, 'message': f'不支持的波特率: {target_baud_rate}'}

        add_log(f'35电机配置: 当前站号={current_station}, 目标站号={target_station}, 目标波特率={target_baud_rate}', 'info')

        # 确保串口连接
        if not self.is_connected():
            for baud in KNOWN_BAUD_RATES:
                if self.connect(self.port or 'COM2', baud):
                    break
            if not self.is_connected():
                return {'success': False, 'message': '串口未连接'}

        def try_write_and_verify(station: int, baud: int) -> bool:
            """尝试写入站号和波特率，写入响应即包含回显验证"""
            add_log(f'尝试写入: 站号={station}, 波特率={baud}', 'info')
            if self.baud_rate != baud:
                self.connect(self.port or 'COM2', baud)
                time.sleep(0.1)

            # 写入站号（write_register 已自动验证回显）
            if not self.write_register(station, 0x0066, target_station):
                add_log(f'站号写入失败 (站号={station}, 波特率={baud})', 'error')
                return False

            time.sleep(0.1)

            # 写入波特率 — 站号已变更，使用目标站号
            if not self.write_register(target_station, 0x0009, baud_val):
                add_log(f'波特率写入失败 (站号={station}, 波特率={baud})', 'error')
                return False

            add_log(f'写入并验证成功: 站号={target_station}, 波特率={target_baud_rate}', 'success')
            return True

        def save_power_off(station: int, baud: int) -> bool:
            """断电保存"""
            if self.baud_rate != baud:
                self.connect(self.port or 'COM2', baud)
                time.sleep(0.1)

            saved = self.write_register(station, 0x00DC, 1)
            if not saved:
                time.sleep(0.5)
                saved = self.write_register(station, 0x00DC, 1)
            return saved

        # 第一轮：使用当前站号，依次尝试115200和9600
        current_baud = self.baud_rate
        for baud in KNOWN_BAUD_RATES:
            if try_write_and_verify(current_station, baud):
                # 验证成功，切换到目标波特率并保存
                time.sleep(0.2)
                self._serial.baudrate = target_baud_rate
                self.baud_rate = target_baud_rate
                current_baud = target_baud_rate
                time.sleep(0.1)

                if save_power_off(target_station, target_baud_rate):
                    return {'success': True, 'message': f'35电机配置成功: 站号={target_station}, 波特率={target_baud_rate}', 'current_baud_rate': current_baud}
                else:
                    return {'success': False, 'message': '配置成功但断电保存失败', 'current_baud_rate': current_baud}

        # 第二轮：切换站号2-30，每站号尝试9600和115200
        for station in range(2, 31):
            for baud in [9600, 115200]:
                if try_write_and_verify(station, baud):
                    # 验证成功，切换到目标波特率并保存
                    time.sleep(0.2)
                    self._serial.baudrate = target_baud_rate
                    self.baud_rate = target_baud_rate
                    current_baud = target_baud_rate
                    time.sleep(0.1)

                    if save_power_off(target_station, target_baud_rate):
                        return {'success': True, 'message': f'35电机配置成功: 站号={target_station}, 波特率={target_baud_rate}', 'current_baud_rate': current_baud}
                    else:
                        return {'success': False, 'message': '配置成功但断电保存失败', 'current_baud_rate': current_baud}

        return {'success': False, 'message': '35电机配置失败，设备无响应', 'current_baud_rate': current_baud}

    def inspect_35(self, station: int, target_station: int, target_baud_rate: int) -> dict:
        """
        35电机检测：验证站号和波特率
        1. 尝试以当前波特率读取
        2. 无响应则切换波特率重试
        3. 对比读取值与数据库值
        """
        target_baud_val = BAUD_RATE_MAP.get(target_baud_rate, -1)

        add_log(f'35电机检测: 目标站号={target_station}, 目标波特率={target_baud_rate}', 'info')

        # 确保串口连接
        if not self.is_connected():
            for baud in KNOWN_BAUD_RATES:
                if self.connect(self.port or 'COM2', baud):
                    break
            if not self.is_connected():
                return {'passed': False, 'items': [{'name': '串口连接', 'passed': False}], 'current_baud_rate': None}

        items = []
        current_baud = self.baud_rate

        # 尝试读取（自动切换波特率重试）
        read_station = -1
        read_baud = -1
        for baud in KNOWN_BAUD_RATES:
            add_log(f'尝试以波特率 {baud} 读取...', 'info')
            if self.baud_rate != baud:
                self.connect(self.port or 'COM2', baud)
                time.sleep(0.1)

            read_station = self.read_register(station, 0x0066)
            if read_station >= 0:
                current_baud = baud
                read_baud = self.read_register(station, 0x0009)
                if read_baud >= 0:
                    add_log(f'读取成功: 站号={read_station}, 波特率值={read_baud}', 'success')
                    break

        # 验证结果
        if read_station >= 0 and read_baud >= 0:
            station_passed = read_station == target_station
            baud_passed = read_baud == target_baud_val

            items.append({
                'name': '站号验证',
                'passed': station_passed,
                'detail': f'读取站号值={read_station}, 期望={target_station}'
            })
            items.append({
                'name': '波特率验证',
                'passed': baud_passed,
                'detail': f'读取波特率值={read_baud}, 期望={target_baud_val}'
            })
        else:
            items.append({
                'name': '站号验证',
                'passed': False,
                'detail': '设备无响应'
            })
            items.append({
                'name': '波特率验证',
                'passed': False,
                'detail': '设备无响应'
            })

        return {
            'passed': all(item['passed'] for item in items),
            'items': items,
            'station': target_station,
            'current_baud_rate': current_baud
        }

    # ═══════════════════════════════════════════
    # 老化测试专用方法
    # ═══════════════════════════════════════════

    def read_multi_registers(self, station: int, address: int, count: int = 1) -> bytes:
        """读取多个寄存器（功能码 0x03），返回原始字节"""
        cmd = struct.pack('>BBHH', station, 0x03, address, count)
        frame = build_frame(cmd)
        if not self.send_raw(frame):
            return b''
        # 响应: 站号(1) + 功能码(1) + 字节数(1) + 数据(n) + CRC(2)
        resp_len = 5 + count * 2
        resp = self.read_response(resp_len)
        if len(resp) >= 5 and resp[1] == 0x03:
            data_len = resp[2]
            return resp[3:3 + data_len]
        return b''

    def read_position(self, station: int) -> int:
        """读取电机实时位置（0x0004~0x0005, INT32, 单位 pulses）"""
        data = self.read_multi_registers(station, 0x0004, 2)
        if len(data) >= 4:
            val = struct.unpack('>i', data[:4])[0]
            add_log(f'读取位置 站号={station}: {val} pulses', 'info')
            return val
        return None

    def read_status(self, station: int) -> int:
        """读取状态寄存器（0x0006~0x0007, UINT32）"""
        data = self.read_multi_registers(station, 0x0006, 2)
        if len(data) >= 4:
            val = struct.unpack('>I', data[:4])[0]
            return val
        return None

    def is_in_position(self, station: int) -> bool:
        """检查电机是否到位（状态寄存器 bit12）"""
        status = self.read_status(station)
        if status is None:
            return False
        return bool((status >> 12) & 0x01)

    def is_motor_running(self, station: int) -> bool:
        """检查电机是否正在运行（状态寄存器 bit8-9 = 11）"""
        status = self.read_status(station)
        if status is None:
            return False
        bits89 = (status >> 8) & 0x03
        return bits89 == 0x03

    def read_speed(self, station: int) -> int:
        """读取实时速度（0x00D6~0x00D7, INT32, 单位 0.01rpm）"""
        data = self.read_multi_registers(station, 0x00D6, 2)
        if len(data) >= 4:
            val = struct.unpack('>i', data[:4])[0]
            return val
        return None

    def write_dword(self, station: int, address: int, value: int) -> bool:
        """写32位值到连续两个寄存器（功能码 0x10）"""
        packed = struct.pack('>i', value)
        # 高16位在前，低16位在后
        high = (value >> 16) & 0xFFFF
        low = value & 0xFFFF
        cmd = struct.pack('>BBHH', station, 0x10, address, 2)  # 2 registers
        cmd += struct.pack('B', 4)  # 4 bytes
        cmd += struct.pack('>HH', high, low)
        frame = build_frame(cmd)
        if not self.send_raw(frame):
            return False
        resp = self.read_response(8)
        if len(resp) >= 6 and resp[1] == 0x10:
            resp_addr = struct.unpack('>H', resp[2:4])[0]
            if resp_addr == address:
                return True
        return False

    def move_to_absolute(self, station: int, position: int) -> bool:
        """
        运行到绝对位置（0x00E8~0x00E9, INT32）
        电机静止或运行中都可执行，运行时收到新指令立即切换
        """
        add_log(f'移动到绝对位置 站号={station}, 位置={position} pulses', 'info')
        return self.write_dword(station, 0x00E8, position)

    def move_to_absolute_when_stopped(self, station: int, position: int) -> bool:
        """运行到绝对位置（0x00D0~0x00D1），仅电机静止时可执行"""
        add_log(f'移动到绝对位置(仅静止) 站号={station}, 位置={position} pulses', 'info')
        return self.write_dword(station, 0x00D0, position)

    def move_relative(self, station: int, pulses: int) -> bool:
        """
        相对运动（0x00DE~0x00DF, INT32）
        运行时接收到新指令立即执行，当前指令强行结束
        """
        add_log(f'相对运动 站号={station}, 脉冲={pulses}', 'info')
        return self.write_dword(station, 0x00DE, pulses)

    def set_speed(self, station: int, speed_rpm: int) -> bool:
        """
        设置运行速度（0x00D8~0x00D9, INT32, 单位 0.01rpm）
        如300rpm → 30000
        """
        val = speed_rpm * 100
        add_log(f'设置速度 站号={station}, 速度={speed_rpm} rpm', 'info')
        return self.write_dword(station, 0x00D8, val)

    def set_accel_decel(self, station: int, accel_ms: int, decel_ms: int) -> bool:
        """设置加减速时间（0x0098 加速, 0x0099 减速, 单位 ms）"""
        ok = True
        if not self.write_register(station, 0x0098, accel_ms):
            add_log(f'加速时间设置失败: {accel_ms}ms', 'warning')
            ok = False
        time.sleep(0.05)
        if not self.write_register(station, 0x0099, decel_ms):
            add_log(f'减速时间设置失败: {decel_ms}ms', 'warning')
            ok = False
        return ok

    def motor_enable(self, station: int, enable: bool = True) -> bool:
        """使能/脱机（0x00D4）：写0使能马达，写1释放马达"""
        val = 0 if enable else 1
        add_log(f'电机{"使能" if enable else "脱机"} 站号={station}', 'info')
        return self.write_register(station, 0x00D4, val)

    def emergency_stop(self, station: int) -> bool:
        """急停（写 256 到 0x00C8）"""
        add_log(f'急停 站号={station}', 'warning')
        return self.write_register(station, 0x00C8, 256)

    def stop_decelerate(self, station: int) -> bool:
        """减速停止（写 0 到 0x00C8）"""
        add_log(f'减速停止 站号={station}', 'info')
        return self.write_register(station, 0x00C8, 0)

    def home_return(self, station: int, direction: int = 0, speed_rpm: int = 200) -> bool:
        """
        执行回原点（0x00C9）
        direction: 0=正向, 1=反向
        speed_rpm: 回原点速度
        """
        # 编码: bit15=方向, bit14-6=速度(0-511)
        speed_val = min(speed_rpm, 511)
        cmd_val = (direction << 15) | (speed_val << 6) | 0x20  # 减速停止
        add_log(f'回原点 站号={station}, 方向={direction}, 速度={speed_rpm}rpm', 'info')
        return self.write_register(station, 0x00C9, cmd_val)

    def set_current_position(self, station: int, position: int) -> bool:
        """设定当前电机绝对位置（0x00D2~0x00D3），不改变物理位置"""
        add_log(f'设定当前位置 站号={station}, 位置={position}', 'info')
        return self.write_dword(station, 0x00D2, position)

    def clear_alarm(self, station: int) -> bool:
        """清除报警状态（0x00A4）"""
        return self.write_register(station, 0x00A4, 0)
