# FIB Layer Color Setup Guide

## 推荐颜色配置

FIB Tool 使用三个专用图层，推荐使用以下颜色以便于区分：

| Layer | Name | Color | RGB Values |
|-------|------|-------|------------|
| 337 | FIB_CUT | 粉色 (Pink) | 255, 105, 180 |
| 338 | FIB_CONNECT | 黄色 (Yellow) | 255, 255, 0 |
| 339 | FIB_PROBE | 白色 (White) | 255, 255, 255 |

## 设置方法

### 步骤 1: 启用 Layer Toolbox

1. 在 KLayout 菜单栏选择：**View → Layer Toolbox**
2. 确保 Layer Toolbox 面板可见（通常在右侧）

### 步骤 2: 设置图层颜色

对每个 FIB 图层（337, 338, 339）执行以下操作：

1. 在 **Layer Toolbox** 中找到对应的图层
2. **右键点击**该图层
3. 选择 **Properties**（属性）
4. 在属性对话框中：
   - **Fill Color**（填充颜色）：输入 RGB 值或使用颜色选择器
   - **Frame Color**（边框颜色）：建议设置为相同颜色
5. 点击 **OK** 保存

### 步骤 3: 验证

- 在 Layer Toolbox 中查看图层，应该显示设置的颜色
- 在版图视图中，FIB markers 应该以对应颜色显示

## 详细设置

### Layer 337 (FIB_CUT) - 粉色

```
Fill Color RGB: 255, 105, 180
Frame Color RGB: 255, 105, 180
Hex: #FF69B4
```

用于标记 FIB 切断操作的位置。

### Layer 338 (FIB_CONNECT) - 黄色

```
Fill Color RGB: 255, 255, 0
Frame Color RGB: 255, 255, 0
Hex: #FFFF00
```

用于标记 FIB 连接操作的路径。

### Layer 339 (FIB_PROBE) - 白色

```
Fill Color RGB: 255, 255, 255
Frame Color RGB: 255, 255, 255
Hex: #FFFFFF
```

用于标记 FIB 探针测试点，同时也用于坐标文本标签。

## 注意事项

### 颜色持久化

- KLayout 会记住图层颜色设置
- 设置一次后，下次打开相同的 GDS 文件时颜色会保持
- 不同的 GDS 文件可能需要重新设置

### Layer Toolbox vs Layer Panel

- **Layer Toolbox**：用于设置图层属性（颜色、可见性等）
- **Layer Panel**：用于查看和选择图层

确保在 **Layer Toolbox** 中设置颜色，而不是 Layer Panel。

### 自动颜色设置

FIB Tool 会尝试自动设置图层颜色，但由于 KLayout Python API 的限制，自动设置可能不总是有效。如果颜色没有自动应用，请按照上述步骤手动设置。

## 故障排除

### 问题：找不到 Layer Toolbox

**解决方案**：
1. 菜单栏：View → Layer Toolbox
2. 如果仍然看不到，尝试：View → Restore Default Window Layout

### 问题：图层不在 Layer Toolbox 中

**解决方案**：
1. 确保已经创建了 FIB markers（插件会自动创建图层）
2. 或者手动创建图层：在 Layer Toolbox 中右键 → New Layer
3. 输入 Layer/Datatype：337/0, 338/0, 339/0

### 问题：颜色设置后不显示

**解决方案**：
1. 检查图层是否可见（Layer Toolbox 中图层前面的眼睛图标）
2. 尝试刷新视图：按 F5 或 View → Redraw
3. 检查是否在正确的 cellview 中

### 问题：每次打开文件都要重新设置颜色

**解决方案**：
1. 保存 Layer Properties：File → Save Layer Properties
2. 保存为 .lyp 文件
3. 下次打开时：File → Load Layer Properties

## 快速参考

```
Layer 337 (FIB_CUT):    RGB(255, 105, 180) - Pink
Layer 338 (FIB_CONNECT): RGB(255, 255, 0)   - Yellow
Layer 339 (FIB_PROBE):   RGB(255, 255, 255) - White
```

**设置位置**：View → Layer Toolbox → 右键图层 → Properties

## 相关文档

- [KLayout Layer Properties Documentation](https://www.klayout.de/doc-qt5/manual/layer_properties.html)
- [FIB Tool README](../README.md)
