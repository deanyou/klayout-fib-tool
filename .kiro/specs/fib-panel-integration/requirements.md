# FIB Tool 面板集成需求文档

## Introduction

本文档描述将 FIB Tool 集成为 KLayout 主窗口侧边面板的需求。参考截图中的 FIB 面板设计，实现一个功能完整的 FIB 标记管理界面。

## Glossary

- **FIB**: Focused Ion Beam，聚焦离子束
- **Panel**: KLayout 主窗口中的可停靠面板
- **Marker**: FIB 操作标记（CUT/CONNECT/PROBE）
- **Group**: 标记分组，用于组织相关的 FIB 操作
- **Corner Picture**: 角落截图，用于定位参考

## Requirements

### Requirement 1: 面板创建与停靠

**User Story:** As a FIB 工程师, I want to have a dedicated FIB panel docked in KLayout's main window, so that I can access FIB tools without opening separate dialogs.

#### Acceptance Criteria

1. WHEN the FIB Tool is loaded THEN the system SHALL create a dockable panel in KLayout's main window
2. WHEN the panel is created THEN the system SHALL allow docking to left, right, or floating positions
3. WHEN the user closes the panel THEN the system SHALL provide a way to reopen it from the menu
4. WHEN KLayout restarts THEN the system SHALL restore the panel's last position and state

### Requirement 2: 项目管理功能

**User Story:** As a FIB 工程师, I want to create and manage FIB projects, so that I can organize my work efficiently.

#### Acceptance Criteria

1. WHEN the user clicks "New" button THEN the system SHALL create a new FIB project
2. WHEN the user clicks "Close" button THEN the system SHALL close the current project with confirmation
3. WHEN the user clicks "More" dropdown THEN the system SHALL show additional project options (Save, Load, Export)
4. WHEN the user clicks "GenData" button THEN the system SHALL generate FIB data output

### Requirement 3: 标记创建功能

**User Story:** As a FIB 工程师, I want to create CUT, CONNECT, and PROBE markers by clicking buttons and then clicking on the layout, so that I can mark FIB operations quickly.

#### Acceptance Criteria

1. WHEN the user clicks "Cut" button THEN the system SHALL activate CUT marker creation mode
2. WHEN the user clicks "Connect" button THEN the system SHALL activate CONNECT marker creation mode and highlight the button
3. WHEN the user clicks "Probe" button THEN the system SHALL activate PROBE marker creation mode
4. WHEN a marker is created THEN the system SHALL add it to the FIB Doc structure tree

### Requirement 4: 文档结构树视图

**User Story:** As a FIB 工程师, I want to see all my FIB markers organized in a tree structure, so that I can easily navigate and manage them.

#### Acceptance Criteria

1. WHEN markers are created THEN the system SHALL display them in a hierarchical tree view
2. WHEN a marker is selected in the tree THEN the system SHALL highlight it in the layout view
3. WHEN the user expands a marker node THEN the system SHALL show marker details (coordinates, layers, notes, screenshots)
4. WHEN the user double-clicks a marker THEN the system SHALL zoom to that marker in the layout

### Requirement 5: 标记详情显示

**User Story:** As a FIB 工程师, I want to see detailed information about each marker, so that I can verify the FIB operation parameters.

#### Acceptance Criteria

1. WHEN a CUT marker is expanded THEN the system SHALL show its coordinates and target layer
2. WHEN a CONNECT marker is expanded THEN the system SHALL show start/end points (pts) and layers for both endpoints
3. WHEN a PROBE marker is expanded THEN the system SHALL show its position and target layer
4. WHEN a marker has notes THEN the system SHALL display the notes in the tree

### Requirement 6: 分组和组织功能

**User Story:** As a FIB 工程师, I want to group related markers together, so that I can organize complex FIB operations.

#### Acceptance Criteria

1. WHEN the user clicks "Group" button THEN the system SHALL create a new group for selected markers
2. WHEN the user clicks "CornerPicture" button THEN the system SHALL capture corner reference screenshots
3. WHEN the user clicks "Edit" button THEN the system SHALL allow editing the selected marker or group
4. WHEN the user checks "SelectAll" THEN the system SHALL select all markers in the current view

### Requirement 7: 报告和布局选项卡

**User Story:** As a FIB 工程师, I want to switch between Report and Layout views, so that I can review my work from different perspectives.

#### Acceptance Criteria

1. WHEN the user clicks "Report" tab THEN the system SHALL show the report generation interface
2. WHEN the user clicks "Layout" tab THEN the system SHALL show the layout-related options
3. WHEN in Report view THEN the system SHALL provide options to generate HTML/PDF reports

### Requirement 8: AutoCutGroupRegion 功能

**User Story:** As a FIB 工程师, I want to define margins for automatic cut grouping, so that I can batch process similar operations.

#### Acceptance Criteria

1. WHEN the user enables AutoCutGroupRegion THEN the system SHALL group nearby cut markers automatically
2. WHEN the user sets MarginX value THEN the system SHALL use this horizontal margin for grouping
3. WHEN the user sets MarginY value THEN the system SHALL use this vertical margin for grouping

