# Export PDF with Screenshots - 使用说明

## 功能概述

Export PDF 功能现在会为每个 marker 自动生成 3 张截图：

1. **Overview (全图)** - 显示整个布局，十字标尺指向 marker，带比例尺
2. **Zoom 2x (中等缩放)** - marker 区域放大 10 倍，带比例尺
3. **Detail (细节)** - marker 区域放大 2 倍，带比例尺

所有截图都包含比例尺，单位为微米 (μm)。

## 使用步骤

### 1. 创建 Markers

在 KLayout 中使用 FIB Tool 创建一些 markers：
- CUT markers
- CONNECT markers  
- PROBE markers
- Multi-point markers

### 2. 导出 PDF

1. 点击 FIB Panel 中的 **"Export PDF"** 按钮
2. 选择保存位置和文件名（例如：`fib_report.pdf`）
3. 等待处理完成

### 3. 查看结果

导出完成后，会生成以下文件：

```
output_directory/
├── fib_report.html          # HTML 报告（主文件）
├── fib_report.pdf           # PDF 报告（如果安装了转换工具）
└── images/
    ├── CUT_0_overview.png   # CUT_0 全图
    ├── CUT_0_zoom2x.png     # CUT_0 中等缩放
    ├── CUT_0_detail.png     # CUT_0 细节
    ├── CONNECT_0_overview.png
    ├── CONNECT_0_zoom2x.png
    ├── CONNECT_0_detail.png
    └── ...
```

## 截图说明

### Overview (全图)

```
┌─────────────────────────────────────────┐
│                                         │
│              ─────│─────                │  ← 十字标尺
│                   │                     │     指向 marker
│                   ▼                     │
│                [Marker]                 │
│                                         │
│  ├────────┤                             │  ← 比例尺
│    10 μm                                │
└─────────────────────────────────────────┘
```

- 显示整个布局
- 十字标尺指向 marker 中心位置
- 左下角显示比例尺

### Zoom 2x (中等缩放)

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│            [Marker 区域]                │
│                                         │
│                                         │
│  ├────────┤                             │  ← 比例尺
│    5 μm                                 │
└─────────────────────────────────────────┘
```

- marker 区域扩展 10 倍
- 显示 marker 周围环境
- 左下角显示比例尺

### Detail (细节)

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│          [Marker 细节]                  │
│                                         │
│                                         │
│  ├──┤                                   │  ← 比例尺
│   1 μm                                  │
└─────────────────────────────────────────┘
```

- marker 区域扩展 2 倍
- 显示 marker 最大细节
- 左下角显示比例尺

## HTML 报告格式

生成的 HTML 报告包含：

### 1. 报告头部
- 标题
- 生成时间
- Marker 总数

### 2. 统计摘要
- CUT Markers 数量
- CONNECT Markers 数量
- PROBE Markers 数量

### 3. 每个 Marker 的详细信息
- Marker ID
- 类型（CUT/CONNECT/PROBE/Multi-Point）
- 坐标信息
- 备注
- **3 张截图**（Overview, Zoom 2x, Detail）

### 4. 页脚
- 生成工具信息
- 单位说明

## PDF 转换（可选）

### 安装 PDF 转换工具

如果想生成 PDF 文件，需要安装以下工具之一：

#### 方法 1: weasyprint (推荐)

```bash
pip install weasyprint
```

#### 方法 2: wkhtmltopdf

macOS:
```bash
brew install wkhtmltopdf
```

Linux:
```bash
sudo apt-get install wkhtmltopdf
```

### 如果没有安装 PDF 工具

- 系统会自动保存 HTML 版本
- HTML 文件可以在浏览器中打开查看
- 可以使用浏览器的"打印到 PDF"功能手动转换

## 技术细节

### 截图参数

| 参数 | 值 |
|------|-----|
| 图像尺寸 | 800 × 600 像素 |
| 格式 | PNG |
| Overview 缩放 | Fit All (全图) |
| Zoom 2x 扩展 | marker 尺寸 × 10 |
| Detail 扩展 | marker 尺寸 × 2 |
| 最小尺寸 | Zoom 2x: 50μm, Detail: 10μm |

### 比例尺

- 自动计算合适的长度
- 占视图宽度的 10-20%
- 使用标准数值（1, 2, 5, 10, 20, 50, 100...）
- 位置：左下角，5% 边距
- 样式：KLayout Ruler（带刻度和数值）

### 十字标尺

- 水平线：穿过整个布局，经过 marker 中心
- 垂直线：穿过整个布局，经过 marker 中心
- 样式：简单线段
- 仅在 Overview 截图中显示

## 故障排除

### 问题：截图生成失败

**可能原因**：
- 没有活动的布局视图
- Marker 坐标无效

**解决方法**：
- 确保在 KLayout 中打开了 GDS 文件
- 检查控制台输出的错误信息

### 问题：PDF 转换失败

**可能原因**：
- 没有安装 PDF 转换工具

**解决方法**：
- 安装 weasyprint 或 wkhtmltopdf
- 或者直接使用生成的 HTML 文件

### 问题：截图太小/太大

**当前版本**：
- 缩放级别是固定的
- 后续版本会支持自定义缩放倍数

**临时解决方法**：
- 修改 `src/screenshot_export.py` 中的扩展倍数
- `zoom2_bbox = marker_bbox.enlarged(marker_bbox.width() * 5, ...)` 
- 调整数字 5 来改变缩放级别

## 示例输出

### HTML 报告预览

```html
FIB Markers Report with Screenshots
Generated: 2024-12-16 15:30:00
Total Markers: 5

┌─────────────────────────────────────┐
│ CUT Markers: 2                      │
│ CONNECT Markers: 2                  │
│ PROBE Markers: 1                    │
└─────────────────────────────────────┘

CUT_0
Type: CUT
Coordinates: (100.00,200.00) to (150.00,250.00) μm
Notes: Test cut marker

[Overview Image]  [Zoom 2x Image]  [Detail Image]

CONNECT_0
Type: CONNECT (Multi-Point)
Coordinates: 4 points: (50.00,50.00) to (200.00,200.00) μm
Notes: Multi-point connection

[Overview Image]  [Zoom 2x Image]  [Detail Image]

...
```

## 性能考虑

- 每个 marker 生成 3 张截图
- 大量 markers 时可能需要较长时间
- 建议：< 50 markers 时性能良好
- 控制台会显示处理进度

## 未来增强

计划中的功能：
- [ ] 自定义缩放级别
- [ ] 进度条显示
- [ ] 批量导出选项
- [ ] 图层可见性控制
- [ ] 自定义比例尺样式
- [ ] 自定义十字标尺颜色

## 相关文档

- `docs/EXPORT_PDF_SCREENSHOT_SPEC.md` - 技术规格
- `docs/klayout_api_research.md` - KLayout API 参考
- `src/screenshot_export.py` - 源代码