# KLayout FIB Tool - Technical Requirements Document

## 1. Overview

### 1.1 Purpose
开发一个 KLayout 插件，用于在 GDSII 版图上标注 FIB（Focused Ion Beam，聚焦离子束）操作，包括切断连线（CUT）、连接连线（CONNECT）和探针点（PROBE）功能。

### 1.2 Background
FIB 技术在芯片调试和故障分析中广泛使用。工程师需要在版图上精确标注需要进行 FIB 操作的位置，并生成清晰的操作指导文档供 FIB 实验室执行。

### 1.3 Reference
本工具参考 Skipper EDA 软件的 FIB 功能设计，适配 KLayout 平台。

---

## 2. Functional Requirements

### 2.1 FIB 操作标注功能

#### 2.1.1 CUT（切断）操作
| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-CUT-001 | 用户可在版图上点击指定位置创建切断标记 | P0 |
| FR-CUT-002 | 切断标记需显示切断方向（上/下/左/右） | P0 |
| FR-CUT-003 | 切断标记需记录精确坐标 (X, Y) | P0 |
| FR-CUT-004 | 切断标记需记录目标 Layer 信息 | P0 |
| FR-CUT-005 | 切断操作使用专用 Layer Number 存储（可配置） | P0 |
| FR-CUT-006 | 支持为切断操作添加自定义标签/备注 | P1 |
| FR-CUT-007 | 支持编辑已创建的切断标记 | P1 |
| FR-CUT-008 | 支持删除已创建的切断标记 | P0 |

#### 2.1.2 CONNECT（连接）操作
| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-CON-001 | 用户可在版图上点击两点创建连接标记 | P0 |
| FR-CON-002 | 连接标记需显示起点和终点坐标 | P0 |
| FR-CON-003 | 连接标记需绘制连接路径线 | P0 |
| FR-CON-004 | 连接操作使用专用 Layer Number 存储（可配置） | P0 |
| FR-CON-005 | 支持为连接操作添加自定义标签/备注 | P1 |
| FR-CON-006 | 支持编辑已创建的连接标记 | P1 |
| FR-CON-007 | 支持删除已创建的连接标记 | P0 |
| FR-CON-008 | 连接路径支持多段折线（可选） | P2 |

#### 2.1.3 PROBE（探针）操作
| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-PRB-001 | 用户可在版图上点击指定位置创建探针标记 | P0 |
| FR-PRB-002 | 探针标记需记录精确坐标 (X, Y) | P0 |
| FR-PRB-003 | 探针标记需记录目标 Layer 信息 | P0 |
| FR-PRB-004 | 探针操作使用专用 Layer Number 存储（可配置） | P0 |
| FR-PRB-005 | 支持为探针操作添加自定义标签/备注 | P1 |
| FR-PRB-006 | 支持编辑已创建的探针标记 | P1 |
| FR-PRB-007 | 支持删除已创建的探针标记 | P0 |

### 2.2 分组管理功能

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-GRP-001 | 支持创建操作分组（Group） | P0 |
| FR-GRP-002 | 每个分组可包含多个 CUT/CONNECT/PROBE 操作 | P0 |
| FR-GRP-003 | 支持为分组添加名称和备注 | P0 |
| FR-GRP-004 | 支持分组的层级管理（树形结构显示） | P1 |
| FR-GRP-005 | 支持分组的显示/隐藏控制 | P1 |
| FR-GRP-006 | 支持分组的导入/导出 | P1 |

### 2.3 可视化功能

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-VIS-001 | CUT 标记使用 X 符号 + 箭头表示切断位置和方向 | P0 |
| FR-VIS-002 | CONNECT 标记使用连线 + 端点符号表示 | P0 |
| FR-VIS-003 | PROBE 标记使用箭头符号表示探针位置 | P0 |
| FR-VIS-004 | 标记符号大小随缩放级别自适应 | P1 |
| FR-VIS-005 | 支持自定义标记颜色 | P2 |
| FR-VIS-006 | 支持显示操作编号标签（如 CUT_0, CONNECT_1） | P0 |
| FR-VIS-007 | 支持坐标标签显示 | P1 |

### 2.4 数据存储与导出功能

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-DAT-001 | FIB 标记数据存储在 GDS 文件的专用 Layer 中 | P0 |
| FR-DAT-002 | 支持导出 FIB 操作状态为 XML/JSON 格式 | P0 |
| FR-DAT-003 | 支持从 XML/JSON 文件导入 FIB 操作状态 | P0 |
| FR-DAT-004 | 支持生成 HTML 格式的 FIB 操作报告 | P0 |
| FR-DAT-005 | 支持生成 PDF 格式的 FIB 操作报告 | P1 |
| FR-DAT-006 | 支持导出包含 FIB 标记的 GDS 文件 | P0 |
| FR-DAT-007 | 导出 GDS 支持指定区域裁剪 | P1 |
| FR-DAT-008 | 导出 GDS 支持缩放因子设置 | P2 |

