# 通信日志Tab角色权限控制实施计划

## 1. 现状分析

### 1.1 当前状态
当前硬件配置页面（OneClickConfig.vue）的右侧面板包含两个Tab：
- **配置结果** - 显示配置和检测结果
- **通信日志** - 显示串口通信日志

这两个Tab对所有用户都是可见的。

### 1.2 用户需求
- **普通用户**：只显示「配置结果」Tab，隐藏「通信日志」Tab
- **管理员**：显示两个Tab，可以切换查看配置结果和通信日志

### 1.3 角色判断方式
通过 `useUserStore` 的 `isAdmin` 计算属性判断：
- `userStore.isAdmin` = true → 管理员
- `userStore.isNormal` = true → 普通用户

## 2. 需要修改的文件

仅需修改一个文件：
- `d:\Users\OL\Desktop\硬件配置平台\test\hardware-debug\src\views\OneClickConfig.vue`

## 3. 具体修改内容

### 3.1 修改Tab切换部分

**修改位置**: OneClickConfig.vue 第63-68行（Tab切换区域）

**当前代码**：
```vue
<div class="right-section">
  <!-- Tab切换 -->
  <div class="result-tabs">
    <button :class="{ active: activeTab === 'result' }" @click="activeTab = 'result'">配置结果</button>
    <button :class="{ active: activeTab === 'log' }" @click="activeTab = 'log'; serialStore.fetchLogs()">通信日志</button>
  </div>
```

**修改为**：
```vue
<div class="right-section">
  <!-- Tab切换 - 只有管理员可以看到通信日志Tab -->
  <div class="result-tabs">
    <button :class="{ active: activeTab === 'result' }" @click="activeTab = 'result'">配置结果</button>
    <button v-if="userStore.isAdmin" :class="{ active: activeTab === 'log' }" @click="activeTab = 'log'; serialStore.fetchLogs()">通信日志</button>
  </div>
```

### 3.2 修改日志Tab内容区域

**修改位置**: OneClickConfig.vue 第119-132行（日志Tab内容）

**当前代码**：
```vue
<!-- 日志Tab -->
<div v-show="activeTab === 'log'" class="tab-content">
  <div class="log-panel-header">
    <span class="section-title">通信日志</span>
    <button class="btn btn-sm btn-secondary" @click="serialStore.clearLogs()">清空</button>
  </div>
  <div class="log-box" ref="logBoxRef">
    <div v-for="(log, i) in serialStore.logs" :key="i" class="log-line" :class="'log-' + log.type">
      <span class="log-time">[{{ log.timestamp }}]</span>
      <span>{{ log.message }}</span>
    </div>
    <div v-if="!serialStore.logs.length" class="log-empty">暂无通信日志</div>
  </div>
</div>
```

**修改为**：
```vue
<!-- 日志Tab - 只有管理员可以看到 -->
<div v-show="activeTab === 'log' && userStore.isAdmin" class="tab-content">
  <div class="log-panel-header">
    <span class="section-title">通信日志</span>
    <button class="btn btn-sm btn-secondary" @click="serialStore.clearLogs()">清空</button>
  </div>
  <div class="log-box" ref="logBoxRef">
    <div v-for="(log, i) in serialStore.logs" :key="i" class="log-line" :class="'log-' + log.type">
      <span class="log-time">[{{ log.timestamp }}]</span>
      <span>{{ log.message }}</span>
    </div>
    <div v-if="!serialStore.logs.length" class="log-empty">暂无通信日志</div>
  </div>
</div>
```

### 3.3 导入用户存储

需要确保在 script 部分导入 useUserStore：

**当前代码**（第138-147行）：
```vue
<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import { useSerialStore } from '../stores/serial'
import { api } from '../api'

const route = useRoute()
const projectStore = useProjectStore()
const serialStore = useSerialStore()
```

**修改为**：
```vue
<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import { useSerialStore } from '../stores/serial'
import { useUserStore } from '../stores/user'
import { api } from '../api'

const route = useRoute()
const projectStore = useProjectStore()
const serialStore = useSerialStore()
const userStore = useUserStore()
```

## 4. 预期效果

| 用户角色 | 配置结果Tab | 通信日志Tab |
|----------|-------------|-------------|
| 普通用户 | ✅ 可见 | ❌ 隐藏 |
| 管理员 | ✅ 可见 | ✅ 可见 |

## 5. 实施步骤

1. **导入用户存储** - 在 script 中添加 useUserStore 导入
2. **创建用户存储实例** - 添加 userStore 变量
3. **修改Tab切换** - 通信日志Tab添加 v-if="userStore.isAdmin"
4. **修改日志内容** - 日志内容区域添加 userStore.isAdmin 判断

## 6. 验证方式

1. 打开前端页面
2. 使用用户切换功能切换到普通用户
3. 进入硬件配置页面，确认通信日志Tab不可见
4. 切换到管理员，确认通信日志Tab可见并可正常切换
