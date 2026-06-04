# 35电机配置时写入站号 + 波特率

## 需求

- **35电机**（`device_type_id === 1`）：点击"配置"按钮时，将数据库中的站号写入设备，同时写入波特率
- **57电机等其他设备**：保持现有行为不变（只配置波特率，用站号1通信）

---

## 当前状态

[OneClickConfig.vue:L151-L165](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L151-L165) 中：

```javascript
// 35电机特殊处理 — 但代码有误，站号没真正写入
if (config.device_type_id === 1) {
  const stationResult = await api.writeModbusStationNumber({
    old_station: 1,
    new_station: 1        // ← 1→1，站号没有任何变化！
  })
}

// 所有设备共用 — 站号固定为1，不用数据库的值
const result = await api.writeModbusConfig({
  station_number: 1,            // ← 硬编码
  baud_rate: config.baud_rate,
})
```

**问题**：35电机的站号没有被真正写入设备，配置使用的也是固定站号1。

---

## 修改方案

仅修改 1 个文件 `src/views/OneClickConfig.vue`，2 处改动。

### 改动1：写站号使用数据库中的值（L153-L154）

```javascript
// 当前：
old_station: 1,
new_station: 1

// 改为：
old_station: 1,
new_station: config.station_number
```

**含义**：将设备当前的站号（默认1）修改为数据库中配置的目标站号。

### 改动2：写配置时站号根据设备类型区分（L162）

```javascript
// 当前：
station_number: 1,

// 改为：
station_number: config.device_type_id === 1 ? config.station_number : 1
```

**含义**：
- 35电机：使用刚写入的新站号（`config.station_number`）进行通信
- 其他设备：保持站号1

---

## 修改明细

| 文件 | 行 | 当前值 | 改为 |
|------|----|--------|------|
| `OneClickConfig.vue` | L153 | `old_station: 1` | 不变（设备默认站号为1） |
| `OneClickConfig.vue` | L154 | `new_station: 1` | `new_station: config.station_number` |
| `OneClickConfig.vue` | L162 | `station_number: 1` | `station_number: config.device_type_id === 1 ? config.station_number : 1` |

共修改 **1 个文件**，**2 处改动**。

---

## 验证方式

1. 在项目库中设置某35电机的站号为 **2**，波特率 **115200**
2. 进入硬件配置页面，点击该卡片的"配置"按钮
3. 成功后，设备站号变为 2，波特率变为 115200
4. 57电机点击配置按钮，仍以站号1通信，只配置波特率
