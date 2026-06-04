# 修复右侧面板底部对齐计划

## 问题分析
从截图看，右侧面板高度没有正确对齐到第二行卡片的底部。当前使用的是固定高度计算，可能不够准确。

## 解决方案
改为让右侧面板与左侧卡片网格的高度一致，使用 `align-items: stretch` 让两侧高度相同。

## 修改文件
- `src/views/OneClickConfig.vue`

## 实施步骤
1. 修改 `.main-layout` 样式，将 `align-items: start` 改为 `align-items: stretch`
2. 简化 `.right-section` 样式，移除固定高度，让它自动撑满整个高度
3. 确保右侧面板内容有合理的布局
