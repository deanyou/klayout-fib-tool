# KLayout FIB Tool - 安装指南

## 系统要求

- **KLayout** >= 0.28.0
- **Python** 3.8+ (KLayout 内置)
- **操作系统**: Windows / macOS / Linux

## 安装步骤

### 方法 1：手动安装（推荐）

1. **找到 KLayout 插件目录**

   **macOS:**
   ```bash
   ~/.klayout/pymacros/
   ```

   **Linux:**
   ```bash
   ~/.klayout/pymacros/
   ```

   **Windows:**
   ```
   %APPDATA%\KLayout\pymacros\
   ```

2. **复制源代码**

   ```bash
   # macOS/Linux
   cd /Users/dean/Documents/git/klayout-fib-tool/klayout-fib-tool
   cp -r src ~/.klayout/pymacros/fib_tool
   
   # Windows (PowerShell)
   cd C:\path\to\klayout-fib-tool\klayout-fib-tool
   Copy-Item -Recurse src $env:APPDATA\KLayout\pymacros\fib_tool
   ```

3. **重启 KLayout**

4. **验证安装**
   - 打开 KLayout
   - 加载任意 GDS 文件
   - 按 `Ctrl+Shift+F` 或查看工具栏是否有 "FIB Tool" 按钮

### 方法 2：开发模式（用于调试）

如果你要修改代码，可以创建符号链接：

```bash
# macOS/Linux
ln -s /Users/dean/Documents/git/klayout-fib-tool/klayout-fib-tool/src ~/.klayout/pymacros/fib_tool

# Windows (需要管理员权限)
mklink /D %APPDATA%\KLayout\pymacros\fib_tool C:\path\to\src
```

这样修改代码后只需重启 KLayout 即可生效。

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
