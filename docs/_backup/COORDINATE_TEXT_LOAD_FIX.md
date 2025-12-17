# 修复 Load 后坐标文本消失的问题

## 问题描述

当执行以下操作时，坐标文本（coordinate text labels）会消失：
1. Clear All - 清除所有 markers
2. Load - 从文件加载 markers

**现象**：Markers 本身（线条、圆圈、ID 标签）正常显示，但点击位置的坐标文本不见了。

## 根本原因

### 坐标文本的存储位置

FIB Tool 使用两种不同的图层：
1. **Marker 图层**（337/338/339）：存储 marker 的几何形状（线条、圆圈）和 ID 标签
2. **Coordinates 图层**（339）：存储坐标文本标签，如 `CUT_0:(100.123,200.456)`

### 问题所在

在 `load_markers_from_json()` 函数中：

```python
# 只调用了 marker.to_gds() 来绘制 marker
marker.to_gds(cell, fib_layer)

# 但 to_gds() 只绘制 marker 本身，不绘制坐标文本！
```

**`marker.to_gds()` 方法的内容**：
- ✅ 绘制 marker 几何形状（线条、圆圈）
- ✅ 绘制 marker ID 标签（如 "CUT_0"）
- ❌ **不绘制坐标文本**（如 "CUT_0:(100.123,200.456)"）

### 为什么创建时有坐标文本？

在创建 marker 时（`fib_plugin.py`）：

```python
# 1. 点击时添加坐标文本（临时，没有 marker ID）
self._add_coordinate_text(view, x, y)

# 2. 创建 marker 后，更新坐标文本添加 marker ID
update_coordinate_texts_with_marker_id(marker, cell, layout)
```

但在 load 时，这两步都没有执行！

## 解决方案

### 1. 添加 `_recreate_coordinate_texts()` 方法

**文件**：`fib_tool/fib_panel.py`

```python
def _recreate_coordinate_texts(self, marker, cell, layout):
    """Recreate coordinate text labels for a loaded marker"""
    try:
        dbu = layout.dbu
        coord_layer_num = LAYERS['coordinates']
        coord_layer = layout.layer(coord_layer_num, 0)
        
        # Get coordinates based on marker type
        coordinates = []
        
        if hasattr(marker, 'points'):
            # Multi-point marker
            coordinates = marker.points
        elif hasattr(marker, 'x1'):
            # Two-point marker (cut, connect)
            coordinates = [(marker.x1, marker.y1), (marker.x2, marker.y2)]
        elif hasattr(marker, 'x'):
            # Single-point marker (probe)
            coordinates = [(marker.x, marker.y)]
        
        # Create coordinate texts
        for x, y in coordinates:
            coord_text = f"{marker.id}:({x:.3f},{y:.3f})"
            text_x = int(x / dbu)
            text_y = int(y / dbu)
            
            text_obj = pya.Text(coord_text, pya.Trans(pya.Point(text_x, text_y)))
            cell.shapes(coord_layer).insert(text_obj)
        
        print(f"[FIB Panel] Recreated {len(coordinates)} coordinate texts for {marker.id}")
        
    except Exception as e:
        print(f"[FIB Panel] Error recreating coordinate texts: {e}")
```

### 2. 在 Load 时调用

修改 `load_markers_from_json()` 函数：

```python
# 旧代码
marker.to_gds(cell, fib_layer)

# Add to panel
self.add_marker(marker)

# 新代码
marker.to_gds(cell, fib_layer)

# Recreate coordinate texts for this marker
self._recreate_coordinate_texts(marker, cell, layout)

# Add to panel
self.add_marker(marker)
```

## 工作原理

### 坐标文本格式

```
MARKER_ID:(x.xxx,y.yyy)
```

例如：
- `CUT_0:(4254.683,2349.790)`
- `CONNECT_1:(5090.726,2702.084)`
- `PROBE_0:(3500.123,1800.456)`

### 支持的 Marker 类型

1. **Two-point markers** (CUT, CONNECT)
   - 有 `x1, y1, x2, y2` 属性
   - 创建 2 个坐标文本

2. **Single-point markers** (PROBE)
   - 有 `x, y` 属性
   - 创建 1 个坐标文本

3. **Multi-point markers** (MULTIPOINT_CUT, MULTIPOINT_CONNECT)
   - 有 `points` 列表属性
   - 创建 N 个坐标文本（N = 点的数量）

### 坐标精度

使用 3 位小数精度（0.001 μm），与 `GEOMETRIC_PARAMS['coordinate_precision']` 一致。

## 测试步骤

1. **创建一些 markers**
   - 创建 CUT, CONNECT, PROBE markers
   - 确认坐标文本正常显示

2. **保存项目**
   - File → Save Project
   - 保存为 JSON 文件

3. **Clear All**
   - 点击 "Clear All" 按钮
   - 确认所有 markers 和坐标文本都被清除

4. **Load 项目**
   - File → Load Project
   - 选择之前保存的 JSON 文件

5. **验证结果**
   - ✅ Markers 正常显示
   - ✅ 坐标文本正常显示
   - ✅ 坐标文本包含 marker ID
   - ✅ 坐标文本位置正确

## 调试输出

Load 时会看到以下输出：

```
[FIB Panel] Loaded notes dict: {...}
[FIB Panel] Recreated 2 coordinate texts for CUT_0
[FIB Panel] Recreated 2 coordinate texts for CONNECT_1
[FIB Panel] Recreated 1 coordinate texts for PROBE_0
[FIB Panel] Loaded 3 markers from /path/to/file.json
```

## 相关文件

- `fib_tool/fib_panel.py` - 添加了 `_recreate_coordinate_texts()` 方法
- `fib_tool/fib_plugin.py` - 原始的 `_add_coordinate_text()` 和 `update_coordinate_texts_with_marker_id()` 函数
- `fib_tool/markers.py` - `to_gds()` 方法（不包含坐标文本）
- `fib_tool/config.py` - `LAYERS['coordinates']` 配置

## 注意事项

### 为什么不在 `to_gds()` 中添加坐标文本？

考虑过在 `marker.to_gds()` 方法中直接绘制坐标文本，但这样做有问题：

1. **职责分离**：`to_gds()` 负责绘制 marker 本身，坐标文本是辅助信息
2. **图层不同**：Marker 在 337/338/339 层，坐标文本在 339 层
3. **灵活性**：可能需要单独控制坐标文本的显示/隐藏

### 坐标文本的生命周期

1. **创建时**：
   - 点击 → `_add_coordinate_text()` → 临时坐标文本
   - 完成 → `update_coordinate_texts_with_marker_id()` → 添加 marker ID

2. **Load 时**：
   - `marker.to_gds()` → 绘制 marker
   - `_recreate_coordinate_texts()` → 重新创建坐标文本

3. **删除时**：
   - `delete_coordinate_texts_for_marker()` → 删除坐标文本
   - 删除 marker 几何形状

## 总结

通过添加 `_recreate_coordinate_texts()` 方法并在 load 时调用，成功解决了坐标文本消失的问题。现在 Clear All → Load 操作后，坐标文本会正确恢复。
