import sqlite3
import os

DB_PATH = "d:\\Users\\OL\\Desktop\\硬件配置平台\\test\\hardware-debug\\data\\hardware.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(device_configs)")
columns = [col[1] for col in cursor.fetchall()]

if 'custom_name' not in columns:
    print("Adding custom_name column...")
    cursor.execute("ALTER TABLE device_configs ADD COLUMN custom_name TEXT DEFAULT ''")
    conn.commit()
    print("Successfully added custom_name column")
else:
    print("custom_name column already exists")

conn.close()
print("Migration complete!")