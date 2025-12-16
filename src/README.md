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

7. **多点模式**：在 FIB Panel 中选择 "Multi Points" 模式
   - 左键点击添加多个点
   - 右键点击完成输入
   - 支持 3+ 点的复杂路径

8. **右键菜单**：在 FIB Panel 的 Markers 列表中右键点击 marker
   - **Zoom to Fit**：缩放到 marker 位置
   - **Copy Coordinates**：复制坐标到剪贴板
   - **Add Notes**：添加备注信息 ✨
   - **Rename Marker**：重命名 marker
   - **Delete Marker**：删除 marker

9. **Export PDF**：点击 "Export PDF" 按钮
   - 为每个 marker 生成 3 张截图
   - Overview：全图 + 十字标尺指向 marker + 比例尺
   - Zoom 2x：中等缩放 + X/Y 尺寸标尺 + 比例尺
   - Detail：细节视图 + X/Y 尺寸标尺 + 比例尺
   - 自动计算并显示：ΔX、ΔY、线条长度
   - 生成 HTML 报告（可选转换为 PDF）
   - 默认 Notes 自动显示（切断/连接/点测）

10. **默认 Notes**：创建 marker 时自动设置有意义的默认值
    - CUT markers：默认 "切断"
    - CONNECT markers：默认 "连接"  
    - PROBE markers：默认 "点测"
    - 用户可随时修改或保持默认值

## 功能

### ✅ 已实现（当前版本）

- **CUT 标注**：点击两次，画连接两点的直线，默认 notes "切断"
- **CONNECT 标注**：点击两次，起点和终点，默认 notes "连接"
- **PROBE 标注**：点击一次，创建圆形标记，默认 notes "点测"
- **多点模式**：支持 Multi-Point Cut/Connect，右键完成输入
- **鼠标交互**：使用 KLayout Plugin 系统，支持真正的鼠标点击
- **工具栏集成**：自动添加三个工具栏按钮
- **FIB Panel**：侧边栏面板，包含项目管理和 marker 列表
- **右键菜单**：Zoom to Fit, Copy Coordinates, Add Notes, Rename, Delete
- **智能 Notes**：默认值 + 用户自定义，双重存储机制
- **Export PDF**：导出带截图的 HTML/PDF 报告
- **截图系统**：3 级截图 + 十字标尺 + 尺寸标尺 + 比例尺
- **尺寸测量**：自动计算 ΔX、ΔY 和线条长度
- **保存/加载**：JSON 格式项目文件，向后兼容
- **固定线宽**：0.2μm 线宽，PROBE 半径 0.5μm
- **标准图层**：CUT=317, CONNECT=318, PROBE=319, COORDINATES=319

### 🚧 开发中

- 保存/加载 XML 文件
- 批量操作功能
- 自定义标尺颜色
- 图层可见性控制

## 代码结构

```
src/
├── fib_plugin.py              # 主程序（Plugin 系统 + 鼠标事件处理）
├── fib_panel.py               # FIB 面板（项目管理、marker 列表）
├── markers.py                 # 3 种标记类（CutMarker, ConnectMarker, ProbeMarker）
├── multipoint_markers.py      # 多点标记类
├── marker_menu.py             # 右键菜单（缩放、复制、编辑、删除）
├── screenshot_export.py       # 截图导出（3级截图 + 标尺）
├── config.py                  # 配置（Layer 映射、符号尺寸）
├── smart_counter.py           # 智能计数器
├── file_dialog_helper.py      # 文件对话框辅助
├── cleanup_orphaned_markers.py # 清理工具（可选）
├── storage.py                 # XML 序列化（待集成）
├── report.py                  # HTML 报告生成（待集成）
├── utils.py                   # 工具函数
└── README.md                  # 项目说明
```

**核心文件简洁，主程序 < 200 行。**

## 主要特性

### 📐 智能尺寸测量
- **自动计算**：ΔX、ΔY、线条长度
- **可视化标尺**：X/Y 方向标尺显示在截图中
- **精确测量**：微米级精度，支持复杂路径

### 📝 智能 Notes 系统
- **默认值**：CUT(切断)、CONNECT(连接)、PROBE(点测)
- **双重存储**：marker 对象 + 集中字典，确保数据安全
- **用户友好**：右键编辑，支持自定义内容

### 📸 专业截图导出
- **3 级截图**：Overview(全图) → Zoom 2x(中等) → Detail(细节)
- **智能标注**：十字标尺定位 + 尺寸标尺测量 + 比例尺参考
- **HTML 报告**：包含截图、坐标、尺寸、notes 的完整报告

### 🎯 多点路径支持
- **复杂路径**：支持 3+ 点的多点 Cut/Connect
- **直观操作**：左键添加点，右键完成（CAD 标准）
- **路径可视化**：清晰显示连接路径和节点

### 💾 项目管理
- **保存/加载**：JSON 格式，包含所有 marker 数据
- **向后兼容**：支持旧版本项目文件
- **数据完整性**：notes、截图、图层信息完整保存

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

### 标尺颜色设置
- 十字标尺和尺寸标尺颜色由 KLayout 设置控制
- 设置为白色：`KLayout → Preferences → Display → Rulers/Annotations`
- 设置 RGB 为 `(255, 255, 255)` 纯白色

### PDF 导出问题
- 如果 PDF 转换失败，会生成 HTML 报告
- 安装 PDF 工具：`pip install weasyprint` 或 `wkhtmltopdf`
- 检查输出目录的写入权限

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
