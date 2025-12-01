# KLayout FIB Tool - MVP

**简单、实用的 FIB 标注工具。零废话，直接能用。**

## 快速开始

### 1. 安装

将 `src` 目录复制到 KLayout 的 Python 插件目录：

**macOS:**
```bash
cp -r src ~/.klayout/pymacros/fib_tool
```

**Linux:**
```bash
cp -r src ~/.klayout/pymacros/fib_tool
```

**Windows:**
```bash
xcopy /E /I src %APPDATA%\KLayout\pymacros\fib_tool
```

### 2. 使用

1. 打开 KLayout，加载一个 GDS 文件
2. 按 `Ctrl+Shift+F` 或从工具栏点击 "FIB Tool"
3. 点击 Cut/Connect/Probe 按钮
4. 在版图上点击创建标记
5. 点击 "Save" 保存为 XML
6. 点击 "Generate Report" 生成 HTML 报告

## 功能

### ✅ 已实现（MVP）

- **CUT 标注**：点击两次，第一次定位置，第二次定方向
- **CONNECT 标注**：点击两次，起点和终点
- **PROBE 标注**：点击一次，定位置
- **删除标记**：选中后点击 Delete
- **保存/加载**：XML 文件持久化
- **生成报告**：HTML 报告 + 截图

### ❌ 未实现（v1.1+）

- 分组管理
- PDF 报告
- 三级视图截图
- 撤销/重做
- 快捷键（除了启动）
- 属性编辑

## 代码结构

```
src/
├── __init__.py      # 插件注册入口
├── plugin.py        # 核心逻辑（鼠标事件处理）
├── markers.py       # 3 种标记类
├── storage.py       # XML 序列化
├── ui.py            # Qt 界面
├── report.py        # HTML 报告生成
├── config.py        # 配置（Layer 映射、符号尺寸）
└── utils.py         # 工具函数（目前为空）
```

**每个文件 < 300 行，简单直接。**

## 设计哲学

遵循 Linus Torvalds 的编程原则：

1. **数据结构优先**：用 `dataclass` 存数据，简单清晰
2. **消除特殊情况**：用多态，不用 if/else
3. **扁平优于嵌套**：early return，最多 2 层缩进
4. **实用主义**：解决真实问题，不过度设计

### 代码示例

**好品味：**
```python
@dataclass
class CutMarker:
    id: str
    x: float
    y: float
    direction: str
    layer: int
    
    def to_gds(self, cell, fib_layer):
        """一个方法做一件事"""
        self._draw_x_symbol(cell, fib_layer)
        self._draw_arrow(cell, fib_layer)
        self._draw_label(cell, fib_layer)
```

**不要这样：**
```python
class MarkerFactory:
    def create_marker(self, type, **kwargs):
        if type == "cut":
            return CutMarker(**kwargs)
        # 过度抽象，解决不存在的问题
```

## 配置

编辑 `config.py` 修改：

- **Layer 映射**：`LAYERS = {'cut': 200, 'connect': 201, 'probe': 202}`
- **符号尺寸**：`SYMBOL_SIZES` 字典
- **截图设置**：`SCREENSHOT_DPI`, `SCREENSHOT_MARGIN`

## 故障排查

### 插件没有加载
- 检查文件是否复制到正确的目录
- 重启 KLayout
- 查看 KLayout 的 Macro Development 窗口是否有错误

### 点击没有反应
- 确保已经打开了 GDS 文件
- 确保点击了 Cut/Connect/Probe 按钮激活模式
- 查看状态栏是否显示当前模式

### 标记没有显示
- 检查 Layer 200-202 是否可见
- 尝试缩放视图

## 开发

### 添加新功能

1. 保持简单：能用函数就别用类
2. 早返回：避免嵌套 if
3. 一个函数做一件事
4. 测试：在 KLayout 中实际运行

### 代码审查清单

- [ ] 能删掉这个 if 吗？
- [ ] 能少一层缩进吗？
- [ ] 这个类真的需要吗？
- [ ] 能用标准库吗？
- [ ] 函数 < 50 行吗？

## 许可证

MIT License

## 作者

遵循 Linus 的哲学：代码说话，少废话。
