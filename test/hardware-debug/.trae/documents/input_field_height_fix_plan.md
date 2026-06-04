# 编辑项目页面波特率选择框文字裁剪问题修复计划（TDD）

## 问题描述
编辑项目对话框中的波特率选择框（`<select>`），"9600" 和 "115200" 等选项文字在垂直方向上被裁剪约三分之一，未居中显示。

## 根因分析

- `.input-field` 全局样式：`height: 40px`，`padding: 12px 14px`
- 内容区域高度 = `40 - 12 - 12 = 16px`
- 字体大小 = `var(--text-base)` = 1rem = **17px**
- **文字高度 (17px) 超过内容区域 (16px)**，导致文字顶部和底部被裁剪

## 修复方案

将 `.input-field` 的 `height` 从 40px 增大到 **44px**，确保内容区域足以容纳 17px 文字：

```
内容区域 = 44 - 12 - 12 = 20px > 17px ✅
```

## TDD 实施步骤

### 第一阶段：RED（写失败测试）

#### Step 1: 创建测试文件 `tests/input-field-sizing.test.js`
测试内容：
1. 验证 `.input-field` 的内容区域高度（height - padding-top - padding-bottom）>= font-size
2. 定义常量 INPUT_FIELD_MIN_HEIGHT = 44px 并断言当前值 40px < 44px（将失败）
3. 验证 `.input-field` 的 padding 和 height 比例合理（padding-top + padding-bottom 不超过 height 的 60%）

**预期：测试 2 失败**（因为当前 height 是 40px，小于 44px）

### 第二阶段：GREEN（修复代码）

#### Step 2: 修改 `src/style.css`
将 `.input-field` 的 `height: 40px` 改为 `height: 44px`

### 第三阶段：REFACTOR（验证）

#### Step 3: 运行全部测试，确认全部 PASS
- `node tests/input-field-sizing.test.js`
- `node tests/typography-tokens.test.js`
- `node tests/card-tokens.test.js`
- `node tests/test_add_device_custom_name.js`
- `node tests/test_save_device_name.js`

#### Step 4: 构建验证
- `npm run build`

---

## 影响范围分析

- `.input-field` 是全局类，修改 `height` 会影响所有 input 和 select 元素
- 从 40px → 44px 增加 4px，影响很小，但需要确认：
  - 按钮高度：`.btn` 保持 40px 不变（独立设置 `height: 40px`），不受影响
  - 布局：编辑对话框中的三列网格（设备编辑字段）空间充足，4px 差异无影响
  - 串口配置弹框：同样使用 `.input-field`，44px 高度更舒适

## 验证清单

- [ ] RED 测试正确失败
- [ ] GREEN 修复后测试通过
- [ ] 全部 5 组测试通过
- [ ] `npm run build` 成功
- [ ] 波特率选择框文字不再被裁剪