### Requirement 9: 右键上下文菜单

**User Story:** As a FIB 工程师, I want to right-click on markers in the tree view to access common operations, so that I can quickly manage markers without navigating through menus.

#### Acceptance Criteria

1. WHEN the user right-clicks on a marker (CUT/CONNECT/PROBE) in the tree view THEN the system SHALL display a context menu with the following options:
   - **Fit**: 缩放视图以适应该标记
   - **Delete**: 删除该标记
   - **Rename**: 重命名该标记
   - **Edit Notes**: 编辑标记的备注信息
   - **Edit Screenshots**: 编辑/管理标记的截图

2. WHEN the user clicks "Fit" THEN the system SHALL zoom the layout view to center on and fit the selected marker

3. WHEN the user clicks "Delete" THEN the system SHALL:
   - Show a confirmation dialog
   - Remove the marker from the layout (GDS layer)
   - Remove the marker from the tree view
   - Update the marker counter

4. WHEN the user clicks "Rename" THEN the system SHALL:
   - Show a text input dialog with the current marker name
   - Update the marker ID in the data model
   - Update the marker label in the GDS layout
   - Update the tree view display

5. WHEN the user clicks "Edit Notes" THEN the system SHALL:
   - Show a text editor dialog for entering/editing notes
   - Save the notes to the marker's data model
   - Display notes count or preview in the tree view

6. WHEN the user clicks "Edit Screenshots" THEN the system SHALL:
   - Show a screenshot management dialog
   - Allow adding new screenshots (capture from current view)
   - Allow deleting existing screenshots
   - Allow viewing screenshots in full size
   - Display screenshot count in the tree view

7. WHEN the user right-clicks on a Group node THEN the system SHALL show additional options:
   - **Expand All**: 展开组内所有节点
   - **Collapse All**: 折叠组内所有节点
   - **Delete Group**: 删除整个组（可选择是否删除组内标记）
   - **Rename Group**: 重命名组

8. WHEN the user right-clicks on "General Notes" THEN the system SHALL show:
   - **Edit**: 编辑通用备注

9. WHEN the user right-clicks on "Corner Screenshots" THEN the system SHALL show:
   - **Add Screenshot**: 添加角落截图
   - **View All**: 查看所有角落截图
   - **Clear All**: 清除所有角落截图

## Technical Research Notes

### KLayout Panel API 研究方向

1. **QDockWidget 集成**
   - KLayout 使用 Qt 框架
   - 可以通过 `pya.QDockWidget` 创建可停靠面板
   - 需要研究如何将面板添加到主窗口

2. **主窗口访问**
   - `pya.Application.instance().main_window()` 获取主窗口
   - 主窗口是 `QMainWindow` 类型
   - 可以使用 `addDockWidget()` 方法添加面板

3. **面板内容**
   - 使用 Qt Widgets 构建界面
   - `QTreeWidget` 用于文档结构树
   - `QPushButton` 用于操作按钮
   - `QTabWidget` 用于 Report/Layout 选项卡

4. **事件处理**
   - 面板按钮点击事件
   - 树节点选择事件
   - 与现有 Plugin 系统的集成

### 参考截图分析

从提供的截图可以看到：

```
┌─────────────────────────────────────┐
│ FIB                            [□][X]│
├─────────────────────────────────────┤
│ [New] [Close] [More ▼]    [GenData] │
├─────────────────────────────────────┤
│ Current FIB Project                  │
│ ┌─────────┬─────────┐               │
│ │ Report  │ Layout  │               │
│ └─────────┴─────────┘               │
├─────────────────────────────────────┤
│ ☑ AutoCutGroupRegion                │
│ MarginX: [0.0    ] MarginY: [0.0  ] │
├─────────────────────────────────────┤
│ Add                                  │
│ [Cut] [Connect] [Probe]             │
├─────────────────────────────────────┤
│ FIB Doc structure                    │
│ [Group] [CornerPicture] [Edit] ☐SelectAll│
├─────────────────────────────────────┤
│ ├─ General Notes                     │
│ ├─ Corner Screenshots          0     │
│ ├─ □ function1_fix                   │
│ │   ├─ box    (507.441,1636.843...)  │
│ │   ├─ layers L1.0                   │
│ │   ├─ Notes                         │
│ │   └─ Screenshots             2     │
│ ├─ ⊕ CUT_0                          │
│ └─ ⊟ CONNECT_0                      │
│     ├─ pts    (521.111,1646.241)... │
│     ├─ layers L1.0;L1.0             │
│     ├─ Notes                         │
│     └─ Screenshots             3     │
└─────────────────────────────────────┘
```

### 实现优先级

1. **Phase 1: 基础面板**
   - 创建可停靠面板
   - 添加基本按钮（Cut/Connect/Probe）
   - 与现有 Plugin 系统集成

2. **Phase 2: 文档结构树**
   - 实现树视图
   - 显示标记列表
   - 标记详情展开

3. **Phase 3: 项目管理**
   - New/Close/Save/Load 功能
   - 报告生成
   - 数据导出

4. **Phase 4: 高级功能**
   - 分组功能
   - 角落截图
   - AutoCutGroupRegion
