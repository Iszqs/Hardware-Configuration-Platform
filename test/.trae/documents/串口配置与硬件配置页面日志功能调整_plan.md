# 串口配置与硬件配置页面日志功能调整

## Summary

1. 从串口配置页面（SerialModal.vue）移除通信日志显示
2. 在硬件配置页面（OneClickConfig.vue）的通信日志框添加清空日志按钮

## Current State Analysis

- **SerialModal.vue**：当前有一个完整的通信日志面板，包括标题、清空按钮、日志列表，还有定时器刷新功能
- **OneClickConfig.vue**：当前有通信日志Tab，但缺少清空按钮

## Proposed Changes

### 1. 修改 SerialModal.vue - 移除通信日志

**文件**：`src/components/SerialModal.vue`

**修改内容**：
- 移除整个 `<div class="log-panel">` 部分（第64-76行）
- 移除日志刷新相关的逻辑：
  - 移除 `logBoxRef` 变量
  - 移除 `logRefreshInterval` 变量
  - 移除 `onMounted`/`onUnmounted` 生命周期钩子
  - 移除监听 `props.visible` 的 `watch` 中的日志刷新逻辑
  - 移除监听 `serialStore.logs.length` 的 `watch`
- 更新 modal-body 的 grid 布局，因为现在只有 config-panel 了
- 移除 `.log-panel`、`.log-box`、`.log-line` 等相关样式

### 2. 修改 OneClickConfig.vue - 添加清空日志按钮

**文件**：`src/views/OneClickConfig.vue`

**修改内容**：
- 在日志面板添加标题和清空按钮（参考 SerialModal.vue 的样式）
- 点击清空按钮调用 `serialStore.clearLogs()`

## Verification Steps

1. 打开串口配置弹窗，确认通信日志面板已被移除
2. 打开硬件配置页面，切换到"通信日志"Tab，确认有清空按钮
3. 点击清空按钮，确认日志被清空（前端和后端）
