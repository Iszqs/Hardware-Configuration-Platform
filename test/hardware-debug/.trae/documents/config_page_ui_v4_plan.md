# 硬件配置页面 UI 优化计划 v4

## 任务清单

1. 硬件配置页面调整为点击卡片和点击配置或者检测按钮都会选中卡片
2. 右侧结果显示区域的底部和第二行卡片的底部水平对齐，高度为2卡片的高度

## 修改文件

- `src/views/OneClickConfig.vue`

## 实施步骤

### 步骤 1: 点击按钮时也选中卡片
- 在 `configSingle` 和 `inspectSingle` 函数开始时添加 `selectedIndex.value = idx`
- 确保点击按钮时也能选中对应的卡片

### 步骤 2: 调整右侧面板高度和对齐
- 移除右侧面板的 `sticky` 定位
- 设置右侧面板高度为 `calc(var(--card-min-height) * 2 + var(--spacing-md))` (2个卡片高度 + 间距)
- 调整布局让右侧面板与左侧网格对齐
