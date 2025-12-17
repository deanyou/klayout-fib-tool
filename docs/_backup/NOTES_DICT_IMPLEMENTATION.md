# Notes Dictionary Implementation

## 改进说明

为了确保 notes 数据的可靠性，现在使用**双重存储**机制：

1. **Marker 对象属性**：`marker.notes`
2. **集中字典**：`panel.marker_notes_dict[marker_id]`

## 数据结构

### 集中字典

```python
class FIBPanel:
    def __init__(self):
        self.marker_notes_dict = {}  # marker_id -> notes
```

示例：
```python
{
    "CUT_0": "Beam 30kV, 10pA",
    "CONNECT_0": "连接这两点的A2",
    "PROBE_0": "GND test point"
}
```

## 工作流程

### 1. 添加 Notes

```python
def add_notes(self):
    # 用户输入 notes
    new_notes = "Your notes here"
    
    # 双重存储
    marker.notes = new_notes  # 存储在 marker 对象
    panel.marker_notes_dict[marker_id] = new_notes  # 存储在字典
```

### 2. 保存项目

```json
{
  "version": "1.0",
  "markers": [
    {
      "id": "CUT_0",
      "notes": "Beam 30kV, 10pA",
      ...
    }
  ],
  "marker_notes_dict": {
    "CUT_0": "Beam 30kV, 10pA",
    "CONNECT_0": "连接这两点的A2"
  }
}
```

### 3. 加载项目

```python
# 1. 加载字典
panel.marker_notes_dict = data['marker_notes_dict']

# 2. 恢复 marker notes（优先从字典）
if marker_id in panel.marker_notes_dict:
    marker.notes = panel.marker_notes_dict[marker_id]
else:
    marker.notes = marker_data.get('notes', '')
```

### 4. PDF 导出

```python
# 从 marker 对象读取（已从字典恢复）
notes = getattr(marker, 'notes', '')
```

## 优势

### 1. 数据冗余

- 如果 marker 对象的 notes 丢失，可以从字典恢复
- 如果字典丢失，marker 对象仍有 notes

### 2. 集中管理

- 可以快速查看所有 markers 的 notes
- 便于批量操作和搜索

### 3. 调试友好

```python
# 打印所有 notes
print(panel.marker_notes_dict)

# 输出：
# {
#   "CUT_0": "Beam 30kV, 10pA",
#   "CONNECT_0": "连接这两点的A2",
#   "PROBE_0": "GND test point"
# }
```

## 调试输出

### 添加 Notes 时

```
[Marker Menu] Stored in dict: CUT_0 -> 'Beam 30kV, 10pA'
[Marker Menu] Updated notes for CUT_0: 'Beam 30kV, 10pA'
[Marker Menu] Marker object id: 140123456789
[Marker Menu] Total markers in panel: 3
[Marker Menu]   CUT_0: notes='Beam 30kV, 10pA' (obj_id=140123456789)
[Marker Menu]   CONNECT_0: notes='连接这两点的A2' (obj_id=140123456790)
[Marker Menu]   PROBE_0: notes='' (obj_id=140123456791)
[Marker Menu] Centralized dict: {'CUT_0': 'Beam 30kV, 10pA', 'CONNECT_0': '连接这两点的A2'}
```

### 加载项目时

```
[FIB Panel] Loaded notes dict: {'CUT_0': 'Beam 30kV, 10pA', 'CONNECT_0': '连接这两点的A2'}
[FIB Panel] Restored notes from dict for CUT_0: 'Beam 30kV, 10pA'
[FIB Panel] Restored notes from dict for CONNECT_0: '连接这两点的A2'
```

### 导出 PDF 时

```
[Screenshot Export] CUT_0: notes='Beam 30kV, 10pA' (obj_id=140123456789)
[Screenshot Export] CONNECT_0: notes='连接这两点的A2' (obj_id=140123456790)
[Screenshot Export] PROBE_0: notes='' (obj_id=140123456791)
```

## 向后兼容

### 旧版本项目文件

如果加载的 JSON 文件没有 `marker_notes_dict` 字段：

```python
if 'marker_notes_dict' in data:
    self.marker_notes_dict = data['marker_notes_dict']
else:
    self.marker_notes_dict = {}  # 初始化为空字典
```

### 旧版本 marker 对象

如果 marker 对象没有 notes 属性：

```python
notes = getattr(marker, 'notes', '')  # 安全访问，默认为空字符串
```

## 测试验证

### 测试 1: 添加多个 notes

```python
# 创建 3 个 markers
CUT_0, CONNECT_0, PROBE_0

# 添加不同的 notes
CUT_0: "Note 1"
CONNECT_0: "Note 2"
PROBE_0: "Note 3"

# 验证字典
print(panel.marker_notes_dict)
# 输出: {'CUT_0': 'Note 1', 'CONNECT_0': 'Note 2', 'PROBE_0': 'Note 3'}
```

### 测试 2: 保存和加载

```python
# 保存项目
panel.save_markers_to_json('test.json')

# 检查 JSON 文件
{
  "marker_notes_dict": {
    "CUT_0": "Note 1",
    "CONNECT_0": "Note 2",
    "PROBE_0": "Note 3"
  }
}

# 加载项目
panel.load_markers_from_json('test.json')

# 验证恢复
for marker in panel.markers_list:
    print(f"{marker.id}: {marker.notes}")
```

### 测试 3: PDF 导出

```python
# 导出 PDF
panel.export_markers_to_pdf('report.pdf', view)

# 检查 HTML 报告
# 每个 marker 应该显示正确的 notes
```

## 修改的文件

1. **`src/fib_panel.py`**
   - 添加 `self.marker_notes_dict = {}`
   - 保存时包含字典
   - 加载时恢复字典
   - 加载 marker 时优先从字典恢复 notes

2. **`src/marker_menu.py`**
   - `add_notes()` 同时更新字典和 marker 对象
   - 添加调试输出显示字典内容

3. **`src/screenshot_export.py`**
   - 添加调试输出显示每个 marker 的 notes

## 版本信息

| 版本 | 日期 | 描述 |
|------|------|------|
| 1.1 | 2024-12-16 | 添加集中字典存储，双重存储机制 |

---

**改进完成！** 🎉

现在 notes 使用双重存储，确保数据可靠性和易于调试。
