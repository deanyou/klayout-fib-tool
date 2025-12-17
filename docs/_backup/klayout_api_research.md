# KLayout API Research for FIB Tool Development

## 概述

本文档总结了为 KLayout FIB 工具开发所需的关键 API 研究结果，涵盖了布局操作、图形创建、用户交互、截图生成和 GUI 开发等方面。

---

## 1. 核心模块和导入

### 1.1 在 KLayout 内部运行

```python
import pya

# 获取应用实例
app = pya.Application.instance()
mw = app.main_window()
view = mw.current_view()
```

### 1.2 独立 Python 模块（外部使用）

```python
import klayout.db as db    # 布局数据库
import klayout.lay as lay  # 布局视图（需要 GUI 支持）
```

**注意**：独立模块不支持 GUI 功能如 `Application`、`MainWindow` 等，这些仅在 KLayout 内部可用。

---

## 2. 布局和单元格操作

### 2.1 创建和加载布局

```python
import pya

# 创建新布局
layout = pya.Layout()
layout.dbu = 0.001  # 设置数据库单位为 1nm

# 读取 GDS 文件
layout.read("my_layout.gds")

# 写入 GDS 文件
layout.write("output.gds")

# 从 GUI 加载布局
mw = pya.MainWindow.instance()
mw.load_layout("path/to/file.gds", 1)  # 1 = 打开新标签页
```

### 2.2 单元格操作

```python
# 创建单元格
top_cell = layout.create_cell("TOP")

# 获取顶层单元格
top = layout.top_cell()

# 遍历所有顶层单元格
for index in layout.each_top_cell():
    cell = layout.cell(index)
    cell_name = cell.name

# 获取单元格边界框（微米单位）
bbox = top_cell.dbbox()
```

### 2.3 图层操作

```python
# 创建/获取图层
layer_index = layout.layer(1, 0)  # layer 1, datatype 0

# 获取图层信息
layer_info = layout.get_info(layer_index)  # 返回 LayerInfo 对象

# 插入新图层
layer_index = layout.insert_layer(pya.LayerInfo(200, 0))

# 添加缺失图层到视图
view.add_missing_layers()
```

---

## 3. 图形形状创建

### 3.1 基本形状

```python
# 获取当前视图和布局
view = pya.Application.instance().main_window().current_view()
cell_view = view.active_cellview()
layout = cell_view.layout()
cell = cell_view.cell

# 获取图层
layer = layout.layer(200, 0)

# Box（矩形）
box = pya.Box(0, 0, 1000, 2000)  # 整数坐标（dbu单位）
cell.shapes(layer).insert(box)

# DBox（浮点矩形，微米单位）
dbox = pya.DBox(0.0, 0.0, 1.0, 2.0)
cell.shapes(layer).insert(dbox)

# Polygon（多边形）
pts = [pya.Point(0, 0), pya.Point(1000, 0), pya.Point(500, 1000)]
polygon = pya.Polygon(pts)
cell.shapes(layer).insert(polygon)

# DPolygon（浮点多边形）
dpts = [pya.DPoint(0, 0), pya.DPoint(1.0, 0), pya.DPoint(0.5, 1.0)]
dpolygon = pya.DPolygon(dpts)
cell.shapes(layer).insert(dpolygon)
```

### 3.2 路径（Path）

```python
# 创建路径
point1 = pya.DPoint(0.0, 0.0)
point2 = pya.DPoint(15.0, 15.0)
point3 = pya.DPoint(30.0, 30.0)

# DPath: 点列表 + 宽度
path = pya.DPath([point1, point2, point3], 1.0)  # 宽度 1.0 微米
cell.shapes(layer).insert(path)
```

### 3.3 文本（Text）

```python
# 创建文本标签
text = pya.Text("CUT_0", pya.Trans(pya.Point(1000, 2000)))
cell.shapes(layer).insert(text)

# DText（浮点坐标）
dtext = pya.DText("PROBE_1", pya.DTrans(pya.DPoint(10.0, 20.0)))
cell.shapes(layer).insert(dtext)
```

---

## 4. 视图和显示控制

### 4.1 获取当前视图

```python
# 方法 1
view = pya.Application.instance().main_window().current_view()

# 方法 2（简写）
view = pya.LayoutView.current()

# 获取活动的 CellView
cell_view = view.active_cellview()
layout = cell_view.layout()
cell = cell_view.cell
```

