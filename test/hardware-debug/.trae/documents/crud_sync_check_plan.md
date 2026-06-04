# CRUD 与页面显示同步性检查计划（TDD）

## 问题描述
检查项目中所有 CRUD 操作与页面显示是否同步，避免出现"数据库已更新但页面未刷新"或"页面已更新但数据库未保存"等不同步问题。

## 检查范围

### 1. 项目 CRUD 同步
| 操作 | 触发点 | 数据流 |
|------|--------|--------|
| 新建项目 | ProjectList.vue `createProject()` → `addProject()` | 弹框→API→store→页面 |
| 删除项目 | `doDelete()` → `deleteProject()` | 弹框→API→store→页面 |
| 编辑项目 | `saveEdit()` → `updateProject()` | 弹框→API→store→页面 |

### 2. 设备配置 CRUD 同步（编辑项目对话框内）
| 操作 | 触发点 | 数据流 |
|------|--------|--------|
| 添加硬件 | `addDeviceToEdit()` | 仅本地，保存时 `updateProject` 统一处理 |
| 删除硬件 | `removeDeviceFromEdit()` | 仅本地+记录 `removedConfigIds`，保存时统一处理 |
| 编辑硬件名 | `saveDeviceName()` | 仅本地，保存时统一处理 |
| 编辑硬件参数 | 直接 v-model | 仅本地，保存时统一处理 |

### 3. 硬件库 CRUD 同步
| 操作 | 触发点 | 数据流 |
|------|--------|--------|
| 新增分类 | `saveCategory()` → `addCategory()` | 弹框→API→store→页面 |
| 编辑分类 | `saveCategory()` → `updateCategory()` | 弹框→API→store→页面 |
| 删除分类 | `deleteSelectedCategory()` | 弹框→API→store→页面 |
| 新增硬件 | `saveDevice()` → `addDeviceType()` | 弹框→API→store→页面 |
| 编辑硬件 | `saveDevice()` → `updateDeviceType()` | 弹框→API→store→页面 |
| 删除硬件 | `deleteSelectedDevice()` | 弹框→API→store→页面 |

## 同步性潜在问题分析

### 1. **已修复的同步点**（无需再处理）
- ✅ `addProject` 使用 `push()`（与后端 `asc()` 排序一致）
- ✅ `addDeviceToEdit` 中 `custom_name` 默认为设备类型标签
- ✅ 编辑项目页面删除/编辑只改本地，保存时统一处理
- ✅ `saveDeviceName` 不再即时调用 API

### 2. **潜在同步风险点**
| 风险点 | 位置 | 风险 |
|--------|------|------|
| 编辑分类名称时 | HardwareLibrary.vue `editCategoryName()` | 编辑按钮点击后立即弹出弹框，但**状态显示在弹框中** |
| 编辑硬件名 | ProjectList.vue `saveDeviceName(index)` | 已修复，编辑图标一直显示 |
| 串口连接 | SerialConfig.vue | 串口状态与硬件配置使用单例后已修复 |
| `confirm()` 提示 | HardwareLibrary.vue `deleteSelectedCategory()` | 使用浏览器原生 `confirm()`，可能与 Vue 状态不同步 |
| 硬件库 `addDeviceType` 后 | projectStore.addDeviceType | `refreshAll()` 已调用，但 `subTypes` 是 computed，依赖 `allDeviceTypes` |

### 3. **可能的 Bug**
- **A. 硬件库删除分类**：`confirm()` 弹出后，如果用户取消，`selectedCategory.value = null` 不会执行，可能没问题
- **B. 编辑项目时 `device_configs` 同步**：保存时遍历 `device_configs`，对每个 config 调用 `updateDeviceConfig` 或 `addDeviceConfig`，已保存设备（id存在）即时更新
- **C. 硬件库编辑分类后**：`updateCategory` 调用 `refreshAll()`，store 重新拉取数据
- **D. 串口配置单例**：已修复，配置/检测按钮能正常发送指令

## TDD 实施步骤

### 第一阶段：RED（写失败测试）

#### Step 1: 创建测试文件 `tests/crud-sync.test.js`
测试内容（基于源代码静态分析 + 行为验证）：

1. **测试 1：项目 CRUD 同步**
   - 验证 `addProject` 使用 `push` 而非 `unshift`
   - 验证 `deleteProject` 从 store 中过滤删除的项目
   - 验证 `updateProject` 完成后调用 `refreshAll`

2. **测试 2：设备配置 CRUD 同步**
   - 验证 `addDeviceToEdit` 中 `custom_name` 默认值非空
   - 验证 `removeDeviceFromEdit` 记录到 `removedConfigIds`
   - 验证 `saveDeviceName` 不调用 API

3. **测试 3：硬件库 CRUD 同步**
   - 验证 `addCategory`/`updateCategory`/`deleteCategory` 后调用 `refreshAll`
   - 验证 `addDeviceType`/`updateDeviceType`/`deleteDeviceType` 后调用 `refreshAll`

4. **测试 4：状态显示与数据同步**
   - 验证 `subTypes` computed 正确从 `allDeviceTypes` 派生
   - 验证 `getDeviceTypeLabel`/`getCategoryLabel` 从 store 数据查找
   - 验证 `init()` 中 `loaded.value` 在数据加载完成后才置为 true

**预期：所有测试通过**（如果有任何不同步问题，测试会失败并指出）

### 第二阶段：GREEN（修复问题）

根据测试结果修复发现的不同步问题。

### 第三阶段：REFACTOR（验证）

#### Step 2: 运行全部测试
- `node tests/crud-sync.test.js`
- `node tests/modbus-singleton.test.js`
- `node tests/input-field-sizing.test.js`
- `node tests/typography-tokens.test.js`
- `node tests/card-tokens.test.js`
- `node tests/test_add_device_custom_name.js`
- `node tests/test_save_device_name.js`

#### Step 3: 构建验证
- `npm run build`

---

## 验证清单

- [ ] 测试文件创建完成
- [ ] 所有 CRUD 同步测试通过
- [ ] 全部 7 组测试通过
- [ ] `npm run build` 成功
- [ ] 无新增同步问题