import assert from 'assert/strict';
import { execSync } from 'child_process';

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('\n=== Test: ModbusService singleton verification ===');
  try {
    const pythonTest = `
import sys
sys.path.insert(0, 'backend')

from routers.serial import modbus_service as serial_service
from routers.modbus import modbus_service as modbus_service

# 测试两个模块是否使用同一个实例
same_instance = serial_service is modbus_service
print(f"SAME_INSTANCE={same_instance}")
    `;
    
    const result = execSync(`python -c "${pythonTest}"`).toString().trim();
    const sameInstance = result.includes('SAME_INSTANCE=True');
    
    assert.ok(
      sameInstance,
      'FAIL: serial.py 和 modbus.py 使用了不同的 ModbusService 实例！' +
      '这会导致串口连接状态不同步，配置/检测指令无法发送。'
    );
    
    console.log('✓ PASS: serial.py 和 modbus.py 使用同一个 ModbusService 实例');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test: Connection state propagation ===');
  try {
    const pythonTest = `
import sys
sys.path.insert(0, 'backend')

from routers.serial import modbus_service as serial_service
from routers.modbus import modbus_service as modbus_service

# 模拟连接状态
serial_service._serial = object()  # 模拟连接

# 检查 modbus_service 是否也显示已连接
modbus_connected = serial_service.is_connected() and modbus_service.is_connected()
print(f"CONNECTED_BOTH={modbus_connected}")
    `;
    
    const result = execSync(`python -c "${pythonTest}"`).toString().trim();
    const connectedBoth = result.includes('CONNECTED_BOTH=True');
    
    assert.ok(
      connectedBoth,
      'FAIL: 连接状态未在两个实例之间传播！'
    );
    
    console.log('✓ PASS: 连接状态在共享实例间正确传播');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test Results ===');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests();