# 面板多点坐标显示修复

## 问题描述

用户反馈：HTML 报告中多点坐标显示正确，但面板中的 marker 列表仍然只显示两个点的坐标。

## 问题分析

### HTML 报告 vs 面板显示

**HTML 报告（已修复）：**
```
3 points: (4417.09,2304.88) → (4573.48,2310.72) → (4629.74,2289.02)
```

**面板显示（修复前）：**
```
CUT_1 - CUT (MULTI) - 3 pts: (4417.09,2304.88) to (4629.74,2289.02)
```

### 根本原因

面板和 HTML 报告使用了不同的坐标格式化逻辑：

- `src/screenshot_export.py` - HTML 报告（已修复）
- `src/fib_panel.py` - 面板显示（需要修复）

## 解决方案

### 修复前的代码

```python
# src/fib_panel.py - add_marker() 方法
if hasattr(marker, 'points') and len(marker.points) > 0:
    first_point = marker.points[0]
    last_point = marker.points[-1]
    coords = f"{len(marker.points)} pts: ({first_point[0]:.2f},{first_point[1]:.2f}) to ({last_point[0]:.2f},{last_point[1]:.2f})"
```

### 修复后的代码

```python
# src/fib_panel.py - add_marker() 方法
if hasattr(marker, 'points') and len(marker.points) > 0:
    if len(marker.points) <= 3:
        # For 3 or fewer points, show all coordinates in panel
        point_strs = [f"({p[0]:.2f},{p[1]:.2f})" for p in marker.points]
        coords = f"{len(marker.points)} pts: " + " → ".join(point_strs)
    else:
        # For more than 3 points, show first 2, ..., last 1 (shorter for panel)
        first_points = [f"({p[0]:.2f},{p[1]:.2f})" for p in marker.points[:2]]
        last_point = f"({marker.points[-1][0]:.2f},{marker.points[-1][1]:.2f})"
        coords = f"{len(marker.points)} pts: " + " → ".join(first_points) + " → ... → " + last_point
```

## 显示规则

### 面板显示（考虑空间限制）

**≤ 3 个点：** 显示所有点
```
CUT_1 - CUT (MULTI) - 3 pts: (100.00,200.00) → (150.00,250.00) → (200.00,300.00)
```

**> 3 个点：** 显示前 2 个 + ... + 最后 1 个
```
CUT_2 - CUT (MULTI) - 6 pts: (100.00,200.00) → (150.00,250.00) → ... → (600.00,700.00)
```

### HTML 报告显示（空间充足）

**≤ 5 个点：** 显示所有点
```
3 points: (100.00,200.00) → (150.00,250.00) → (200.00,300.00)
```

**> 5 个点：** 显示前 3 个 + ... + 后 2 个
```
6 points: (100.00,200.00) → (150.00,250.00) → (200.00,300.00) → ... → (500.00,600.00) → (600.00,700.00)
```

## 修复效果

### 修复前

**面板显示：**
```
CUT_1 - CUT (MULTI) - 3 pts: (4417.09,2304.88) to (4629.74,2289.02)
```

**HTML 报告：**
```
3 points: (4417.09,2304.88) → (4573.48,2310.72) → (4629.74,2289.02)
```

### 修复后

**面板显示：**
```
CUT_1 - CUT (MULTI) - 3 pts: (4417.09,2304.88) → (4573.48,2310.72) → (4629.74,2289.02)
```

**HTML 报告：**
```
3 points: (4417.09,2304.88) → (4573.48,2310.72) → (4629.74,2289.02)
```

## 设计考虑

### 面板空间限制

面板的 marker 列表宽度有限，需要平衡：
- **信息完整性** - 显示足够的路径信息
- **可读性** - 避免文本过长导致显示问题
- **一致性** - 与 HTML 报告保持风格一致

### 不同场景的显示策略

| 点数 | 面板显示 | HTML 显示 | 原因 |
|------|---------|-----------|------|
| 2 | 全部显示 | 全部显示 | 普通 marker |
| 3 | 全部显示 | 全部显示 | 信息量适中 |
| 4-5 | 前2+...+后1 | 全部显示 | 面板空间限制 |
| 6+ | 前2+...+后1 | 前3+...+后2 | 不同的省略策略 |

## 测试验证

### 测试场景

1. **3 点路径**
   - 面板：显示所有 3 个点
   - HTML：显示所有 3 个点

2. **6 点路径**
   - 面板：显示前 2 个 + ... + 最后 1 个
   - HTML：显示前 3 个 + ... + 后 2 个

3. **普通 2 点 marker**
   - 面板：显示不变
   - HTML：显示不变

### 预期结果

✅ 面板和 HTML 都显示完整路径信息
✅ 面板显示适应宽度限制
✅ HTML 显示提供更详细信息
✅ 普通 markers 显示不受影响

## 相关文件

- `src/fib_panel.py` - 面板显示逻辑（已修复）
- `src/screenshot_export.py` - HTML 报告逻辑（之前已修复）

## 版本信息

| 版本 | 日期 | 描述 |
|------|------|------|
| 1.0 | 2024-12-16 | HTML 报告多点坐标显示 |
| 1.1 | 2024-12-16 | 面板多点坐标显示修复 ✅ |

---

**面板多点坐标显示修复完成！** 🎉

现在面板和 HTML 报告都正确显示多点 marker 的完整路径信息。