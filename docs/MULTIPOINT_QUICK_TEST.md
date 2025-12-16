# Multi-Point Mode Quick Test Guide

## 快速测试步骤

### 测试 Multi-Point Cut

1. **激活模式**
   - 打开 FIB Panel
   - 在 Cut 按钮旁边的下拉菜单选择 "Multi Points"
   - 点击 "Cut" 按钮
   - 看到消息: "CUT multi-point mode: Click points, double-click to finish"

2. **添加点**
   - 在布局上点击第一个点 → 看到坐标文本
   - 点击第二个点 → 看到坐标文本和消息 "Cut path: 2 points..."
   - 点击第三个点 → 看到坐标文本和消息 "Cut path: 3 points..."
   - 点击第四个点 → 看到坐标文本和消息 "Cut path: 4 points..."

3. **完成路径**
   - 在最后一个点的位置**快速双击**
   - 应该看到:
     - 创建了 CUT_0 marker
     - 路径连接所有点（不包括双击的重复点）
     - 每个顶点有小圆圈
     - 坐标文本更新为 "CUT_0:(x,y)"

### 测试 Multi-Point Connect

1. **激活模式**
   - 在 Connect 按钮旁边的下拉菜单选择 "Multi Points"
   - 点击 "Connect" 按钮

2. **添加点**
   - 点击多个点（至少2个）
   - 每次点击都会显示点数

3. **完成路径**
   - 双击完成
   - 应该看到:
     - 创建了 CONNECT_0 marker
     - 路径连接所有点
     - 起点和终点有大圆圈
     - 中间点有小圆圈

## 预期行为

### 正确的行为
✓ 每次单击添加一个新点
✓ 双击时使用已有的点创建路径（不添加双击的点）
✓ 路径连接所有已收集的点
✓ 至少需要2个点才能创建 marker

### 错误的行为（已修复）
✗ 只画出前两个点就停止
✗ 双击时添加重复的点
✗ 路径不连接所有点

## 双击检测参数

- **时间阈值**: 500 毫秒
- **距离阈值**: 0.5 微米

如果双击没有被检测到，尝试：
1. 点击更快（两次点击间隔 < 500ms）
2. 点击位置更接近（< 0.5 微米）
3. 在完全相同的位置点击两次

## 调试信息

在 KLayout 的 Macro Development 控制台中查看调试信息：

```
[DEBUG] Position (x, y) - Tap detection temporarily disabled
[DEBUG] Stored points: N total
[DEBUG] Double-click detected! time_diff=XXXms, distance=X.XXXum
[DEBUG] Double-click: Finishing cut_multi with N existing points
[DEBUG] Created multi-point cut marker CUT_0 with N points
```

## 切换回 2-Point 模式

1. 在下拉菜单选择 "2 Points"
2. 点击 Cut 或 Connect 按钮
3. 现在是传统的两点模式

## 常见问题

**Q: 为什么双击后路径只有 N-1 个点？**
A: 这是正确的！双击是完成信号，不应该添加新点。路径使用双击前已收集的所有点。

**Q: 如何取消当前的多点输入？**
A: 切换到其他模式或点击同一个按钮来取消。

**Q: 可以撤销最后一个点吗？**
A: 目前还不支持，这是未来的增强功能。现在需要取消并重新开始。

**Q: 双击检测不灵敏怎么办？**
A: 尝试点击更快、更接近。或者在代码中调整阈值参数。