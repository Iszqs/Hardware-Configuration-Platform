import sqlite3
import os

OLD_DB_PATH = "d:\\Users\\OL\\Desktop\\硬件配置平台\\test\\hardware-debug\\data\\hardware.db"
NEW_DB_PATH = "d:\\Users\\OL\\Desktop\\硬件配置平台\\test\\hardware-debug\\data\\hardware_new.db"

conn_old = sqlite3.connect(OLD_DB_PATH)
cursor_old = conn_old.cursor()

cursor_old.execute("SELECT * FROM categories")
categories = cursor_old.fetchall()

cursor_old.execute("SELECT * FROM device_types")
device_types = cursor_old.fetchall()

cursor_old.execute("SELECT * FROM projects")
projects = cursor_old.fetchall()

cursor_old.execute("SELECT * FROM device_configs")
device_configs = cursor_old.fetchall()

conn_old.close()

conn_new = sqlite3.connect(NEW_DB_PATH)
cursor_new = conn_new.cursor()

cursor_new.execute('''
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL
)
''')

cursor_new.execute('''
CREATE TABLE device_types (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
''')

cursor_new.execute('''
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP
)
''')

cursor_new.execute('''
CREATE TABLE device_configs (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    category_id INTEGER,
    device_type_id INTEGER,
    station_number INTEGER,
    baud_rate INTEGER,
    data_bits INTEGER,
    stop_bits INTEGER,
    parity TEXT,
    custom_name TEXT DEFAULT '',
    purpose TEXT DEFAULT '',
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (device_type_id) REFERENCES device_types(id)
)
''')

cursor_new.executemany('INSERT INTO categories VALUES (?, ?)', categories)
cursor_new.executemany('INSERT INTO device_types VALUES (?, ?, ?)', device_types)
cursor_new.executemany('INSERT INTO projects VALUES (?, ?, ?, ?)', projects)

new_device_configs = []
for cfg in device_configs:
    new_cfg = list(cfg)
    if len(new_cfg) == 10:
        new_cfg.insert(9, '')
    new_device_configs.append(tuple(new_cfg))

cursor_new.executemany('INSERT INTO device_configs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', new_device_configs)

conn_new.commit()
conn_new.close()

print("Successfully migrated data to new database!")
print(f"Categories: {len(categories)}")
print(f"Device Types: {len(device_types)}")
print(f"Projects: {len(projects)}")
print(f"Device Configs: {len(device_configs)}")

os.remove(OLD_DB_PATH)
os.rename(NEW_DB_PATH, OLD_DB_PATH)
print("Replaced old database with new one!")