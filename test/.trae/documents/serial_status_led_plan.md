# 串口连接状态圆点动态效果实施计划

## 1. 现状分析

### 1.1 当前状态显示
当前串口状态显示已经使用了 `led` 元素：
- **位置**: `App.vue` 第9行 - `<span class="led" :class="'led-' + serialStore.statusColor"></span>`
- **样式**: `style.css` 第449-476行定义了基本的 led 样式

### 1.2 当前状态颜色映射（serial.js）
- `statusColor` 返回值：
  - `'green'` - 已连接
  - `'amber'` - 连接中
  - `'off'` - 未连接

### 1.3 当前样式问题
当前的 led 只是静态圆点，没有动态效果。用户希望增加动态效果来更好地展示连接状态。

## 2. 需要修改的文件

主要修改一个文件：
- `d:\Users\OL\Desktop\硬件配置平台\test\hardware-debug\src\style.css`

## 3. 具体修改内容

### 3.1 添加动态动画效果

为不同状态添加不同的动态效果：

| 状态 | 颜色 | 动画效果 |
|------|------|----------|
| 已连接 (green) | 绿色 | 持续发光效果 + 轻微呼吸动画 |
| 连接中 (amber) | 橙色 | 脉冲闪烁动画 |
| 未连接 (off) | 灰色 | 静态（无动画）|

### 3.2 修改样式

**修改位置**: style.css 第449-476行（led样式部分）

**当前代码**：
```css
.led {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.led-success {
  background: var(--color-success);
}

.led-error {
  background: var(--color-error);
}

.led-warning {
  background: var(--color-warning);
}

.led-info {
  background: var(--color-info);
}

.led-off {
  background: var(--text-dim);
  opacity: 0.4;
}
```

**修改为**：
```css
.led {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
  position: relative;
}

.led-success {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
  animation: ledBreathe 2s ease-in-out infinite;
}

.led-error {
  background: var(--color-error);
  box-shadow: 0 0 8px var(--color-error);
}

.led-warning {
  background: var(--color-warning);
  box-shadow: 0 0 8px var(--color-warning);
  animation: ledPulse 1s ease-in-out infinite;
}

.led-info {
  background: var(--color-info);
  box-shadow: 0 0 8px var(--color-info);
}

.led-off {
  background: var(--text-dim);
  opacity: 0.4;
}

.led-green {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
  animation: ledBreathe 2s ease-in-out infinite;
}

.led-amber {
  background: var(--color-warning);
  box-shadow: 0 0 8px var(--color-warning);
  animation: ledPulse 1s ease-in-out infinite;
}

@keyframes ledBreathe {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 8px var(--color-success);
  }
  50% {
    opacity: 0.6;
    transform: scale(0.9);
    box-shadow: 0 0 4px var(--color-success);
  }
}

@keyframes ledPulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(1.2);
  }
}
```

## 4. 预期效果

修改后的串口状态圆点：

| 状态 | 效果 |
|------|------|
| ✅ 已连接 (green) | 绿色圆点 + 柔和的呼吸动画（渐明渐暗）|
| ⏳ 连接中 (amber) | 橙色圆点 + 快速脉冲闪烁动画 |
| ❌ 未连接 (off) | 灰色圆点（静态，无动画）|

## 5. 实施步骤

1. **修改全局样式** - 在 style.css 中添加动态动画效果
2. **测试验证** - 确保不同状态显示正确的动态效果

## 6. 验证方式

1. 打开前端页面
2. 观察顶部状态栏的串口状态指示灯
3. 点击打开串口配置弹窗
4. 测试连接、断开状态下的指示灯效果
