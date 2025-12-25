# KLayout FIB Tool / KLayout FIB 标注工具

<div align="center">
  <img src="docs/images/fib_icon.jpg" alt="FIB Tool Icon" width="200"/>
</div>

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![KLayout](https://img.shields.io/badge/KLayout-%3E%3D0.28-green.svg)
![Version](https://img.shields.io/badge/version-1.0.1-orange.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)

**A simple, practical FIB marking tool for IC layout. Following Linus Torvalds' philosophy: No BS, just works.**

**简单、实用的 IC 版图 FIB 标注工具。遵循 Linus Torvalds 编程哲学：零废话，直接能用。**

---

> **Development Status / 开发状态**: Production ready. Fully functional with comprehensive documentation.
> 
> 生产就绪。功能完整，文档齐全。

## Project Status / 项目状态

✅ **Production Ready / 生产就绪**
- Core functionality complete / 核心功能完整
- Comprehensive documentation / 文档齐全
- Cross-platform support (Windows/macOS/Linux) / 跨平台支持
- SALT package ready / SALT 包就绪

## Quick Start / 快速开始

### Installation / 安装

**Method 1: Manual Installation / 方式 1: 手动安装**

**Linux/Mac:**
```bash
./install.sh
```

**Windows:**
```cmd
install.bat
```

Or manually / 或手动安装:
```bash
# Linux/Mac
cp -r python/fib_tool ~/.klayout/salt/fib-tool/python/
cp -r pymacros/*.lym ~/.klayout/salt/fib-tool/pymacros/

# 建议！Windows - Open File Explorer and navigate to / 打开文件资源管理器，导航到:
C:\Users\<Your Username>\KLayout\salt\fib-tool\
# Then copy klayout-fib-tool/* to the fib-tool folder / 然后复制klayout-fib-tool/*下所有文件 到fib-tool文件夹
```

> **Windows Note / Windows 说明**:
> - KLayout SALT directory is at / KLayout SALT 目录位于: `%APPDATA%\KLayout\salt\`
> - If using portable version / 如果使用便携版: `<KLayout folder>\salt\`
> - Restart KLayout after installation / 安装后重启 KLayout

**Method 2: SALT Package Manager (Recommended) / 方式 2: SALT 包管理器（推荐）**
```
Tools → Manage Packages → Install from URL
Enter GitHub Release URL / 输入 GitHub Release URL
```

**Method 3: Development Mode / 方式 3: 开发模式**

```python
# In KLayout Macro Development (F5) / 在 KLayout 宏开发窗口 (F5) 中:
FIB_TOOL_PATH = '/path/to/klayout-fib-tool'  # Set your path / 设置你的路径
exec(open(FIB_TOOL_PATH + '/load_fib_tool.py', encoding='utf-8').read())
```

> **Windows**: Use `r'C:\path\to\...'` format for paths / 路径使用 `r'C:\...'` 格式

For detailed instructions / 详细说明: [HOW_TO_LOAD.md](HOW_TO_LOAD.md) | [INSTALLATION.md](INSTALLATION.md)

### Usage / 使用

**Launch Methods / 启动方式:**
- **Method 1 / 方式 1**: Menu **Tools → FIB Tool** / 菜单 **Tools → FIB Tool**
- **Method 2 / 方式 2**: Shortcut `Ctrl+Shift+F` / 快捷键 `Ctrl+Shift+F`
- **Method 3 / 方式 3**: Toolbar buttons (Cut/Connect/Probe) / 工具栏按钮

**Interface Overview / 界面概览:**
- **Main Panel**: Dockable panel with marker tree and mode controls
- **Toolbar**: Quick access buttons for Cut/Connect/Probe modes
- **Status Bar**: Real-time feedback on current mode and operations
- **Layer Toolbox**: Displays FIB layers (337, 338, 339) with recommended colors

**Basic Workflow / 基本流程:**
1. Open a GDS file / 打开 GDS 文件
2. Launch FIB Tool (use any method above) / 启动 FIB Tool（使用上述任一方式）
3. Click Cut/Connect/Probe buttons / 点击 Cut/Connect/Probe 按钮
4. Click on layout to create markers / 在版图上点击创建标记
5. Save as XML or generate HTML report / 保存为 XML 或生成 HTML 报告

**Layer Colors (Recommended) / 图层颜色（推荐）:**
- Layer 337 (FIB_CUT): Pink / 粉色 - RGB(255, 105, 180)
- Layer 338 (FIB_CONNECT): Yellow / 黄色 - RGB(255, 255, 0)
- Layer 339 (FIB_PROBE): White / 白色 - RGB(255, 255, 255)

Setup / 设置方法: View → Layer Toolbox → Right-click layer → Properties → Set color
查看 → 图层工具箱 → 右键图层 → 属性 → 设置颜色

For details / 详细说明: [Layer Color Setup / 图层颜色设置](docs/LAYER_COLOR_SETUP.md)

## Detailed Usage Guide / 详细使用指南

### Marker Types and Usage / 标记类型与使用

#### 1. CUT Marker / CUT 标记

**Purpose**: Create cutting paths with direction indicators
**Layer**: 337
**Visual**: X symbol with direction arrow

**Standard Mode (2 Points) / 标准模式（2点）:**
1. Click the **Cut** button (turns green when active)
2. **First click**: Set center position on the layout
3. **Second click**: Set direction of the cut
4. Marker is created with automatic ID (e.g., CUT_0)

**Multi-Point Mode / 多点模式:**
1. Click the dropdown next to **Cut** button
2. Select **Multi Points** from the dropdown
3. Click the **Cut** button to activate multi-point mode
4. **Left-click** to add multiple vertices
5. **Right-click** to finish (standard CAD workflow)
6. Minimum 2 points required
7. Result: CUT marker with continuous path through all points

#### 2. CONNECT Marker / CONNECT 标记

**Purpose**: Create connection paths between points
**Layer**: 338
**Visual**: Line with endpoint circles

**Standard Mode (2 Points) / 标准模式（2点）:**
1. Click the **Connect** button (turns green when active)
2. **First click**: Set start point on the layout
3. **Second click**: Set end point
4. Marker is created with automatic ID (e.g., CONNECT_0)

**Multi-Point Mode / 多点模式:**
1. Click the dropdown next to **Connect** button
2. Select **Multi Points** from the dropdown
3. Click the **Connect** button to activate multi-point mode
4. **Left-click** to add multiple junction points
5. **Right-click** to finish
6. Minimum 2 points required
7. Result: CONNECT marker with path through all points
8. Visual: Large circles at endpoints, small circles at junctions

#### 3. PROBE Marker / PROBE 标记

**Purpose**: Mark probe test points
**Layer**: 339
**Visual**: Downward arrow

**Standard Mode / 标准模式:**
1. Click the **Probe** button (turns green when active)
2. **Single click**: Set probe position on the layout
3. Marker is created with automatic ID (e.g., PROBE_0)

### Context Menu Operations / 右键菜单操作

**Right-click on any marker** to access the context menu:
1. **Zoom to Fit**: Center and zoom to the marker
2. **Copy Coordinates**: Copy marker coordinates to clipboard
3. **Add Notes**: Add descriptive notes to the marker
4. **Rename Marker**: Customize marker ID
5. **Delete Marker**: Remove the marker

### Adding Notes / 添加备注

**Step-by-step**: 
1. Right-click on any marker
2. Select **Add Notes** from the context menu
3. Enter descriptive text in the dialog box
4. Click **OK** to save
5. Notes are automatically saved with the marker

**Example notes**: 
- "Beam 30kV, 10pA, Dwell 1us"
- "Device A - Metal layer 3"
- "GND test point"

### Data Management / 数据管理

#### Saving and Loading / 保存与加载

**Save Project / 保存项目:**
1. Click the **Save** button in the FIB Panel
2. Select XML file location
3. All markers, notes, and settings are saved

**Load Project / 加载项目:**
1. Click the **Load** button in the FIB Panel
2. Select XML file
3. All markers are restored to their original positions

#### Exporting Reports / 导出报告

**Generate HTML Report / 生成 HTML 报告:**
1. Click the **Export HTML** button in the FIB Panel
2. Select output directory
3. The tool generates:
   - HTML report with marker details
   - Screenshots of each marker
   - Notes and coordinates for each marker
   - Layer information
   - Project metadata

**Report Features / 报告特点:**
- Interactive marker list
- Zoomable screenshots
- Searchable content
- Responsive design for different screen sizes

### Advanced Features / 高级功能

#### Auto Layer Creation / 自动图层创建
- Tool automatically creates FIB layers (337, 338, 339) if they don't exist
- Layer names: FIB_CUT, FIB_CONNECT, FIB_PROBE
- No manual layer setup required

#### Smart Numbering / 智能编号
- Automatic incrementing marker IDs
- Customizable prefixes (CUT_, CONNECT_, PROBE_)
- Maintains sequential numbering after deletions

#### Layer Detection / 图层检测
- Automatically detects layers at click positions
- Displays layer information in status bar
- Useful for identifying target layers

#### Coordinate Display / 坐标显示
- Real-time coordinate feedback during marker creation
- Coordinate texts show at each click position
- Formatted as (X, Y) in microns

### Troubleshooting / 故障排除

**Common Issues and Solutions / 常见问题与解决方案:**

1. **Buttons not appearing / 按钮不显示**
   - Ensure GDS file is open first
   - Check console for error messages
   - Restart KLayout

2. **Markers not visible / 标记不可见**
   - Check Layer Toolbox: Ensure FIB layers are visible
   - Use "Zoom to Fit" on a marker
   - Verify layer colors are set correctly

3. **Multi-point mode not working / 多点模式不工作**
   - Ensure minimum 2 points are added
   - Right-click to finish (not double-click)
   - Check mode indicator in status bar

4. **Cannot save/load project / 无法保存/加载项目**
   - Check file permissions
   - Ensure XML file is not corrupted
   - Verify file path is valid

5. **HTML export fails / HTML 导出失败**
   - Check screenshot dependencies
   - Ensure output directory exists
   - Check console for error messages

For more troubleshooting / 更多故障排除: [GitHub Issues](https://github.com/yourusername/klayout-fib-tool/issues)

## Tips and Best Practices / 提示与最佳实践

### Workflow Efficiency / 工作流程效率

1. **Use keyboard shortcuts**: `Ctrl+Shift+F` to toggle the FIB Panel
2. **Double-click markers**: Quickly zoom to any marker
3. **Right-click to cancel**: Exit mode without creating a marker
4. **Batch operations**: Create multiple markers in sequence
5. **Regular saves**: Save your project frequently to avoid data loss

### Precision and Accuracy / 精度与准确性

1. **Zoom in**: For precise point placement
2. **Use grid**: Enable KLayout's grid for alignment
3. **Check coordinates**: Verify marker positions in the panel
4. **Layer visibility**: Ensure only relevant layers are visible
5. **Coordinate text**: Use visible coordinate texts for verification

### Organization / 组织管理

1. **Descriptive notes**: Add clear notes to each marker
2. **Logical naming**: Customize marker IDs when needed
3. **Group markers**: Organize markers by function or area
4. **Consistent colors**: Follow recommended layer color scheme
5. **Version control**: Save different project versions with meaningful names

### Performance / 性能

1. **Limit marker count**: Keep under 1000 markers for optimal performance
2. **Close unused windows**: Free up memory
3. **Regular restarts**: Refresh KLayout occasionally during long sessions
4. **Optimize GDS**: Use simplified GDS files for FIB marking
5. **Update KLayout**: Ensure you're using KLayout 0.28 or later

## Example Workflow / 示例工作流程

### Typical FIB Marking Session / 典型 FIB 标注流程

1. **Preparation / 准备**
   - Open GDS file
   - Launch FIB Tool via menu or shortcut
   - Set recommended layer colors

2. **CUT Markers / CUT 标记**
   - Select **Cut** mode
   - Create 5-10 CUT markers with direction indicators
   - Add notes for beam settings

3. **CONNECT Markers / CONNECT 标记**
   - Select **Connect** mode
   - Create connection paths between test points
   - Use multi-point mode for complex paths

4. **PROBE Markers / PROBE 标记**
   - Select **Probe** mode
   - Mark probe test locations
   - Add device identification notes

5. **Verification / 验证**
   - Review all markers in the panel
   - Check coordinates and notes
   - Zoom to each marker for visual inspection

6. **Documentation / 文档**
   - Save project as XML
   - Generate HTML report with screenshots
   - Share report with team members

7. **Export / 导出**
   - Ensure all layers are visible
   - Export final GDS with FIB markers
   - Prepare for FIB machine input

## Visual Reference / 视觉参考

### Toolbar and Panel / 工具栏与面板

![FIB Tool Interface](docs/images/screenshot.png)

*Main interface showing toolbar, panel, and markers in a GDS file*

### Marker Types / 标记类型

| Marker Type | Layer | Color | Visual Representation |
|-------------|-------|-------|----------------------|
| CUT         | 337   | Pink  | X symbol + direction arrow |
| CONNECT     | 338   | Yellow | Line with endpoint circles |
| PROBE       | 339   | White | Downward arrow |

### Layer Setup / 图层设置

![Layer Toolbox](docs/images/refesh_fib_layers.png)

*Recommended layer configuration in KLayout Layer Toolbox*

## Project Structure / 项目结构

```
klayout-fib-tool/
├── python/fib_tool/             # Source code (SALT package) / 源代码（SALT 包）
│   ├── klayout_package.py       # SALT entry point / SALT 入口点
│   ├── __init__.py              # Package initialization / 包初始化
│   ├── fib_plugin.py            # Main plugin (Plugin Factory) / 主插件
│   ├── fib_panel.py             # Panel UI / 面板界面
│   ├── markers.py               # Basic marker classes / 基础标记类
│   ├── multipoint_markers.py    # Multi-point markers / 多点标记
│   ├── config.py                # Configuration / 配置管理
│   ├── layer_manager.py         # Auto layer creation / 自动图层创建
│   ├── screenshot_export.py     # Screenshot export / 截图导出
│   ├── marker_menu.py           # Context menu / 右键菜单
│   └── layer_tap.py             # Layer detection / 图层检测
│
├── pymacros/                    # KLayout macros / KLayout 宏
│   ├── fib_menu.lym             # Tools menu entry / 工具菜单入口
│   └── fib_tool.lym             # Plugin registration / 插件注册
│
├── docs/                        # Documentation / 文档
│   ├── LAYER_COLOR_SETUP.md     # Layer color guide / 图层颜色指南
│   └── ...                      # Other docs / 其他文档
│
├── install.sh                   # Installation script (Unix) / 安装脚本
├── install.bat                  # Installation script (Windows) / 安装脚本
├── uninstall.sh                 # Uninstall script (Unix) / 卸载脚本
├── uninstall.bat                # Uninstall script (Windows) / 卸载脚本
├── load_fib_tool.py             # Development loader / 开发加载器
├── grain.xml                    # SALT package descriptor / SALT 包描述
└── README.md                    # This file / 本文件
```

## Features / 功能特性

### Core Features / 核心功能
- **CUT Markers / CUT 标注**: X symbol + direction arrow / X 符号 + 方向箭头
- **CONNECT Markers / CONNECT 标注**: Line + endpoint circles / 连线 + 端点圆圈
- **PROBE Markers / PROBE 标注**: Downward arrow / 向下箭头
- **Multi-point Support / 多点支持**: Create complex paths / 创建复杂路径
- **Layer Detection / 图层检测**: Auto-detect layers at click position / 自动检测点击位置的图层

### UI Features / 界面功能
- **Panel Interface / 面板界面**: Dockable panel with marker tree / 可停靠面板，带标记树
- **Context Menu / 右键菜单**: Right-click operations / 右键操作
- **Toolbar Buttons / 工具栏按钮**: Quick access to marker modes / 快速访问标记模式
- **Keyboard Shortcuts / 键盘快捷键**: `Ctrl+Shift+F` to toggle panel / 切换面板

### Data Management / 数据管理
- **Save/Load / 保存/加载**: XML file persistence / XML 文件持久化
- **Export Reports / 导出报告**: HTML reports with screenshots / HTML 报告带截图
- **Smart Numbering / 智能编号**: Auto-increment marker IDs / 自动递增标记 ID
- **Notes / 备注**: Add notes to each marker / 为每个标记添加备注

### Advanced Features / 高级功能
- **Auto Layer Creation / 自动图层创建**: Creates FIB layers (337, 338, 339) / 自动创建 FIB 图层
- **Zoom to Marker / 缩放到标记**: Double-click to zoom / 双击缩放
- **Coordinate Display / 坐标显示**: Shows marker coordinates / 显示标记坐标
- **Cross-platform / 跨平台**: Windows, macOS, Linux support / 支持 Windows、macOS、Linux

## Design Philosophy / 设计哲学

Following **Linus Torvalds**' programming principles / 遵循 **Linus Torvalds** 的编程原则:

1. **Data structures first / 数据结构优先**: Good data structures make code naturally simple / 好的数据结构让代码自然简洁
2. **Eliminate special cases / 消除特殊情况**: Use polymorphism, not if/else / 用多态，不用 if/else
3. **Flat is better than nested / 扁平优于嵌套**: Early returns, max 2 levels of indentation / 早返回，最多 2 层缩进
4. **Pragmatism / 实用主义**: Solve real problems, don't over-engineer / 解决真实问题，不过度设计

For details / 详细哲学: [LinusTorvalds.md](LinusTorvalds.md)

## Code Quality / 代码质量

**Clean, simple, no BS / 简洁、直接、无废话**

- Modular architecture / 模块化架构
- Comprehensive error handling / 完善的错误处理
- Cross-platform compatibility / 跨平台兼容
- Well-documented / 文档完善

## Documentation / 文档

### User Documentation / 用户文档
- [Installation Guide / 安装指南](INSTALLATION.md)
- [How to Load / 加载方法](HOW_TO_LOAD.md)
- [Layer Color Setup / 图层颜色设置](docs/LAYER_COLOR_SETUP.md)

### Developer Documentation / 开发文档
- [Context Transfer Fixes / 上下文转移修复](CONTEXT_TRANSFER_FIXES.md)
- [Fix Circular Import / 修复循环导入](FIX_CIRCULAR_IMPORT.md)
- [Fix Unicode Encoding / 修复 Unicode 编码](FIX_UNICODE_ENCODING.md)
- [Programming Philosophy / 编程哲学](LinusTorvalds.md)

### Troubleshooting / 故障排除
- [Panel Button Error / 面板按钮错误](FIX_PANEL_BUTTON_ERROR.md)
- [Tools Menu Feature / 工具菜单功能](TOOLS_MENU_FEATURE.md)
- [Which Loader to Use / 使用哪个加载器](WHICH_LOADER_TO_USE.md)

## Testing / 测试

Run in KLayout Macro Development (F5) / 在 KLayout 宏开发窗口运行:

```python
# Load FIB Tool / 加载 FIB Tool
FIB_TOOL_PATH = '/home/meow/git'  # Set your path / 设置你的路径
exec(open(FIB_TOOL_PATH + '/klayout-fib-tool/load_fib_tool.py', encoding='utf-8').read())
```

## Roadmap / 路线图

### v1.0 (Current / 当前)
- ✅ Core marking functionality / 核心标注功能
- ✅ XML save/load / XML 保存/加载
- ✅ HTML report generation / HTML 报告生成
- ✅ Multi-point markers / 多点标记
- ✅ Layer detection / 图层检测
- ✅ Cross-platform support / 跨平台支持

### v1.1 (Planned / 计划中)
- Group management / 分组管理
- PDF export / PDF 导出
- Undo/Redo / 撤销/重做
- More keyboard shortcuts / 更多快捷键

## License / 许可证

MIT License

## Acknowledgments / 致谢

Following Linus Torvalds' programming philosophy / 遵循 Linus Torvalds 的编程哲学:
> "Talk is cheap. Show me the code."
> 
> "空谈无益，代码说话。"

## Contributing / 贡献

Contributions are welcome! Please feel free to submit issues and pull requests.

欢迎贡献！请随时提交问题和拉取请求。

## Support / 支持

- Report bugs / 报告错误: [GitHub Issues](https://github.com/yourusername/klayout-fib-tool/issues)
- Documentation / 文档: See `docs/` folder / 查看 `docs/` 文件夹
- Contact / 联系: youliuyi61@qq.com [Your contact info / 你的联系方式]

---

**Simple, practical, no BS. Code speaks. / 简单、实用、零废话。代码说话。**

Made for KLayout / 为 KLayout 打造