### 4.2 缩放控制

```python
# 缩放到指定区域（微米坐标）
view.zoom_box(pya.DBox(0, 0, 100, 100))

# 缩放到全部
view.zoom_fit()

# 显示所有层次
view.max_hier()

# 显示所有单元格
view.show_all_cells()
```

### 4.3 图层可见性控制

```python
# 遍历所有图层并控制可见性
for layer_props in view.each_layer():
    if layer_props.source_layer == 1 and layer_props.source_datatype == 0:
        layer_props.visible = True
    else:
        layer_props.visible = False

# 使用迭代器方式
li = view.begin_layers()
while not li.at_end():
    lp = li.current()
    if lp.source_layer == target_layer:
        new_lp = lp.dup()
        new_lp.visible = True
        view.set_layer_properties(li, new_lp)
    li.next()
```

---

## 5. 截图和图像生成

### 5.1 基本截图

```python
view = pya.Application.instance().main_window().current_view()

# 保存当前视图截图
view.save_image("screenshot.png", 640, 480)  # 宽度 x 高度
```

### 5.2 指定区域截图

```python
# 获取布局边界框
ly = pya.CellView.active().layout()
bbox = ly.top_cell().dbbox()

# 计算保持宽高比的图像尺寸
w = 640
h = int(0.5 + w * bbox.height() / bbox.width())

# 保存指定区域的截图
view.save_image_with_options(
    'output.png',  # 文件路径
    w, h,          # 宽度、高度
    0, 0, 0,       # 线宽超采样、过采样、分辨率
    bbox,          # 要截图的区域（DBox）
    True           # 单色背景
)
```

### 5.3 获取 QImage 对象

```python
# 获取图像为 QImage（可进一步处理）
qimage = view.get_image(400, 400)

# 转换为 QPixmap
pixmap = pya.QPixmap().fromImage(qimage)
```

---

## 6. 标注和标尺（Annotation）

### 6.1 创建标尺/标注

```python
view = pya.Application.instance().main_window().current_view()

# 创建标注对象
ant = pya.Annotation()
ant.p1 = pya.DPoint(0, 0)       # 起点
ant.p2 = pya.DPoint(100, 50)    # 终点
ant.style = pya.Annotation.StyleRuler  # 标尺样式

# 插入标注
view.insert_annotation(ant)
```

### 6.2 标注样式

```python
# 可用样式
pya.Annotation.StyleRuler          # 标尺样式（带刻度）
pya.Annotation.StyleArrowEnd       # 末端箭头
pya.Annotation.StyleArrowStart     # 起始箭头
pya.Annotation.StyleArrowBoth      # 双向箭头
pya.Annotation.StyleLine           # 简单线段
```

### 6.3 清除标注

```python
# 清除所有标注
view.clear_annotations()
```

---

## 7. Marker（标记器）

### 7.1 创建视觉标记

```python
view = pya.Application.instance().main_window().current_view()

# 创建 Marker
marker = pya.Marker(view)
marker.line_style = 2  # 虚线样式
marker.vertex_size = 0  # 无顶点标记

# 设置标记形状
box = pya.DBox(10, 10, 50, 50)
marker.set(box)

# 销毁标记
marker._destroy()
```

---

## 8. 插件开发（Plugin）

### 8.1 Plugin 和 PluginFactory 基础结构

