# KLayout FIB Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![KLayout](https://img.shields.io/badge/KLayout-%3E%3D0.28-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/status-MVP%20Complete-brightgreen.svg)

**简单、实用的 FIB 标注工具。遵循 Linus Torvalds 编程哲学：零废话，直接能用。**

> **开发阶段说明**: MVP 已完成，功能完整。正在准备发布到 KLayout SALT Mine。

## 项目状态

✅ **MVP 已完成** - 1028 行代码，8 个核心文件

## 快速开始

### 安装

**方式 1: SALT Package Manager（推荐）**
```
Tools → Manage Packages → Install from URL
输入 GitHub Release URL
```

**方式 2: 手动安装**

Linux/Mac:
```bash
cp -r fib_tool ~/.klayout/salt/
```

Windows:

> **说明**：Windows 版 KLayout 默认没有 `~/.klayout/salt/` 路径（因为 Windows 没有"家目录"符号 `~`），对应位置是 `%USERPROFILE%\KLayout\salt\`

1. 打开资源管理器，在地址栏输入以下路径并回车：
   ```
   %USERPROFILE%\KLayout\salt\
   ```
   如果 `salt` 子目录不存在，请手动新建一个。

2. 把解压后的 `fib_tool` 整个文件夹复制到该目录下，最终形成：
   ```
   %USERPROFILE%\KLayout\salt\fib_tool\
   ```

3. 重启 KLayout，菜单 **Tools → Salt** 里就能看到 `fib_tool`，或者直接出现在 **Tools** 菜单里。

**注意事项**：
- 不要把 `fib_tool` 再套一层文件夹，KLayout 只认 `salt\xxx\xxx.lym` 这种结构
- 如果装的是"便携版"（绿色 zip），则路径是 `<KLayout 解压目录>\salt\` 而不是用户目录
- 安装后重启 KLayout 生效

**方式 3: 开发调试**

Linux/Mac:
```python
# 在 KLayout Macro Development (F5) 中执行
import sys; sys.path.insert(0, '/path/to/klayout-fib-tool/fib_tool')
exec(open('/path/to/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())
```

Windows:
```python
# 在 KLayout Macro Development (F5) 中执行
import sys; sys.path.insert(0, r'C:\path\to\klayout-fib-tool\fib_tool')
exec(open(r'C:\path\to\klayout-fib-tool\fib_tool\fib_plugin.py', encoding='utf-8').read())
```

> **注意**：Windows 路径使用 `r'C:\...'` 格式（原始字符串），避免反斜杠转义问题

详细安装说明：[INSTALL.md](INSTALL.md) | [SALT 安装指南](docs/SALT_INSTALLATION.md)

### 使用

**启动方式：**
- **方式 1**：点击菜单 **Tools → FIB Tool**
- **方式 2**：按快捷键 `Ctrl+Shift+F`
- **方式 3**：点击工具栏按钮（Cut/Connect/Probe）

**基本流程：**
1. 打开 GDS 文件
2. 启动 FIB Tool（使用上述任一方式）
3. 点击 Cut/Connect/Probe 按钮
4. 在版图上点击创建标记
5. 保存为 XML 或生成 HTML 报告

**图层颜色设置（推荐）：**
- Layer 337 (FIB_CUT): 粉色 RGB(255, 105, 180)
- Layer 338 (FIB_CONNECT): 黄色 RGB(255, 255, 0)
- Layer 339 (FIB_PROBE): 白色 RGB(255, 255, 255)

设置方法：View → Layer Toolbox → 右键图层 → Properties → 设置颜色

详细说明：[图层颜色设置指南](docs/LAYER_COLOR_SETUP.md) | [使用说明](src/README.md)

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
