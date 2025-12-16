# FIB Tool - PDF 导出依赖说明

## 📄 PDF 导出功能

FIB Tool 的 PDF 导出功能是**可选的**，不是必需的。

### 默认行为

- ✅ **HTML 报告**：始终可用，包含所有截图和标记信息
- ⚠️ **PDF 转换**：需要额外安装工具（可选）

---

## 🔧 PDF 转换工具（可选）

FIB Tool 支持两种 PDF 转换工具，**任选其一**即可：

### 方式 1: wkhtmltopdf（推荐）

**优点**：
- ✅ 独立程序，不需要 Python 依赖
- ✅ 转换速度快
- ✅ 支持复杂 HTML/CSS

**安装方法**：

**macOS:**
```bash
brew install wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

**Windows:**
- 下载安装包：https://wkhtmltopdf.org/downloads.html
- 安装后确保 `wkhtmltopdf` 在 PATH 中

---

### 方式 2: weasyprint

**优点**：
- ✅ Python 包，易于安装
- ✅ 纯 Python 实现

**缺点**：
- ⚠️ 需要额外的系统依赖
- ⚠️ 可能与 KLayout 的 Python 环境冲突

**安装方法**：

**macOS:**
```bash
# 安装系统依赖
brew install python3 cairo pango gdk-pixbuf libffi

# 安装 weasyprint
pip3 install weasyprint
```

**Linux (Ubuntu/Debian):**
```bash
# 安装系统依赖
sudo apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0

# 安装 weasyprint
pip3 install weasyprint
```

**Windows:**
```bash
# 需要 GTK+ 运行时
# 下载：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

# 安装 weasyprint
pip install weasyprint
```

---

## 🚀 使用说明

### 不安装 PDF 工具

如果你不安装任何 PDF 转换工具：

1. **导出功能仍然可用**
2. **生成 HTML 报告**（包含所有截图）
3. **弹出提示**：
   ```
   PDF conversion tools not installed.
   
   HTML report with screenshots saved to:
   /path/to/fib_markers_report.html
   
   To enable PDF export, install:
     pip install weasyprint
   or install wkhtmltopdf
   ```

4. **HTML 报告功能完整**：
   - ✅ 所有标记信息
   - ✅ 3 级缩放截图
   - ✅ 坐标和尺寸
   - ✅ 可以在浏览器中打开
   - ✅ 可以手动打印为 PDF（浏览器打印功能）

---

### 安装 PDF 工具后

安装任一 PDF 工具后：

1. **自动转换为 PDF**
2. **保留 HTML 文件**（在 `images/` 目录）
3. **生成 PDF 文件**：`fib_markers_report.pdf`

---

## 🔍 故障排除

### 问题 1: "No module named 'weasyprint'"

**原因**：weasyprint 未安装

**解决方案**：
1. **不需要修复**：HTML 报告已经生成，功能完整
2. **如果需要 PDF**：安装 wkhtmltopdf（更简单）或 weasyprint

---

### 问题 2: wkhtmltopdf 找不到

**症状**：
```
[FIB Panel] wkhtmltopdf not available: [Errno 2] No such file or directory: 'wkhtmltopdf'
```

**解决方案**：
1. 确认已安装：`wkhtmltopdf --version`
2. 检查 PATH：`which wkhtmltopdf`（macOS/Linux）
3. 重启 KLayout

---

### 问题 3: weasyprint 依赖错误

**症状**：
```
ImportError: cannot import name 'HTML' from 'weasyprint'
```

**解决方案**：
1. 使用 wkhtmltopdf 代替（推荐）
2. 或重新安装 weasyprint：
   ```bash
   pip3 uninstall weasyprint
   pip3 install weasyprint
   ```

---

### 问题 4: KLayout Python 环境冲突

**症状**：weasyprint 安装后 KLayout 报错

**原因**：KLayout 使用内置 Python，可能与系统 Python 冲突

**解决方案**：
1. **推荐**：使用 wkhtmltopdf（独立程序，无冲突）
2. 或不安装 PDF 工具，使用 HTML 报告

---

## 📊 功能对比

| 功能 | 无 PDF 工具 | wkhtmltopdf | weasyprint |
|------|------------|-------------|------------|
| HTML 报告 | ✅ | ✅ | ✅ |
| 截图导出 | ✅ | ✅ | ✅ |
| PDF 生成 | ❌ | ✅ | ✅ |
| 安装难度 | 无需安装 | 简单 | 中等 |
| 系统依赖 | 无 | 无 | 多个 |
| 兼容性 | 完美 | 好 | 可能冲突 |

---

## 💡 推荐方案

### 场景 1: 只需要查看标记信息

**推荐**：不安装任何 PDF 工具

- HTML 报告已经包含所有信息
- 可以在浏览器中查看
- 需要时可以手动打印为 PDF

---

### 场景 2: 需要分享 PDF 报告

**推荐**：安装 wkhtmltopdf

```bash
# macOS
brew install wkhtmltopdf

# Linux
sudo apt-get install wkhtmltopdf
```

**原因**：
- 安装简单
- 无 Python 依赖冲突
- 转换质量好

---

### 场景 3: 无法安装 wkhtmltopdf

**推荐**：使用 HTML + 浏览器打印

1. 导出 HTML 报告
2. 在浏览器中打开
3. 使用浏览器的打印功能（Ctrl+P / Cmd+P）
4. 选择"保存为 PDF"

**优点**：
- 无需额外安装
- 效果与 PDF 工具相同
- 完全控制打印设置

---

## 🎯 总结

### 关键点

1. **PDF 工具不是必需的**
   - HTML 报告功能完整
   - 包含所有截图和信息

2. **推荐安装 wkhtmltopdf**
   - 如果需要自动生成 PDF
   - 安装简单，无冲突

3. **weasyprint 可选**
   - 如果 wkhtmltopdf 不可用
   - 注意可能的依赖冲突

4. **浏览器打印是备选方案**
   - 始终可用
   - 效果相同

---

## 📚 相关文档

- [INSTALL.md](../INSTALL.md) - 安装指南
- [SALT_INSTALLATION.md](SALT_INSTALLATION.md) - SALT 安装
- [README.md](../README.md) - 项目概述

---

**简单、实用、零废话。HTML 报告已经足够，PDF 只是锦上添花。** 🎯
