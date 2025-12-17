# KLayout FIB Tool - MVP Plan (Minimum Viable Product)

## 1. MVP 目标

**核心价值**：实现基本的 FIB 标注功能，让用户能够在 KLayout 版图上标注 CUT/CONNECT/PROBE 操作，并生成简单的操作报告。

**时间目标**：4-6 周完成开发和测试

**成功标准**：
- 用户能够在版图上创建 CUT、CONNECT、PROBE 标记
- 标记能够存储在 GDS 文件中并持久化
- 能够生成包含基本信息的 HTML 报告
- 工具稳定运行，无崩溃

---

## 2. MVP 功能范围

### 2.1 包含功能（Must Have）

#### ✅ 核心标注功能
| 功能 | 优先级 | 实现范围 |
|------|--------|----------|
| **CUT 标注** | P0 | • 单点击创建切断标记<br>• X 形符号 + 简单箭头<br>• 记录坐标和方向<br>• 显示操作编号（CUT_0, CUT_1...）|
| **CONNECT 标注** | P0 | • 两点击创建连接标记<br>• 直线连接路径<br>• 圆形端点符号<br>• 显示操作编号（CONNECT_0...）|
| **PROBE 标注** | P0 | • 单点击创建探针标记<br>• 向下箭头符号<br>• 记录坐标<br>• 显示操作编号（PROBE_0...）|
| **删除标记** | P0 | • 支持删除选中的标记<br>• 简单的确认对话框 |

#### ✅ 数据存储
| 功能 | 优先级 | 实现范围 |
|------|--------|----------|
| **GDS Layer 存储** | P0 | • 使用专用 Layer 200-202 存储标记<br>• 基本图形元素（Path、Polygon、Text）|
| **XML 状态文件** | P0 | • 保存所有标记数据到 XML<br>• 从 XML 加载标记数据<br>• 记录基本元数据（Library、Cell、时间戳）|

#### ✅ 用户界面
| 功能 | 优先级 | 实现范围 |
|------|--------|----------|
| **工具面板** | P0 | • 3 个操作按钮（Cut / Connect / Probe）<br>• 操作状态指示<br>• 简单的操作列表 |
| **交互操作** | P0 | • 鼠标点击创建标记<br>• Esc 取消当前操作<br>• 鼠标悬停显示坐标 |

#### ✅ 报告生成
| 功能 | 优先级 | 实现范围 |
|------|--------|----------|
| **HTML 报告** | P0 | • 设计基本信息表格<br>• 操作列表和详细信息<br>• 单级截图（每个操作一张图）<br>• 坐标和 Layer 信息 |
| **截图功能** | P0 | • 使用 KLayout API 截图<br>• 固定缩放比例（1:1）|

---

### 2.2 不包含功能（Not in MVP）

#### ❌ 延后到 v1.1 或 v2.0
| 功能 | 延后原因 | 计划版本 |
|------|----------|----------|
| 分组管理 | 非核心工作流，增加复杂度 | v1.1 |
| PDF 报告 | HTML 已足够，PDF 需额外依赖 | v1.1 |
| 三级视图截图 | 简化实现，单级截图足够 | v1.1 |
| 图片放大功能 | 非必需，增加复杂度 | v2.0 |
| 撤销/重做 | 可手动删除替代 | v1.1 |
| 快捷键 | 按钮操作已足够 | v1.1 |
| 自定义颜色 | 使用默认颜色即可 | v2.0 |
| 属性编辑 | 创建时设置即可 | v1.1 |
| 区域裁剪导出 | 导出完整 GDS 即可 | v1.1 |
| 自适应符号大小 | 使用固定尺寸 | v2.0 |
| 多段折线 CONNECT | 直线连接足够 | v2.0 |
| 备注标签 | 简化功能 | v1.1 |

---

## 3. 技术架构

### 3.1 模块划分

```
klayout_fib_tool/
├── __init__.py              # 插件入口
├── plugin.py                # KLayout Plugin 实现
├── markers.py               # 标记类定义（CutMarker, ConnectMarker, ProbeMarker）
├── storage.py               # 数据存储（GDS Layer + XML）
├── ui.py                    # 用户界面（Qt Dialog）
├── report.py                # HTML 报告生成
├── config.py                # 配置管理（Layer 映射等）
└── utils.py                 # 工具函数
```

### 3.2 核心类设计

