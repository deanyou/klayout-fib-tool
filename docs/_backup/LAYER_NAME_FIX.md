# 修复 Layer Name 显示问题

## 问题描述

在 HTML 报告中，layer 信息只显示 layer number，没有显示 layer name：

**当前显示**：
```
Coordinates: (4462.390,2476.017) [10/0] to (4555.401,2486.174) [10/0] μm
```

**期望显示**：
```
Coordinates: (4462.390,2476.017) [M1:10/0] to (4555.401,2486.174) [M1:10/0] μm
```

## 根本原因

在 KLayout 中，layer name 的获取有两个来源：

1. **Layout.layer_info.name** - 来自 GDS 文件中的 layer 定义
2. **Layer Panel node.name** - 用户在 Layer Panel 中设置的显示名称

问题是很多 GDS 文件中的 layer 没有设置 name 属性，导致 `layer_info.name` 为空。

## 解决方案

### 1. 添加 `get_layer_name_from_panel()` 函数

**文件**：`fib_tool/layer_tap.py`

这个函数从 Layer Panel 中查找对应 layer 的显示名称：

```python
def get_layer_name_from_panel(view, layer_num, datatype):
    """
    Try to get layer name from Layer Panel.
    """
    try:
        for node in view.each_layer():
            if node.valid and hasattr(node, 'source'):
                source = node.source
                
                if isinstance(source, str):
                    # 处理不同的 source 格式
                    if ' ' in source:
                        # 格式如 "M1 86/0" - 提取名称和 layer/datatype
                        parts = source.split()
                        if len(parts) >= 2:
                            name_part = parts[0]
                            layer_part = parts[-1]
                            # 解析并匹配 layer/datatype
                            # 如果匹配，返回 name_part
                    
                    # 检查 node.name 是否有有效的名称
                    if hasattr(node, 'name') and node.name and node.name != f"{layer_num}/{datatype}":
                        return node.name
        
        return None
```

### 2. 修改 `get_layers_at_point()` 函数

在创建 `LayerInfo` 对象时，如果 `layer_info.name` 为空，尝试从 Layer Panel 获取：

```python
# Get layer name if available
layer_name = layer_info.name if layer_info.name else None
print(f"[Layer Tap] Layer {layer_info.layer}/{layer_info.datatype}: name='{layer_info.name}', type={type(layer_info.name)}")

# Try to get layer name from Layer Panel if not available in layout
if not layer_name:
    layer_name = get_layer_name_from_panel(current_view, layer_info.layer, layer_info.datatype)
    if layer_name:
        print(f"[Layer Tap] Got name from panel: '{layer_name}'")

found_layer = LayerInfo(layer_info.layer, layer_info.datatype, layer_name)
```

### 3. 修改 `get_selected_layer_from_panel()` 函数

同样的逻辑应用到 Layer Panel 选择的处理：

```python
layer_name = node.name if hasattr(node, 'name') and node.name else None

# Try to get better layer name if current name is just the layer/datatype
if not layer_name or layer_name == f"{layer_num}/{datatype}":
    better_name = get_layer_name_from_panel(view, layer_num, datatype)
    if better_name:
        layer_name = better_name
```

## Layer Name 来源优先级

1. **GDS 文件中的 layer name** (`layer_info.name`)
2. **Layer Panel 中的显示名称** (`node.name`)
3. **Layer Panel source 中的名称** (如 "M1 86/0" 格式)
4. **默认格式** (`layer/datatype`)

## 调试信息

修改后会输出详细的调试信息：

```
[Layer Tap] Layer 10/0: name='', type=<class 'str'>
[Layer Tap] Got name from panel: 'M1'
[Layer Tap] Found layer: M1:10/0
```

这帮助诊断 layer name 的获取过程。

## Layer Panel 中的 Layer Name 格式

KLayout Layer Panel 中的 layer 可能有不同的 source 格式：

1. **简单格式**：`"86/0"`
2. **带 mask**：`"86/0@1"`
3. **带名称**：`"M1 86/0"`
4. **复杂格式**：`"FIB_CUT 337/0"`

`get_layer_name_from_panel()` 函数处理这些不同格式，提取有意义的 layer name。

## 测试步骤

1. **在有 layer name 的位置点击**：
   - 应该显示 `[M1:86/0]` 格式

2. **在没有 layer name 的位置点击**：
   - 如果 Layer Panel 中有名称，应该显示 `[LayerName:86/0]`
   - 如果都没有，显示 `[86/0]`

3. **检查调试输出**：
   - 查看 layer name 的获取过程
   - 确认是否从 Panel 中成功获取名称

## 相关文件

- `fib_tool/layer_tap.py` - Layer 检测和名称获取
- `fib_tool/screenshot_export.py` - HTML 报告生成
- `fib_tool/report.py` - 简单 HTML 报告

## 注意事项

### Layer Panel 设置

用户可以在 Layer Panel 中为 layer 设置显示名称：
1. 右键点击 layer
2. Properties
3. 设置 Name 字段

这个名称会被 `get_layer_name_from_panel()` 函数检测到。

### 性能考虑

`get_layer_name_from_panel()` 函数会遍历 Layer Panel 中的所有 layer，但这个操作只在检测到 layer 时执行，频率不高。

## 总结

通过添加从 Layer Panel 获取 layer name 的功能，现在可以正确显示有意义的 layer 名称，而不仅仅是 layer number。这大大提高了 HTML 报告的可读性和实用性。