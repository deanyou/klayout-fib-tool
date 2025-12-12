# KLayout FIB Tool - MVP

**简单、实用的 FIB 标注工具。零废话，直接能用。**

## 快速开始

### 方法 1: 一键加载（推荐）

1. 打开 KLayout，加载一个 GDS 文件
2. 按 `F5` 打开 Macro Development 窗口
3. 复制粘贴以下命令：

```python
import sys; sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/src'); 

exec(open('/Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py', encoding='utf-8').read())
```

4. 按 Enter，工具栏会出现 FIB Cut、FIB Connect、FIB Probe 按钮

### 方法 2: 安装到宏目录

将文件复制到 KLayout 宏目录：

**macOS:**
```bash
cp src/fib_plugin.py ~/KLayout/macros/
cp src/markers.py ~/KLayout/macros/
cp src/config.py ~/KLayout/macros/
```

然后在 KLayout 中：Macros → fib_plugin.py → Run

### 使用方法

1. **CUT 标记**：点击 "FIB Cut" 按钮，然后在布局上点击两次
   - 第1次：起点
   - 第2次：终点
   - 会画一条连接两点的直线

2. **CONNECT 标记**：点击 "FIB Connect" 按钮，然后在布局上点击两次
   - 第1次：起点
   - 第2次：终点

3. **PROBE 标记**：点击 "FIB Probe" 按钮，然后在布局上点击一次
   - 创建圆形标记

4. **坐标文本**：每次点击都会自动添加坐标文本
   - 显示格式：`(100.25,150.30)`
   - 显示在 Layer 319（与 PROBE 标记共用）

5. **层检测**：自动检测点击位置的层信息
   - 标记名称包含层信息，如：`CUT_0_L1/0`

6. **清除坐标**：在控制台调用 `clear_coordinate_texts()` 清除所有坐标文本

## 功能

### ✅ 已实现（当前版本）

- **CUT 标注**：点击两次，画连接两点的直线
- **CONNECT 标注**：点击两次，起点和终点
- **PROBE 标注**：点击一次，创建圆形标记
- **鼠标交互**：使用 KLayout Plugin 系统，支持真正的鼠标点击
- **工具栏集成**：自动添加三个工具栏按钮
- **固定线宽**：0.2μm 线宽，PROBE 半径 0.5μm
- **标准图层**：CUT=317, CONNECT=318, PROBE=319, COORDINATES=319

### 🚧 开发中

- 保存/加载 XML 文件
- 生成 HTML 报告
- 删除标记功能
- UI 对话框

## 代码结构

```
src/
├── fib_plugin.py    # 主程序（Plugin 系统 + 鼠标事件处理）
├── fib_tool.lym     # KLayout 宏版本（备用）
├── markers.py       # 3 种标记类（CutMarker, ConnectMarker, ProbeMarker）
├── config.py        # 配置（Layer 映射、符号尺寸）
├── storage.py       # XML 序列化（待集成）
├── report.py        # HTML 报告生成（待集成）
├── utils.py         # 工具函数
└── README.md        # 项目说明
```

**核心文件简洁，主程序 < 200 行。**

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
    x1: float  # 第一个点
    y1: float
    x2: float  # 第二个点
    y2: float
    layer: int
    
    def to_gds(self, cell, fib_layer):
        """直接连接两个鼠标点击点"""
        pts = [pya.Point(p1_x, p1_y), pya.Point(p2_x, p2_y)]
        cell.shapes(fib_layer).insert(pya.Path(pts, width))
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

- **Layer 映射**：`LAYERS = {'cut': 317, 'connect': 318, 'probe': 319, 'coordinates': 319}`
- **符号尺寸**：`SYMBOL_SIZES` 字典
- **线宽**：固定 0.2μm
- **PROBE 半径**：0.5μm
- **坐标文本**：Layer 319（与 PROBE 共用）

## 故障排查

### 加载失败
- 确保已经打开了 GDS 文件
- 检查路径是否正确：`/Users/dean/Documents/git/klayout-fib-tool/src`
- 查看 Macro Development 窗口的错误信息

### 按钮没有出现
- 检查控制台输出，确认 "FIB Tool loaded successfully"
- 重新运行加载命令

### 点击没有反应
- 确保点击了工具栏按钮激活模式
- 查看控制台调试信息
- 确认鼠标点击在布局区域内

### 标记没有显示
- 检查 Layer Panel，确保 Layer 317/318/319 可见
- 使用 "Fit All" 查看整个布局
- 调整视图缩放级别

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
