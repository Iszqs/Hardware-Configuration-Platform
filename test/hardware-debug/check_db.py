import sqlite3

DB_PATH = "d:\\Users\\OL\\Desktop\\硬件配置平台\\test\\hardware-debug\\data\\hardware.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Categories ===")
cursor.execute("SELECT * FROM categories")
print(cursor.fetchall())

print("\n=== Device Types ===")
cursor.execute("SELECT * FROM device_types")
print(cursor.fetchall())

print("\n=== Projects ===")
cursor.execute("SELECT * FROM projects")
print(cursor.fetchall())

print("\n=== Device Configs ===")
cursor.execute("PRAGMA table_info(device_configs)")
print("Columns:", [col[1] for col in cursor.fetchall()])

cursor.execute("SELECT * FROM device_configs")
print(cursor.fetchall())

conn.close()