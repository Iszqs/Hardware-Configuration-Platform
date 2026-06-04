# 硬件库修复计划

## 问题
1. 选中卡片后边框为2px，用户希望保持1px + 蓝色发光阴影
2. 选中硬件时，"新增"按钮无色禁用，用户希望它和编辑/删除一起显示为可用的主色

## 修改文件
- `src/views/HardwareLibrary.vue`

## 修改内容

### 1. 选中边框恢复1px
删除 `.category-card.selected` 中的 `border-width: 2px`，保持默认1px边框，保留蓝色发光阴影

### 2. 简化"新增"按钮禁用逻辑
当前 "新增" 按钮同时检查 `selectedCategoryId` 和 `selectedCategory?.id`，但 `selectCategory` 函数会设置 `selectedCategoryId = null`，导致条件判断可能出错。
改为只检查 `selectedCategory`（无论点击卡片还是点击硬件都会正确设置），确保选中硬件时"新增"按钮可用且为蓝色