#### Marker 基类
```python
class Marker:
    def __init__(self, marker_id, position, layer_info):
        self.id = marker_id              # 例如 "CUT_0"
        self.position = position          # (x, y) 坐标，单位 μm
        self.layer_info = layer_info      # 目标 Layer
        
    def to_gds(self, cell, fib_layer):
        """将标记转换为 GDS 图形并插入到指定 Cell"""
        pass
    
    def to_xml(self):
        """将标记数据导出为 XML 元素"""
        pass
```

#### CutMarker 类
```python
class CutMarker(Marker):
    def __init__(self, marker_id, position, direction, layer_info):
        super().__init__(marker_id, position, layer_info)
        self.direction = direction  # "up", "down", "left", "right"
    
    def to_gds(self, cell, fib_layer):
        # 绘制 X 符号（两条交叉线）
        # 绘制方向箭头
        # 添加文本标签 (CUT_0)
        pass
```

#### ConnectMarker 类
```python
class ConnectMarker(Marker):
    def __init__(self, marker_id, start, end, layer_info):
        super().__init__(marker_id, start, layer_info)
        self.end = end  # 终点坐标
    
    def to_gds(self, cell, fib_layer):
        # 绘制连接路径（直线）
        # 绘制起点和终点圆形符号
        # 添加文本标签 (CONNECT_0)
        pass
```

#### ProbeMarker 类
```python
class ProbeMarker(Marker):
    def __init__(self, marker_id, position, layer_info):
        super().__init__(marker_id, position, layer_info)
    
    def to_gds(self, cell, fib_layer):
        # 绘制向下箭头符号
        # 添加文本标签 (PROBE_0)
        pass
```

### 3.3 KLayout Plugin 集成

使用 `pya.PluginFactory` 注册工具：

```python
class FIBTool(pya.Plugin):
    """FIB Tool Plugin"""
    
    def __init__(self):
        self.mode = None  # "cut", "connect", "probe"
        self.markers = []
        self.temp_points = []  # 临时存储多点操作的中间点
        
    def mouse_click_event(self, p, buttons, prio):
        """处理鼠标点击事件"""
        if self.mode == "cut":
            # 第一次点击：记录位置
            # 第二次点击：确定方向，创建 CutMarker
            pass
        elif self.mode == "connect":
            # 第一次点击：记录起点
            # 第二次点击：记录终点，创建 ConnectMarker
            pass
        elif self.mode == "probe":
            # 单击创建 ProbeMarker
            pass
    
    def mouse_moved_event(self, p, buttons, prio):
        """处理鼠标移动事件，显示预览"""
        # 显示临时标记预览（使用 pya.Marker）
        pass
```

---

## 4. 开发计划

### 4.1 Sprint 1 (Week 1-2): 基础框架

**目标**：搭建插件骨架，实现基本的 UI 和鼠标交互

**任务**：
- [ ] 创建项目目录结构
- [ ] 实现 `plugin.py` - 注册 KLayout 插件
- [ ] 实现 `ui.py` - 创建基本的工具面板（3 个按钮）
- [ ] 实现鼠标点击事件捕获和坐标获取
- [ ] 测试：能够点击按钮并在版图上点击获取坐标

**交付物**：
- 可在 KLayout 中启动的插件
- 简单的 UI 面板
- 基本的鼠标交互

---

### 4.2 Sprint 2 (Week 3-4): 标记创建与显示

**目标**：实现 CUT/CONNECT/PROBE 标记的创建和 GDS 显示

**任务**：
- [ ] 实现 `markers.py` - 定义 Marker 基类和三个子类
- [ ] 实现 `CutMarker.to_gds()` - 绘制 X 符号 + 箭头 + 标签
- [ ] 实现 `ConnectMarker.to_gds()` - 绘制连线 + 端点 + 标签
- [ ] 实现 `ProbeMarker.to_gds()` - 绘制箭头 + 标签
- [ ] 实现 `config.py` - Layer 映射配置（200-202）
- [ ] 测试：创建标记并在版图上正确显示

**交付物**：
- 能够创建并显示三种标记
- 标记存储在正确的 GDS Layer
- 标记符号清晰可辨

