# 硬件库按钮显示逻辑优化计划

## 需求
1. 选中硬件时，所属分类的卡片也高亮（当前逻辑已支持）
2. 新增、编辑、删除按钮只在不选中任何内容时隐藏，选中卡片或硬件时显示
3. 悬停不再显示按钮，只有选中才显示

## 修改文件
- `src/views/HardwareLibrary.vue`

## 修改内容
将 `.category-actions-bar` 的显示逻辑改为：默认 `opacity: 0`，仅在 `.category-card.selected` 时 `opacity: 1`
