# KLayout FIB Tool - 安装指南

## 系统要求

- **KLayout** >= 0.28.0
- **Python** 3.8+ (KLayout 内置)
- **操作系统**: Windows / macOS / Linux

### 可选依赖（用于 PDF 导出）

- **wkhtmltopdf**（推荐）或 **weasyprint**
- 不安装也可以使用，会生成 HTML 报告
- 详见：[PDF 导出依赖说明](docs/PDF_EXPORT_DEPENDENCIES.md)

---

## 安装方式对比

| 方式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **SALT Package** | 生产使用 | 一键安装、自动更新 | 需要 GitHub Release |
| **手动复制** | 内部团队 | 简单直接 | 需要手动更新 |
| **exec() 加载** | 开发调试 | 快速重载 | 每次启动需重新加载 |

---

## 方法 1：SALT Package Manager（推荐）

### 安装步骤

1. **打开 Salt Package Manager**
   - 菜单：`Tools` → `Manage Packages`

2. **安装包**
   - 点击 `Install New Packages` 标签
   - 点击 `Add Package Source`
   - 输入 GitHub Release URL：
     ```
     https://github.com/yourusername/klayout-fib-tool/releases/download/v1.0.0/klayout-fib-tool-1.0.0.zip
     ```
   - 点击 `Install`

3. **重启 KLayout**

4. **验证安装**
   - 工具栏应出现：`FIB Cut`, `FIB Connect`, `FIB Probe` 三个按钮
   - 控制台显示 "FIB Tool initialized successfully"

详细说明：[SALT 安装指南](docs/SALT_INSTALLATION.md)

---

## 方法 2：手动安装

### 安装步骤

1. **下载代码**
   ```bash
   git clone https://github.com/yourusername/klayout-fib-tool.git
   cd klayout-fib-tool
   ```

2. **复制到 SALT 目录**

   **macOS/Linux:**
   ```bash
   cp -r fib_tool ~/.klayout/salt/
   ```

   **Windows:**
   ```cmd
   xcopy /E /I fib_tool %USERPROFILE%\KLayout\salt\fib_tool
   ```

3. **重启 KLayout**

4. **验证安装**
   - 工具栏应出现三个 FIB 按钮
   - 按 `F5` 打开控制台，查看初始化日志

### 目录结构

安装后：
```
~/.klayout/salt/fib_tool/
├── klayout_package.py      # SALT 入口点
├── fib_plugin.py            # 主插件
├── fib_panel.py             # 面板 UI
└── ...其他文件
```

---

## 方法 3：exec() 加载（开发调试）

### 适用场景
- 开发新功能
- 调试问题
- 快速测试修改

### 使用步骤

1. **打开 KLayout**

2. **按 F5 打开 Macro Development 窗口**

3. **执行加载命令**
   ```python
   import sys
   sys.path.insert(0, '/path/to/klayout-fib-tool/fib_tool')
   exec(open('/path/to/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())
   ```

4. **验证**
   - 控制台显示 "FIB Tool Initialization"
   - 工具栏出现三个按钮

### macOS 示例
```python
import sys
sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/fib_tool')
exec(open('/Users/dean/Documents/git/klayout-fib-tool/fib_tool/fib_plugin.py', encoding='utf-8').read())
```

### 重新加载

修改代码后，重新执行上述命令即可（部分功能可能需要重启 KLayout）。

## 验证安装

### 1. 运行测试脚本

在 KLayout 中：
1. 打开 **Tools → Macro Development**
2. 加载 `test_markers.py`
3. 点击 **Run**
4. 查看输出是否显示 "✓"

### 2. 手动测试

1. 打开一个 GDS 文件
2. 按 `Ctrl+Shift+F` 启动 FIB Tool
3. 点击 "Cut" 按钮
4. 在版图上点击两次
5. 检查 Layer 200 是否出现 X 符号

## 故障排查

### 问题：插件没有加载

**症状**：按 `Ctrl+Shift+F` 没反应，工具栏没有 FIB Tool

**解决方案**：
1. 检查文件路径是否正确
   ```bash
   ls ~/.klayout/pymacros/fib_tool/__init__.py
   ```
2. 查看 KLayout 错误日志
   - **Tools → Macro Development → Messages**
3. 确保所有 Python 文件都已复制
4. 重启 KLayout

### 问题：导入错误

**症状**：KLayout 启动时报错 "ImportError" 或 "ModuleNotFoundError"

**解决方案**：
1. 检查 `__init__.py` 中的导入语句
2. 确保所有文件在同一目录下
3. 检查文件权限（应该可读）

### 问题：点击没有反应

**症状**：点击 Cut/Connect/Probe 按钮后，在版图上点击没有创建标记

**解决方案**：
1. 确保已经打开了 GDS 文件
2. 查看状态栏是否显示当前模式
3. 检查 Layer 200-202 是否可见
4. 尝试缩放视图

### 问题：标记不显示

**症状**：创建标记后看不到

**解决方案**：
1. 打开 Layer Panel，确保 Layer 200-202 可见
2. 调整视图缩放级别
3. 检查标记是否在视图范围内

## 卸载

删除插件目录：

```bash
# macOS/Linux
rm -rf ~/.klayout/pymacros/fib_tool

# Windows
rmdir /S %APPDATA%\KLayout\pymacros\fib_tool
```

重启 KLayout。

## 下一步

安装完成后，查看：
- `src/README.md` - 使用说明
- `docs/mvp_checklist.md` - 功能清单
- `docs/mvp_plan.md` - 详细设计

## 获取帮助

如果遇到问题：
1. 查看 KLayout 的 Macro Development 窗口错误信息
2. 检查本文档的故障排查部分
3. 查看源代码注释