### 2.5 报告生成功能

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| FR-RPT-001 | 报告包含设计基本信息（Library, Cell, BBox） | P0 |
| FR-RPT-002 | 报告包含所有 FIB 操作的详细列表 | P0 |
| FR-RPT-003 | 每个操作包含三级视图截图：全局视图、局部视图、详细视图 | P0 |
| FR-RPT-004 | 截图显示范围和比例可配置 | P1 |
| FR-RPT-005 | 报告包含操作坐标和 Layer 信息 | P0 |
| FR-RPT-008 | PDF 报告支持图片放大功能，放大倍数可调 | P0 |
| FR-RPT-009 | 图片放大倍数范围：1x - 10x，步进 0.5x | P0 |
| FR-RPT-010 | 支持为每个视图级别（全局/局部/详细）单独设置放大倍数 | P1 |
| FR-RPT-006 | 报告包含分组信息和备注 | P0 |
| FR-RPT-007 | 支持自定义报告模板 | P2 |

---

## 3. Non-Functional Requirements

### 3.1 性能要求

| 需求ID | 描述 | 指标 |
|--------|------|------|
| NFR-PER-001 | 标记创建响应时间 | < 100ms |
| NFR-PER-002 | 报告生成时间（100 个操作） | < 30s |
| NFR-PER-003 | 支持的最大操作数量 | ≥ 1000 |
| NFR-PER-004 | GDS 文件大小增量（每 100 个标记） | < 1MB |

### 3.2 兼容性要求

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| NFR-CMP-001 | 支持 KLayout 0.28.0 及以上版本 | P0 |
| NFR-CMP-002 | 支持 Windows/Linux/macOS 平台 | P0 |
| NFR-CMP-003 | 支持 Python 3.8+ | P0 |
| NFR-CMP-004 | 兼容标准 GDSII 文件格式 | P0 |
| NFR-CMP-005 | 兼容 OASIS 文件格式 | P2 |

### 3.3 可用性要求

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| NFR-USA-001 | 提供图形用户界面（GUI） | P0 |
| NFR-USA-002 | 支持键盘快捷键操作 | P1 |
| NFR-USA-003 | 提供操作撤销/重做功能 | P1 |
| NFR-USA-004 | 提供用户操作手册 | P1 |

### 3.4 可维护性要求

| 需求ID | 描述 | 优先级 |
|--------|------|--------|
| NFR-MNT-001 | 代码模块化设计，便于扩展 | P0 |
| NFR-MNT-002 | 提供配置文件管理 Layer 映射 | P0 |
| NFR-MNT-003 | 提供日志记录功能 | P1 |

---

## 4. Technical Specifications

### 4.1 Layer Number 分配方案

| 操作类型 | 默认 Layer | 默认 Datatype | 用途 |
|----------|------------|---------------|------|
| CUT | 200 | 0 | 切断标记符号 |
| CUT | 200 | 1 | 切断方向箭头 |
| CUT | 200 | 10 | 切断文本标签 |
| CONNECT | 201 | 0 | 连接路径线 |
| CONNECT | 201 | 1 | 连接端点符号 |
| CONNECT | 201 | 10 | 连接文本标签 |
| PROBE | 202 | 0 | 探针标记符号 |
| PROBE | 202 | 10 | 探针文本标签 |
| ANNOTATION | 203 | 0 | 通用标注 |
| GROUP_BOX | 204 | 0 | 分组边界框 |

*注：Layer Number 可通过配置文件自定义*

### 4.2 数据存储格式

#### 4.2.1 XML 状态文件结构
```xml
<?xml version="1.0" encoding="UTF-8"?>
<fib_project>
    <metadata>
        <library>lib_name</library>
        <cell>cell_name</cell>
        <created>2024-01-01T12:00:00</created>
        <modified>2024-01-02T12:00:00</modified>
    </metadata>
    <groups>
        <group id="g1" name="Group1">
            <notes>备注信息</notes>
            <bbox>x1,y1,x2,y2</bbox>
            <operations>
                <cut id="CUT_0">
                    <position x="223.615" y="65.7"/>
                    <direction>down</direction>
                    <layer>6</layer>
                    <tags>tag1,tag2</tags>
                </cut>
                <connect id="CONNECT_0">
                    <start x="100.0" y="200.0"/>
                    <end x="150.0" y="250.0"/>
                    <layer>6</layer>
                </connect>
                <probe id="PROBE_0">
                    <position x="300.0" y="400.0"/>
                    <layer>6</layer>
                </probe>
            </operations>
        </group>
    </groups>
</fib_project>
```

