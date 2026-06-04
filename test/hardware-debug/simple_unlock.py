import os
import sys
import time
import sqlite3

DB_FOLDER = "d:\\Users\\OL\\Desktop\\硬件配置平台\\test\\hardware-debug\\data"
DB_PATH = os.path.join(DB_FOLDER, "hardware.db")

print("清理数据库锁定文件...")

lock_files = ['hardware.db-journal', 'hardware.db-wal', 'hardware.db-shm']
for f in lock_files:
    fp = os.path.join(DB_FOLDER, f)
    if os.path.exists(fp):
        try:
            os.remove(fp)
            print(f"已删除: {f}")
        except Exception as e:
            print(f"无法删除 {f}: {e}")

print("\n尝试添加 custom_name 字段...")
try:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(device_configs)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"当前字段: {columns}")
    
    if 'custom_name' not in columns:
        print("添加 custom_name 字段...")
        cursor.execute("ALTER TABLE device_configs ADD COLUMN custom_name TEXT DEFAULT ''")
        conn.commit()
        print("✅ 成功添加 custom_name 字段!")
    else:
        print("custom_name 字段已存在")
    
    conn.close()
    print("\n✅ 数据库解锁成功！")
    
except Exception as e:
    print(f"数据库操作出错: {e}")
    import traceback
    traceback.print_exc()

print("\n完成！")