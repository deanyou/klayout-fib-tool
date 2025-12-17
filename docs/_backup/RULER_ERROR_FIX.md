# Ruler Error Fix

## 问题描述

在 Detail 视图中显示错误：
```
Error: unknown variable or function "$" at position ...
```

## 问题原因

在 `create_marker_dimension_rulers()` 函数中使用了错误的格式字符串：

```python
# 错误的代码
x_ruler.fmt = "$(sprintf('%.2f',abs($D)))"  # 导致 $ 语法错误
x_ruler.outline = pya.Annotation.OutlineBox
```

KLayout 的 Annotation 格式字符串语法不支持这种 `$()` 表达式。

## 解决方案

移除自定义格式字符串，使用 KLayout 默认的标尺显示：

```python
# 修复后的代码
x_ruler = pya.Annotation()
x_ruler.p1 = pya.DPoint(x1, y1)
x_ruler.p2 = pya.DPoint(x2, y1)
x_ruler.style = pya.Annotation.StyleRuler  # 使用默认格式
# 移除 fmt 和 outline 设置
view.insert_annotation(x_ruler)
```

## 修复效果

✅ **修复前：**
- Detail 视图显示错误信息
- 标尺无法正常显示

✅ **修复后：**
- 错误信息消失
- X 和 Y 方向标尺正常显示
- 使用 KLayout 默认的测量值格式

## 功能保持

- ✅ X 方向标尺（水平）
- ✅ Y 方向标尺（垂直）
- ✅ 自动显示测量值
- ✅ HTML 报告中的计算值（ΔX, ΔY, Length）

## 测试验证

1. 创建一个 CONNECT marker
2. 导出 PDF
3. 查看 Detail 视图
4. 确认：
   - 无错误信息
   - 显示 X 和 Y 标尺
   - 标尺有测量数值

---

**问题已修复！** ✅