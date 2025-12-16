# Multi-Point Mode Debug Guide

## 当前状态

多点模式已实现，但需要验证双击检测是否正常工作。

## 调试步骤

### 1. 重新加载插件

在 KLayout Macro Development 控制台运行：

```python
import sys
sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/src')
exec(open('/Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py', encoding='utf-8').read())
```

应该看到：
```
[FIB Plugin] Multi-point markers available
```

### 2. 激活多点模式

1. 在 FIB Panel 中，Cut 按钮旁的下拉菜单选择 "Multi Points"
2. 点击 "Cut" 按钮
3. 看到消息: "CUT multi-point mode: Click points, double-click to finish"

### 3. 测试点击

**第一次点击：**
```
[DEBUG] Double-click check: mode=cut_multi, last_pos=None, last_time=0
[DEBUG] Position (x, y) - Tap detection temporarily disabled
[DEBUG] Stored points: 1 total
```

**第二次点击：**
```
[DEBUG] Double-click check: mode=cut_multi, last_pos=(x1, y1), last_time=...
[DEBUG] Checking double-click: time_diff=...ms, distance=...um
[DEBUG] ✗ Not a double-click: time too long or distance too far
[DEBUG] Stored points: 2 total
```

**第三次点击：**
```
[DEBUG] Stored points: 3 total
```

**双击完成：**
```
[DEBUG] Checking double-click: time_diff=XXXms, distance=X.XXum
[DEBUG] ✓ Double-click detected!
[DEBUG] Double-click confirmed in multi-point mode! Points collected: 3
[DEBUG] MULTIPOINT_AVAILABLE = True
[DEBUG] Creating multi-point CUT marker...
[DEBUG] _create_multipoint_cut_marker called with 3 points
[DEBUG] Marker ID: CUT_0
[DEBUG] Points to create marker: [(x1,y1), (x2,y2), (x3,y3)]
[DEBUG] Marker object created: ...
[DEBUG] Marker drawn to GDS
[DEBUG] ✓ Successfully created multi-point cut marker CUT_0 with 3 points
```

## 双击检测参数

当前设置：
- **时间阈值**: 500 毫秒
- **距离阈值**: 5.0 微米（已增加以便更容易检测）

## 如果双击不工作

### 检查 1: MULTIPOINT_AVAILABLE

在控制台运行：
```python
import sys
from fib_plugin import MULTIPOINT_AVAILABLE
print(f"MULTIPOINT_AVAILABLE = {MULTIPOINT_AVAILABLE}")
```

应该输出 `True`。如果是 `False`，检查 multipoint_markers.py 是否有语法错误。

### 检查 2: 双击速度

尝试：
1. 点击更快（两次点击间隔 < 500ms）
2. 点击位置更接近（< 5 微米）
3. 在完全相同的位置点击两次

### 检查 3: 调整阈值

如果仍然检测不到，可以临时增加阈值：

在 `fib_plugin.py` 的 `__init__` 方法中：
```python
self.double_click_threshold = 1000  # 增加到 1 秒
self.double_click_distance = 10.0   # 增加到 10 微米
```

### 检查 4: 查看完整日志

确保在 Macro Development 控制台中看到所有调试消息。如果没有看到 `[DEBUG]` 消息，可能是：
1. 插件没有正确加载
2. 模式没有正确激活
3. 点击事件没有被捕获

## 预期行为

### 正确的流程
1. 点击 3-4 次添加点
2. 快速双击（在最后一个点附近）
3. 看到 "Double-click detected" 消息
4. 看到 marker 创建消息
5. 在布局上看到连接所有点的路径

### 如果只看到点但没有路径
- 检查是否看到 "Double-click detected" 消息
- 如果没有，说明双击没有被检测到
- 尝试点击更快或更接近

### 如果看到错误消息
- 复制完整的错误堆栈
- 检查 multipoint_markers.py 是否正确导入
- 检查 MULTIPOINT_AVAILABLE 标志

## 手动测试双击检测

可以运行测试脚本：
```bash
cd /Users/dean/Documents/git/klayout-fib-tool/src
python3 test_double_click.py
```

这会测试双击检测逻辑是否正常工作。

## 常见问题

**Q: 为什么我的双击总是被当作两次单击？**
A: 可能是点击速度太慢或位置太远。尝试：
- 点击更快
- 在完全相同的位置点击
- 增加阈值参数

**Q: 如何知道双击被检测到了？**
A: 查看控制台输出，应该看到：
```
[DEBUG] ✓ Double-click detected!
```

**Q: 双击后什么都没发生？**
A: 检查：
1. 是否有至少 2 个点
2. MULTIPOINT_AVAILABLE 是否为 True
3. 是否有错误消息

**Q: 路径只连接了 2 个点？**
A: 这说明双击在第 2 个点后就被检测到了。尝试：
- 点击更慢（让每次点击间隔 > 500ms）
- 点击位置更分散（> 5 微米）