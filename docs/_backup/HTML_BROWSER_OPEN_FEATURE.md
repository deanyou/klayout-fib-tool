# HTML 报告浏览器打开功能

## 新增功能

保存 HTML 报告后，询问用户是否在浏览器中打开，浏览器优先级：**Edge > Chrome > IE**

## 功能描述

### 1. 询问对话框

当 HTML 报告生成完成后，显示确认对话框：

```
HTML Report Generated

HTML report saved successfully!

/path/to/report.html

Would you like to open it in your browser?

[Yes] [No]
```

### 2. 浏览器优先级

**Windows**:
1. **Microsoft Edge** - 优先选择
   - `C:\Program Files\Microsoft\Edge\Application\msedge.exe`
   - `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

2. **Google Chrome** - 次选
   - `C:\Program Files\Google\Chrome\Application\chrome.exe`
   - `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`

3. **Internet Explorer** - 最后选择
   - `C:\Program Files\Internet Explorer\iexplore.exe`
   - `C:\Program Files (x86)\Internet Explorer\iexplore.exe`

4. **默认浏览器** - 兜底方案
   - 使用 `os.startfile()`

**macOS**:
1. Microsoft Edge
2. Google Chrome
3. Safari
4. 默认浏览器 (`open` 命令)

**Linux**:
1. microsoft-edge
2. google-chrome / chromium-browser
3. firefox
4. 默认浏览器 (`xdg-open`)

## 实现细节

### 1. 添加的函数

**文件**: `fib_tool/fib_panel.py`

#### `_ask_to_open_html(html_filename)`
- 显示询问对话框
- 如果用户选择 "Yes"，调用浏览器打开函数

#### `_open_html_in_browser(html_filename)`
- 检测操作系统
- 按优先级尝试打开浏览器
- 提供兜底方案

### 2. 调用位置

在两个地方调用 `_ask_to_open_html()`:

1. **PDF 生成成功后**:
   ```python
   print(f"[FIB Panel] PDF report created: {filename}")
   # Ask user if they want to open the HTML file
   self._ask_to_open_html(html_filename)
   ```

2. **只生成 HTML 时**（PDF 转换失败）:
   ```python
   pya.MessageBox.info("FIB Panel", "PDF conversion tools not installed...")
   # Ask user if they want to open the HTML file
   self._ask_to_open_html(html_filename)
   ```

### 3. 错误处理

- 如果所有浏览器都无法打开，显示手动打开的提示
- 包含完整的文件路径供用户复制
- 不会因为浏览器打开失败而影响报告生成

## 用户体验

### 成功流程
1. 用户点击 "Export to PDF/HTML"
2. 报告生成完成
3. 弹出询问对话框
4. 用户点击 "Yes"
5. 自动在 Edge（或其他可用浏览器）中打开 HTML 报告

### 兜底流程
1. 如果找不到指定浏览器，使用默认浏览器
2. 如果无法自动打开，显示文件路径让用户手动打开
3. 不影响报告的正常生成和保存

## 调试信息

函数会输出详细的调试信息：

```
[FIB Panel] Opening HTML with: msedge.exe
```

或

```
[FIB Panel] Using default browser
```

或

```
[FIB Panel] Error opening HTML in browser: [error details]
```

## 跨平台兼容性

### Windows
- 支持 Edge、Chrome、IE 的标准安装路径
- 支持 32 位和 64 位版本
- 使用 `os.startfile()` 作为兜底

### macOS
- 使用 `open -a` 命令指定应用
- 支持应用名称匹配
- 使用 `open` 命令作为兜底

### Linux
- 支持常见的浏览器命令名
- 使用 `xdg-open` 作为兜底
- 兼容不同发行版

## 配置选项

目前浏览器优先级是硬编码的，未来可以考虑添加配置选项：

```python
# 可能的配置扩展
BROWSER_PRIORITY = {
    'windows': ['edge', 'chrome', 'ie'],
    'macos': ['edge', 'chrome', 'safari'],
    'linux': ['edge', 'chrome', 'firefox']
}
```

## 测试建议

### 基本测试
1. 在有 Edge 的系统上测试 - 应该打开 Edge
2. 在只有 Chrome 的系统上测试 - 应该打开 Chrome
3. 在没有指定浏览器的系统上测试 - 应该使用默认浏览器

### 错误测试
1. 在没有任何浏览器的环境测试 - 应该显示手动打开提示
2. 测试文件路径包含特殊字符的情况
3. 测试网络驱动器上的文件

### 用户体验测试
1. 点击 "No" - 不应该打开浏览器
2. 点击 "Yes" - 应该立即打开浏览器
3. 多次导出 - 每次都应该询问

## 相关文件

- `fib_tool/fib_panel.py` - 主要实现
- `fib_tool/screenshot_export.py` - HTML 报告生成

## 总结

这个功能提供了便捷的 HTML 报告查看方式，支持跨平台，有完善的错误处理，不会影响核心功能的稳定性。用户可以选择是否打开，提供了良好的用户体验。