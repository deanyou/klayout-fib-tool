# Add Notes Feature

## 功能说明

为 FIB markers 添加了右键菜单 "Add Notes" 功能，允许用户为每个 marker 添加备注信息。

## 使用方法

### 1. 添加 Notes

1. 在 FIB Panel 的 Markers 列表中，右键点击任意 marker
2. 选择 "Add Notes" 菜单项
3. 在弹出的对话框中输入备注信息
4. 点击 OK 保存

### 2. 编辑 Notes

- 重复上述步骤，可以修改已有的 notes
- 清空输入框可以删除 notes

### 3. 查看 Notes

Notes 会在以下位置显示：

1. **PDF/HTML 报告**
   - 导出 PDF 时，notes 会显示在每个 marker 的信息区域
   - 格式：`Notes: [your notes here]`
   - 如果没有 notes，显示为 `-`

2. **保存/加载项目**
   - Notes 会保存到 JSON 项目文件中
   - 加载项目时会恢复 notes

## 右键菜单选项

完整的右键菜单包括：

1. **Zoom to Fit** - 缩放视图到 marker 位置
2. **Copy Coordinates** - 复制 marker 坐标到剪贴板
3. **Add Notes** - 添加或编辑 marker 备注 ✨ 新功能
4. **Rename Marker** - 重命名 marker
5. **Delete Marker** - 删除 marker

## 实现细节

### 数据存储

Notes 存储在 marker 对象的 `notes` 属性中：

```python
marker.notes = "Your notes here"
```

### PDF 导出

在 HTML 报告中，notes 显示在 marker 信息区域：

```html
<div class="marker-info">
    <p><strong>Type:</strong> CUT</p>
    <p><strong>Coordinates:</strong> (100.00,200.00) to (150.00,250.00) μm</p>
    <p><strong>Notes:</strong> This is a test cut marker</p>
</div>
```

### JSON 保存格式

```json
{
  "markers": [
    {
      "id": "CUT_0",
      "type": "cut",
      "x1": 100.0,
      "y1": 200.0,
      "x2": 150.0,
      "y2": 250.0,
      "notes": "This is a test cut marker",
      "screenshots": [],
      "target_layers": []
    }
  ]
}
```

## 使用场景

### 示例 1: 标记特殊区域

```
Marker: CUT_0
Notes: Critical area - use low beam current
```

### 示例 2: 记录参数

```
Marker: CONNECT_1
Notes: Beam: 30kV, Current: 10pA, Dwell: 1us
```

### 示例 3: 工艺说明

```
Marker: PROBE_2
Notes: Contact pad for electrical testing - avoid contamination
```

## 技术实现

### 修改的文件

- `src/marker_menu.py` - 添加 "Add Notes" 菜单项和处理函数

### 新增函数

```python
def add_notes(self):
    """Add or edit notes for the selected marker"""
    # 1. 获取选中的 marker
    # 2. 显示输入对话框
    # 3. 保存 notes 到 marker.notes
    # 4. 显示确认消息
```

### 已有功能（无需修改）

- `src/screenshot_export.py` - 已支持 notes 显示
- `src/fib_panel.py` - 已支持 notes 保存/加载
- `src/fib_plugin.py` - 创建 marker 时初始化 notes = ""

## 测试建议

1. **基本测试**
   - 创建一个 marker
   - 右键点击，选择 "Add Notes"
   - 输入 notes 并保存
   - 导出 PDF，验证 notes 显示

2. **编辑测试**
   - 对已有 notes 的 marker 再次添加 notes
   - 验证可以修改现有 notes

3. **清空测试**
   - 清空 notes 输入框
   - 验证 notes 被删除

4. **保存/加载测试**
   - 添加 notes 后保存项目
   - 加载项目，验证 notes 恢复

5. **PDF 导出测试**
   - 创建多个 markers，部分有 notes，部分没有
   - 导出 PDF，验证：
     - 有 notes 的显示正确
     - 没有 notes 的显示 `-`

## 版本信息

| 版本 | 日期 | 描述 |
|------|------|------|
| 1.0 | 2024-12-16 | 初始实现 - 右键菜单添加 notes 功能 |

---

**功能完成！** 🎉

现在可以为每个 marker 添加备注信息，并在 PDF 报告中查看。