```python
import pya

class FIBPluginFactory(pya.PluginFactory):
    """插件工厂类 - 创建插件实例"""
    
    def __init__(self):
        super(FIBPluginFactory, self).__init__()
        pya.MainWindow.instance()  # 解决 bug 191
        # 注册插件：优先级, 标识符, 显示名称
        self.register(-1000, "fib_tool", "FIB Tool")
    
    def create_plugin(self, manager, root, view):
        return FIBPlugin(view)

# 保持单例实例
FIBPluginFactory.instance = FIBPluginFactory()


class FIBPlugin(pya.Plugin):
    """插件实现类 - 处理用户交互"""
    
    def __init__(self, view):
        super(FIBPlugin, self).__init__()
        self.view = view
        self.marker = None
    
    def activated(self):
        """插件激活时调用"""
        self.grab_mouse()  # 捕获鼠标事件
        pya.MainWindow.instance().message("FIB Tool activated", 10000)
    
    def deactivated(self):
        """插件停用时调用"""
        self.ungrab_mouse()
        pya.MainWindow.instance().message("", 0)
    
    def mouse_moved_event(self, p, buttons, prio):
        """鼠标移动事件
        
        Args:
            p: DPoint - 鼠标位置（微米坐标）
            buttons: int - 按钮状态
            prio: bool - 是否优先处理
        
        Returns:
            bool - True 表示消费事件
        """
        if prio:
            self.set_cursor(pya.Cursor.Cross)
        return False
    
    def mouse_click_event(self, p, buttons, prio):
        """鼠标点击事件
        
        Args:
            p: DPoint - 点击位置（微米坐标）
            buttons: int - 按钮状态
            prio: bool - 是否优先处理
        
        Returns:
            bool - True 表示消费事件
        """
        if prio:
            # 处理点击
            print(f"Clicked at: ({p.x}, {p.y})")
            return True
        return False
    
    def mouse_double_click_event(self, p, buttons, prio):
        """鼠标双击事件"""
        if prio:
            return True
        return False
    
    def mouse_button_pressed_event(self, p, buttons, prio):
        """鼠标按下事件"""
        return False
    
    def mouse_button_released_event(self, p, buttons, prio):
        """鼠标释放事件"""
        return False
```

### 8.2 隐藏/显示工具栏按钮

```python
# 隐藏工具栏按钮
pya.MainWindow.instance().menu().action("@toolbar.fib_tool").visible = False

# 触发工具
pya.MainWindow.instance().menu().action("@toolbar.fib_tool").trigger()

# 取消当前操作
pya.MainWindow.instance().cancel()
```

---

## 9. 菜单和 Action

### 9.1 添加菜单项

```python
import pya

def on_triggered():
    pya.MessageBox.info("FIB", "FIB Tool triggered!", pya.MessageBox.Ok)

# 创建 Action
action = pya.Action()
action.title = "FIB Tool"
action.on_triggered = on_triggered

# 添加到菜单
menu = pya.Application.instance().main_window().menu()
menu.insert_item("tools_menu.end", "fib_tool", action)

# 添加到工具栏
menu.insert_item("@toolbar.end", "fib_tool_btn", action)
```

### 9.2 触发内置 Action

```python
menu = pya.MainWindow.instance().menu()

# 触发对齐功能
menu.action("edit_menu.selection_menu.align").trigger()

# 切换到选择工具
menu.action("@toolbar.select").trigger()
```

---

## 10. Qt GUI 组件

### 10.1 创建对话框

```python
import pya

class FIBDialog(pya.QDialog):
    def __init__(self, parent=None):
        super(FIBDialog, self).__init__(pya.Application.instance().main_window())
        
        self.setWindowTitle("FIB Tool")
        self.setGeometry(100, 100, 400, 300)
        
        # 创建布局
        layout = pya.QVBoxLayout(self)
        
        # 添加按钮
        self.cut_btn = pya.QPushButton("Cut", self)
        self.connect_btn = pya.QPushButton("Connect", self)
        self.probe_btn = pya.QPushButton("Probe", self)
        
        layout.addWidget(self.cut_btn)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.probe_btn)
        
        # 连接信号
        self.cut_btn.clicked(self.on_cut)
        self.connect_btn.clicked(self.on_connect)
        self.probe_btn.clicked(self.on_probe)
        
        self.setLayout(layout)
    
    def on_cut(self):
        print("Cut mode activated")
    
    def on_connect(self):
        print("Connect mode activated")
    
    def on_probe(self):
        print("Probe mode activated")

# 显示对话框
dialog = FIBDialog()
dialog.show()
# 或者模态显示
# dialog.exec_()
```

### 10.2 常用 Qt 组件

```python
# 标签
label = pya.QLabel("Text", parent)

# 输入框
line_edit = pya.QLineEdit(parent)
line_edit.text  # 获取文本
line_edit.setText("value")  # 设置文本

# 按钮
button = pya.QPushButton("Click Me", parent)
button.clicked(callback_function)

# 复选框
checkbox = pya.QCheckBox("Option", parent)
checkbox.isChecked()

# 下拉框
combo = pya.QComboBox(parent)
combo.addItem("Option 1")
combo.addItem("Option 2")
combo.currentIndex

# 列表控件
list_widget = pya.QListWidget(parent)
list_widget.addItem("Item 1")

# 树形控件
tree = pya.QTreeWidget(parent)

# 分组框
group = pya.QGroupBox("Group Title", parent)

# 滚动区域
scroll = pya.QScrollArea()
scroll.setWidgetResizable(True)
```

