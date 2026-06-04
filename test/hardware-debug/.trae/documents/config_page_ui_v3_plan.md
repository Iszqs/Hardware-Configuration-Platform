# 硬件配置页面 UI 优化计划

## 任务清单

1. 右侧检测结果显示区域的底部和第二行卡片的底部水平对齐
2. 硬件配置页面的配置和检测按钮不要一直显示，鼠标悬停或者选择卡片时再显示按钮

## 修改文件
- `src/views/OneClickConfig.vue`

## 实施步骤

### 步骤 1: 右侧结果区域底部对齐
- 调整右侧面板样式，确保底部与左侧第二行卡片对齐
- 可能需要调整 `.right-section` 的高度或布局

### 步骤 2: 卡片按钮默认隐藏，悬停/选中时显示
- 给 `.device-card-footer` 添加默认样式 `opacity: 0`
- 给 `.device-card:hover .device-card-footer` 和 `.device-card.selected .device-card-footer` 添加 `opacity: 1`
- 添加过渡动画效果
