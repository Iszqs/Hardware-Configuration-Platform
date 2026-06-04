# 右侧结果面板高度调整计划

## 需求
右侧结果面板的高度为设备卡片高度的两倍

## 修改文件
- `src/views/OneClickConfig.vue`

## 实施步骤
1. 设备卡片最小高度是 `--card-min-height` (220px)
2. 右侧面板高度设为两倍设备卡片高度 + 间距
3. 计算方式：`calc(var(--card-min-height) * 2 + var(--spacing-md))`
4. 确保内容溢出时可以滚动
