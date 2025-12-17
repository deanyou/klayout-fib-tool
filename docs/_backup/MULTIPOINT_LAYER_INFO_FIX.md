# Multi-Point Markers Layer 信息显示修复

## 问题描述

Multi-point markers (CUT 和 CONNECT) 在 FIB Panel 中没有显示 layer 信息，只显示坐标。

**之前显示**：
```
MULTIPOINT_CUT_0 - CUT (MULTI) - 3 pts: (100.0,200.0) → (150.0,250.0) → (200.0,300.0)
```

**期望显示**：
```
MULTIPOINT_CUT_0 - CUT (MULTI) - 3 pts: (100.0,200.0) [M1:86/0] → (150.0,250.0) [M2:87/0] → (200.0,300.0) [M3:88/0]
```

## 根本原因

在 `fib_panel.py` 的 `add_marker()` 函数中，multi-point markers 的显示逻辑没有包含 layer 信息。

**问题代码**：
```python
# 只显示坐标，没有 layer 信息
point_strs = [f"({p[0]:.3f},{p[1]:.3f})" for p in marker.points]
```

## 解决方案

### 修改 `add_marker()` 函数

**文件**：`fib_tool/fib_panel.py`

**修改位置**：第 1510-1525 行

**新的实现**：

#### 1. 少于等于 3 个点的情况

```python
# 显示所有坐标和 layer 信息
point_strs = []
for i, p in enumerate(marker.points):
    layer_info = ""
    if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
        layer_info = f" [{marker.point_layers[i]}]"
    point_strs.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")
coords = f"{len(marker.points)} pts: " + " → ".join(point_strs)
```

#### 2. 超过 3 个点的情况

```python
# 显示前 2 个点 + ... + 最后 1 个点，都包含 layer 信息
first_points = []
for i in range(2):
    p = marker.points[i]
    layer_info = ""
    if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
        layer_info = f" [{marker.point_layers[i]}]"
    first_points.append(f"({p[0]:.3f},{p[1]:.3f}){layer_info}")

# 最后一个点
last_p = marker.points[-1]
last_layer_info = ""
if hasattr(marker, 'point_layers') and len(marker.point_layers) > 0 and marker.point_layers[-1]:
    last_layer_info = f" [{marker.point_layers[-1]}]"
last_point = f"({last_p[0]:.3f},{last_p[1]:.3f}){last_layer_info}"

coords = f"{len(marker.points)} pts: " + " → ".join(first_points) + " → ... → " + last_point
```

## Layer 信息来源

Multi-point markers 的 layer 信息存储在 `point_layers` 列表中：

```python
@dataclass
class MultiPointCutMarker:
    id: str
    points: List[Tuple[float, float]]
    layer: int
    point_layers: List[str] = field(default_factory=list)  # 每个点的 layer 信息
```

### Layer 信息的填充

在创建 multi-point marker 时，通过 `layer_tap.py` 检测每个点击位置的 layer：

```python
# fib_plugin.py 中的创建逻辑
point_layers = []
for x, y in points:
    layer_info = get_layer_at_point_with_selection(x, y)
    layer_str = format_layer_for_display(layer_info)
    point_layers.append(layer_str)

marker = create_multipoint_cut_marker(marker_id, points, point_layers)
```

## 显示效果

### 3 个点或更少

```
MULTIPOINT_CUT_0 - CUT (MULTI) - 3 pts: (100.0,200.0) [M1:86/0] → (150.0,250.0) [M2:87/0] → (200.0,300.0) [M3:88/0]
```

### 超过 3 个点

```
MULTIPOINT_CUT_1 - CUT (MULTI) - 5 pts: (100.0,200.0) [M1:86/0] → (150.0,250.0) [M2:87/0] → ... → (300.0,400.0) [M5:90/0]
```

### 没有 Layer 信息的情况

```
MULTIPOINT_CUT_2 - CUT (MULTI) - 2 pts: (100.0,200.0) [N/A] → (150.0,250.0) [N/A]
```

或者（如果 point_layers 为空）：

```
MULTIPOINT_CUT_3 - CUT (MULTI) - 2 pts: (100.0,200.0) → (150.0,250.0)
```

## 兼容性处理

### 向后兼容

代码检查 `point_layers` 属性是否存在和有效：

```python
if hasattr(marker, 'point_layers') and i < len(marker.point_layers) and marker.point_layers[i]:
    layer_info = f" [{marker.point_layers[i]}]"
```

这确保了：
- 旧的 marker 对象（没有 `point_layers` 属性）不会出错
- `point_layers` 列表长度不足时不会越界
- 空的 layer 信息不会显示空的方括号

### 数据完整性

如果 `point_layers` 列表长度小于 `points` 列表长度，只有有 layer 信息的点会显示 layer，其他点只显示坐标。

## 测试建议

### 基本测试

1. **创建 multi-point CUT marker**：
   - 在不同 layer 上点击 3 个点
   - 检查 Panel 中是否显示每个点的 layer 信息

2. **创建 multi-point CONNECT marker**：
   - 在不同 layer 上点击多个点
   - 检查 Panel 中的显示

3. **创建超过 3 个点的 marker**：
   - 检查是否正确显示前 2 个 + ... + 最后 1 个

### 边界测试

1. **在空白区域点击**：
   - 应该显示 `[N/A]` 或不显示方括号

2. **混合情况**：
   - 有些点在 layer 上，有些在空白区域
   - 应该只为有 layer 的点显示信息

3. **Load 旧数据**：
   - 加载没有 `point_layers` 信息的旧 JSON 文件
   - 应该正常显示，只是没有 layer 信息

## 相关文件

- `fib_tool/fib_panel.py` - Panel 显示逻辑
- `fib_tool/multipoint_markers.py` - Multi-point marker 数据结构
- `fib_tool/fib_plugin.py` - Multi-point marker 创建逻辑
- `fib_tool/layer_tap.py` - Layer 检测逻辑

## 总结

现在 multi-point markers 在 FIB Panel 中会正确显示每个点的 layer 信息，提供了更完整的上下文信息，帮助用户理解每个点击位置的 layer 情况。显示格式简洁明了，支持不同数量的点，并且向后兼容旧数据。