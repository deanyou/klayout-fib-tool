# KLayout FIB Tool - MVP 执行清单

## 📋 MVP 核心价值

**在 4-6 周内实现基本的 FIB 标注功能，让用户能够：**
1. 在版图上标注 CUT/CONNECT/PROBE 操作
2. 保存和加载标注数据
3. 生成简单的 HTML 操作报告

---

## 🎯 功能范围

### ✅ MVP 包含功能

```
┌─────────────────────────────────────────────────────────┐
│  核心功能            │  实现范围                        │
├─────────────────────────────────────────────────────────┤
│  CUT 标注            │  单点击 → X符号 + 箭头 + 编号    │
│  CONNECT 标注        │  两点击 → 直线 + 端点 + 编号     │
│  PROBE 标注          │  单点击 → 箭头符号 + 编号        │
│  删除标记            │  选中后删除                      │
│  保存/加载状态       │  XML 文件持久化                  │
│  生成 HTML 报告      │  包含操作列表 + 单级截图         │
└─────────────────────────────────────────────────────────┘
```

### ❌ MVP 不包含（延后到 v1.1+）

- 分组管理
- PDF 报告生成
- 三级视图截图
- 图片放大功能
- 撤销/重做
- 快捷键支持
- 属性编辑
- 自定义颜色

---

## 🏗️ 代码结构

```
klayout_fib_tool/src/
├── __init__.py              # 插件入口，注册到 KLayout
├── plugin.py                # 核心插件逻辑（鼠标事件处理）
├── markers.py               # 标记类（CutMarker, ConnectMarker, ProbeMarker）
├── storage.py               # 数据存储（GDS + XML）
├── ui.py                    # 用户界面（Qt Dialog）
├── report.py                # HTML 报告生成（Jinja2）
├── config.py                # 配置管理（Layer 映射）
└── utils.py                 # 工具函数
```

---

## 📅 4 周开发计划

### Week 1-2: 基础框架 ✅
```
任务清单：
□ 创建项目结构
□ 实现 plugin.py - 注册 KLayout 插件
□ 实现 ui.py - 创建工具面板（3 个按钮）
□ 捕获鼠标点击事件并获取坐标
□ 测试：能够在版图上点击并获取坐标

技术要点：
- 使用 pya.PluginFactory 注册插件
- 使用 pya.Plugin.mouse_click_event() 捕获点击
- 使用 pya.QDialog 创建界面
```

### Week 3-4: 标记创建 🎨
```
任务清单：
□ 实现 markers.py - Marker 基类和 3 个子类
□ 实现 CutMarker.to_gds() - 绘制 X + 箭头 + 标签
□ 实现 ConnectMarker.to_gds() - 绘制连线 + 端点 + 标签
□ 实现 ProbeMarker.to_gds() - 绘制箭头 + 标签
□ 实现 config.py - Layer 200-202 映射
□ 测试：标记正确显示在版图上

技术要点：
- 使用 pya.Path, pya.Polygon, pya.Text 绘制图形
- 使用 cell.shapes(layer).insert() 插入图形
- 符号尺寸：CUT=2μm, CONNECT端点=0.5μm, PROBE=3μm
```

### Week 5: 数据存储 💾
```
任务清单：
□ 实现 storage.py - XML 序列化/反序列化
□ 实现 Marker.to_xml() - 导出为 XML
□ 实现 from_xml() - 从 XML 创建 Marker
□ UI 添加 Save 和 Load 按钮
□ 测试：保存后重启 KLayout 能恢复标记

技术要点：
- 使用 xml.etree.ElementTree
- XML 存储：坐标、方向、Layer、时间戳
```

### Week 6: 报告生成 📄
```
任务清单：
□ 实现 report.py - HTML 报告生成
□ 创建 Jinja2 模板
□ 实现截图功能（view.save_image_with_options）
□ UI 添加 Generate Report 按钮
□ 测试：生成完整 HTML 报告

技术要点：
- 使用 Jinja2 模板引擎
- 截图参数：DPI=150, 固定缩放 1:1
- 报告包含：设计信息表 + 操作列表 + 截图
```

---

## 🔑 核心技术点

### 1. 标记绘制示例

```python
# CUT 标记：X 符号 + 箭头
def draw_cut_marker(cell, layer, center, direction):
    x, y = center
    size = 2.0  # 2μm
    
    # X 符号（两条交叉线）
    half = size / 2
    line1 = pya.Path([pya.Point(x-half, y+half), 
                      pya.Point(x+half, y-half)], width=100)
    line2 = pya.Path([pya.Point(x-half, y-half), 
                      pya.Point(x+half, y+half)], width=100)
    cell.shapes(layer).insert(line1)
    cell.shapes(layer).insert(line2)
    
    # 方向箭头
    arrow_length = 3.0
    if direction == "down":
        arrow_end = pya.Point(x, y - arrow_length)
    elif direction == "up":
        arrow_end = pya.Point(x, y + arrow_length)
    # ... 其他方向
    
    arrow = pya.Path([pya.Point(x, y), arrow_end], width=100)
    cell.shapes(layer).insert(arrow)
    
    # 文本标签
    text = pya.Text("CUT_0", pya.Trans(arrow_end))
    cell.shapes(layer).insert(text)
```

