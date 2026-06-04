# 串口通信日志保存功能

## 需求

1. 通信日志显示"完成日志"（配置完成等信息）
2. 日志自动保存到本地文件
3. 按每天日期保存（文件名格式：`serial_YYYY-MM-DD.log`）

---

## 当前状态

- **前端** `serial.js` store：日志仅存储在内存中 (`logs.value` 数组)
- **前端** `SerialConfig.vue`：日志显示在UI中，支持清空
- **后端** `serial.py`：无日志保存相关API
- **数据库** `SerialLog` model：存在但未使用

---

## 测试文件

### 文件：`tests/test_serial_logging.py`

```python
import sys
sys.path.insert(0, 'backend')

import os
import unittest
import tempfile
import shutil
from datetime import date
from unittest.mock import patch, MagicMock

# Test the log saving functionality
class TestSerialLogSaving(unittest.TestCase):
    """串口日志保存功能测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_log_file_named_by_date(self):
        """日志文件名包含日期"""
        from services.log_service import save_serial_log
        today = date.today()
        expected_filename = f"serial_{today.isoformat()}.log"
        log_path = save_serial_log(self.test_dir, "测试消息", "info")
        self.assertTrue(os.path.exists(log_path))
        self.assertEqual(os.path.basename(log_path), expected_filename)

    def test_log_contains_timestamp_and_message(self):
        """日志内容包含时间戳和消息"""
        from services.log_service import save_serial_log
        message = "串口连接成功"
        log_path = save_serial_log(self.test_dir, message, "success")
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(message, content)

    def test_multiple_logs_appended_to_same_file(self):
        """多次日志追加到同一文件"""
        from services.log_service import save_serial_log
        save_serial_log(self.test_dir, "消息1", "info")
        save_serial_log(self.test_dir, "消息2", "info")
        today = date.today()
        log_path = os.path.join(self.test_dir, f"serial_{today.isoformat()}.log")
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("消息1", lines[0])
        self.assertIn("消息2", lines[1])

    def test_log_format_includes_type(self):
        """日志格式包含类型（info/success/error）"""
        from services.log_service import save_serial_log
        log_path = save_serial_log(self.test_dir, "错误消息", "error")
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("[error]", content)

    def test_log_directory_created_if_not_exists(self):
        """日志目录不存在时自动创建"""
        from services.log_service import save_serial_log
        new_dir = os.path.join(self.test_dir, "subdir", "logs")
        log_path = save_serial_log(new_dir, "测试", "info")
        self.assertTrue(os.path.exists(log_path))
```

---

## 实施步骤

### Step 1: 创建日志服务

**文件**: `backend/services/log_service.py`

```python
import os
from datetime import datetime, date

def get_log_dir():
    """获取日志目录，默认为 backend/logs"""
    return os.path.join(os.path.dirname(__file__), '..', 'logs')

def get_log_filename():
    """获取今日日志文件名"""
    return f"serial_{date.today().isoformat()}.log"

def get_log_filepath():
    """获取今日日志完整路径"""
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, get_log_filename())

def save_serial_log(message: str, log_type: str = 'info') -> str:
    """
    保存串口日志到文件。
    返回: 日志文件路径
    """
    log_path = get_log_filepath()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{log_type.upper()}] {message}\n")
    return log_path
```

### Step 2: 添加后端API

**文件**: `backend/routers/serial.py`

```python
from .log_service import save_serial_log

@router.post('/logs')
async def save_log(data: dict):
    message = data.get('message', '')
    log_type = data.get('type', 'info')
    if not message:
        return {'success': False, 'message': '消息不能为空'}
    log_path = save_serial_log(message, log_type)
    return {'success': True, 'path': log_path}
```

### Step 3: 修改前端API

**文件**: `src/api/index.js`

```javascript
saveSerialLog(data) { return request('/api/serial/logs', { method: 'POST', body: data }) },
```

### Step 4: 修改serial store

**文件**: `src/stores/serial.js`

```javascript
function addLog(message, type = 'info') {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({ timestamp, message, type })

  // 发送到后端保存
  api.saveSerialLog({ message, type }).catch(() => {})

  if (logs.value.length > 200) {
    logs.value = logs.value.slice(-200)
  }
}
```

---

## 修改汇总

| 文件 | 改动 |
|------|------|
| `backend/services/log_service.py` | 新增日志保存服务 |
| `backend/routers/serial.py` | 新增 `POST /api/serial/logs` 路由 |
| `src/api/index.js` | 新增 `saveSerialLog()` API |
| `src/stores/serial.js` | 修改 `addLog()` 同时发送日志到后端 |

---

## 日志格式

```
[2026-06-03 14:30:15] [INFO] 正在连接 COM1...
[2026-06-03 14:30:16] [SUCCESS] COM1 连接成功 (115200 bps)
[2026-06-03 14:30:20] [INFO] 发送: 01 06 00 09 00 0C ...
[2026-06-03 14:30:20] [SUCCESS] 35电机配置成功: 站号 1, 波特率 115200
```

---

## 验证步骤

1. 运行 `python -m pytest tests/test_serial_logging.py -v` 确认RED（失败）
2. 创建 `log_service.py` 实现日志保存
3. 运行测试确认GREEN（通过）
4. 重启后端服务
5. 打开串口配置页面，连接串口
6. 观察 `backend/logs/serial_YYYY-MM-DD.log` 文件是否生成并包含日志
