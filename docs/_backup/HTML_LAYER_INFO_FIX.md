# HTML 报告中添加 Layer 信息显示

## 问题描述

在 HTML 报告中，坐标信息没有显示对应的 layer 信息：

**之前**：
```
Type: CUT
Coordinates: (4466.869,2242.266) to (4472.655,2233.130) μm
```

**期望**：
```
Type: CUT
Coordinates: (4466.869,2242.266) [M1:86/0] to (4472.655,2233.130) [M2:87/0] μm
```

## 解决方案

### 修改的文件

1. **`fib_tool/screenshot_export.py`** - 主要的 HTML 报告生成
2. **`fib_tool/report.py`** - 简单的 HTML 报告生成

### 具体修改

#### 1. Two-point markers (CUT, CONNECT)

**之前**：
```python
coords = f"({marker.x1:.3f},{marker.y1:.3f}) to ({marker.x2:.3f},{marker.y2:.3f})"
```

**之后**：
```python
layer1_info = f" [{marker.layer1}]" if hasattr(marker, 'layer1') and marker.layer1 else ""
layer2_info = f" [{marker.layer2}]" if hasattr(marker, 'layer2') and marker.layer2 else ""
coords = f"({marker.x1:.3f},{marker.y1:.3f}){layer1_info} to ({marker.x2:.3f},{marker.y2:.3f}){layer2_info}"
```

#### 2. Single-point markers (PROBE)

**之前**：
```python
coords = f"({marker.x:.3f},{marker.y:.3f})"
```

**之后**：
```python
layer_info = f" [{marker.target_layer}]" if hasattr(marker, 'target_layer') and marker.target_layer else ""
coords = f"({marker.x:.3f},{marker.y:.3f}){layer_info}"
```

#### 3. Multi-point markers (MULTIPOINT_CUT, MULTIPOINT_CONNECT)

**之前**：
```python
point_strs = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points]
```

**之后**：
```python
point_strs = []
for i, p in enumerate(marker.points):
    layer_info = ""
    if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
        layer_info = f" [{marker.point_layers[i]}]"
    point_strs.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
```

## Layer 信息格式

Layer 信息以方括号显示，格式为 `[layername:layer/datatype]`：

- `[M1:86/0]` - 有 layer name 的情况
- `[86/0]` - 只有 layer/datatype 的情况
- `[N/A]` - 没有检测到 layer 的情况
- 无方括号 - 没有 layer 信息（旧数据或检测失败）

## 示例输出

### CUT Marker
```
Type: CUT
Coordinates: (4466.869,2242.266) [M1:86/0] to (4472.655,2233.130) [M2:87/0] μm
```

### CONNECT Marker
```
Type: CONNECT
Coordinates: (5090.726,2702.084) [314/0] to (4249.838,2161.667) [N/A] μm
```

### PROBE Marker
```
Type: PROBE
Coordinates: (3500.123,1800.456) [VIA:88/0] μm
```

### Multi-point Marker
```
Type: MULTIPOINT_CUT
Coordinates: 4 points: (100.0,200.0) [M1:86/0] → (150.0,200.0) [M1:86/0] → (150.0,250.0) [M2:87/0] → (200.0,250.0) [M2:87/0] μm
```

## 兼容性

### 向后兼容

- 检查 `hasattr(marker, 'layer1')` 确保属性存在
- 检查 `marker.layer1` 不为空
- 如果没有 layer 信息，不显示方括号

### 数据来源

Layer 信息来自 marker 对象的以下属性：

- **CutMarker**: `layer1`, `layer2`
- **ConnectMarker**: `layer1`, `layer2`
- **ProbeMarker**: `target_layer`
- **MultiPointCutMarker**: `point_layers` (列表)
- **MultiPointConnectMarker**: `point_layers` (列表)

这些属性在创建 marker 时通过 `layer_tap.py` 模块自动检测并填充。

## 测试建议

1. **创建不同类型的 markers**：
   - 在有 layer 的位置点击
   - 在空白区域点击
   - 在多层重叠区域点击

2. **生成 HTML 报告**：
   - File → Export to PDF/HTML
   - 检查坐标显示是否包含 layer 信息

3. **验证格式**：
   - 有 layer name: `[M1:86/0]`
   - 无 layer name: `[86/0]`
   - 无 layer: `[N/A]`
   - 旧数据: 无方括号

## 相关文件

- `fib_tool/screenshot_export.py` - 主要 HTML 报告生成
- `fib_tool/report.py` - 简单 HTML 报告生成
- `fib_tool/layer_tap.py` - Layer 信息检测
- `fib_tool/markers.py` - Marker 数据结构
- `fib_tool/multipoint_markers.py` - 多点 marker 数据结构

## 总结

现在 HTML 报告中的坐标信息会显示对应的 layer 信息，帮助用户更好地理解每个点击位置的 layer 上下文。这对于 FIB 操作的精确定位非常重要。