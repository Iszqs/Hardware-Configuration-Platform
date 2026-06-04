# 调整老化测试位置和页面计划

## 仓库研究结论
- 硬件库在 `adminNavItems` 中，仅管理员可见
- 老化测试当前在 `navItems` 中，所有用户可见
- 需要把老化测试移到 `adminNavItems` 中，放在硬件库下方
- 老化测试页面需要改成空白页面

## 需要修改的文件

1. `src/components/AppSidebar.vue` - 调整导航项位置
2. `src/views/AgingTest.vue` - 改为空白页面

## 实施步骤

### 步骤 1: 调整侧边栏导航项
- 把老化测试从 `navItems` 移到 `adminNavItems`
- 位置放在硬件库下方

### 步骤 2: 修改老化测试页面
- 把 `AgingTest.vue` 改为空白页面，只保留基本结构
