# 文本修改计划

## 修改内容

| 文件 | 位置 | 修改前 | 修改后 |
|------|------|--------|--------|
| `src/views/HardwareLibrary.vue` | 第6行 | `<p>管理系统中的硬件类型</p>` | 删除该行 |
| `src/views/HardwareLibrary.vue` | 第44行 | `{{ ...length }} 种硬件` | `{{ ...length }} 硬件` |
| `src/views/ProjectList.vue` | 第30行 | `{{ ...length }} 设备` | `{{ ...length }} 硬件` |

## 实施步骤

1. 修改 `HardwareLibrary.vue` 第6行，删除 `<p>管理系统中的硬件类型</p>`
2. 修改 `HardwareLibrary.vue` 第44行，将"种硬件"改为"硬件"
3. 修改 `ProjectList.vue` 第30行，将"设备"改为"硬件"
4. 构建验证

## 验证清单

- [ ] HardwareLibrary.vue 第6行已删除
- [ ] HardwareLibrary.vue 第44行已修改
- [ ] ProjectList.vue 第30行已修改
- [ ] `npm run build` 成功