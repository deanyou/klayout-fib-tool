# Rearrange Markers Feature / 重新排列标记功能

## Overview / 概述

The "Rearrange New Order" feature allows users to automatically renumber markers of the same type (CUT, CONNECT, PROBE) based on their current position in the marker list.

"重新排列顺序"功能允许用户根据标记列表中的当前位置，自动重新编号相同类型的标记（CUT、CONNECT、PROBE）。

## How to Use / 使用方法

### Step 1: Reorder Markers / 步骤1：重新排列标记

First, arrange your markers in the desired order using one of these methods:

首先，使用以下方法之一按所需顺序排列标记：

1. **Move Up/Down Buttons** / **上移/下移按钮**
   - Select a marker in the list
   - Click "↑ Move Up" or "↓ Move Down" buttons
   - 在列表中选择一个标记
   - 点击"↑ 上移"或"↓ 下移"按钮

2. **Drag and Drop** (if supported) / **拖放**（如果支持）
   - Click and drag markers to reorder them
   - 点击并拖动标记以重新排序

### Step 2: Rearrange / 步骤2：重新排列

1. Right-click on any marker in the list
2. Select **"Rearrange New Order"** from the context menu
3. Review the confirmation dialog showing how many markers will be renumbered
4. Click "Yes" to proceed

---

1. 右键点击列表中的任何标记
2. 从上下文菜单中选择 **"Rearrange New Order"**
3. 查看确认对话框，显示将重新编号多少个标记
4. 点击"是"继续

## What It Does / 功能说明

The feature will:

该功能将：

1. **Group markers by type** / **按类型分组标记**
   - CUT markers
   - CONNECT markers  
   - PROBE markers

2. **Renumber each group from 0** / **从0开始重新编号每组**
   - Based on current list order
   - 基于当前列表顺序

3. **Update all references** / **更新所有引用**
   - Marker IDs in the panel
   - Coordinate texts in the GDS layout
   - 面板中的标记ID
   - GDS布局中的坐标文本

4. **Reset smart counters** / **重置智能计数器**
   - Ensures next new marker uses correct number
   - 确保下一个新标记使用正确的编号

## Example / 示例

### Before Rearrange / 重新排列前

```
CONNECT_1 - (100, 100) to (200, 200)
CONNECT_0 - (50, 50) to (150, 150)
CONNECT_3 - (300, 300) to (400, 400)
CUT_2 - (250, 250) to (350, 350)
CUT_0 - (10, 10) to (20, 20)
```

### After Moving and Rearranging / 移动和重新排列后

If you move markers to this order and then click "Rearrange New Order":

如果您将标记移动到此顺序，然后点击"重新排列顺序"：

```
CONNECT_0 - (50, 50) to (150, 150)      ← Was CONNECT_0, stays CONNECT_0
CONNECT_1 - (100, 100) to (200, 200)    ← Was CONNECT_1, stays CONNECT_1
CONNECT_2 - (300, 300) to (400, 400)    ← Was CONNECT_3, becomes CONNECT_2
CUT_0 - (10, 10) to (20, 20)            ← Was CUT_0, stays CUT_0
CUT_1 - (250, 250) to (350, 350)        ← Was CUT_2, becomes CUT_1
```

## Menu Location / 菜单位置

The "Rearrange New Order" option appears in the marker context menu:

"重新排列顺序"选项出现在标记上下文菜单中：

```
Right-click on marker → Context Menu:
  Add Notes
  Zoom to Fit
  Copy Coordinates
  Rename Marker
  Rearrange New Order    ← New feature / 新功能
  ────────────────────
  ↑ Move Up
  ↓ Move Down
  ────────────────────
  Delete Marker
```

## Technical Details / 技术细节

### Implementation / 实现

- **File**: `python/fib_tool/marker_menu.py`
- **Method**: `rearrange_markers()`
- **Line**: ~420-520

### Features / 特性

1. **Type-based grouping** / **基于类型的分组**
   - Handles CUT, CONNECT, and PROBE markers separately
   - Preserves relative order within each type
   - 分别处理CUT、CONNECT和PROBE标记
   - 保留每种类型内的相对顺序

2. **Two-phase renaming to avoid conflicts** / **两阶段重命名避免冲突**
   - Phase 1: Rename all markers to temporary names (TEMP_TYPE_N)
   - Phase 2: Rename from temporary to final names (TYPE_N)
   - This prevents conflicts when markers swap positions
   - 阶段1：将所有标记重命名为临时名称（TEMP_TYPE_N）
   - 阶段2：从临时名称重命名为最终名称（TYPE_N）
   - 这可以防止标记交换位置时的冲突

