# KLayout 面板集成技术研究

## 1. KLayout Qt 集成概述

KLayout 基于 Qt 框架构建，提供了 Python 绑定来访问 Qt 功能。

### 1.1 主要 API 入口

```python
import pya

# 获取应用程序实例
app = pya.Application.instance()

# 获取主窗口
main_window = app.main_window()

# 主窗口类型
# main_window 是 pya.MainWindow，继承自 QMainWindow
```

### 1.2 可用的 Qt 类

KLayout 通过 `pya` 模块暴露了许多 Qt 类：

- `pya.QWidget` - 基础窗口部件
- `pya.QDialog` - 对话框
- `pya.QDockWidget` - 可停靠窗口
- `pya.QMainWindow` - 主窗口
- `pya.QTreeWidget` - 树形视图
- `pya.QPushButton` - 按钮
- `pya.QVBoxLayout` / `pya.QHBoxLayout` - 布局管理器
- `pya.QTabWidget` - 选项卡控件
- `pya.QGroupBox` - 分组框
- `pya.QCheckBox` - 复选框
- `pya.QLineEdit` - 文本输入框
- `pya.QLabel` - 标签

## 2. 创建可停靠面板的方法

### 2.1 方法 1: 使用 QDockWidget

```python
import pya

class FIBPanel(pya.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("FIB", parent)
        
        # 创建主容器
        container = pya.QWidget()
        layout = pya.QVBoxLayout(container)
        
        # 添加控件
        btn_cut = pya.QPushButton("Cut")
        layout.addWidget(btn_cut)
        
        self.setWidget(container)

# 添加到主窗口
main_window = pya.Application.instance().main_window()
panel = FIBPanel(main_window)
main_window.addDockWidget(pya.Qt.RightDockWidgetArea, panel)
```

### 2.2 方法 2: 使用 KLayout 的 Browser 系统

KLayout 有内置的 Browser 面板系统，可能更适合集成：

```python
# 研究 KLayout 的 BrowserPanel 或类似 API
# 需要查看 KLayout 源码或文档
```

### 2.3 方法 3: 使用 Plugin 的 configure_view

```python
class FIBPluginFactory(pya.PluginFactory):
    def __init__(self):
        super().__init__()
        self.register(-999, "fib_tool", "FIB Tool")
    
    def create_plugin(self, manager, root, view):
        # 可能可以在这里创建面板
        pass
```

## 3. 面板布局设计

### 3.1 顶部工具栏

```
[New] [Close] [More ▼]              [GenData]
```

- New: 创建新项目
- Close: 关闭当前项目
- More: 下拉菜单（Save, Load, Export）
- GenData: 生成数据

### 3.2 项目选项卡

```
┌─────────┬─────────┐
│ Report  │ Layout  │
└─────────┴─────────┘
```

### 3.3 AutoCutGroupRegion 区域

```
☑ AutoCutGroupRegion
MarginX: [0.0    ] MarginY: [0.0  ]
```

### 3.4 添加标记区域

```
Add
[Cut] [Connect] [Probe]
```

### 3.5 文档结构区域

```
FIB Doc structure
[Group] [CornerPicture] [Edit] ☐SelectAll

├─ General Notes
├─ Corner Screenshots          0
├─ □ function1_fix
│   ├─ box    (507.441,1636.843,543.430,1646.241)
│   ├─ layers L1.0
│   ├─ Notes
│   └─ Screenshots             2
├─ ⊕ CUT_0
└─ ⊟ CONNECT_0
    ├─ pts    (521.111, 1646.241),(507.441, 1643.892)
    ├─ layers L1.0;L1.0
    ├─ Notes
    └─ Screenshots             3
```

## 4. 数据模型设计

### 4.1 FIB 项目结构

```python
class FIBProject:
    name: str
    general_notes: str
    corner_screenshots: List[Screenshot]
    markers: List[FIBMarker]
    groups: List[FIBGroup]

class FIBMarker:
    id: str
    type: str  # 'cut', 'connect', 'probe'
    coordinates: Tuple[float, ...]
    layers: List[str]
    notes: str
    screenshots: List[Screenshot]

class FIBGroup:
    name: str
    markers: List[FIBMarker]
    box: Tuple[float, float, float, float]  # bounding box
```

### 4.2 树节点结构

