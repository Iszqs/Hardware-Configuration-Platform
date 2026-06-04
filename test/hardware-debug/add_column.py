import sqlite3

DB_PATH = r"d:\Users\OL\Desktop\硬件配置平台\test\hardware-debug\data\hardware.db"

print("连接数据库...")
conn = sqlite3.connect(DB_PATH, timeout=30)
cursor = conn.cursor()

print("检查字段...")
cursor.execute("PRAGMA table_info(device_configs)")
cols = [c[1] for c in cursor.fetchall()]
print(f"当前字段: {cols}")

if 'custom_name' not in cols:
    print("添加 custom_name 字段...")
    cursor.execute("ALTER TABLE device_configs ADD COLUMN custom_name TEXT DEFAULT ''")
    conn.commit()
    print("✅ 添加成功!")

cursor.execute("PRAGMA table_info(device_configs)")
cols = [c[1] for c in cursor.fetchall()]
print(f"更新后字段: {cols}")

conn.close()
print("\n完成!")