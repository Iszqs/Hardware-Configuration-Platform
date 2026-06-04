# 修复硬件配置页面分类名称不同步问题

## 问题
在硬件库修改分类名称后，硬件配置页面的分类标签仍显示旧名称。原因是 `project` computed 只依赖于 `projects` 数组，没监听 `categories` 的变化，导致组件不会重新渲染。

## 修改文件
- `src/views/OneClickConfig.vue`

## 修改内容
在 `project` computed 中显式访问 `projectStore.categories` 和 `projectStore.allDeviceTypes`，建立响应式依赖关系，确保分类/设备类型更新时组件也会重新渲染。

### 当前代码(line 125)
```js
const project = computed(() => projectStore.getProject(route.params.projectId))
```

### 修改后
```js
const project = computed(() => {
  projectStore.categories
  projectStore.allDeviceTypes
  return projectStore.getProject(route.params.projectId)
})
```
