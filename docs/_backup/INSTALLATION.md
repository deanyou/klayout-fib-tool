# FIB Tool - 安装指南

## 前提条件

在安装前，确保项目已迁移到 SALT 包结构：

```bash
# 检查是否有正确的目录结构
ls python/fib_tool/  # 应该看到 Python 文件
ls pymacros/         # 应该看到 .lym 文件
```

如果没有这些目录，先运行：

```bash
./refactor.sh
```

## 安装方法

### macOS / Linux

#### 方式 1: 使用安装脚本（推荐）

```bash
# 使脚本可执行
chmod +x install.sh

# 运行安装
./install.sh
```

安装时会提示选择：
- **选项 1**: Symbolic link（符号链接）- 推荐用于开发
- **选项 2**: Copy files（复制文件）- 推荐用于正式使用

#### 方式 2: 手动安装

```bash
# 创建目标目录
mkdir -p ~/.klayout/salt/fib-tool

# 复制文件
cp -r python ~/.klayout/salt/fib-tool/
cp -r pymacros ~/.klayout/salt/fib-tool/
cp grain.xml ~/.klayout/salt/fib-tool/
```

### Windows

#### 使用安装脚本

```cmd
REM 双击运行或在命令行中执行
install.bat
```

**注意**: 
- 选项 1（符号链接）需要管理员权限
- 推荐使用选项 2（复制文件）

#### 手动安装

```cmd
REM 创建目标目录
mkdir %APPDATA%\KLayout\salt\fib-tool

REM 复制文件
xcopy /E /I python %APPDATA%\KLayout\salt\fib-tool\python
xcopy /E /I pymacros %APPDATA%\KLayout\salt\fib-tool\pymacros
copy grain.xml %APPDATA%\KLayout\salt\fib-tool\
```

## 验证安装

### 使用验证脚本

```bash
chmod +x verify_installation.sh
./verify_installation.sh
```

### 手动验证

检查以下文件是否存在：

**macOS/Linux**:
```bash
ls ~/.klayout/salt/fib-tool/grain.xml
ls ~/.klayout/salt/fib-tool/python/fib_tool/
ls ~/.klayout/salt/fib-tool/pymacros/
```

**Windows**:
```cmd
dir %APPDATA%\KLayout\salt\fib-tool\grain.xml
dir %APPDATA%\KLayout\salt\fib-tool\python\fib_tool\
dir %APPDATA%\KLayout\salt\fib-tool\pymacros\
```

## 在 KLayout 中使用

### 启动 FIB Tool

1. **完全关闭 KLayout**（重要！）
2. 重新打开 KLayout
3. 打开一个 GDS 文件
4. 按 `Ctrl+Shift+F` 或使用菜单：Tools → Toggle FIB Tool Panel

### 验证功能

- ✓ Panel 出现在右侧
- ✓ 可以看到 CUT/CONNECT/PROBE 按钮
- ✓ 点击按钮可以创建标记
- ✓ 可以 Save/Load JSON
- ✓ 可以 Export PDF/HTML

## 开发模式

如果你正在开发 FIB Tool，推荐使用 symbolic link 安装，然后：

### 在 Macro Development 中测试

1. 打开 KLayout
2. 按 `F5` 打开 Macro Development
3. 运行：

```python
exec(open('/path/to/klayout-fib-tool/load_fib_tool.py', encoding='utf-8').read())
```

这样可以快速测试代码修改，无需重启 KLayout。

## 卸载

### 使用卸载脚本

```bash
chmod +x uninstall.sh
./uninstall.sh
```

### 手动卸载

**macOS/Linux**:
```bash
rm -rf ~/.klayout/salt/fib-tool
```

**Windows**:
```cmd
rmdir /s /q %APPDATA%\KLayout\salt\fib-tool
```

## 故障排除

### Panel 不出现

1. **检查安装**:
   ```bash
   ./verify_installation.sh
   ```

2. **检查控制台**:
   - 在 KLayout 中按 `F5`
   - 查看是否有错误信息

3. **完全重启 KLayout**:
   - 确保完全退出（不是只关闭窗口）
   - 重新打开

### 导入错误

如果看到 "No module named 'fib_tool'" 错误：

1. 检查目录结构是否正确
2. 确保运行了 `./refactor.sh`
3. 重新安装：`./install.sh`

### 功能不工作

1. **检查 layers**:
   - 按 `F4` 打开 Layer Panel
   - 确保 layers 337, 338, 339 存在且可见

2. **查看详细日志**:
   - 按 `F5` 打开 Macro Development
   - 查看控制台输出

3. **使用诊断脚本**:
   ```bash
   # 在 KLayout Macro Development 中运行
   exec(open('/path/to/diagnose_layer_issue.py').read())
   ```

## 安装位置

### macOS
```
~/.klayout/salt/fib-tool/
├── python/
│   └── fib_tool/
├── pymacros/
└── grain.xml
```

### Linux
```
~/.klayout/salt/fib-tool/
├── python/
│   └── fib_tool/
├── pymacros/
└── grain.xml
```

### Windows
```
%APPDATA%\KLayout\salt\fib-tool\
├── python\
│   └── fib_tool\
├── pymacros\
└── grain.xml
```

## 更新

### Symbolic Link 安装

如果使用 symbolic link 安装：
1. 在源代码目录修改代码
2. 重启 KLayout
3. 修改立即生效

### Copy 安装

如果使用 copy 安装：
1. 修改源代码
2. 重新运行 `./install.sh`
3. 选择选项 2（Copy）
4. 重启 KLayout

## 多版本管理

如果需要同时保留多个版本：

```bash
# 安装到不同目录
cp -r . ~/.klayout/salt/fib-tool-dev
cp -r . ~/.klayout/salt/fib-tool-stable

# 在 KLayout 中只启用一个
# 通过重命名 grain.xml 来禁用：
mv ~/.klayout/salt/fib-tool-dev/grain.xml ~/.klayout/salt/fib-tool-dev/grain.xml.disabled
```

## 相关文档

- `REFACTOR_GUIDE.md` - 重构指南
- `QUICK_REFACTOR.md` - 快速重构
- `FIX_IMPORT_ERRORS.md` - 导入错误修复
- `compare_loading_methods.md` - 加载方式对比

## 需要帮助？

1. 查看 `TROUBLESHOOTING.md`
2. 运行诊断脚本
3. 检查 KLayout 控制台输出（F5）
4. 查看 GitHub Issues

---

**安装时间**: 约 1-2 分钟

**难度**: 简单

**推荐**: 开发用 symbolic link，生产用 copy
