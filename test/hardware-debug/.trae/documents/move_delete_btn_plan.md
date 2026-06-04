# 将编辑项目页面的删除按钮移动到右侧

## 需求
在项目编辑弹窗"硬件参数配置"中，将删除按钮移到最右侧。

## 当前结构
```
.device-edit-top (flex, space-between)
  .device-edit-info
    .device-name-wrapper (设备名)
    按钮 [删除]   ← 按钮在 info 内
```

## 修改后结构
```
.device-edit-top (flex, space-between)
  .device-edit-info
    .device-name-wrapper (设备名)
  按钮 [删除]   ← 按钮在顶层，自动靠右
```

## 修改文件
- `src/views/ProjectList.vue`

## 修改内容
将第134行的删除按钮移出 `device-edit-info`，放到 `device-edit-top` 的直接子级
