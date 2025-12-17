# 右键完成方案 - Right-Click to Finish

## 问题分析

双击检测在 KLayout 中很难实现，因为：
1. 用户很难在完全相同的位置点击两次
2. 时间控制也很困难（需要 < 500ms）
3. 从日志看，实际点击间隔都是 1-9 秒，距离 12-14 微米

## 解决方案：右键完成

改用**右键点击**来完成多点输入，这是 CAD 软件的标准做法：
- AutoCAD: 右键完成
- QGIS: 右键完成
- Inkscape: 右键完成
- 大多数绘图软件都使用右键完成

## 新的工作流程

### Multi-Point Cut
```
1. 选择 "Multi Points" 从下拉菜单
2. 点击 "Cut" 按钮
3. 左键点击添加点:
   - 左键点击 1: 添加点 (x1, y1)
   - 左键点击 2: 添加点 (x2, y2) → "2 points. Right-click to finish"
   - 左键点击 3: 添加点 (x3, y3) → "3 points. Right-click to finish"
   - 左键点击 4: 添加点 (x4, y4) → "4 points. Right-click to finish"
4. 右键点击完成 → 创建 CUT_0 连接所有 4 个点
```

### Multi-Point Connect
```
同上，但创建 CONNECT marker
```

## 优势

1. **简单直观**: 左键添加，右键完成
2. **符合标准**: CAD 软件的通用做法
3. **无需精确**: 右键可以在任何位置点击
4. **无需计时**: 不需要快速点击

## 测试步骤

1. **重新加载插件**:
```python
import sys
sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/src')
exec(open('/Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py', encoding='utf-8').read())
```

2. **激活多点模式**:
   - 选择 "Multi Points"
   - 点击 "Cut" 按钮
   - 看到: "Left-click to add points, right-click to finish"

3. **添加点**:
   - 左键点击 3-4 个位置
   - 每次看到点数更新

4. **完成**:
   - 右键点击（任何位置）
   - 看到路径创建

## 调试输出

正确的流程应该看到：

```
[DEBUG] Position (x1, y1) - Tap detection temporarily disabled
[DEBUG] Stored points: 1 total

[DEBUG] Position (x2, y2) - Tap detection temporarily disabled
[DEBUG] Stored points: 2 total

[DEBUG] Position (x3, y3) - Tap detection temporarily disabled
[DEBUG] Stored points: 3 total

[DEBUG] Right-click detected in mode: cut_multi
[DEBUG] Right-click: Finishing cut_multi with 3 points
[DEBUG] MULTIPOINT_AVAILABLE = True
[DEBUG] Creating multi-point CUT marker...
[DEBUG] _create_multipoint_cut_marker called with 3 points
[DEBUG] Marker ID: CUT_0
[DEBUG] Points to create marker: [(x1,y1), (x2,y2), (x3,y3)]
[DEBUG] ✓ Successfully created multi-point cut marker CUT_0 with 3 points
```

## 代码变更

### 主要修改
1. 移除了双击检测逻辑
2. 添加了 `_handle_right_click_finish()` 方法
3. 更新了所有提示消息
4. 简化了鼠标事件处理

### 文件修改
- `src/fib_plugin.py` - 右键处理逻辑
- `src/fib_panel.py` - 状态消息更新
- `docs/MULTIPOINT_USAGE.md` - 使用说明更新

## 常见问题

**Q: 为什么改用右键？**
A: 双击检测太难实现，右键是 CAD 软件的标准做法，更简单可靠。

**Q: 右键会不会触发上下文菜单？**
A: 在多点模式下，右键被插件捕获用于完成输入，不会触发菜单。

**Q: 可以在任何位置右键吗？**
A: 是的，右键位置不重要，只是用来发送"完成"信号。

**Q: 如果误点了右键怎么办？**
A: 如果点数 < 2，会提示继续添加点。如果 >= 2，会创建 marker。

**Q: 可以撤销吗？**
A: 目前不支持撤销单个点，但可以切换模式来取消整个输入。