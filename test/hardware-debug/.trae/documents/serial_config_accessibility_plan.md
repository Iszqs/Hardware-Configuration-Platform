# 串口配置弹框中老年人阅读体验优化计划

## 目标
对串口配置弹框（SerialModal.vue）进行适老化改造，提升中老年用户的可读性和操作便利性。

---

## 现状分析

基于 Web Interface Guidelines 审计结果：

### 审计发现

**文件：`src/components/SerialModal.vue`**

| 行号 | 问题 | 严重程度 |
|------|------|----------|
| L2 | 弹框标题 h2 字号 1rem(15px) — 偏小 | 中 |
| L17 | section-title 字号 0.733rem(~11px) — 太小 | 高 |
| L20 | input-group label 字号 0.733rem(~11px) — 太小 | 高 |
| L23 | select 选项文本字号 0.867rem(~13px) — 偏小 | 中 |
| L48 | 状态文本 status-text 字号 0.867rem(~13px) — 偏小 | 中 |
| L86 | 日志面板内容字号 0.767rem(~11.5px) — 极小 | 高 |
| L7 | 关闭按钮 28x28px — 小于 WCAG 推荐的最小触控区域 44x44px | 高 |
| L4 | 弹框整体 max-width: 800px — 可接受 | - |
| L37 | 连接/断开按钮 height: 40px — 可用但偏小 | 低 |
| L44 | LED 指示灯 10px 直径 — 太小不易看清 | 中 |

---

## 改造方案

### 1. 字体放大（全局影响）

| 当前值 | 目标值 | 说明 |
|--------|--------|------|
| html font-size: 15px | html font-size: 17px | 基础字号放大，所有 rem 单位元素跟随放大 |

> 注：此修改在 `src/style.css` 的 `:root` 之后，`html` 选择器中。

### 2. SerialModal.vue 专有样式修改

#### 2.1 弹框标题
```css
/* 当前 */
.modal-header h2 { font-size: 1rem; }
/* 改为 */
.modal-header h2 { font-size: 1.2rem; }
```

#### 2.2 section-title（"连接参数"、"通信日志"）
```css
/* 当前 */
.section-title { font-size: 0.733rem; }
/* 改为 */
.section-title { font-size: 0.9rem; }
```

#### 2.3 表单标签（"串口号"、"波特率"等）
```css
/* 当前 */
.input-group label { font-size: 0.733rem; }
/* 改为 */
.input-group label { font-size: 0.95rem; }
```

#### 2.4 select 下拉框
```css
/* 当前 */
.input-field { font-size: 0.867rem; padding: 8px 12px; }
/* 改为 */
.input-field { font-size: 1rem; padding: 10px 14px; }
```

#### 2.5 状态文本
```css
/* 当前省略，跟随 .status-row/status-text */
/* 改为显式设置 */
.status-text { font-size: 1rem; }
```

#### 2.6 日志面板
```css
/* 当前 */
.log-box { font-size: 0.767rem; }
/* 改为 */
.log-box { font-size: 0.95rem; }
```

#### 2.7 关闭按钮尺寸（触控友好）
```css
/* 当前 */
.close-btn { width: 28px; height: 28px; }
/* 改为 */
.close-btn { width: 44px; height: 44px; }
.close-btn svg { width: 20px; height: 20px; }
```

#### 2.8 LED 指示灯
```css
/* 当前 — 未在 SerialModal.vue 中显式覆盖，使用全局 .led */
.led { width: 10px; height: 10px; }
/* 改为在 SerialModal.vue scoped 中覆盖 */
:deep(.led) { width: 16px; height: 16px; }
```

#### 2.9 连接/断开按钮增大
```css
/* 当前 — 使用全局 .btn 类 height: 40px */
/* 改为在 modal 中增强 */
.btn { height: 48px; font-size: 1rem; }
```

### 3. 对比度优化（深色主题）

当前背景 `#14151C`，文字 `#F2F4F8`（主文字）、`#9AA0AE`（次要文字）。
- 主文字对比度：`#F2F4F8` / `#14151C` = ~14.8:1 ✅ 通过 WCAG AAA
- 次要文字：`#9AA0AE` / `#14151C` = ~6.8:1 ✅ 通过 WCAG AA
- 较淡文字：`#5C6170` / `#14151C` = ~3.5:1 ⚠️ 通过 AA 大文本，但建议加强

### 4. prefers-reduced-motion

当前全局已支持 `prefers-reduced-motion`（`style.css L604-621`），弹框动画 `.fadeIn` 和 `.slideUp` 会跟随禁用 ✅

### 5. touch-action 优化

```css
/* 在弹框内添加 */
.modal button, .modal select {
  touch-action: manipulation;
}
```

---

## 实施步骤

1. **修改 `src/style.css`** — `html` 基础字号从 15px → 17px
2. **修改 `src/components/SerialModal.vue`** — 按上述方案调整所有字号、触控尺寸
3. **验证** — 检查无样式冲突、布局不溢出

---

## 注意事项

- `html` 基础字号改动会影响全站，需检查其他页面布局是否正常
- 如不希望全局改动，可仅在 SerialModal.vue 中通过 scoped 样式覆盖，但弹框内所有字号需逐一设置
- 字号增大后需检查弹框 `max-height: 70vh` 内内容是否完整显示，必要时增加滚动
- 响应式 `@media (max-width: 700px)` 布局不变，仅字号增大