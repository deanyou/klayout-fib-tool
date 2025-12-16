# FIB Tool - SALT Package Installation Guide

## 安装方式对比

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **SALT Package Manager** | 生产使用 | 一键安装、自动更新 | 需要 GitHub Release |
| **手动复制** | 内部团队 | 简单直接 | 需要手动更新 |
| **exec() 加载** | 开发调试 | 快速重载 | 每次启动需重新加载 |

---

## 方式 1: SALT Package Manager（推荐）

### 前提条件
- KLayout 0.28 或更高版本
- 互联网连接

### 安装步骤

1. **打开 Salt Package Manager**
   - 菜单：`Tools` → `Manage Packages`
   - 或按快捷键（通常是 `Ctrl+Shift+M`）

2. **添加包源**
   - 点击 `Install New Packages` 标签
   - 点击 `Add Package Source` 按钮
   - 输入 GitHub Release URL：
     ```
     https://github.com/yourusername/klayout-fib-tool/releases/download/v1.0.0/klayout-fib-tool-1.0.0.zip
     ```
   - 点击 `OK`

3. **安装包**
   - 在包列表中找到 `fib-tool`
   - 点击 `Install` 按钮
   - 等待安装完成

4. **重启 KLayout**
   - 关闭并重新打开 KLayout
   - 工具栏应该出现三个按钮：`FIB Cut`, `FIB Connect`, `FIB Probe`

### 验证安装

打开 KLayout 后，检查：
- ✅ 工具栏有三个 FIB 按钮
- ✅ 控制台显示 "FIB Tool initialized successfully"
- ✅ 可以打开 FIB Panel（如果有）

### 更新包

1. 打开 Salt Package Manager
2. 切换到 `Installed Packages` 标签
3. 找到 `fib-tool`
4. 如果有新版本，点击 `Update` 按钮

### 卸载包

1. 打开 Salt Package Manager
2. 切换到 `Installed Packages` 标签
3. 找到 `fib-tool`
4. 点击 `Uninstall` 按钮
5. 重启 KLayout

---

## 方式 2: 手动复制（内部团队）

### 安装步骤

1. **下载代码**
   ```bash
   git clone https://github.com/yourusername/klayout-fib-tool.git
   cd klayout-fib-tool
   ```

2. **复制到 KLayout 目录**
   
   **macOS/Linux:**
   ```bash
   cp -r fib_tool ~/.klayout/salt/
   ```
   
   **Windows:**
   ```cmd
   xcopy /E /I fib_tool %USERPROFILE%\KLayout\salt\fib_tool
   ```

3. **重启 KLayout**

### 目录结构

安装后的目录结构：
```
~/.klayout/salt/fib_tool/
├── klayout_package.py      # SALT 入口点
├── __init__.py              # 包初始化
├── fib_plugin.py            # 主插件
├── fib_panel.py             # 面板 UI
├── markers.py               # 标记类
├── multipoint_markers.py    # 多点标记
├── config.py                # 配置
├── layer_manager.py         # 图层管理
├── screenshot_export.py     # 截图导出
├── marker_menu.py           # 右键菜单
├── storage.py               # 存储
├── report.py                # 报告生成
├── smart_counter.py         # 计数器
├── utils.py                 # 工具函数
└── file_dialog_helper.py    # 文件对话框
```

### 更新

重新复制 `fib_tool/` 目录即可：
```bash
cd klayout-fib-tool
git pull
cp -r fib_tool ~/.klayout/salt/
```

---

## 方式 3: exec() 加载（开发调试）

### 适用场景
- 开发新功能
- 调试问题
- 快速测试修改

### 使用步骤

1. **打开 KLayout**

2. **加载 GDS 文件**（可选，但建议先加载）

3. **打开 Macro Development 窗口**
   - 按 `F5` 键
   - 或菜单：`Macros` → `Macro Development`

