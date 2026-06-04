import os
from datetime import datetime, date

# 内存日志缓冲区（存储最近的日志）
_log_buffer = []
MAX_BUFFER_SIZE = 500

def get_log_dir(base_dir=None):
    """获取日志目录，默认为 backend/logs"""
    if base_dir:
        return base_dir
    return os.path.join(os.path.dirname(__file__), '..', 'logs')

def get_log_filename():
    """获取今日日志文件名"""
    return f"serial_{date.today().isoformat()}.log"

def get_log_filepath(base_dir=None):
    """获取今日日志完整路径"""
    log_dir = get_log_dir(base_dir)
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, get_log_filename())

def add_log(message: str, log_type: str = 'info'):
    """
    添加日志到内存缓冲区和文件
    """
    global _log_buffer
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = {'timestamp': timestamp, 'message': message, 'type': log_type}
    _log_buffer.append(log_entry)
    if len(_log_buffer) > MAX_BUFFER_SIZE:
        _log_buffer = _log_buffer[-MAX_BUFFER_SIZE:]
    # 同时保存到文件
    save_serial_log(message, None, log_type)

def get_logs():
    """获取内存中的日志列表"""
    return _log_buffer.copy()

def clear_logs():
    """清空内存日志"""
    global _log_buffer
    _log_buffer = []

def save_serial_log(message: str, base_dir=None, log_type: str = 'info') -> str:
    """
    保存串口日志到文件。
    返回: 日志文件路径
    """
    log_path = get_log_filepath(base_dir)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{log_type.upper()}] {message}\n")
    return log_path
