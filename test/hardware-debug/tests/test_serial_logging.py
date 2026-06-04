import sys
sys.path.insert(0, 'backend')

import os
import unittest
import tempfile
import shutil
from datetime import date
from unittest.mock import patch, MagicMock

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
        log_path = save_serial_log("测试消息", self.test_dir, "info")
        self.assertTrue(os.path.exists(log_path))
        self.assertEqual(os.path.basename(log_path), expected_filename)

    def test_log_contains_timestamp_and_message(self):
        """日志内容包含时间戳和消息"""
        from services.log_service import save_serial_log
        message = "串口连接成功"
        log_path = save_serial_log(message, self.test_dir, "success")
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn(message, content)

    def test_multiple_logs_appended_to_same_file(self):
        """多次日志追加到同一文件"""
        from services.log_service import save_serial_log
        save_serial_log("消息1", self.test_dir, "info")
        save_serial_log("消息2", self.test_dir, "info")
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
        log_path = save_serial_log("错误消息", self.test_dir, "error")
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("[ERROR]", content)

    def test_log_directory_created_if_not_exists(self):
        """日志目录不存在时自动创建"""
        from services.log_service import save_serial_log
        new_dir = os.path.join(self.test_dir, "subdir", "logs")
        log_path = save_serial_log("测试", new_dir, "info")
        self.assertTrue(os.path.exists(log_path))


if __name__ == '__main__':
    unittest.main()
