# 模拟数据迁移至数据库方案（修正版）

## 概述

将前端 localStorage 中**立三电机**的模拟数据迁移至 SQLite 数据库，前端改为通过 API 读取数据库数据，Modbus 通信按照立三电机协议实现真实硬件通信。

## 关键修正

1. **仅迁移立三电机数据** — 47电机改为57电机
2. **Modbus 协议**：严格按照立三电机文档实现读取和写入指令
3. **读取指令格式（0x03）**：
   ```
   读取站号(0x0066): [ID] 03 00 66 00 [新站号Hex] [CRC]
   读取波特率(0x0009): [ID] 03 00 09 00 [波特率字典Hex] [CRC]
   ```

## 当前需要修改的文件

| 文件 | 修改内容 |
|------|----------|
| `backend/models.py` | DeviceConfig 添加 purpose 字段 |
| `backend/database.py` | 修改默认分类和初始化数据，仅立三电机 |
| `backend/services/modbus_service.py` | 按立三电机文档实现 Modbus RTU 通信 |
| `backend/routers/modbus.py` | 对接真实 Modbus 服务 |
| `backend/routers/migrate.py` | **新建**，数据迁移 API |
| `backend/main.py` | 注册迁移路由 |
| `src/api/index.js` | **新建**，前端 HTTP 客户端 |
| `src/stores/projects.js` | 重写，localStorage → API |
| `src/stores/serial.js` | 重写，模拟 → API |
| `src/views/OneClickConfig.vue` | 配置/检测改为 API 调用 |
| `src/views/QualityInspect.vue` | 检测改为 API 调用 |
| `src/views/HardwareLibrary.vue` | CRUD 改为 API |
| `src/views/SerialConfig.vue` | 串口列表改为 API |
| `src/components/SerialModal.vue` | 串口操作改为 API |

## 不变的模块

`user.js`, `router`, `App.vue`, `AppSidebar.vue`, `style.css`, `package.json`
