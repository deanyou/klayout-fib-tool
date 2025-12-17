# Notes Isolation Debug Guide

## 问题描述

用户报告："只允许存一个 marker"，需要验证每个 marker 的 notes 是否正确隔离。

## 当前实现

每个 marker 对象都有自己的 `notes` 属性：

```python
marker.notes = "Your notes here"
```

## 调试步骤

### 1. 添加调试输出

已在以下位置添加调试信息：

**`src/marker_menu.py` - add_notes() 函数：**
```python
print(f"[Marker Menu] Updated notes for {marker_id}: '{new_notes}'")
print(f"[Marker Menu] Marker object id: {id(marker)}")
print(f"[Marker Menu] Total markers in panel: {len(self.panel.markers_list)}")

# Verify the update by checking all markers
for m in self.panel.markers_list:
    if hasattr(m, 'notes'):
        print(f"[Marker Menu]   {m.id}: notes='{m.notes}' (obj_id={id(m)})")
```

**`src/screenshot_export.py` - generate_html_report_with_screenshots()：**
```python
print(f"[Screenshot Export] {marker.id}: notes='{notes}' (obj_id={id(marker)})")
```

### 2. 测试步骤

1. **创建多个 markers**
   ```
   - 创建 CUT_0
   - 创建 CONNECT_0
   - 创建 PROBE_0
   ```

2. **为每个 marker 添加不同的 notes**
   ```
   CUT_0: "Note for CUT"
   CONNECT_0: "Note for CONNECT"
   PROBE_0: "Note for PROBE"
   ```

3. **检查控制台输出**
   ```
   [Marker Menu] Updated notes for CUT_0: 'Note for CUT'
   [Marker Menu] Marker object id: 140123456789
   [Marker Menu] Total markers in panel: 3
   [Marker Menu]   CUT_0: notes='Note for CUT' (obj_id=140123456789)
   [Marker Menu]   CONNECT_0: notes='' (obj_id=140123456790)
   [Marker Menu]   PROBE_0: notes='' (obj_id=140123456791)
   ```

4. **导出 PDF 并检查输出**
   ```
   [Screenshot Export] CUT_0: notes='Note for CUT' (obj_id=140123456789)
   [Screenshot Export] CONNECT_0: notes='Note for CONNECT' (obj_id=140123456790)
   [Screenshot Export] PROBE_0: notes='Note for PROBE' (obj_id=140123456791)
   ```

5. **验证 PDF 报告**
   - 打开生成的 HTML 文件
   - 检查每个 marker 的 Notes 字段
   - 确认每个 marker 显示正确的 notes

### 3. 预期结果

✅ **正确的情况：**
- 每个 marker 有不同的 object id
- 每个 marker 的 notes 独立存储
- PDF 报告中每个 marker 显示正确的 notes

❌ **错误的情况：**
- 所有 markers 共享同一个 notes 值
- 修改一个 marker 的 notes 会影响其他 markers
- PDF 报告中所有 markers 显示相同的 notes

## 可能的问题原因

### 1. 类级别共享属性

如果在 marker 类定义中使用了类级别的可变默认值：

```python
# 错误示例
@dataclass
class CutMarker:
    notes: list = []  # 这会被所有实例共享！
```

**解决方案：**
```python
# 正确示例
@dataclass
class CutMarker:
    notes: str = field(default="")  # 每个实例独立
```

### 2. 引用传递问题

如果 notes 是一个可变对象（如 dict 或 list），可能会被意外共享。

**当前实现：**
```python
marker.notes = ""  # 字符串是不可变的，安全
```

### 3. find_marker_by_id 返回错误对象

如果 find_marker_by_id 总是返回同一个对象。

**当前实现：**
```python
def find_marker_by_id(self, marker_id):
    for marker in self.panel.markers_list:
        if marker.id == marker_id:
            return marker  # 返回正确的 marker 对象
    return None
```

## 验证脚本

运行 `test_notes_isolation.py` 来验证 notes 隔离：

```bash
python test_notes_isolation.py
```

预期输出：
```
=== Test 1: Notes Isolation ===
marker1.notes = 'Note for CUT_0'
marker2.notes = 'Note for CONNECT_0'
marker3.notes = 'Note for PROBE_0'

=== Test 2: Modify One Marker ===
After modifying marker1:
marker1.notes = 'Modified note for CUT_0'
marker2.notes = 'Note for CONNECT_0'
marker3.notes = 'Note for PROBE_0'

=== Test 3: Object Identity ===
marker1 id: 140123456789
marker2 id: 140123456790
marker3 id: 140123456791
Are they different objects? True

=== Test Complete ===
If all markers have different notes, the isolation is working correctly.
```

## 解决方案

如果确认存在 notes 共享问题，可以采用以下方案：

### 方案 1: 使用 dataclass field (推荐)

修改 `src/markers.py`：

```python
from dataclasses import dataclass, field

@dataclass
class CutMarker:
    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    layer: int
    notes: str = field(default="")
    target_layers: list = field(default_factory=list)
    screenshots: list = field(default_factory=list)
```

### 方案 2: 使用全局 notes 字典

在 `src/fib_panel.py` 中添加：

```python
class FIBPanel:
    def __init__(self):
        self.markers_list = []
        self.marker_notes = {}  # marker_id -> notes
```

修改 `src/marker_menu.py`：

```python
def add_notes(self):
    # ...
    if ok:
        # Store in global dict
        self.panel.marker_notes[marker_id] = new_notes
        # Also store in marker object
        marker.notes = new_notes
```

### 方案 3: 使用 __dict__ 动态属性

确保每次都创建新的属性：

```python
marker.__dict__['notes'] = new_notes
```

## 当前状态

根据代码审查，当前实现应该是正确的：

✅ 每个 marker 对象独立创建
✅ notes 是字符串（不可变类型）
✅ find_marker_by_id 返回正确的对象
✅ 保存/加载逻辑正确遍历所有 markers

**需要用户提供更多信息：**
1. 具体的复现步骤
2. 控制台的调试输出
3. 保存的 JSON 文件内容

---

**调试信息已添加，请重新测试并提供控制台输出。**