3. **Multi-point marker support** / **多点标记支持**
   - Works with both regular and multi-point markers
   - 适用于常规和多点标记

4. **GDS layout synchronization** / **GDS布局同步**
   - Updates coordinate texts in all layers
   - Uses search-and-replace across entire layout
   - 更新所有图层中的坐标文本
   - 在整个布局中使用搜索和替换

5. **Smart counter reset** / **智能计数器重置**
   - Automatically resets counters after rearrange
   - Next new marker will use correct number
   - 重新排列后自动重置计数器
   - 下一个新标记将使用正确的编号

### Error Handling / 错误处理

- Validates marker types before renumbering
- Shows confirmation dialog with summary
- Provides detailed console logging
- Handles exceptions gracefully

---

- 重新编号前验证标记类型
- 显示带摘要的确认对话框
- 提供详细的控制台日志
- 优雅地处理异常

## Related Features / 相关功能

- **Rename Marker**: Rename individual markers manually
- **Move Up/Down**: Change marker order in the list
- **Smart Counter**: Automatically finds next available number

---

- **重命名标记**：手动重命名单个标记
- **上移/下移**：更改列表中的标记顺序
- **智能计数器**：自动查找下一个可用编号

## Notes / 注意事项

1. This operation cannot be undone. Save your project before rearranging if needed.
2. All markers of the same type will be renumbered, not just selected ones.
3. The feature only affects marker IDs and coordinate texts, not marker geometry or positions.
4. **Conflict-free renaming**: Uses a two-phase approach to prevent naming conflicts when markers swap positions (e.g., CONNECT_1 ↔ CONNECT_0).

---

1. 此操作无法撤消。如需要，请在重新排列前保存项目。
2. 相同类型的所有标记都将重新编号，而不仅仅是选定的标记。
3. 该功能仅影响标记ID和坐标文本，不影响标记几何形状或位置。
4. **无冲突重命名**：使用两阶段方法防止标记交换位置时的命名冲突（例如 CONNECT_1 ↔ CONNECT_0）。

## Bug Fix History / Bug修复历史

### Issue 1: Naming Conflicts During Rearrange / 问题1：重新排列时的命名冲突

**Problem**: When rearranging markers, if CONNECT_1 needs to become CONNECT_0 while CONNECT_0 exists, direct renaming causes conflicts, resulting in duplicate names.

**问题**：重新排列标记时，如果 CONNECT_1 需要变成 CONNECT_0，而 CONNECT_0 已存在，直接重命名会导致冲突，产生重复的名称。

**Solution**: Implemented two-phase renaming strategy:
- Phase 1: All markers renamed to temporary names (TEMP_CUT_0, TEMP_CONNECT_1, etc.)
- Phase 2: Temporary names renamed to final names (CUT_0, CONNECT_1, etc.)

**解决方案**：实现两阶段重命名策略：
- 阶段1：所有标记重命名为临时名称（TEMP_CUT_0、TEMP_CONNECT_1等）
- 阶段2：临时名称重命名为最终名称（CUT_0、CONNECT_1等）

**Example**:
```
Before:  CONNECT_1, CONNECT_0
Phase 1: TEMP_CONNECT_0, TEMP_CONNECT_1  (no conflicts)
Phase 2: CONNECT_0, CONNECT_1            (safe to rename)
```

### Issue 2: Temporary Names Left Behind / 问题2：残留临时名称

**Problem**: When reordering markers like 0→2, 1→1, 2→0, markers that don't need renaming (1→1) were skipped in Phase 1, but this left TEMP_CUT_2 behind.

**问题**：当重新排列标记如 0→2, 1→1, 2→0 时，不需要重命名的标记（1→1）在阶段1被跳过，但这会留下 TEMP_CUT_2 残留。

**Solution**: Always rename ALL markers in both phases, even if the final name equals the original name. This ensures complete cleanup.

**解决方案**：在两个阶段中始终重命名所有标记，即使最终名称等于原始名称。这确保完全清理。

**Example**:
```
Before:     CUT_0, CUT_1, CUT_2
Reorder to: CUT_2, CUT_1, CUT_0

Phase 1 (ALL markers):
  CUT_0 -> TEMP_CUT_2
  CUT_1 -> TEMP_CUT_1  (even though final will be CUT_1)
  CUT_2 -> TEMP_CUT_0

Phase 2 (ALL markers):
  TEMP_CUT_2 -> CUT_2
  TEMP_CUT_1 -> CUT_1  (no TEMP names left behind!)
  TEMP_CUT_0 -> CUT_0
```
