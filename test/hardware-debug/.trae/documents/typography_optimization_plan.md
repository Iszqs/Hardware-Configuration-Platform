# 全站字体格式与大小统一优化计划（TDD）

## 目标
统一全站字体大小、字重体系，建立清晰的排版设计规范，消除散乱的硬编码 font-size/font-weight 值。

---

## 现状分析

当前全站共有 **78 处 font-size** 声明，使用约 **15 种不同的 rem 值**，缺乏统一规范。

| 当前值(rem) | 出现次数 | 使用场景 |
|------------|---------|---------|
| 0.7 | 2 | 单选框文字 |
| 0.75 | 8 | labels, btn-sm, badge, section-title, device-field-label |
| 0.8 | 1 | SerialConfig 日志框 |
| 0.8125 | 5 | btn, back-link, category-tab, device-add-btn |
| 0.933/0.9375 | 10 | input-field, device-badge, param-label, page-header p |
| 0.95 | 2 | SerialModal labels, log-box |
| 1.0 | 12 | body text, card-desc, inputs, result text |
| 1.1 | 1 | empty-state h3 |
| 1.125 | 8 | dialog h2, device-name, param-value, result-title |
| 1.2 | 1 | SerialModal h2 |
| 1.25 | 6 | card-title, brand-text, result-purpose |
| 1.5 | 3 | device-purpose |
| 1.6 | 1 | page-header h1 |

---

## 设计方案

### 字体大小体系（Typography Scale）

| Token | 值 (rem) | 对应 px (17px 基准) | 用途 |
|-------|----------|-------------------|------|
| `--text-xs` | 0.75rem | 12.75px | 极小标签、单选框标记、徽标说明 |
| `--text-sm` | 0.875rem | 14.875px | 按钮文字、返回链接、分类Tab、设备添加按钮 |
| `--text-base` | 1rem | 17px | 正文、输入框、卡片描述、检测结果 |
| `--text-md` | 1.125rem | 19.125px | 对话标题、设备名称、参数值、节标题 |
| `--text-lg` | 1.25rem | 21.25px | 卡片标题、品牌名、模态框标题、强调结果 |
| `--text-xl` | 1.5rem | 25.5px | 突出数值（设备用途） |
| `--text-2xl` | 1.6rem | 27.2px | 页面主标题 h1 |

### 字重体系（Font Weight Tokens）

| Token | 值 | 用途 |
|-------|-----|------|
| `--fw-normal` | 400 | 正文 |
| `--fw-medium` | 500 | 按钮、标签（当前 500） |
| `--fw-semibold` | 600 | 强调文字、导航、徽标 |
| `--fw-bold` | 700 | 标题、强强调 |

### 卡片相关字体（已统一，直接映射）

| Token | 映射到 | 说明 |
|-------|--------|------|
| `--card-title-font-size` | `--text-lg` | 卡片标题 |
| `--card-title-font-weight` | `--fw-bold` | 卡片标题字重 |
| `--card-label-font-size` | `--text-base` | 卡片标签 |
| `--card-label-font-weight` | `--fw-semibold` | 卡片标签字重 |
| `--card-count-font-size` | `--text-base` | 卡片计数 |

---

## TDD 实施步骤

### 第一阶段：RED

#### Step 1: 创建排版 token 常量文件
- `src/styles/typography-tokens.js` — 定义 JS 常量

#### Step 2: 创建测试文件 `tests/typography-tokens.test.js`
测试内容：
1. token 文件可导入，所有 token 已定义
2. 各 token 值符合设计规范（--text-xs=0.75rem, --text-sm=0.875rem, 等）
3. card tokens 正确映射到排版 tokens
4. 不存在小于 0.75rem 的 font-size（确保 0.7rem 被替换）

**预期：全部 FAIL**（文件不存在 / 值不符合）

### 第二阶段：GREEN

#### Step 3: 创建排版 token 文件
- `src/styles/typography-tokens.js`

#### Step 4: 更新 `src/style.css`
- 在 `:root` 中添加排版 token CSS 变量
- 更新全局类（`.btn`, `.btn-sm`, `.btn-lg`, `.input-field`, `.section-title`, `.badge`, `.input-group label` 等）使用 token 变量

#### Step 5: 替换全站组件中的硬编码 font-size
批量替换规则（按文件）：

| 文件 | 替换模式 |
|------|---------|
| **ProjectList.vue** | `.project-radio` 0.7rem→xs, `.card-desc` 1rem→base, `.dialog h2` 1.125rem→md, `.category-tab` 0.8125rem→sm, `.device-add-btn` 0.8125rem→sm, `.device-field-label` 0.75rem→xs |
| **HardwareLibrary.vue** | `.device-radio` 0.7rem→xs, `.dialog h2` 1.125rem→md |
| **OneClickConfig.vue** | `.back-link` 0.8125rem→sm, `.device-purpose` 1.5rem→xl, `.param-value` 1.125rem→md, `.result-title` 1.125rem→md, `.result-purpose` 1.25rem→lg |
| **QualityInspect.vue** | `.back-link` 0.8125rem→sm, `.device-name` 1.125rem→md, `.device-purpose` 1.5rem→xl, `.param-value` 1.125rem→md, `.device-result-tag` 1rem→base |
| **SerialModal.vue** | 保持现有值（已适老化优化），仅同步 token 引用 |
| **SerialConfig.vue** | `.log-box` 0.8rem→sm |
| **AppSidebar.vue** | `.brand-text` 1.25rem→lg, `.nav-label` 1rem→base |

#### Step 6: 更新全局样式类
- `.btn` → `font-size: var(--text-sm); font-weight: var(--fw-medium)`
- `.btn-sm` → `font-size: var(--text-xs)`
- `.btn-lg` → `font-size: var(--text-base)`
- `.input-group label` → `font-size: var(--text-xs)`
- `.input-field` → `font-size: var(--text-base)`
- `.section-title` → `font-size: var(--text-xs); font-weight: var(--fw-semibold)`
- `.badge` → `font-size: var(--text-xs)`
- `.page-header h1` → `font-size: var(--text-2xl)`
- `.page-header p` → `font-size: var(--text-base)`

### 第三阶段：REFACTOR

#### Step 7: 运行全部测试，确认全部 PASS
- `node tests/typography-tokens.test.js`
- `node tests/card-tokens.test.js`
- `node tests/test_add_device_custom_name.js`
- `node tests/test_save_device_name.js`

#### Step 8: 构建验证
- `npm run build`

---

## 注意事项

- **Card tokens 不动**：--card-* 变量是已有的，仅增加与排版 token 的映射关系
- **SerialModal.vue 不降级**：前次适老化已优化到较大字号，保持现状
- **0.7rem → 0.75rem**：单选框文字从 0.7 提升到 --text-xs
- **0.8125rem → 0.875rem**：按钮从 13.8px 提升到 14.9px
- **0.933rem 全部归一到 --text-base(1rem)**：部分页面描述文字从 15.9px 提升到 17px
- **font-family 保持不变**：已统一使用 CSS 变量，不再改动

## 验证清单

- [ ] 所有 RED 测试正确失败
- [ ] 所有 GREEN 测试通过
- [ ] 全站不再出现 0.7rem / 0.8rem / 0.8125rem / 0.867rem 等散乱值
- [ ] 全局样式类的 font-size 全部使用 token
- [ ] `npm run build` 成功