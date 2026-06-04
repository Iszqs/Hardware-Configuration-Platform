# 修复按钮不显示问题计划

## 问题原因
点击 `device-type-item`（行36）的 `@click="selectDevice(subType, category.id)"` 没有使用 `.stop` 阻止事件冒泡。
事件流程：点击硬件 → selectDevice 设置 selectedCategory → 冒泡到卡片 → selectCategory 又把 selectedCategory 设为 null → 卡片失去选中状态 → 按钮隐藏

## 修改文件
- `src/views/HardwareLibrary.vue`

## 修改内容
在第36行 `@click` 后添加 `.stop` 修饰符，阻止事件冒泡到卡片
