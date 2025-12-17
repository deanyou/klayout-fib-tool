# Export PDF 截图功能需求规格

## 需求对齐

### 用户需求
为每个 marker 导出 3 张截图到 HTML/PDF 报告中：
1. **全图 (Fit All)** - 显示整个布局，用十字标尺标记 marker 位置
2. **Zoom In x2** - 中等缩放级别，聚焦 marker 区域
3. **Zoom In to Marker** - 最大缩放，只显示 marker 细节

### KLayout API 调研结果

#### 核心截图 API

```python
# 方法 1: 基本截图
view.save_image("screenshot.png", width, height)

# 方法 2: 指定区域截图（推荐）
view.save_image_with_options(
    'output.png',     # 文件路径
    width, height,    # 图像尺寸
    0, 0, 0,          # 线宽超采样, 过采样, 分辨率
    bbox,             # 要截图的区域 (DBox)
    True              # 单色背景
)

# 方法 3: 获取 QImage 对象
qimage = view.get_image(width, height)
```

#### 标注/标尺 API

```python
# 创建十字标尺标注
ant = pya.Annotation()
ant.p1 = pya.DPoint(x1, y1)  # 起点
ant.p2 = pya.DPoint(x2, y2)  # 终点
ant.style = pya.Annotation.StyleRuler  # 标尺样式

# 可用样式
pya.Annotation.StyleRuler       # 标尺（带刻度）
pya.Annotation.StyleArrowEnd    # 末端箭头
pya.Annotation.StyleArrowBoth   # 双向箭头
pya.Annotation.StyleLine        # 简单线段

# 插入标注
view.insert_annotation(ant)

# 清除所有标注
view.clear_annotations()
```

#### 视图控制 API

```python
# 缩放到全部
view.zoom_fit()

# 缩放到指定区域
view.zoom_box(pya.DBox(x1, y1, x2, y2))

# 获取当前视图边界
current_box = view.box()
```

---

## 技术方案

### 方案概述

```
┌─────────────────────────────────────────────────────────────┐
│                    Export PDF 流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 遍历所有 markers                                        │
│     │                                                       │
│     ▼                                                       │
│  2. 对每个 marker 生成 3 张截图:                            │
│     ├─ 截图1: Fit All + 十字标尺                           │
│     ├─ 截图2: Zoom x2 (marker 周围区域)                    │
│     └─ 截图3: Zoom to Marker (marker 细节)                 │
│     │                                                       │
│     ▼                                                       │
│  3. 生成 HTML 报告                                          │
│     │                                                       │
│     ▼                                                       │
│  4. (可选) 转换为 PDF                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 截图详细规格

#### 截图 1: Fit All (全图)

| 属性 | 值 |
|------|-----|
| 视图范围 | 整个布局 (zoom_fit) |
| 图像尺寸 | 800 x 600 像素 |
| 标注 | 十字标尺指向 marker 中心 |
| 文件名 | `{marker_id}_overview.png` |

**十字标尺实现**:
```
                    │
                    │ (垂直线)
                    │
    ────────────────┼──────────────── (水平线)
                    │
                    │
                    ▼
                 [Marker]
```

#### 截图 2: Zoom x2 (中等缩放)

| 属性 | 值 |
|------|-----|
| 视图范围 | marker 边界框 × 10 (扩展10倍) |
| 图像尺寸 | 800 x 600 像素 |
| 标注 | 无 |
| 文件名 | `{marker_id}_zoom2x.png` |

**计算方法**:
```python
marker_bbox = get_marker_bbox(marker)
center = marker_bbox.center()
expanded_bbox = marker_bbox.enlarged(marker_bbox.width() * 5, marker_bbox.height() * 5)
```

#### 截图 3: Zoom to Marker (最大缩放)

| 属性 | 值 |
|------|-----|
| 视图范围 | marker 边界框 × 2 (扩展2倍) |
| 图像尺寸 | 800 x 600 像素 |
| 标注 | 无 |
| 文件名 | `{marker_id}_detail.png` |

**计算方法**:
```python
marker_bbox = get_marker_bbox(marker)
detail_bbox = marker_bbox.enlarged(marker_bbox.width() * 0.5, marker_bbox.height() * 0.5)
```

---

### 实现步骤

#### Step 1: 获取 Marker 边界框

```python
def get_marker_bbox(marker):
    """获取 marker 的边界框"""
    if hasattr(marker, 'points'):  # Multi-point marker
        xs = [p[0] for p in marker.points]
        ys = [p[1] for p in marker.points]
        return pya.DBox(min(xs), min(ys), max(xs), max(ys))
    elif hasattr(marker, 'x1'):  # CUT or CONNECT
        return pya.DBox(
            min(marker.x1, marker.x2), min(marker.y1, marker.y2),
            max(marker.x1, marker.x2), max(marker.y1, marker.y2)
        )
    else:  # PROBE
        r = 1.0  # 默认半径
        return pya.DBox(marker.x - r, marker.y - r, marker.x + r, marker.y + r)
