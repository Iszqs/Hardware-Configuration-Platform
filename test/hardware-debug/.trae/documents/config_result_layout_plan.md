# 配置结果卡片布局统一计划

## 需求
配置结果卡片(`lastResult`)的显示布局与检测结果卡片(`lastInspectResult`)完全一致。

## 当前差异

当前两个卡片的布局结构不同：

**配置结果卡片** (当前):
```
📝 配置结果
[LED] 分类/设备名 [用途]
站号: X    波特率: Y (result-details，行内样式)
配置成功 (result-message，单独一行)
```

**检测结果卡片** (当前):
```
🔍 检测结果
[LED] 分类/设备名 [用途]
[检测tag1] [检测tag2] (check-items)
─── border-top ───
站号: X    波特率: Y (result-params)
```

## 修改文件
- `src/views/OneClickConfig.vue`

## 修改内容
将配置结果卡片改为与检测结果卡片一致的布局：

### 模板改动
1. 将 `result-details` 改为 `result-params`（带 border-top 分割线）
2. 将 `result-message` 改为与 `check-items` 类似的结构，用 tag 显示配置状态（成功/失败）

### 代码示例
```html
<div v-if="lastResult" class="result-card" :class="'result-' + lastResult.status">
  <div class="result-type-title">📝 配置结果</div>
  <div class="result-header">
    <span class="led" ...></span>
    <span class="result-title">...</span>
    <span v-if="lastResult.purpose" class="result-purpose">{{ lastResult.purpose }}</span>
  </div>
  <div class="check-items">
    <span class="check-tag" :class="lastResult.status === 'success' ? 'pass' : 'fail'">
      {{ lastResult.message }}
    </span>
  </div>
  <div class="result-params">
    <span class="result-param">站号: {{ lastResult.station_number }}</span>
    <span class="result-param">波特率: {{ lastResult.baud_rate }}</span>
  </div>
</div>
```
