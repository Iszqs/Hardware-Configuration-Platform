# 配置按钮文本固定与按钮状态互不影响

## 需求

1. 配置按钮始终显示"配置"，不切换为"重新配置"
2. 点击某张卡片的配置或检测按钮时，其他卡片的按钮颜色不发生变化

---

## 问题分析

### 问题1：按钮文本 "配置" / "重新配置" 切换

**位置**：[OneClickConfig.vue:L47](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L47)

```vue
{{ configuredIndexes.includes(idx) ? '重新配置' : '配置' }}
```

配置成功后，`configuredIndexes` 会推入当前卡片索引，导致按钮文本从"配置"变为"重新配置"。

### 问题2：其他卡片按钮同步变色

**位置**：[OneClickConfig.vue:L45](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L45) 和 [L52](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L52)

```vue
<button class="btn btn-config" :disabled="configInProgress">  ← 全局 configInProgress
<button class="btn btn-inspect" :disabled="inspectInProgress"> ← 全局 inspectInProgress
```

- `configInProgress` 和 `inspectInProgress` 是**单一的全局 ref**（[L134](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L134)、[L139](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L139)）
- 任意卡片点击按钮 → 全局变量变为 `true` → **所有卡片**的按钮同时应用 `:disabled` CSS → 按钮颜色全部变灰

---

## 修改方案

### 修改1：按钮文本始终显示"配置"

**文件**：`src/views/OneClickConfig.vue`
**位置**：第47行

将：
```vue
{{ configuredIndexes.includes(idx) ? '重新配置' : '配置' }}
```
改为：
```vue
配置
```

**效果**：按钮文本永远显示"配置"。

### 修改2：移除全局 `:disabled`，保留串口锁

**文件**：`src/views/OneClickConfig.vue`
**位置**：第45行和第52行

配置按钮：
```vue
<!-- 当前 -->
<button :disabled="configInProgress" @click.stop="configSingle(idx)">
<!-- 改为 -->
<button @click.stop="configSingle(idx)">
```

检测按钮：
```vue
<!-- 当前 -->
<button :disabled="inspectInProgress" @click.stop="inspectSingle(idx)">
<!-- 改为 -->
<button @click.stop="inspectSingle(idx)">
```

**同时保留函数头部的全局锁**（[L148](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L148) 和 [L203](file:///d:/Users/OL/Desktop/硬件配置平台/test/hardware-debug/src/views/OneClickConfig.vue#L203)）：
```javascript
async function configSingle(idx) {
  if (!project.value || configInProgress.value) return  // ← 保留
  // ...
}

async function inspectSingle(idx) {
  if (!project.value || inspectInProgress.value) return  // ← 保留
  // ...
}
```

### 修改3：移除已配置徽章的显示

由于按钮不再显示"重新配置"，"已配置"徽章显得不协调且用户未要求保留。

**文件**：`src/views/OneClickConfig.vue`
**位置**：第25行

删除：
```vue
<span v-if="configuredIndexes.includes(idx)" class="configured-badge">已配置</span>
```

---

## 修改汇总

| 文件 | 改动 | 行 |
|------|------|----|
| `src/views/OneClickConfig.vue` | 按钮文本直写"配置" | L47 |
| `src/views/OneClickConfig.vue` | 移除配置按钮 `:disabled` | L45 |
| `src/views/OneClickConfig.vue` | 移除检测按钮 `:disabled` | L52 |
| `src/views/OneClickConfig.vue` | 移除已配置徽章 | L25 |

共修改 **1 个文件**，**4 处改动**。

---

## 验证方式

1. 打开硬件配置页面，所有卡片的按钮均显示"配置"
2. 点击任意卡片的"配置"按钮 → 其他卡片按钮颜色不变
3. 配置成功或失败后 → 按钮文本仍为"配置"
4. 点击检测按钮 → 其他卡片按钮颜色不变