```

#### Step 2: 创建十字标尺

```python
def create_crosshair_annotation(view, center_x, center_y, layout_bbox):
    """创建指向 marker 的十字标尺"""
    # 清除现有标注
    view.clear_annotations()
    
    # 水平线 (从布局左边到右边，经过 marker 中心)
    h_ant = pya.Annotation()
    h_ant.p1 = pya.DPoint(layout_bbox.left, center_y)
    h_ant.p2 = pya.DPoint(layout_bbox.right, center_y)
    h_ant.style = pya.Annotation.StyleLine
    view.insert_annotation(h_ant)
    
    # 垂直线 (从布局上边到下边，经过 marker 中心)
    v_ant = pya.Annotation()
    v_ant.p1 = pya.DPoint(center_x, layout_bbox.bottom)
    v_ant.p2 = pya.DPoint(center_x, layout_bbox.top)
    v_ant.style = pya.Annotation.StyleLine
    view.insert_annotation(v_ant)
```

#### Step 3: 截图函数

```python
def take_marker_screenshots(view, marker, output_dir):
    """为单个 marker 生成 3 张截图"""
    
    # 获取布局边界框
    cellview = view.active_cellview()
    layout_bbox = cellview.cell.dbbox()
    
    # 获取 marker 边界框
    marker_bbox = get_marker_bbox(marker)
    center = marker_bbox.center()
    
    screenshots = []
    
    # === 截图 1: Fit All + 十字标尺 ===
    view.zoom_fit()
    create_crosshair_annotation(view, center.x, center.y, layout_bbox)
    
    overview_path = os.path.join(output_dir, f"{marker.id}_overview.png")
    view.save_image(overview_path, 800, 600)
    screenshots.append(('Overview', overview_path))
    
    # 清除标注
    view.clear_annotations()
    
    # === 截图 2: Zoom x2 (中等缩放) ===
    zoom2_bbox = marker_bbox.enlarged(
        marker_bbox.width() * 5, 
        marker_bbox.height() * 5
    )
    # 确保最小尺寸
    if zoom2_bbox.width() < 50:
        zoom2_bbox = zoom2_bbox.enlarged(25, 25)
    
    view.zoom_box(zoom2_bbox)
    
    zoom2_path = os.path.join(output_dir, f"{marker.id}_zoom2x.png")
    view.save_image(zoom2_path, 800, 600)
    screenshots.append(('Zoom 2x', zoom2_path))
    
    # === 截图 3: Zoom to Marker (最大缩放) ===
    detail_bbox = marker_bbox.enlarged(
        marker_bbox.width() * 0.5, 
        marker_bbox.height() * 0.5
    )
    # 确保最小尺寸
    if detail_bbox.width() < 10:
        detail_bbox = detail_bbox.enlarged(5, 5)
    
    view.zoom_box(detail_bbox)
    
    detail_path = os.path.join(output_dir, f"{marker.id}_detail.png")
    view.save_image(detail_path, 800, 600)
    screenshots.append(('Detail', detail_path))
    
    # 恢复视图
    view.zoom_fit()
    
    return screenshots
```

#### Step 4: HTML 报告模板

```html
<!-- 每个 marker 的截图部分 -->
<div class="marker-screenshots">
    <h3>{marker.id}</h3>
    
    <div class="screenshot-row">
        <div class="screenshot">
            <h4>Overview (Fit All)</h4>
            <img src="{marker.id}_overview.png" alt="Overview">
            <p>十字标尺标记 marker 位置</p>
        </div>
        
        <div class="screenshot">
            <h4>Zoom 2x</h4>
            <img src="{marker.id}_zoom2x.png" alt="Zoom 2x">
            <p>中等缩放视图</p>
        </div>
        
        <div class="screenshot">
            <h4>Detail</h4>
            <img src="{marker.id}_detail.png" alt="Detail">
            <p>Marker 细节视图</p>
        </div>
    </div>
    
    <div class="marker-info">
        <p><strong>Type:</strong> {marker.type}</p>
        <p><strong>Coordinates:</strong> {marker.coordinates}</p>
        <p><strong>Notes:</strong> {marker.notes}</p>
    </div>
