# KLayout FIB Tool / KLayout FIB 标注工具

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![KLayout](https://img.shields.io/badge/KLayout-%3E%3D0.28-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)
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
%APPDATA%\KLayout\salt\
# Then copy the fib-tool folder / 然后复制 fib-tool 文件夹
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

## 项目结构

```
klayout-fib-tool/
├── fib_tool/                    # 源代码（SALT 包）
│   ├── klayout_package.py       # SALT 入口点
│   ├── __init__.py              # 包初始化
│   ├── fib_plugin.py            # 主插件（Plugin Factory）
│   ├── fib_panel.py             # 面板 UI
│   ├── markers.py               # 基础标记类
│   ├── multipoint_markers.py    # 多点标记
│   ├── config.py                # 配置管理
│   ├── layer_manager.py         # 自动图层创建
│   ├── screenshot_export.py     # 截图导出
│   ├── marker_menu.py           # 右键菜单
│   ├── storage.py               # XML 序列化
│   ├── report.py                # HTML/PDF 报告
│   ├── smart_counter.py         # 智能计数器
│   ├── utils.py                 # 工具函数
│   └── file_dialog_helper.py    # 文件对话框
│
├── docs/                        # 文档
│   ├── SALT_INSTALLATION.md     # SALT 安装指南
│   ├── LAYER_AUTO_CREATION_TEST.md  # 图层测试
│   └── ...                      # 其他设计文档
│
├── salt.xml                     # SALT 包描述文件
├── test_layer_creation.py       # 图层创建测试脚本
├── INSTALL.md                   # 安装指南
└── README.md                    # 本文件
```

## 已实现功能

- **CUT 标注**：X 符号 + 方向箭头
- **CONNECT 标注**：连线 + 端点圆圈
- **PROBE 标注**：向下箭头符号
- **删除标记**：选中后删除
- **保存/加载**：XML 文件持久化
- **生成报告**：HTML 报告 + 截图

## 设计哲学

遵循 **Linus Torvalds** 的编程原则：

1. **数据结构优先**：好的数据结构让代码自然简洁
2. **消除特殊情况**：用多态，不用 if/else
3. **扁平优于嵌套**：早返回，最多 2 层缩进
4. **实用主义**：解决真实问题，不过度设计

详细哲学：[LinusTorvalds.md](LinusTorvalds.md)

## 代码质量

```
总代码行数：1028 行
平均每文件：114 行
最大文件：plugin.py (250 行)
缩进层次：最多 2 层
函数长度：最长 45 行
```

**符合 Linus 标准：简洁、直接、无废话**

## 文档

- **用户文档**
  - [安装指南](INSTALL.md)
  - [使用说明](src/README.md)
  - [验证清单](VERIFICATION.md)

- **开发文档**
  - [技术需求](docs/requirements.md)
  - [产品需求](docs/prd.md)
  - [MVP 规划](docs/mvp_plan.md)
  - [实现总结](MVP_SUMMARY.md)

- **参考文档**
  - [KLayout API 研究](docs/klayout_api_research.md)
  - [编程哲学](LinusTorvalds.md)

## 测试

```bash
# 在 KLayout Macro Development 窗口运行
python src/test_markers.py
```

手动测试清单：[VERIFICATION.md](VERIFICATION.md)

## 下一步

### v1.0 MVP（当前）
- 基本标注功能
- XML 保存/加载
- HTML 报告生成

### v1.1 增强版（规划中）
- 分组管理
- PDF 报告
- 三级视图截图
- 撤销/重做
- 快捷键支持

## 许可证

MIT License

## 致谢

遵循 Linus Torvalds 的编程哲学：
> "Talk is cheap. Show me the code."

---

**简单、实用、零废话。代码说话。** for klayout
