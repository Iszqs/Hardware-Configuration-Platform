# 硬件配置页面 UI 优化计划

## 任务清单

1. 左侧保持卡片四列排序
2. 右侧配置结果显示用途（purpose）
3. 取消"清除结果"按钮
4. 每次配置或检测后自动刷新右侧区域显示

## 修改文件

- `src/views/OneClickConfig.vue` - 主要修改文件

## 实施步骤

### 步骤 1: 左侧卡片改为四列排序
- 修改 `.device-grid` 的 CSS
- 从 `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- 改为 `grid-template-columns: repeat(4, 1fr)` 实现固定四列

### 步骤 2: 右侧配置结果显示用途
- 在 `result-card` 组件中添加用途显示
- 位置：在结果标题后添加 `purpose` 显示
- 样式：与检测结果的用途样式保持一致

### 步骤 3: 取消清除按钮
- 移除 `inspect-results-section` 中的清除按钮
- 删除 `clearInspectResults` 函数调用

### 步骤 4: 自动刷新右侧区域
- 保持现有逻辑不变
- 配置/检测结果自动显示在右侧面板
- 无需手动清除，历史记录累积显示

## TDD 工作流程

1. 修改代码实现功能
2. 构建验证
3. 手动测试确认