</div>
```

---

### 文件结构

```
output_directory/
├── fib_report.html           # 主报告文件
├── fib_report.pdf            # PDF 版本 (可选)
├── images/
│   ├── CUT_0_overview.png    # CUT_0 全图
│   ├── CUT_0_zoom2x.png      # CUT_0 中等缩放
│   ├── CUT_0_detail.png      # CUT_0 细节
│   ├── CONNECT_0_overview.png
│   ├── CONNECT_0_zoom2x.png
│   ├── CONNECT_0_detail.png
│   └── ...
└── style.css                 # 样式文件 (可选)
```

---

### 注意事项

1. **视图状态恢复**: 截图完成后需要恢复原始视图状态
2. **标注清理**: 每次截图后清除标注，避免影响下一张
3. **边界框计算**: 需要处理 multi-point markers 的边界框
4. **最小尺寸**: 确保缩放区域有最小尺寸，避免过度放大
5. **性能**: 大量 markers 时可能需要进度提示

---

### 可选增强

1. **自定义缩放级别**: 允许用户配置缩放倍数
2. **图像质量设置**: DPI、抗锯齿等
3. **标注样式**: 自定义十字标尺颜色、线宽
4. **批量导出**: 进度条显示
5. **图层控制**: 截图时隐藏/显示特定图层

---

## 需求确认 ✓

| 需求项 | 确认结果 |
|--------|---------|
| 十字标尺样式 | 简单线段，使用 KLayout 自带的 Annotation 系统 |
| 缩放级别 | 当前设定，后期可自定义倍数 |
| 图像尺寸 | 800×600 (A4 纸宽度可放下) |
| 输出格式 | HTML 优先 |
| 坐标网格 | 需要 |
| 比例尺 | 需要，单位 μm |

---

## 比例尺实现方案

### KLayout Annotation API

```python
# 创建比例尺标注
scale_bar = pya.Annotation()
scale_bar.p1 = pya.DPoint(x1, y1)  # 起点
scale_bar.p2 = pya.DPoint(x2, y2)  # 终点
scale_bar.style = pya.Annotation.StyleRuler  # 标尺样式（带刻度和数值）

# 插入标注
view.insert_annotation(scale_bar)
```

### 比例尺位置

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│              [Layout View]              │
│                                         │
│                                         │
│  ├────────────┤                         │
│     10 μm        ← 比例尺 (左下角)      │
└─────────────────────────────────────────┘
```

### 比例尺长度计算

```python
def calculate_scale_bar_length(view_bbox):
    """计算合适的比例尺长度"""
    view_width = view_bbox.width()
    
    # 比例尺占视图宽度的 10-20%
    target_length = view_width * 0.15
    
    # 取整到合适的数值 (1, 2, 5, 10, 20, 50, 100, ...)
    nice_values = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    
    for val in nice_values:
        if val >= target_length * 0.5:
            return val
    
    return nice_values[-1]
```

### 完整的标注创建函数

```python
def create_marker_annotations(view, marker_center, layout_bbox, view_bbox):
    """创建十字标尺和比例尺"""
    view.clear_annotations()
    
    # === 十字标尺 (指向 marker) ===
    # 水平线
    h_ruler = pya.Annotation()
    h_ruler.p1 = pya.DPoint(layout_bbox.left, marker_center.y)
    h_ruler.p2 = pya.DPoint(layout_bbox.right, marker_center.y)
    h_ruler.style = pya.Annotation.StyleLine
    view.insert_annotation(h_ruler)
    
    # 垂直线
    v_ruler = pya.Annotation()
    v_ruler.p1 = pya.DPoint(marker_center.x, layout_bbox.bottom)
    v_ruler.p2 = pya.DPoint(marker_center.x, layout_bbox.top)
    v_ruler.style = pya.Annotation.StyleLine
    view.insert_annotation(v_ruler)
    
    # === 比例尺 (左下角) ===
    scale_length = calculate_scale_bar_length(view_bbox)
    
    # 比例尺位置: 左下角，留出 5% 边距
    margin_x = view_bbox.width() * 0.05
    margin_y = view_bbox.height() * 0.05
    
    scale_x = view_bbox.left + margin_x
    scale_y = view_bbox.bottom + margin_y
    
    scale_bar = pya.Annotation()
    scale_bar.p1 = pya.DPoint(scale_x, scale_y)
    scale_bar.p2 = pya.DPoint(scale_x + scale_length, scale_y)
    scale_bar.style = pya.Annotation.StyleRuler  # 带刻度和数值
    view.insert_annotation(scale_bar)
```

---

## 最终实现计划

### 文件结构

```
src/
├── screenshot_export.py    # 新文件: 截图导出功能
└── fib_panel.py           # 修改: 调用截图导出

output/
├── fib_report.html        # HTML 报告
└── images/
    ├── CUT_0_overview.png
    ├── CUT_0_zoom2x.png
    ├── CUT_0_detail.png
    └── ...
```

### 核心函数

```python
# screenshot_export.py

def export_markers_with_screenshots(markers, view, output_dir):
    """导出所有 markers 的截图和 HTML 报告"""
    pass

def take_marker_screenshots(marker, view, output_dir):
    """为单个 marker 生成 3 张截图"""
    pass

def create_crosshair_annotation(view, center, layout_bbox):
    """创建十字标尺"""
    pass

def create_scale_bar(view, view_bbox):
    """创建比例尺"""
    pass

def generate_html_report(markers, screenshots, output_path):
    """生成 HTML 报告"""
    pass
```

---

## 下一步

需求已完全确认，可以开始编码实现。是否现在开始？