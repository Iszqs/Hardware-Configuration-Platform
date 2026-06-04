# 右侧检测结果自动刷新计划

## 任务描述
将右侧检测结果从累计显示改为自动刷新，每次只显示最新一条结果。

## 修改文件
- `src/views/OneClickConfig.vue`

## 实施步骤

### 步骤 1: 修改检测结果存储方式
- 将 `inspectResults` 从数组改为单个对象 `lastInspectResult`
- 每次检测完成后直接替换，不再 push 到数组

### 步骤 2: 更新模板显示
- 将 `v-for="(r, i) in inspectResults"` 改为直接使用 `lastInspectResult`
- 移除 `inspectPassCount` 计算属性
- 移除 `inspect-overview` 中的计数显示

### 步骤 3: 清理无用代码
- 移除 `clearInspectResults` 函数
- 简化相关计算属性