4. **执行加载命令**
   
   在控制台中输入：
   ```python
   import sys
   sys.path.insert(0, '/path/to/klayout-fib-tool/fib_tool')
   exec(open('/path/to/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())
   ```
   
   **注意**：将 `/path/to/klayout-fib-tool` 替换为实际路径
   
   **macOS 示例**：
   ```python
   import sys
   sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/fib_tool')
   exec(open('/Users/dean/Documents/git/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())
   ```

5. **验证加载**
   - 控制台应显示 "FIB Tool Initialization"
   - 工具栏出现三个 FIB 按钮

### 重新加载

修改代码后，重新执行上述命令即可。

**注意**：由于双重初始化保护，plugin factories 只会创建一次。如果需要完全重新加载，请重启 KLayout。

### 创建快捷脚本

为了方便，可以创建一个宏：

1. 在 Macro Development 窗口中
2. 点击 `New Macro`
3. 命名为 `Load FIB Tool`
4. 粘贴加载命令
5. 保存

以后只需点击这个宏即可加载。

---

## 故障排除

### 问题 1: 工具栏没有 FIB 按钮

**可能原因**：
- 插件未正确加载
- KLayout 版本过低（需要 0.28+）

**解决方案**：
1. 检查控制台输出（`F5` 打开 Macro Development）
2. 查找错误信息
3. 确认 KLayout 版本：`Help` → `About KLayout`

### 问题 2: 提示 "Module not found"

**可能原因**：
- 路径不正确
- 文件缺失

**解决方案**：
1. 检查 `fib_tool/` 目录是否完整
2. 确认所有 `.py` 文件都存在
3. 检查文件权限

### 问题 3: 图层未自动创建

**可能原因**：
- 布局为只读
- 权限问题

**解决方案**：
1. 确保 GDS 文件可编辑
2. 查看控制台的图层创建日志
3. 手动创建图层 317/0, 318/0, 319/0

### 问题 4: 双重初始化（按钮重复）

**可能原因**：
- 同时使用了 SALT 和 exec() 加载

**解决方案**：
1. 选择一种加载方式
2. 如果需要两种方式，重启 KLayout 清除状态
3. 双重初始化保护应该防止这个问题

### 问题 5: Panel 未显示

**可能原因**：
- Panel 创建失败
- Qt 版本不兼容

**解决方案**：
1. 检查控制台的 Panel 创建日志
2. 工具栏按钮仍然可用（Panel 是可选的）
3. 尝试手动创建 Panel（如果有相关函数）

---

## 开发者注意事项

### 双重初始化保护

代码中使用了全局标志防止双重初始化：

```python
# fib_plugin.py
_FIB_PLUGIN_FACTORIES_CREATED = False

if not _FIB_PLUGIN_FACTORIES_CREATED:
    # 创建 plugin factories
    _FIB_PLUGIN_FACTORIES_CREATED = True
```

这确保即使多次加载，plugin factories 也只创建一次。

### SALT 入口点

`klayout_package.py` 是 SALT 的标准入口点：

```python
def init_fib_tool():
    """初始化 FIB Tool"""
    import fib_plugin  # 这会触发 plugin 注册

# 自动调用
if __name__ != "__main__":
    init_fib_tool()
```

### 路径处理

所有模块都使用相对导入或动态路径：

```python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
```

这确保无论安装在哪里都能正确导入。

---

## 版本历史

### v1.0.0 (2024-12-16)
- ✅ 初始 SALT 包发布
- ✅ 支持三种安装方式
- ✅ 双重初始化保护
- ✅ 自动图层创建
- ✅ 多点标记支持
- ✅ PDF 导出功能

---

## 相关文档

- [README.md](../README.md) - 项目概述
- [INSTALL.md](../INSTALL.md) - 详细安装说明
- [fib_tool/README.md](../fib_tool/README.md) - 使用说明
- [LAYER_AUTO_CREATION_TEST.md](LAYER_AUTO_CREATION_TEST.md) - 图层创建测试

---

## 支持

- GitHub Issues: https://github.com/yourusername/klayout-fib-tool/issues
- Email: your.email@example.com

---

**简单、实用、零废话。一键安装，立即使用。**