### 4.3 标记符号规格

#### 4.3.1 CUT 标记
- 基本符号：X 形（两条交叉线）
- 尺寸：可配置，默认 2μm × 2μm
- 方向箭头：从 X 中心指向切断方向
- 标签位置：箭头末端

#### 4.3.2 CONNECT 标记
- 连接线：从起点到终点的路径
- 端点符号：圆形或方形标记
- 尺寸：端点直径默认 1μm
- 标签位置：路径中点

#### 4.3.3 PROBE 标记
- 基本符号：向下箭头（↓）
- 尺寸：可配置，默认高度 3μm
- 标签位置：箭头上方

---

## 5. Interface Requirements

### 5.1 用户界面

#### 5.1.1 主工具栏
- New：创建新的 FIB 项目
- Open：打开已有 FIB 状态文件
- Save：保存当前 FIB 状态
- Close：关闭 FIB 工具

#### 5.1.2 操作面板
- Cut 按钮：激活切断标记模式
- Connect 按钮：激活连接标记模式
- Probe 按钮：激活探针标记模式
- 取消当前操作按钮

#### 5.1.3 分组管理面板
- 分组树形列表
- 新建分组按钮
- 删除分组按钮
- 分组属性编辑

#### 5.1.4 属性面板
- 显示选中操作的详细信息
- 支持编辑操作属性

#### 5.1.5 导出面板
- GDS 导出选项
- 报告导出选项
- 区域选择工具

### 5.2 配置文件接口

配置文件格式：YAML 或 JSON

```yaml
# fib_config.yaml
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

symbols:
  cut:
    size: 2.0  # μm
    line_width: 0.1
  connect:
    endpoint_size: 1.0
    line_width: 0.1
  probe:
    size: 3.0
    line_width: 0.1

report:
  screenshot_dpi: 150
  overview_scale: 0.1
  local_scale: 1.0
  detail_scale: 5.0
  
  # PDF 图片放大设置
  pdf_image_zoom:
    enabled: true
    default_zoom: 2.0        # 默认放大倍数
    min_zoom: 1.0            # 最小放大倍数
    max_zoom: 10.0           # 最大放大倍数
    zoom_step: 0.5           # 放大步进值
    per_view_zoom:           # 各视图级别独立放大设置
      overview: 1.5          # 全局视图放大倍数
      local: 2.0             # 局部视图放大倍数
      detail: 3.0            # 详细视图放大倍数
```

---

## 6. Constraints and Assumptions

### 6.1 约束条件
1. 必须在 KLayout 环境中运行
2. 使用 KLayout 的 Python API (pya 模块)
3. 不能修改原始设计数据，FIB 标记存储在独立 Layer
4. 生成的 GDS 文件必须符合 GDSII 标准

### 6.2 假设条件
1. 用户具备基本的版图查看操作能力
2. 用户了解 FIB 操作的基本概念
3. 系统已安装 KLayout 0.28.0 或更高版本
4. 系统已安装所需的 Python 依赖库

---

## 7. Dependencies

### 7.1 外部依赖

| 依赖项 | 版本要求 | 用途 |
|--------|----------|------|
| KLayout | ≥ 0.28.0 | 核心平台 |
| Python | ≥ 3.8 | 脚本语言 |
| Jinja2 | ≥ 3.0 | HTML 报告模板 |
| PyYAML | ≥ 6.0 | 配置文件解析 |
| Pillow | ≥ 9.0 | 图像处理（可选） |
| ReportLab | ≥ 3.6 | PDF 生成（可选） |

### 7.2 KLayout API 依赖
- pya.Layout
- pya.Cell
- pya.Layer
- pya.Box, pya.Path, pya.Polygon, pya.Text
- pya.Action
- pya.QDialog (Qt bindings)

---

## 8. Glossary

| 术语 | 定义 |
|------|------|
| FIB | Focused Ion Beam，聚焦离子束，用于芯片微修和故障分析 |
| CUT | 切断操作，使用 FIB 切断金属连线 |
| CONNECT | 连接操作，使用 FIB 沉积金属连接两点 |
| PROBE | 探针操作，使用 FIB 露出金属层以供探针测试 |
| Layer | GDS 文件中的图层 |
| Datatype | GDS 文件中图层的数据类型 |
| BBox | Bounding Box，边界框 |

---

## Document History

| 版本 | 日期 | 作者 | 描述 |
|------|------|------|------|
| 0.1 | 2024-12-01 | - | 初始版本 |
