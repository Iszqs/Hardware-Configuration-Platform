# 硬件配置页面添加通信日志Tab切换

## Summary
在硬件配置页面的右侧栏添加Tab切换功能，让用户可以在"配置/检测结果"和"通信日志"之间切换显示。

## Current State Analysis

**当前布局** (`OneClickConfig.vue`)：
```
main-layout (grid: 1fr 420px)
├── left-section: 设备卡片网格
└── right-section (420px固定)
    ├── 配置结果卡片 (lastResult)
    ├── 检测结果卡片 (lastInspectResult)
    └── 空状态提示 (!lastResult && !lastInspectResult)
```

**serialStore** (`stores/serial.js`)：
- `logs` - 响应式数组，存储日志列表
- `fetchLogs()` - 从后端获取日志
- 日志格式：`{ timestamp, message, type }`

**日志来源**：
- 后端 `log_service.py` 的内存缓冲区
- 前端每2秒调用 `GET /api/serial/logs` 刷新

## Proposed Changes

### 1. 修改 `OneClickConfig.vue` - 添加Tab切换和日志显示

**文件**: `src/views/OneClickConfig.vue`

**布局调整**：
```vue
right-section
├── Tab栏 (结果 / 通信日志)
├── 结果Tab内容
│   ├── 配置结果卡片 (lastResult)
│   ├── 检测结果卡片 (lastInspectResult)
│   └── 空状态提示
└── 日志Tab内容
    └── 日志面板 (ref: logBoxRef)
```

**具体修改**：

1. 添加 `activeTab` 响应式变量，默认为 `'result'`
2. 添加 `logBoxRef` 引用日志滚动容器
3. 添加 `logRefreshInterval` 定时器
4. 在 `onMounted` 时启动日志刷新
5. 在 `onUnmounted` 时清除定时器
6. 添加 `watch` 监听 `serialStore.logs.length` 自动滚动
7. 添加Tab切换的HTML结构和CSS样式

### 2. 样式设计

**Tab栏样式**：
- 两个Tab按钮：左侧"结果"，右侧"通信日志"
- 当前Tab高亮显示（底部边框或背景色）
- Tab栏固定在右侧栏顶部

**日志面板样式**（参考 `SerialModal.vue`）：
- 背景色：`var(--bg-primary)`
- 字体：`var(--font-mono)`
- 字号：`0.95rem`
- 每行日志显示时间戳 + 消息
- 不同类型日志颜色：
  - `log-success` / success: 绿色
  - `log-error` / error: 红色
  - `log-warning` / warning: 黄色
  - 其他: 灰色

## Implementation Details

### OneClickConfig.vue 模板部分修改

```vue
<div class="right-section">
  <!-- Tab切换 -->
  <div class="result-tabs">
    <button :class="{ active: activeTab === 'result' }" @click="activeTab = 'result'">配置结果</button>
    <button :class="{ active: activeTab === 'log' }" @click="activeTab = 'log'; fetchLogs()">通信日志</button>
  </div>

  <!-- 结果Tab -->
  <div v-show="activeTab === 'result'" class="tab-content">
    <!-- 现有的结果卡片 -->
  </div>

  <!-- 日志Tab -->
  <div v-show="activeTab === 'log'" class="tab-content">
    <div class="log-box" ref="logBoxRef">
      <div v-for="(log, i) in serialStore.logs" :key="i" class="log-line" :class="'log-' + log.type">
        <span class="log-time">[{{ log.timestamp }}]</span>
        <span>{{ log.message }}</span>
      </div>
      <div v-if="!serialStore.logs.length" class="log-empty">暂无通信日志</div>
    </div>
  </div>
</div>
```

### OneClickConfig.vue 脚本部分修改

```javascript
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const activeTab = ref('result')
const logBoxRef = ref(null)
let logRefreshInterval = null

onMounted(() => {
  // 启动日志刷新
  logRefreshInterval = setInterval(() => {
    serialStore.fetchLogs()
  }, 2000)
})

onUnmounted(() => {
  if (logRefreshInterval) {
    clearInterval(logRefreshInterval)
  }
})

watch(() => serialStore.logs.length, () => {
  nextTick(() => {
    if (logBoxRef.value) {
      logBoxRef.value.scrollTop = logBoxRef.value.scrollHeight
    }
  })
})
```

### OneClickConfig.vue 样式部分修改

```css
.right-section {
  /* 现有样式 */
  display: flex;
  flex-direction: column;
}

.result-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-default);
  margin-bottom: 16px;
}

.result-tabs button {
  flex: 1;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.result-tabs button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}

.log-box {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 12px;
  font-family: var(--font-mono);
  font-size: 0.95rem;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
}

.log-line {
  padding: 3px 0;
  color: var(--text-secondary);
}

.log-success { color: var(--color-success); }
.log-error { color: var(--color-error); }
.log-warning { color: var(--color-warning); }

.log-time {
  color: var(--text-dim);
  margin-right: 8px;
}

.log-empty {
  text-align: center;
  padding-top: 60px;
  color: var(--text-dim);
}
```

## Verification Steps

1. 打开硬件配置页面，右侧栏默认显示"配置结果"Tab
2. 点击"通信日志"Tab，切换到日志面板
3. 进行配置或检测操作，日志会实时更新
4. 切换回"配置结果"Tab，可以继续操作设备
5. 再次切换到"通信日志"Tab，可以看到完整的通信过程