```python
class TreeNode:
    text: str
    value: Any
    children: List[TreeNode]
    expanded: bool
    checked: bool
```

## 5. 事件处理

### 5.1 按钮点击

```python
btn_cut.clicked(self.on_cut_clicked)

def on_cut_clicked(self):
    # 激活 CUT 模式
    # 与现有 Plugin 系统集成
    pass
```

### 5.2 树节点选择

```python
tree.itemClicked(self.on_item_clicked)

def on_item_clicked(self, item):
    # 获取选中的标记
    # 在布局中高亮显示
    pass
```

### 5.3 树节点双击

```python
tree.itemDoubleClicked(self.on_item_double_clicked)

def on_item_double_clicked(self, item):
    # 缩放到标记位置
    pass
```

## 6. 与现有代码集成

### 6.1 与 fib_plugin.py 集成

```python
# 面板需要能够：
# 1. 调用 create_cut_marker, create_connect_marker, create_probe_marker
# 2. 访问 marker_counter 和已创建的标记列表
# 3. 响应标记创建事件，更新树视图
```

### 6.2 标记列表管理

```python
# 需要维护一个全局的标记列表
markers_list = []

def on_marker_created(marker):
    markers_list.append(marker)
    update_tree_view()
```

## 7. 实现步骤

### Phase 1: 基础面板框架
1. 创建 QDockWidget 子类
2. 添加基本布局
3. 添加 Cut/Connect/Probe 按钮
4. 集成到主窗口

### Phase 2: 文档结构树
1. 添加 QTreeWidget
2. 实现标记节点显示
3. 实现节点展开/折叠
4. 实现节点选择事件

### Phase 3: 项目管理
1. 实现 New/Close 功能
2. 实现 Save/Load 功能
3. 实现 GenData 功能

### Phase 4: 高级功能
1. 实现分组功能
2. 实现角落截图
3. 实现 AutoCutGroupRegion
4. 实现报告生成

## 8. 潜在问题和解决方案

### 8.1 Qt 版本兼容性
- KLayout 可能使用特定版本的 Qt
- 需要测试 API 可用性

### 8.2 面板持久化
- 需要保存面板位置和状态
- 可能需要使用 KLayout 的配置系统

### 8.3 与 Plugin 系统的冲突
- 面板和 Plugin 都需要处理鼠标事件
- 需要设计好事件分发机制

### 8.4 性能考虑
- 大量标记时树视图的性能
- 截图存储和显示的内存使用

## 9. 右键上下文菜单实现

### 9.1 QTreeWidget 右键菜单

```python
# 启用右键菜单
tree.setContextMenuPolicy(pya.Qt.CustomContextMenu)
tree.customContextMenuRequested(self.on_context_menu)

def on_context_menu(self, position):
    # 获取点击的节点
    item = self.tree.itemAt(position)
    if not item:
        return
    
    # 创建上下文菜单
    menu = pya.QMenu()
    
    # 根据节点类型添加不同的菜单项
    node_type = item.data(0, pya.Qt.UserRole)
    
    if node_type in ['cut', 'connect', 'probe']:
        # 标记节点的菜单
        action_fit = menu.addAction("Fit")
        action_delete = menu.addAction("Delete")
        action_rename = menu.addAction("Rename")
        menu.addSeparator()
        action_notes = menu.addAction("Edit Notes")
        action_screenshots = menu.addAction("Edit Screenshots")
        
        # 连接信号
        action_fit.triggered(lambda: self.fit_to_marker(item))
        action_delete.triggered(lambda: self.delete_marker(item))
        action_rename.triggered(lambda: self.rename_marker(item))
        action_notes.triggered(lambda: self.edit_notes(item))
        action_screenshots.triggered(lambda: self.edit_screenshots(item))
    
    elif node_type == 'group':
        # 组节点的菜单
        action_expand = menu.addAction("Expand All")
        action_collapse = menu.addAction("Collapse All")
        menu.addSeparator()
        action_delete_group = menu.addAction("Delete Group")
        action_rename_group = menu.addAction("Rename Group")
    
    # 显示菜单
    menu.exec_(self.tree.viewport().mapToGlobal(position))
```

### 9.2 菜单操作实现

