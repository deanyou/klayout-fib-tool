# KLayout FIB Tool / KLayout FIB 标注工具

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

**Method 1: SALT Package Manager (Recommended) / 方式 1: SALT 包管理器（推荐）**
```
Tools → Manage Packages → Install from URL
Enter GitHub Release URL / 输入 GitHub Release URL
```

**Method 2: Manual Installation / 方式 2: 手动安装**

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

# Windows - Open File Explorer and navigate to / 打开文件资源管理器，导航到:
%APPDATA%\KLayout\salt\fib-tool\
# Then copy klayout-fib-tool/* to the fib-tool folder / 然后复制klayout-fib-tool/*到fib-tool文件夹
```

> **Windows Note / Windows 说明**: 
> - KLayout SALT directory is at / KLayout SALT 目录位于: `%APPDATA%\KLayout\salt\`
> - If using portable version / 如果使用便携版: `<KLayout folder>\salt\`
> - Restart KLayout after installation / 安装后重启 KLayout

**Method 3: Development Mode / 方式 3: 开发模式**

```python
# In KLayout Macro Development (F5) / 在 KLayout 宏开发窗口 (F5) 中:
FIB_TOOL_PATH = '/path/to/klayout-fib-tool'  # Set your path / 设置你的路径
exec(open(FIB_TOOL_PATH + '/load_fib_tool.py', encoding='utf-8').read())
```

> **Windows**: Use `r'C:\path\to\...'` format for paths / 路径使用 `r'C:\...'` 格式

For detailed instructions / 详细说明: [HOW_TO_LOAD.md](HOW_TO_LOAD.md) | [INSTALLATION.md](INSTALLATION.md)

## 📹 Video Tutorial / 视频教程

**Watch the complete usage demonstration / 观看完整使用演示:**

<div align="center">

### [🎬 Click to Download Video Tutorial (40MB)](docs/klayout-fib-tool.wmv)

**[📥 Direct Download / 直接下载](https://github.com/deanyou/klayout-fib-tool/raw/main/docs/klayout-fib-tool.wmv)**

*Video format: WMV | Size: 40MB | Duration: Complete workflow demonstration*
*视频格式: WMV | 大小: 40MB | 时长: 完整工作流程演示*

</div>

> **Note / 提示**:
> - Click the link above to download the video tutorial / 点击上方链接下载视频教程
> - The video demonstrates complete FIB marking workflow / 视频展示完整的 FIB 标注工作流程
> - Covers marker creation, editing, and export / 包括标注创建、编辑和导出

---

### Usage / 使用

**Launch Methods / 启动方式:**
- **Method 1 / 方式 1**: Menu **Tools → FIB Tool** / 菜单 **Tools → FIB Tool**
- **Method 2 / 方式 2**: Shortcut `Ctrl+Shift+F` / 快捷键 `Ctrl+Shift+F`
- **Method 3 / 方式 3**: Toolbar buttons (Cut/Connect/Probe) / 工具栏按钮

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

Run diagnostics in KLayout Macro Development (F5) / 在 KLayout 宏开发窗口运行诊断:

```python
# Diagnose panel activation / 诊断面板激活
exec(open('/path/to/diagnose_panel_activation.py', encoding='utf-8').read())

# Diagnose layer creation / 诊断图层创建
exec(open('/path/to/diagnose_layer_creation.py', encoding='utf-8').read())
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
