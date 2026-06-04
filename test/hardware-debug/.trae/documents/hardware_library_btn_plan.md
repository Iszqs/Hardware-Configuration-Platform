# 硬件库卡片操作按钮优化计划

## 需求
1. 选中硬件类型时，所属分类的卡片也高亮显示（`selected` 状态）
2. 编辑和删除按钮一直保持显示（移除 hover/selected 才显示的隐藏逻辑）
3. 新增按钮选中卡片才可用（当前逻辑已满足，无需修改）

## 修改文件
- `src/views/HardwareLibrary.vue`

## 修改内容

### 1. 编辑/删除按钮一直可见
删除 `.category-actions-bar` 的 `opacity: 0` 和 `:hover/:selected` 条件显示逻辑

### 2. 选中硬件时同时选中卡片
当前 `selectDevice` 函数已经设置了 `selectedCategory`，但确保 `selectDevice` 中正确设置 `selectedCategoryId` 和 `selectedCategory`
