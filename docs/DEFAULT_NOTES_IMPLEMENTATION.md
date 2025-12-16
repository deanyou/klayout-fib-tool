# 默认 Notes 实现

## 功能说明

为不同类型的 marker 设置默认的 notes 值，并修复 notes 显示问题。

## 默认值设置

### 默认 Notes 值

| Marker 类型 | 默认 Notes |
|------------|-----------|
| CUT        | 切断      |
| CONNECT    | 连接      |
| PROBE      | 点测      |

### 适用范围

- ✅ 普通 markers（CutMarker, ConnectMarker, ProbeMarker）
- ✅ Multi-point markers（MultiPointCutMarker, MultiPointConnectMarker）

## 实现位置

### 1. 创建 Marker 时设置默认值

**`src/fib_plugin.py`**
```python
# CUT markers
marker.notes = "切断"  # Default notes for CUT markers

# CONNECT markers  
marker.notes = "连接"  # Default notes for CONNECT markers

# PROBE markers
marker.notes = "点测"  # Default notes for PROBE markers
```

**`src/multipoint_markers.py`**
```python
# Multi-point CUT markers
marker.notes = "切断"  # Default notes for multi-point CUT markers

# Multi-point CONNECT markers
marker.notes = "连接"  # Default notes for multi-point CONNECT markers
```

### 2. Add Notes 对话框显示默认值

**`src/marker_menu.py`**
```python
# Get current notes
current_notes = getattr(marker, 'notes', '')

# If notes is empty, set default based on marker type
if not current_notes:
    marker_class = marker.__class__.__name__
    if 'Cut' in marker_class:
        current_notes = "切断"
    elif 'Connect' in marker_class:
        current_notes = "连接"
    elif 'Probe' in marker_class:
        current_notes = "点测"
```

### 3. 加载项目时设置默认值

**`src/fib_panel.py`**
```python
loaded_notes = marker_data.get('notes', '')
# If no notes in file, set default based on marker type
if not loaded_notes:
    if marker_type == 'cut' or marker_type == 'multipoint_cut':
        loaded_notes = "切断"
    elif marker_type == 'connect' or marker_type == 'multipoint_connect':
        loaded_notes = "连接"
    elif marker_type == 'probe':
        loaded_notes = "点测"
marker.notes = loaded_notes
```

### 4. PDF 导出时确保默认值

**`src/screenshot_export.py`**
```python
# Try to get notes from marker
notes = getattr(marker, 'notes', '')

# If notes is empty, set default based on marker type
if not notes:
    if 'Cut' in marker_class:
        notes = "切断"
    elif 'Connect' in marker_class:
        notes = "连接"
    elif 'Probe' in marker_class:
        notes = "点测"
```

## 用户体验

### 创建 Marker

1. 用户创建 CUT marker
2. 自动设置 notes = "切断"
3. 在 PDF 报告中显示默认值

### 编辑 Notes

1. 用户右键点击 marker → Add Notes
2. 对话框显示当前值（如果为空则显示默认值）
3. 用户可以修改或保持默认值

### 加载项目

1. 加载旧项目文件（可能没有 notes）
2. 自动为空的 notes 设置默认值
3. 确保向后兼容

## 调试输出

### PDF 导出时

```
[Screenshot Export] CUT_0: notes='切断' (obj_id=140123456789)
[Screenshot Export] Marker class: CutMarker
[Screenshot Export] CONNECT_0: notes='连接' (obj_id=140123456790)
[Screenshot Export] Marker class: ConnectMarker
[Screenshot Export] PROBE_0: notes='点测' (obj_id=140123456791)
[Screenshot Export] Marker class: ProbeMarker
```

### Add Notes 时

```
[Marker Menu] Updated notes for CUT_0: '切断'
[Marker Menu] Stored in dict: CUT_0 -> '切断'
[Marker Menu] Centralized dict: {'CUT_0': '切断', 'CONNECT_0': '连接'}
```

## HTML 报告效果

### 示例输出

```html
<!-- CUT Marker -->
<div class="marker-info">
    <p><strong>Type:</strong> CUT</p>
    <p><strong>Coordinates:</strong> (100.00,200.00) to (150.00,250.00) μm</p>
    <p><strong>Dimensions:</strong> ΔX = 50.00 μm, ΔY = 50.00 μm</p>
    <p><strong>Length:</strong> 70.71 μm</p>
    <p><strong>Notes:</strong> 切断</p>
</div>

<!-- CONNECT Marker -->
<div class="marker-info">
    <p><strong>Type:</strong> CONNECT</p>
    <p><strong>Coordinates:</strong> (200.00,300.00) to (250.00,350.00) μm</p>
    <p><strong>Dimensions:</strong> ΔX = 50.00 μm, ΔY = 50.00 μm</p>
    <p><strong>Length:</strong> 70.71 μm</p>
    <p><strong>Notes:</strong> 连接</p>
</div>

<!-- PROBE Marker -->
<div class="marker-info">
    <p><strong>Type:</strong> PROBE</p>
    <p><strong>Coordinates:</strong> (300.00,400.00) μm</p>
    <p><strong>Dimensions:</strong> Single point marker</p>
    <p><strong>Length:</strong> -</p>
    <p><strong>Notes:</strong> 点测</p>
</div>
```

## 向后兼容

### 旧项目文件

- ✅ 加载没有 notes 字段的旧项目
- ✅ 自动设置默认值
- ✅ 不影响已有的自定义 notes

### 空 Notes

- ✅ 如果用户清空 notes，会在下次加载时恢复默认值
- ✅ PDF 导出时确保显示默认值而不是空白

## 测试场景

### 测试 1: 新建 Markers

1. 创建 CUT, CONNECT, PROBE markers
2. 导出 PDF
3. 验证显示默认 notes

### 测试 2: 编辑 Notes

1. 右键 → Add Notes
2. 验证对话框显示默认值
3. 修改并保存

### 测试 3: 保存/加载

1. 保存项目
2. 重新加载
3. 验证 notes 正确恢复

### 测试 4: 旧项目兼容

1. 加载没有 notes 的旧项目文件
2. 验证自动设置默认值

---

**默认 Notes 功能完成！** 🎉

现在所有 markers 都有有意义的默认 notes，提升用户体验。