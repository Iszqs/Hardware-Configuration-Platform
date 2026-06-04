# 硬件库按钮颜色统一计划

## 需求
选中卡片或硬件时，三个按钮各自显示不同颜色且均可使用：
- 新增：蓝色 `btn-primary`
- 编辑：绿色 `btn-success`
- 删除：红色 `btn-danger`

## 修改内容
将编辑和删除按钮的 `:class` 颜色条件改为与禁用条件一致，都基于卡片是否选中。

## 修改文件
- `src/views/HardwareLibrary.vue`