### 10.3 布局管理

```python
# 垂直布局
vbox = pya.QVBoxLayout()
vbox.addWidget(widget1)
vbox.addWidget(widget2)
vbox.addStretch()

# 水平布局
hbox = pya.QHBoxLayout()
hbox.addWidget(widget1)
hbox.addWidget(widget2)

# 网格布局
grid = pya.QGridLayout()
grid.addWidget(widget, row, col)
grid.addWidget(widget, row, col, rowspan, colspan)
grid.setSpacing(10)

# 设置布局
widget.setLayout(layout)
```

### 10.4 消息框

```python
# 信息框
pya.MessageBox.info("Title", "Message", pya.MessageBox.Ok)

# 警告框
pya.MessageBox.warning("Title", "Warning message", pya.MessageBox.Ok)

# 确认框
result = pya.MessageBox.question("Title", "Are you sure?", 
                                  pya.MessageBox.Yes | pya.MessageBox.No)

# 输入对话框
text = pya.QInputDialog.getText(parent, "Title", "Enter text:", 
                                 pya.QLineEdit.Normal, "default")
```

### 10.5 文件对话框

```python
# 打开文件
filename = pya.QFileDialog.getOpenFileName(
    parent, "Open File", "", "GDS Files (*.gds);;All Files (*)")

# 保存文件
filename = pya.QFileDialog.getSaveFileName(
    parent, "Save File", "", "XML Files (*.xml);;All Files (*)")

# 选择目录
directory = pya.QFileDialog.getExistingDirectory(parent, "Select Directory")
```

---

## 11. 事务和撤销/重做

```python
view = pya.LayoutView.current()

# 开始事务（用于撤销/重做）
view.transaction("FIB Operation")

# ... 执行操作 ...

# 提交事务
view.commit()
```

---

## 12. 会话保存/恢复

```python
mw = pya.Application.instance().main_window()

# 保存会话
mw.save_session("path/to/session.lys")

# 恢复会话
mw.restore_session("path/to/session.lys")
```

---

## 13. FIB 工具实现建议

### 13.1 建议的代码架构

```
klayout_fib_tool/
├── __init__.py
├── fib_plugin.py          # Plugin 和 PluginFactory
├── fib_dialog.py          # Qt 对话框
├── fib_operations.py      # CUT/CONNECT/PROBE 操作
├── fib_markers.py         # 标记管理
├── fib_data.py            # 数据模型和序列化
├── fib_report.py          # HTML/PDF 报告生成
├── fib_export.py          # GDS 导出
└── config.yaml            # 配置文件
```

### 13.2 关键实现点

1. **标记存储**：使用专用 Layer（如 200-204）存储 FIB 标记形状
2. **交互模式**：通过 Plugin API 实现鼠标点击交互
3. **视觉反馈**：使用 Marker 类提供实时视觉反馈
4. **截图生成**：使用 `save_image_with_options` 生成三级视图
5. **数据持久化**：XML 格式保存 FIB 状态
6. **报告生成**：使用 Jinja2 模板生成 HTML，ReportLab 生成 PDF

### 13.3 Layer 分配建议

| Layer | Datatype | 用途 |
|-------|----------|------|
| 200 | 0 | CUT 标记 |
| 200 | 1 | CUT 方向箭头 |
| 200 | 10 | CUT 文本 |
| 201 | 0 | CONNECT 路径 |
| 201 | 1 | CONNECT 端点 |
| 201 | 10 | CONNECT 文本 |
| 202 | 0 | PROBE 标记 |
| 202 | 10 | PROBE 文本 |

---

## 14. 参考资源

- KLayout Python API 文档：https://www.klayout.de/doc/programming/python.html
- KLayout 类参考：https://www.klayout.de/doc/code/index.html
- KLayout 论坛：https://www.klayout.de/forum/
- KLayout GitHub：https://github.com/KLayout/klayout

---

## 文档版本

| 版本 | 日期 | 描述 |
|------|------|------|
| 1.0 | 2024-12-01 | 初始版本 |
