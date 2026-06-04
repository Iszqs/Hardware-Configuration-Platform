# 项目库/硬件库/硬件配置卡片样式统一计划（TDD）

## 目标
统一 ProjectList.vue（项目库）、HardwareLibrary.vue（硬件库）、OneClickConfig.vue（硬件配置）三处卡片的卡片大小和字体大小。

## 统一标准（设计规范）

| CSS 变量 | 值 | 说明 |
|----------|------|------|
| `--card-min-height` | 220px | 卡片最小高度 |
| `--card-padding` | var(--spacing-lg) | 卡片内边距 |
| `--card-title-font-size` | 1.25rem (21.25px) | 卡片标题字号 |
| `--card-title-font-weight` | 700 | 卡片标题字重 |
| `--card-label-font-size` | 0.9375rem (15.9px) | 标签/次要文字字号 |
| `--card-label-font-weight` | 600 | 标签字重 |
| `--card-count-font-size` | 0.9375rem (15.9px) | 计数文字字号 |
| `--card-grid-min-width` | 280px | 网格最小列宽 |
| `--card-border-radius` | var(--radius-lg) | 卡片圆角 |

---

## TDD 实施步骤

### 第一阶段：RED（写失败测试）

#### Step 1: 创建设计 token 常量文件
创建 `src/styles/card-tokens.js`，定义卡片设计规范的 JS 常量（作为测试断言依据）。

#### Step 2: 创建测试文件 `tests/card-tokens.test.js`
编写测试，验证：
- 三处卡片的 `min-height` 是否统一为 220px
- 三处卡片的标题字号是否统一为 1.25rem
- 三处卡片的标签文字字号是否统一为 0.9375rem
- 三处卡片的计数文字字号是否统一为 0.9375rem
- 三处卡片的网格列宽是否统一为 `minmax(280px, 1fr)`
- 三处卡片的内边距是否统一为 `var(--spacing-lg)`

测试方式：通过 Vitest + jsdom 挂载组件，检查渲染后的 computed style。

**预期：所有测试 FAIL**（因为当前样式不统一）。

### 第二阶段：GREEN（实现代码）

#### Step 3: 更新 `src/style.css`
添加 CSS 自定义属性：
```css
:root {
  --card-min-height: 220px;
  --card-title-font-size: 1.25rem;
  --card-title-font-weight: 700;
  --card-label-font-size: 0.9375rem;
  --card-label-font-weight: 600;
  --card-count-font-size: 0.9375rem;
  --card-grid-min-width: 280px;
}
```

#### Step 4: 修改 `src/views/ProjectList.vue`
更新 scoped 样式：
- `.projects-grid` → `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- `.project-card` → `min-height: var(--card-min-height)`
- `.card-header h3` → `font-size: var(--card-title-font-size); font-weight: var(--card-title-font-weight)`
- `.device-badge` → `font-size: var(--card-label-font-size); font-weight: var(--card-label-font-weight)`
- `.device-count` → `font-size: var(--card-count-font-size)`

#### Step 5: 修改 `src/views/HardwareLibrary.vue`
更新 scoped 样式：
- `.hardware-grid` → `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- `.category-card` → `min-height: var(--card-min-height)`
- `.category-header h3` → `font-size: var(--card-title-font-size); font-weight: var(--card-title-font-weight)`
- `.device-type-label` → `font-size: var(--card-label-font-size); font-weight: var(--card-label-font-weight)`
- `.device-count` → `font-size: var(--card-count-font-size); color: var(--text-dim)`

#### Step 6: 修改 `src/views/OneClickConfig.vue`
更新 scoped 样式：
- `.device-grid` → `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`
- `.device-card` → `min-height: var(--card-min-height)`
- `.device-name` → `font-size: var(--card-title-font-size); font-weight: var(--card-title-font-weight)`
- `.category-tag` → `font-size: var(--card-label-font-size)`
- `.configured-badge` → `font-size: var(--card-label-font-size)`
- `.param-label` → `font-size: var(--card-label-font-size)`

### 第三阶段：REFACTOR（清理）

#### Step 7: 运行全部测试，确认全部 PASS
#### Step 8: 运行 `npm run build` 确认构建通过

---

## 注意事项

- 需要确保 `tests/` 目录下已有 Vitest 配置文件
- 如无 Vitest 配置，需先安装 `vitest` 和 `@vue/test-utils` 以及 `jsdom`
- 测试组件需要模拟 Pinia store（使用 `createTestingPinia`）
- 硬件库卡片（category-card）原无 `min-height`，统一后需要设置
- 硬件库 `.device-type-label` 从 0.8125rem 增加到 0.9375rem（增大）
- 项目库标题从 1.5rem 减小到 1.25rem，硬件库标题从 1.125rem 增大到 1.25rem

## 验证清单

- [ ] 所有测试 RED 阶段正确失败
- [ ] 所有测试 GREEN 阶段通过
- [ ] `npm run build` 构建成功
- [ ] 三处卡片视觉上大小一致
- [ ] 三处卡片标题字号一致
- [ ] 三处卡片标签/次要文字字号一致