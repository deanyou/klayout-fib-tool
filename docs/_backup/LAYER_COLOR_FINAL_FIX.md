# FIB Layer Color 最终修复

## 突破！

用户提供了一个关键的代码示例，使用 **直接的 layer/datatype 属性匹配**，这个方法可能有效！

## 关键发现

### 之前的错误方法
```python
# ✗ 解析 source 字符串 - 不可靠
for n in view.each_layer():
    source = n.source  # 字符串，如 "337/0@1"
    # 解析字符串...
```

### 新的正确方法
```python
# ✓ 直接使用 layer 和 datatype 属性
for n in view.each_layer():
    if n.valid and n.layer == 337 and n.datatype == 0:
        n.fill_color = 0xFF69B4  # Pink
        n.frame_color = 0xFF69B4
        view.set_layer_properties(n)
        break
view.update_content()
```

## 关键区别

### 旧方法的问题
1. 依赖解析 `source` 字符串
2. `source` 格式可能变化：`"337/0"`, `"337/0@1"`, `"FIB_CUT 337/0"`
3. 解析逻辑复杂且容易出错

### 新方法的优势
1. **直接访问属性**：`n.layer` 和 `n.datatype` 是整数
2. **不需要解析**：直接比较数值
3. **更可靠**：不受字符串格式影响

## 实现

### 更新的 `set_layer_colors()` 函数

**文件**: `fib_tool/layer_manager.py`

```python
def set_layer_colors(current_view):
    """
    Set colors for FIB layers using direct layer/datatype matching.
    """
    try:
        print("[Layer Manager] Setting FIB layer colors (DIRECT METHOD)...")
        
        # Layer colors configuration
        layer_colors = {
            337: {'color': 0xFF69B4, 'name': 'FIB_CUT'},      # Pink
            338: {'color': 0xFFFF00, 'name': 'FIB_CONNECT'},  # Yellow
            339: {'color': 0xFFFFFF, 'name': 'FIB_PROBE'}     # White
        }
        
        # Ensure all layers are visible in the panel
        current_view.add_missing_layers()
        
        colors_set = 0
        
        # Iterate through all layers
        for target_layer, config in layer_colors.items():
            target_datatype = 0
            color = config['color']
            name = config['name']
            
            print(f"[Layer Manager] Looking for layer {target_layer}/{target_datatype}...")
            
            found = False
            for n in current_view.each_layer():
                # Direct layer/datatype matching - KEY IMPROVEMENT!
                if n.valid and hasattr(n, 'layer') and hasattr(n, 'datatype'):
                    if n.layer == target_layer and n.datatype == target_datatype:
                        found = True
                        print(f"[Layer Manager]   Found! Current: fill=0x{n.fill_color:06X}")
                        
                        # Set the colors
                        n.fill_color = color
                        n.frame_color = color
                        n.dither_pattern = 0
                        n.visible = True
                        
                        if not n.name or n.name == f"{target_layer}/{target_datatype}":
                            n.name = name
                        
                        # Apply the changes
                        current_view.set_layer_properties(n)
                        
                        print(f"[Layer Manager]   ✓ Set to 0x{color:06X} ({name})")
                        colors_set += 1
                        break
            
            if not found:
                print(f"[Layer Manager]   ✗ Not found in panel")
        
        # Force view update
        current_view.update_content()
        
        print(f"[Layer Manager] ✓ Complete: {colors_set}/3 layers updated")
        
        return colors_set == 3
        
    except Exception as e:
        print(f"[Layer Manager] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
```

## 关键改进点

### 1. 直接属性访问
```python
# 旧方法
source = n.source  # "337/0@1"
parts = source.split('/')
layer_num = int(parts[0])

# 新方法
layer_num = n.layer  # 直接获取整数
```

### 2. 简单的条件判断
```python
# 旧方法
if layer_num in layer_config and datatype == 0:
    # 复杂的字符串解析...

# 新方法
if n.layer == target_layer and n.datatype == target_datatype:
    # 直接匹配！
```

### 3. 更清晰的逻辑
- 遍历目标层（337, 338, 339）
- 对每个目标层，遍历 Layer Panel
- 找到匹配的层，设置颜色
- 立即 break，继续下一个目标层

## 测试步骤

1. **重新加载插件**
2. **打开 GDS 文件**
3. **检查控制台输出**：
   ```
   [Layer Manager] Setting FIB layer colors (DIRECT METHOD)...
   [Layer Manager] Looking for layer 337/0...
   [Layer Manager]   Found! Current: fill=0x......
   [Layer Manager]   ✓ Set to 0xFF69B4 (FIB_CUT)
   [Layer Manager] Looking for layer 338/0...
   [Layer Manager]   Found! Current: fill=0x......
   [Layer Manager]   ✓ Set to 0xFFFF00 (FIB_CONNECT)
   [Layer Manager] Looking for layer 339/0...
   [Layer Manager]   Found! Current: fill=0x......
   [Layer Manager]   ✓ Set to 0xFFFFFF (FIB_PROBE)
   [Layer Manager] ✓ Complete: 3/3 layers updated
   ```

4. **检查 Layer Panel**：
   - Layer 337 应该是粉色
   - Layer 338 应该是黄色
   - Layer 339 应该是白色

## 如果仍然失败

如果这个方法还是不行，可能的原因：

### 1. 属性不存在
```python
# 检查属性是否存在
if hasattr(n, 'layer') and hasattr(n, 'datatype'):
    print(f"Layer: {n.layer}, Datatype: {n.datatype}")
else:
    print("Node doesn't have layer/datatype attributes")
```

### 2. set_layer_properties() 不工作
```python
# 尝试不调用 set_layer_properties
n.fill_color = color
n.frame_color = color
# 不调用 set_layer_properties，看颜色是否改变
```

### 3. 需要不同的刷新方法
```python
# 尝试更强力的刷新
current_view.update_content()
current_view.clear_selection()
main_window.redraw()
```

## 为什么这个方法可能有效

1. **用户提供的代码示例**：说明这个方法在某些情况下是有效的
2. **直接属性访问**：比字符串解析更可靠
3. **简单明了**：减少了出错的可能性

## 下一步

1. **测试新实现**
2. **查看调试输出**
3. **检查 Layer Panel**
4. **如果有效**：庆祝！🎉
5. **如果无效**：分析调试输出，找出问题所在

## 备注

- 颜色值已修复：`0xFFFFFF`（白色，6个F）
- 重新启用了 `set_layer_colors()` 调用
- 简化了颜色设置说明对话框
- 保留了详细的调试输出

## 信心指数

**80%** - 这个方法基于用户提供的工作示例，使用直接属性访问而不是字符串解析，应该更可靠。如果 KLayout 的 Python API 支持这些属性，这个方法应该能工作。
