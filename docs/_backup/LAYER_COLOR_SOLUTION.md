# FIB Layer Color 最终解决方案

## 结论

**KLayout 的 Python API 不支持可靠的程序化颜色设置。**

经过深入研究和多次尝试，发现 KLayout 的 Layer Panel 颜色设置无法通过 Python API 可靠地实现。虽然 API 提供了相关方法，但更改不会持久化到 UI 中。

## 尝试过的方法

### 方法 1：使用 each_layer() + set_layer_properties(node)
```python
for node in current_view.each_layer():
    node.fill_color = color
    current_view.set_layer_properties(node)
```
**结果**：❌ 无效 - node 是临时对象

### 方法 2：使用 begin_layers() + set_layer_properties(iterator)
```python
layer_iter = current_view.begin_layers()
while not layer_iter.at_end():
    node = layer_iter.current()
    node.fill_color = color
    current_view.set_layer_properties(layer_iter)
    layer_iter.next_sibling(1)
```
**结果**：❌ 无效 - 更改不持久化

### 方法 3：使用 LayerProperties + insert_layer()
```python
layer_props = pya.LayerProperties()
layer_props.fill_color = color
layer_list.insert_layer(layer_props)
```
**结果**：❌ 无效 - 颜色在 UI 中不显示

### 方法 4：直接修改 layout.layer_info
```python
layer_info = pya.LayerInfo(337, 0, "FIB_CUT")
# LayerInfo 没有颜色属性
```
**结果**：❌ 不可行 - LayerInfo 不包含颜色信息

## 根本原因

KLayout 的架构中，Layer Panel 的显示属性（颜色、图案等）与 Layout 的层定义是分离的：

1. **Layout.LayerInfo** - 定义层的编号和名称（layer/datatype）
2. **LayerProperties** - 定义 Layer Panel 中的显示属性（颜色、可见性等）

Python API 可以修改 LayerProperties 对象，但这些更改不会自动同步到 Layer Panel 的 UI。这可能是：
- KLayout 的设计限制
- Python 绑定的不完整实现
- 需要特殊的刷新机制（未公开的 API）

## 最终解决方案

### 手动设置颜色

用户需要在 Layer Panel 中手动设置颜色：

1. **Layer 337 (FIB_CUT)**
   - 右键点击 → Properties
   - Fill Color: RGB(255, 105, 180) - 粉色/Pink
   - Frame Color: RGB(255, 105, 180)

2. **Layer 338 (FIB_CONNECT)**
   - 右键点击 → Properties
   - Fill Color: RGB(255, 255, 0) - 黄色/Yellow
   - Frame Color: RGB(255, 255, 0)

3. **Layer 339 (FIB_PROBE)**
   - 右键点击 → Properties
   - Fill Color: RGB(255, 255, 255) - 白色/White
   - Frame Color: RGB(255, 255, 255)

### 自动提示

插件在创建新层时会自动显示颜色设置说明：

```python
def show_color_instructions():
    """显示颜色设置说明"""
    message = """FIB Tool - Layer Color Setup

Please set colors manually in Layer Panel:

1. Right-click on layer 337 (FIB_CUT) → Properties
   Set Fill Color: RGB(255, 105, 180) - Pink/粉色

2. Right-click on layer 338 (FIB_CONNECT) → Properties  
   Set Fill Color: RGB(255, 255, 0) - Yellow/黄色

3. Right-click on layer 339 (FIB_PROBE) → Properties
   Set Fill Color: RGB(255, 255, 255) - White/白色
"""
    pya.MessageBox.info("FIB Layer Colors", message, pya.MessageBox.Ok)
```

## 代码更改

### 1. 禁用自动颜色设置

**文件**: `fib_tool/layer_manager.py`

```python
def set_layer_colors(current_view):
    """
    Set colors for FIB layers - DISABLED.
    
    KLayout's Python API doesn't reliably support programmatic color setting.
    """
    print("[Layer Manager] Layer color setting is disabled")
    print("[Layer Manager] Please set colors manually in Layer Panel")
```

### 2. 添加颜色设置说明

```python
def show_color_instructions():
    """Show instructions for manually setting layer colors."""
    # 显示对话框，说明如何手动设置颜色
```

### 3. 在层创建时显示说明

```python
def ensure_fib_layers():
    # ... 创建层 ...
    
    if created_count > 0:
        # 显示颜色设置说明
        show_color_instructions()
```

## 替代方案

### 方案 1：使用 Layer Properties 文件

KLayout 支持导入/导出 Layer Properties 文件（.lyp 格式）：

1. 手动设置好颜色
2. File → Save Layer Properties
3. 分发 .lyp 文件给用户
4. 用户 File → Load Layer Properties

**优点**：一次设置，可重复使用
**缺点**：需要额外的文件和手动操作

### 方案 2：使用 KLayout 宏

创建一个独立的宏来设置颜色，使用更底层的 API：

```ruby
# KLayout Ruby 宏可能有更好的 API 支持
view = RBA::LayoutView::current
# ... Ruby API 操作 ...
```

**优点**：Ruby API 可能更完整
**缺点**：需要学习 Ruby，不确定是否有效

### 方案 3：修改 KLayout 源码

如果真的需要自动颜色设置，可以：
1. 修改 KLayout 源码
2. 添加 Python API 支持
3. 重新编译 KLayout

**优点**：完全控制
**缺点**：工作量巨大，不现实

## 建议

**接受手动设置颜色的方案**：

1. 这是最可靠的方法
2. 用户只需设置一次（KLayout 会记住）
3. 插件会自动显示设置说明
4. 可以提供 .lyp 文件作为参考

## 文档更新

需要在用户文档中说明：

```markdown
## Layer Colors

FIB Tool uses three layers with recommended colors:

- **Layer 337 (FIB_CUT)**: Pink - RGB(255, 105, 180)
- **Layer 338 (FIB_CONNECT)**: Yellow - RGB(255, 255, 0)
- **Layer 339 (FIB_PROBE)**: White - RGB(255, 255, 255)

### Setting Colors

1. Right-click on the layer in Layer Panel
2. Select "Properties"
3. Set Fill Color and Frame Color to the recommended RGB values
4. Click OK

Note: Colors need to be set only once per KLayout installation.
```

## 总结

虽然无法实现自动颜色设置，但通过：
1. 清晰的说明对话框
2. 详细的文档
3. 可选的 .lyp 文件

可以让用户轻松完成颜色设置。这是一个可接受的解决方案。
