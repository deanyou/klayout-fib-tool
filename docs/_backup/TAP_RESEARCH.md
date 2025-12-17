# KLayout Tap 功能研究

## 目标
实现鼠标点击位置的层检测功能，类似 KLayout 内置的 Tap 工具。

## 当前状态
- ✅ 坐标检测正常：能正确获取鼠标点击的坐标
- ✅ 标记创建正常：CUT/CONNECT/PROBE 标记创建成功
- ✅ 坐标文本正常：在点击位置显示坐标文本
- ❌ 层检测失败：无法检测点击位置的图层

## 已尝试的方法

### 方法 1: 形状遍历 + 边界框检测
```python
for layer_info in layer_infos:
    shapes = cell.shapes(layer_index)
    for shape in shapes.each():
        if shape.bbox().contains(point):
            # 找到层
```
**结果**: 失败，没有检测到任何层

### 方法 2: Region 交集检测
```python
search_region = pya.Region(search_box)
layer_region = pya.Region(shapes)
intersection = layer_region & search_region
```
**结果**: 失败，没有检测到交集

### 方法 3: 形状重叠检测
```python
for shape in shapes.each_overlapping(search_box):
    if self._shape_contains_point(shape, point):
        # 找到层
```
**结果**: 失败，没有找到重叠形状

## 需要调研的方向

### 1. KLayout 内置 Tap 工具的实现
- 查看 KLayout 源码中 Tap 工具的实现
- 了解正确的 API 调用方法
- 可能需要使用不同的坐标系统

### 2. 坐标系统问题
- 确认鼠标点击坐标的单位和坐标系
- 检查是否需要考虑视图变换（缩放、平移、旋转）
- 验证数据库单位转换是否正确

### 3. 层和形状访问方法
- 检查 `layout.layer_infos()` 是否返回所有层
- 验证 `cell.shapes(layer_index)` 是否正确获取形状
- 确认形状的几何信息是否正确

### 4. KLayout Plugin 系统限制
- 检查 Plugin 系统是否有访问限制
- 是否需要特殊权限或方法来访问形状数据
- 考虑使用其他 KLayout API

## 调试信息分析

从最近的测试看到：
```
[DEBUG] Checking 0 layers  # 这表明 layer_infos() 返回空列表
```

这可能意味着：
1. 当前 cell 没有任何层数据
2. 访问层信息的方法不正确
3. 需要访问不同的 cell 或 layout

## 下一步计划

1. **验证布局数据**：
   - 检查当前打开的 GDS 文件是否有数据
   - 验证 cell 和 layout 对象是否正确
   - 确认层信息是否存在

2. **研究 KLayout API**：
   - 查阅 KLayout Python API 文档
   - 寻找正确的层检测方法
   - 参考其他插件的实现

3. **简化测试**：
   - 创建最小测试用例
   - 逐步验证每个 API 调用
   - 添加更详细的调试信息

4. **备选方案**：
   - 如果无法实现自动检测，考虑手动选择层
   - 提供层选择对话框
   - 使用预设的常用层列表

## 临时解决方案

当前已实现：
- 标记创建不依赖层检测
- 使用默认命名（如 `CUT_0`, `CONNECT_1`）
- 所有其他功能正常工作

用户可以：
- 正常创建 FIB 标记
- 查看坐标文本
- 手动记录需要操作的层信息