### 2. 鼠标交互模式

```python
class FIBPlugin(pya.Plugin):
    def __init__(self):
        self.mode = None  # "cut", "connect", "probe"
        self.temp_point = None
        
    def activate_cut_mode(self):
        self.mode = "cut"
        self.grab_mouse()  # 捕获鼠标事件
        
    def mouse_click_event(self, p, buttons, prio):
        if self.mode == "cut":
            if not self.temp_point:
                self.temp_point = p  # 第一次点击
            else:
                direction = self.calc_direction(self.temp_point, p)
                marker = CutMarker(id, self.temp_point, direction)
                self.markers.append(marker)
                marker.to_gds(current_cell, cut_layer)
                self.temp_point = None
                self.ungrab_mouse()
        return False  # 继续传递事件
```

### 3. XML 存储格式

```xml
<?xml version="1.0"?>
<fib_project version="1.0">
    <metadata>
        <library>test_lib</library>
        <cell>top_cell</cell>
        <created>2024-12-01T10:00:00</created>
    </metadata>
    <markers>
        <cut id="CUT_0" x="100.5" y="200.3" 
             direction="down" layer="6:0"/>
        <connect id="CONNECT_0" 
                 x1="150.0" y1="250.0" 
                 x2="180.0" y2="280.0" layer="6:0"/>
        <probe id="PROBE_0" x="300.0" y="400.0" layer="6:0"/>
    </markers>
</fib_project>
```

---

## 🧪 测试清单

### 功能测试
- [ ] CUT 标记：点击两次 → X + 箭头显示，编号正确
- [ ] CONNECT 标记：点击两次 → 连线 + 端点显示，编号正确
- [ ] PROBE 标记：点击一次 → 箭头显示，编号正确
- [ ] 删除：选中标记 → 删除 → 标记消失
- [ ] 保存：创建标记 → 保存 → XML 文件生成
- [ ] 加载：重启 KLayout → 加载 → 标记恢复
- [ ] 报告：创建多个标记 → 生成报告 → HTML 包含所有信息

### 性能测试
- [ ] 创建 100 个标记 < 1 秒
- [ ] 生成报告（100 个标记）< 30 秒
- [ ] 保存 XML（100 个标记）< 2 秒
- [ ] 加载 XML（100 个标记）< 5 秒

### 跨平台测试
- [ ] Windows + KLayout 0.28+
- [ ] macOS + KLayout 0.28+
- [ ] Linux + KLayout 0.28+

---

## 📦 依赖项

```txt
# requirements.txt
PyYAML>=6.0        # 配置文件解析
Jinja2>=3.0        # HTML 模板
```

**KLayout 要求**：
- KLayout >= 0.28.0
- Python 支持已启用

---

## ✅ 完成标准

### 必须达成（MVP 交付）
- [x] 能够创建 CUT/CONNECT/PROBE 标记
- [ ] 标记存储在 GDS Layer 200-202
- [ ] 能够保存和加载 XML 状态
- [ ] 能够生成 HTML 报告
- [ ] 无崩溃运行 > 1 小时

### 可选达成（用户体验）
- [ ] 首次使用学习时间 < 30 分钟
- [ ] 标记创建响应 < 100ms
- [ ] 报告生成时间 < 30 秒

---

## 🚀 快速开始

### 步骤 1：项目初始化
```bash
cd /Users/dean/Documents/git/klayout-fib-tool
mkdir -p klayout_fib_tool
cd klayout_fib_tool
touch __init__.py plugin.py markers.py storage.py ui.py report.py config.py utils.py
```

### 步骤 2：创建配置文件
```bash
touch config.yaml
# 填入默认 Layer 映射和符号尺寸
```

### 步骤 3：实现 plugin.py
```python
# 从 pya.PluginFactory 开始，注册插件
# 参考 klayout_api_research.md 中的 Plugin 示例
```

### 步骤 4：测试基本功能
```bash
# 在 KLayout 中加载插件
# 测试能否显示工具面板
# 测试鼠标点击事件捕获
```

---

## 📚 参考文档

- `requirements.md` - 完整技术需求
- `prd.md` - 产品需求文档
- `klayout_api_research.md` - KLayout API 研究
- `mvp_plan.md` - MVP 详细规划

---

## 🎓 学习资源

### KLayout API 关键部分
1. **Plugin 开发**：`pya.Plugin`, `pya.PluginFactory`
2. **图形绘制**：`pya.Path`, `pya.Polygon`, `pya.Text`
3. **鼠标事件**：`mouse_click_event()`, `grab_mouse()`
4. **截图功能**：`view.save_image_with_options()`
5. **UI 组件**：`pya.QDialog`, `pya.QPushButton`

### 示例代码位置
- 标记符号绘制：`markers.py`
- 鼠标交互：`plugin.py`
- XML 序列化：`storage.py`
- 报告模板：`report_template.html`

---

## 📝 下一步行动

1. ✅ 阅读 `mvp_plan.md` 了解详细实现方案
2. [ ] 按照 Week 1-2 任务清单开始编码
3. [ ] 每周结束时进行测试验证
4. [ ] 第 6 周完成 MVP 并进行完整测试

**准备好开始编码了吗？** 🚀