**技术要点**：
```python
# 绘制 X 符号示例
def draw_x_symbol(cell, fib_layer, center, size):
    """绘制 X 形符号"""
    x, y = center
    half = size / 2
    # 左上到右下的对角线
    pts1 = [pya.Point(x-half, y+half), pya.Point(x+half, y-half)]
    path1 = pya.Path(pts1, width=100)  # 宽度 0.1μm
    cell.shapes(fib_layer).insert(path1)
    # 右上到左下的对角线
    pts2 = [pya.Point(x-half, y-half), pya.Point(x+half, y+half)]
    path2 = pya.Path(pts2, width=100)
    cell.shapes(fib_layer).insert(path2)
```

---

### 4.3 Sprint 3 (Week 5): 数据存储与加载

**目标**：实现 XML 状态文件的保存和加载

**任务**：
- [ ] 实现 `storage.py` - XML 序列化和反序列化
- [ ] 实现 `Marker.to_xml()` - 将标记导出为 XML 元素
- [ ] 实现 `from_xml()` - 从 XML 创建 Marker 对象
- [ ] 在 UI 中添加 Save 和 Load 按钮
- [ ] 测试：保存后关闭 KLayout，重新打开能够恢复标记

**交付物**：
- 完整的 XML 保存/加载功能
- 数据持久化验证通过

**XML 格式示例**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<fib_project version="1.0">
    <metadata>
        <library>test_lib</library>
        <cell>test_cell</cell>
        <created>2024-12-01T10:00:00</created>
    </metadata>
    <markers>
        <cut id="CUT_0" x="100.5" y="200.3" direction="down" layer="6:0"/>
        <connect id="CONNECT_0" x1="150.0" y1="250.0" x2="180.0" y2="280.0" layer="6:0"/>
        <probe id="PROBE_0" x="300.0" y="400.0" layer="6:0"/>
    </markers>
</fib_project>
```

---

### 4.4 Sprint 4 (Week 6): 报告生成

**目标**：生成简单的 HTML 报告

**任务**：
- [ ] 实现 `report.py` - HTML 报告生成
- [ ] 使用 Jinja2 模板引擎
- [ ] 实现截图功能（使用 `view.save_image_with_options()`）
- [ ] 在 UI 中添加 Generate Report 按钮
- [ ] 测试：生成的 HTML 报告包含所有标记信息和截图

**交付物**：
- HTML 报告模板
- 完整的报告生成功能

**HTML 报告结构**：
```html
<!DOCTYPE html>
<html>
<head>
    <title>FIB Report</title>
    <style>/* 简单的样式 */</style>
</head>
<body>
    <h1>FIB Operation Report</h1>
    
    <h2>Design Information</h2>
    <table>
        <tr><th>Library</th><td>{{ library }}</td></tr>
        <tr><th>Cell</th><td>{{ cell }}</td></tr>
        <tr><th>Generated</th><td>{{ timestamp }}</td></tr>
    </table>
    
    <h2>Operations</h2>
    {% for marker in markers %}
    <div class="operation">
        <h3>{{ marker.id }}</h3>
        <p>Type: {{ marker.type }}</p>
        <p>Position: {{ marker.position }}</p>
        <p>Layer: {{ marker.layer }}</p>
        <img src="{{ marker.screenshot }}" alt="{{ marker.id }}"/>
    </div>
    {% endfor %}
</body>
</html>
```

---

## 5. 测试计划

### 5.1 功能测试

| 测试项 | 测试步骤 | 预期结果 |
|--------|----------|----------|
| **CUT 标记** | 1. 点击 Cut 按钮<br>2. 点击版图两次 | X 符号和箭头正确显示，标签为 CUT_0 |
| **CONNECT 标记** | 1. 点击 Connect 按钮<br>2. 点击版图两次 | 连线和端点正确显示，标签为 CONNECT_0 |
| **PROBE 标记** | 1. 点击 Probe 按钮<br>2. 点击版图一次 | 箭头符号正确显示，标签为 PROBE_0 |
| **删除标记** | 1. 选中标记<br>2. 按 Delete | 标记从版图中消失 |
| **保存状态** | 1. 创建多个标记<br>2. 点击 Save | 生成 XML 文件 |
| **加载状态** | 1. 关闭 KLayout<br>2. 重新打开<br>3. 点击 Load | 所有标记恢复显示 |
| **生成报告** | 1. 创建多个标记<br>2. 点击 Generate Report | 生成 HTML 文件，包含所有信息 |

### 5.2 性能测试

| 测试项 | 测试条件 | 目标指标 |
|--------|----------|----------|
| 标记创建速度 | 连续创建 100 个标记 | < 1 秒 |
| 报告生成速度 | 100 个标记 | < 30 秒 |
| XML 保存速度 | 100 个标记 | < 2 秒 |
| XML 加载速度 | 100 个标记 | < 5 秒 |

### 5.3 兼容性测试

- [ ] Windows 10/11 + KLayout 0.28+
- [ ] macOS 12+ + KLayout 0.28+
- [ ] Linux (Ubuntu 20.04+) + KLayout 0.28+

---

## 6. 配置文件

### 6.1 config.yaml

MVP 使用简化的配置：

```yaml
# FIB Tool Configuration (MVP)
version: 1.0

