# 设置标尺颜色为纯白色

## 问题说明

KLayout 的 Annotation（标注/标尺）颜色是由视图设置控制的，不能在代码中直接设置。需要在 KLayout 的用户界面中手动配置。

## 解决方案

### 方法 1: 通过 KLayout 界面设置（推荐）

1. **打开 KLayout**

2. **进入设置菜单**
   - macOS: `KLayout → Preferences...`
   - Windows/Linux: `File → Setup`

3. **导航到显示设置**
   - 点击 `Display` 标签
   - 找到 `Rulers/Annotations` 或 `Annotation` 部分

4. **设置颜色为白色**
   - 点击颜色选择器
   - 设置 RGB 值为 `(255, 255, 255)`
   - 或者直接选择纯白色

5. **应用并保存**
   - 点击 `OK` 或 `Apply`
   - 设置会自动保存

### 方法 2: 编辑配置文件

KLayout 的配置文件位置：

**macOS:**
```
~/Library/Application Support/KLayout/klayoutrc
```

**Linux:**
```
~/.klayout/klayoutrc
```

**Windows:**
```
%APPDATA%\KLayout\klayoutrc
```

在配置文件中查找并修改：

```xml
<ruler-color>#ffffff</ruler-color>
```

或者：

```xml
<annotation-color>255,255,255</annotation-color>
```

### 方法 3: 使用 Python 脚本设置（实验性）

```python
import pya

# Get main window
main_window = pya.Application.instance().main_window()

# Get current view
view = main_window.current_view()

# Try to set ruler color (may not work in all versions)
try:
    # This is version-dependent
    view.set_config("ruler-color", "#ffffff")
except:
    print("Cannot set ruler color programmatically")
    print("Please set manually in KLayout preferences")
```

## 验证设置

1. 在 KLayout 中创建一个标尺（Ruler 工具）
2. 检查标尺是否显示为白色
3. 如果是白色，则设置成功

## 截图效果

设置为白色后，导出的 PDF 截图中：

- **十字定位线**：纯白色
- **尺寸标尺**：纯白色
- **比例尺**：纯白色

这样在深色背景上会更加清晰可见。

## 注意事项

1. **全局设置**
   - 这个设置是全局的，会影响所有 KLayout 项目
   - 如果需要不同颜色，需要手动切换

2. **截图前设置**
   - 建议在导出 PDF 前先设置好颜色
   - 设置后立即生效，无需重启

3. **颜色对比度**
   - 白色在深色背景上清晰
   - 如果背景是浅色，可能需要使用深色标尺

## 替代方案：使用图层颜色

如果无法修改标尺颜色，可以考虑：

1. 创建一个专门的标注图层
2. 设置该图层颜色为白色
3. 在该图层上绘制标注线条

但这种方法会修改 GDS 文件，不推荐用于生产环境。

## 常见问题

### Q: 设置后没有生效？

A: 尝试以下步骤：
1. 重启 KLayout
2. 检查是否有多个配置文件
3. 确认修改的是正确的配置文件

### Q: 不同项目需要不同颜色？

A: 可以创建多个 KLayout 配置文件，使用时切换：
```bash
klayout -c /path/to/config1.klayoutrc
klayout -c /path/to/config2.klayoutrc
```

### Q: 可以用其他颜色吗？

A: 可以！常用颜色：
- 纯白色：`#ffffff` 或 `(255, 255, 255)`
- 纯黑色：`#000000` 或 `(0, 0, 0)`
- 红色：`#ff0000` 或 `(255, 0, 0)`
- 绿色：`#00ff00` 或 `(0, 255, 0)`
- 蓝色：`#0000ff` 或 `(0, 255, 255)`
- 黄色：`#ffff00` 或 `(255, 255, 0)`

---

**推荐设置：纯白色 (255, 255, 255)** ✨

这样在大多数 GDS 布局（通常是深色背景）上都能清晰可见。
