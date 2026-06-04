# 降低硬件配置卡片高度计划

## 需求
卡片当前高度约412.83px，用户觉得太高。选择"缩小高度"方案，从220px降到180px。

## 修改文件
1. `src/style.css` - 修改 `--card-min-height`
2. `src/views/OneClickConfig.vue` - 同步调整右侧面板高度

## 修改内容
1. 将 `--card-min-height: 220px` 改为 `--card-min-height: 180px`
2. 右侧面板高度从826px改为700px（同步减少约126px）