```python
def fit_to_marker(self, item):
    """缩放视图以适应标记"""
    marker = item.data(0, pya.Qt.UserRole + 1)
    if marker:
        view = pya.Application.instance().main_window().current_view()
        # 计算标记的边界框
        bbox = self._get_marker_bbox(marker)
        # 缩放到边界框
        view.zoom_box(bbox)

def delete_marker(self, item):
    """删除标记"""
    # 确认对话框
    result = pya.QMessageBox.question(
        self, "Delete Marker",
        f"Are you sure you want to delete {item.text(0)}?",
        pya.QMessageBox.Yes | pya.QMessageBox.No
    )
    if result == pya.QMessageBox.Yes:
        marker = item.data(0, pya.Qt.UserRole + 1)
        # 从 GDS 删除
        self._remove_marker_from_gds(marker)
        # 从树视图删除
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            index = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(index)

def rename_marker(self, item):
    """重命名标记"""
    old_name = item.text(0)
    new_name, ok = pya.QInputDialog.getText(
        self, "Rename Marker",
        "Enter new name:",
        pya.QLineEdit.Normal,
        old_name
    )
    if ok and new_name:
        marker = item.data(0, pya.Qt.UserRole + 1)
        marker.id = new_name
        item.setText(0, new_name)
        # 更新 GDS 中的标签
        self._update_marker_label_in_gds(marker)

def edit_notes(self, item):
    """编辑标记备注"""
    marker = item.data(0, pya.Qt.UserRole + 1)
    current_notes = getattr(marker, 'notes', '')
    
    # 创建多行文本编辑对话框
    dialog = pya.QDialog(self)
    dialog.setWindowTitle("Edit Notes")
    layout = pya.QVBoxLayout(dialog)
    
    text_edit = pya.QTextEdit()
    text_edit.setPlainText(current_notes)
    layout.addWidget(text_edit)
    
    buttons = pya.QDialogButtonBox(
        pya.QDialogButtonBox.Ok | pya.QDialogButtonBox.Cancel
    )
    buttons.accepted(dialog.accept)
    buttons.rejected(dialog.reject)
    layout.addWidget(buttons)
    
    if dialog.exec_() == pya.QDialog.Accepted:
        marker.notes = text_edit.toPlainText()
        # 更新树视图中的 Notes 子节点
        self._update_notes_node(item, marker.notes)

def edit_screenshots(self, item):
    """编辑标记截图"""
    marker = item.data(0, pya.Qt.UserRole + 1)
    # 打开截图管理对话框
    dialog = ScreenshotManagerDialog(self, marker)
    dialog.exec_()
    # 更新树视图中的截图计数
    self._update_screenshots_count(item, len(marker.screenshots))
```

### 9.3 截图管理对话框

```python
class ScreenshotManagerDialog(pya.QDialog):
    def __init__(self, parent, marker):
        super().__init__(parent)
        self.marker = marker
        self.setWindowTitle(f"Screenshots - {marker.id}")
        self.setup_ui()
    
    def setup_ui(self):
        layout = pya.QVBoxLayout(self)
        
        # 截图列表
        self.list_widget = pya.QListWidget()
        self._populate_screenshots()
        layout.addWidget(self.list_widget)
        
        # 按钮
        btn_layout = pya.QHBoxLayout()
        
        btn_capture = pya.QPushButton("Capture")
        btn_capture.clicked(self.capture_screenshot)
        btn_layout.addWidget(btn_capture)
        
        btn_view = pya.QPushButton("View")
        btn_view.clicked(self.view_screenshot)
        btn_layout.addWidget(btn_view)
        
        btn_delete = pya.QPushButton("Delete")
        btn_delete.clicked(self.delete_screenshot)
        btn_layout.addWidget(btn_delete)
        
        layout.addLayout(btn_layout)
        
        # 关闭按钮
        btn_close = pya.QPushButton("Close")
        btn_close.clicked(self.accept)
        layout.addWidget(btn_close)
    
    def capture_screenshot(self):
        """从当前视图捕获截图"""
        view = pya.Application.instance().main_window().current_view()
        # 获取当前视图的图像
        # 保存到标记的截图列表
        pass
    
    def view_screenshot(self):
        """查看选中的截图"""
        pass
    
    def delete_screenshot(self):
        """删除选中的截图"""
        pass
```

## 10. 参考资源

- KLayout Python API 文档
- Qt for Python 文档
- KLayout 源码中的面板实现示例
- 其他 KLayout 插件的面板实现
