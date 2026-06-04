# 硬件库三个按钮都可用计划

## 需求
- 选中卡片或选中硬件时，卡片边框1px蓝色发光阴影 ✅ 已实现
- 三个按钮（新增/编辑/删除）都**显示**且都**可用**（不被禁用）

## 当前问题
- 编辑和删除按钮的 `disabled` 条件为 `!selectedDevice || selectedCategoryId !== category.id`
- 只选中卡片（未选硬件）时 `selectedDevice` 为 null，按钮虽显示但被禁用

## 修改文件
- `src/views/HardwareLibrary.vue`

## 修改内容
将编辑和删除按钮的 `disabled` 条件改为与新增一样，只检查 `selectedCategory?.id !== category.id`
按钮颜色保持：编辑=绿色(选中硬件时)，删除=红色(选中硬件时)，否则灰色边框样式
