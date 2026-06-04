# 串口配置弹窗尺寸优化实施计划

## 1. 现状分析

### 1.1 问题描述
用户反馈串口配置弹窗（SerialModal.vue）太大，占用过多屏幕空间。

### 1.2 当前配置分析
**SerialModal.vue 当前样式：**
- 弹窗宽度：`width: 90%; max-width: 800px`
- 内容布局：4个输入字段纵向排列（每行一个）
- 输入框padding：`padding: 10px 14px`
- 按钮高度：`height: 48px`
- 弹窗body padding：`padding: 20px`
- 弹窗最大高度：`max-height: 70vh`

### 1.3 优化目标
将弹窗从"宽屏"模式改为"紧凑"模式，同时保持功能完整性和良好的用户体验。

## 2. 需要修改的文件

仅需修改一个文件：
- `d:\Users\OL\Desktop\硬件配置平台\test\hardware-debug\src\components\SerialModal.vue`

## 3. 具体修改内容

### 3.1 减小弹窗宽度
**修改位置**: SerialModal.vue 第108-117行（.modal样式）

**当前代码**：
```css
.modal {
  width: 90%;
  max-width: 800px;
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--elevation-lg);
  overflow: hidden;
  animation: slideUp 0.2s ease;
}
```

**修改为**：
```css
.modal {
  width: 90%;
  max-width: 480px;  /* 从800px减小到480px */
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--elevation-lg);
  overflow: hidden;
  animation: slideUp 0.2s ease;
}
```

### 3.2 改为两列网格布局
**修改位置**: SerialModal.vue 第15-45行（表单部分）

**当前代码**：
```html
<div class="form-grid">
  <div class="input-group">
    <label>串口号</label>
    <select class="input-field" v-model="serialStore.config.portName">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>波特率</label>
    <select class="input-field" v-model="serialStore.config.baudRate">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>数据位</label>
    <select class="input-field" v-model="serialStore.config.dataBits">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>校验</label>
    <select class="input-field" v-model="serialStore.config.parity">
      ...
    </select>
  </div>
</div>
```

**修改为**：
```html
<div class="form-grid form-grid-2col">
  <div class="input-group">
    <label>串口号</label>
    <select class="input-field" v-model="serialStore.config.portName">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>波特率</label>
    <select class="input-field" v-model="serialStore.config.baudRate">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>数据位</label>
    <select class="input-field" v-model="serialStore.config.dataBits">
      ...
    </select>
  </div>
  <div class="input-group">
    <label>校验</label>
    <select class="input-field" v-model="serialStore.config.parity">
      ...
    </select>
  </div>
</div>
```

### 3.3 添加两列布局样式
**修改位置**: SerialModal.vue style部分（第193-197行附近）

**当前代码**：
```css
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

**修改为**：
```css
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* 两列等宽布局 */
  gap: 12px;
}
```

### 3.4 减小按钮和输入框尺寸
**修改位置**: SerialModal.vue style部分

**修改内容**：
1. 减小按钮高度：从 `height: 48px` 改为 `height: 40px`
2. 减小输入框padding：从 `padding: 10px 14px` 改为 `padding: 8px 12px`
3. 减小modal-body padding：从 `padding: 20px` 改为 `padding: 16px`

## 4. 预期效果

修改后的弹窗将：
- ✅ 宽度从最大800px减小到480px（减少40%）
- ✅ 表单从4行变为2x2网格布局（高度减少约50%）
- ✅ 按钮更紧凑
- ✅ 整体更加精致，占用屏幕空间更少
- ✅ 保持所有功能完整性

## 5. 实施步骤

1. **修改弹窗最大宽度** - 将 `max-width: 800px` 改为 `max-width: 480px`
2. **修改表单布局** - 添加 `form-grid-2col` class，使用grid两列布局
3. **调整间距和尺寸** - 减小padding、按钮高度、输入框padding
4. **测试验证** - 确保弹窗显示正常，功能完整

## 6. 验证方式

1. 打开前端页面
2. 点击状态栏的串口状态图标
3. 检查弹窗尺寸是否明显缩小
4. 确认所有配置选项都能正常选择
5. 测试连接和断开功能是否正常
