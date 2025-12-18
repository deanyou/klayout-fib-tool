# 在 KLayout 中加载 FIB Tool

## 方法 1: 使用安装脚本（推荐用于正式使用）

```bash
./install.sh
```

然后：
1. 完全关闭 KLayout
2. 重新打开 KLayout
3. 按 `Ctrl+Shift+F` 或从菜单 Tools → Toggle FIB Tool Panel

---

## 方法 2: 在 Macro Development 中加载（推荐用于开发）

### 步骤 1: 打开 Macro Development

在 KLayout 中按 `F5` 打开 Macro Development 窗口

### 步骤 2: 运行加载脚本

在控制台中输入以下命令（选择一个）：

#### 选项 A: 配置版（推荐，最可靠）

```python
exec(open('/Users/dean/Documents/git/klayout-fib-tool/load_fib_tool_configured.py', encoding='utf-8').read())
```

**优势**: 使用配置的路径，不受 KLayout 当前目录影响

#### 选项 B: 完整版（自动检测路径）

```python
exec(open('/Users/dean/Documents/git/klayout-fib-tool/load_fib_tool.py', encoding='utf-8').read())
```

**注意**: 如果路径检测失败，使用选项 A

#### 选项 C: 简化版（快速加载）

```python
exec(open('/Users/dean/Documents/git/klayout-fib-tool/load_fib_tool_simple.py', encoding='utf-8').read())
```

**重要**: 
- 替换路径为你的实际路径！
- 如果遇到路径问题，编辑 `load_fib_tool_configured.py` 中的 `FIB_TOOL_PATH`

### 步骤 3: 查看输出

完整版会显示：
```
======================================================================
FIB Tool - Development Loader
======================================================================

Script directory: /Users/dean/Documents/git/klayout-fib-tool
Python directory: /Users/dean/Documents/git/klayout-fib-tool/python

✓ Added to sys.path: ...
✓ fib_tool module found
✓ Active layout found: ...
✓ FIB Tool initialized successfully
✓ FIB layers verified/created (337, 338, 339)
✓ FIB Panel is now visible

======================================================================
✓ FIB Tool Loaded Successfully!
======================================================================
```

---

## 方法 3: 创建快捷宏（一键加载）

### 步骤 1: 创建宏文件

在 KLayout 中：
1. Tools → Macro Development (F5)
2. File → New Macro
3. 命名为 "Load FIB Tool"

### 步骤 2: 粘贴代码

```python
import sys
import os

# 修改为你的路径
FIB_TOOL_PATH = '/Users/dean/Documents/git/klayout-fib-tool/python'

if FIB_TOOL_PATH not in sys.path:
    sys.path.insert(0, FIB_TOOL_PATH)

from fib_tool import klayout_package
klayout_package.initialize_fib_tool()

from fib_tool.fib_panel import create_fib_panel, get_fib_panel
panel = get_fib_panel() or create_fib_panel()

print("✓ FIB Tool loaded!")
```

### 步骤 3: 保存并运行

1. File → Save
2. 点击 "Run" 按钮或按 F2

---

## 方法 4: 命令行快速测试

### 创建别名（可选）

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
alias load-fib='echo "exec(open(\"/Users/dean/Documents/git/klayout-fib-tool/load_fib_tool.py\", encoding=\"utf-8\").read())" | pbcopy && echo "Command copied to clipboard! Paste in KLayout Macro Development (F5)"'
```

然后在终端运行：
```bash
load-fib
```

命令会被复制到剪贴板，在 KLayout 中按 `Cmd+V` 粘贴即可。

---

## 常见问题

### Q1: "No module named 'fib_tool'"

**原因**: 路径不正确

**解决**:
```python
import os
print(os.path.exists('/Users/dean/Documents/git/klayout-fib-tool/python'))
# 应该输出 True

print(os.listdir('/Users/dean/Documents/git/klayout-fib-tool/python'))
# 应该看到 ['fib_tool']
```

### Q2: "FIB Tool already loaded"

**原因**: 已经加载过了

**解决**: 
- 重启 KLayout（推荐）
- 或继续使用已加载的版本

### Q3: "No GDS file is currently open"

**原因**: 没有打开 GDS 文件

**解决**: 
1. File → Open
2. 选择一个 .gds 文件
3. 重新运行加载脚本

### Q4: 修改代码后如何重新加载？

**方法 1**: 重启 KLayout（最可靠）
1. 完全关闭 KLayout
2. 重新打开
3. 运行加载脚本

**方法 2**: 使用 importlib.reload()（可能不完全）
```python
import importlib
import fib_tool
importlib.reload(fib_tool)
```

---

## 调试技巧

### 查看详细输出

在 Macro Development (F5) 中，所有 `print()` 输出都会显示在控制台。

### 测试特定功能

```python
# 测试配置
from fib_tool.config import LAYERS
print(LAYERS)

# 测试 layer 创建
from fib_tool.layer_manager import ensure_fib_layers
ensure_fib_layers()

# 测试 panel 创建
from fib_tool.fib_panel import create_fib_panel
panel = create_fib_panel()
```

### 检查导入

```python
import sys
print('fib_tool' in sys.modules)  # 应该是 True

import fib_tool
print(dir(fib_tool))  # 查看可用的模块
```

---

## 推荐工作流程

### 开发时

1. 修改代码
2. 在 Macro Development 中运行 `load_fib_tool.py`
3. 测试功能
4. 如需重新加载，重启 KLayout

### 测试时

1. 使用 `load_fib_tool.py`（有详细输出）
2. 查看控制台输出
3. 测试所有功能
4. 记录问题

### 发布时

1. 使用 `./install.sh` 安装
2. 完全重启 KLayout
3. 按 `Ctrl+Shift+F` 测试
4. 验证所有功能

---

## 快速参考

| 操作 | 命令 |
|------|------|
| 打开 Macro Development | `F5` |
| 加载 FIB Tool（完整） | `exec(open('load_fib_tool.py').read())` |
| 加载 FIB Tool（简化） | `exec(open('load_fib_tool_simple.py').read())` |
| 查看已加载模块 | `print(sys.modules.keys())` |
| 检查路径 | `print(sys.path)` |
| 重启 KLayout | `Cmd+Q` 然后重新打开 |

---

## 文件说明

| 文件 | 用途 | 何时使用 |
|------|------|---------|
| `load_fib_tool.py` | 完整加载器，详细输出 | 开发和调试 |
| `load_fib_tool_simple.py` | 简化加载器，快速加载 | 快速测试 |
| `install.sh` | 安装到 KLayout | 正式使用 |

---

**提示**: 
- 开发时使用 `load_fib_tool.py`
- 正式使用时用 `install.sh`
- 遇到问题查看控制台输出（F5）