# Layer 映射
layers:
  cut:
    layer: 200
    datatype: 0
  connect:
    layer: 201
    datatype: 0
  probe:
    layer: 202
    datatype: 0

# 标记符号尺寸（单位：μm）
symbols:
  cut:
    size: 2.0          # X 符号大小
    arrow_length: 3.0  # 箭头长度
    line_width: 0.1    # 线宽
  connect:
    endpoint_radius: 0.5  # 端点半径
    line_width: 0.1       # 线宽
  probe:
    height: 3.0        # 箭头高度
    width: 1.5         # 箭头宽度
    line_width: 0.1    # 线宽

# 截图设置
screenshot:
  dpi: 150
  format: "png"
  margin: 5.0        # 截图边距（μm）

# 报告设置
report:
  template: "report_template.html"
  output_dir: "./fib_reports"
```

---

## 7. 依赖项

### 7.1 Python 依赖

```
# requirements.txt
PyYAML>=6.0
Jinja2>=3.0
```

### 7.2 KLayout 要求

- KLayout >= 0.28.0
- Python 支持已启用

---

## 8. 交付物清单

### 8.1 代码
- [ ] `__init__.py` - 插件入口
- [ ] `plugin.py` - 插件主逻辑
- [ ] `markers.py` - 标记类
- [ ] `storage.py` - 数据存储
- [ ] `ui.py` - 用户界面
- [ ] `report.py` - 报告生成
- [ ] `config.py` - 配置管理
- [ ] `utils.py` - 工具函数

### 8.2 配置文件
- [ ] `config.yaml` - 默认配置
- [ ] `report_template.html` - 报告模板

### 8.3 文档
- [ ] `README.md` - 安装和使用说明
- [ ] `CHANGELOG.md` - 版本变更记录
- [ ] `examples/` - 示例文件

### 8.4 测试
- [ ] 功能测试通过
- [ ] 性能测试通过
- [ ] 跨平台测试通过

---

## 9. 风险管理

### 9.1 技术风险

| 风险 | 缓解措施 |
|------|----------|
| KLayout Plugin API 不熟悉 | 提前验证核心 API（鼠标事件、图形绘制、截图） |
| 鼠标事件捕获不稳定 | 使用 `grab_mouse()` 确保事件正确处理 |
| GDS 图形绘制不精确 | 使用数据库单位（DBU）而非微米，保证精度 |
| 截图质量不理想 | 测试不同 DPI 设置，找到最佳值 |

### 9.2 进度风险

| 风险 | 缓解措施 |
|------|----------|
| 开发时间超出预期 | 严格遵循 MVP 范围，延后非核心功能 |
| API 研究耗时过长 | 已完成 API 研究，直接参考 `klayout_api_research.md` |

---

## 10. 成功标准

### 10.1 必须达成

- [x] 能够创建 CUT/CONNECT/PROBE 标记
- [ ] 标记正确存储在 GDS 专用 Layer
- [ ] 能够保存和加载 XML 状态文件
- [ ] 能够生成包含标记信息的 HTML 报告
- [ ] 工具无崩溃运行 > 1 小时

### 10.2 可选达成

- [ ] 用户首次使用学习时间 < 30 分钟
- [ ] 标记创建响应 < 100ms
- [ ] 报告生成时间 < 30 秒

---

## 11. 下一步（v1.1 规划）

MVP 完成后，v1.1 将添加：

1. **分组管理**：支持创建分组，组织多个操作
2. **PDF 报告**：使用 ReportLab 生成 PDF
3. **撤销/重做**：使用 KLayout 的 transaction 机制
4. **快捷键**：C/N/P 激活不同模式
5. **三级视图截图**：全局/局部/详细三个层次

---

## Document History

| 版本 | 日期 | 作者 | 描述 |
|------|------|------|------|
| 1.0 | 2024-12-01 | - | MVP 初始规划 |
