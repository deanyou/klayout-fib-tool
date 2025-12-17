# FIB Tool 快速开始

## 简化版本

现在只有一个主要版本：**fib_plugin.py** - 支持鼠标点击的完整版本

## 快速使用

### 方法 1: 直接运行（推荐）

1. **打开 KLayout**
2. **打开一个 GDS 文件**（必须先打开文件！）
3. **按 F5** 打开 Macro Development 窗口
4. **复制粘贴这个命令**：
   ```python
   import sys; sys.path.insert(0, '/Users/dean/Documents/git/klayout-fib-tool/src'); exec(open('/Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py', encoding='utf-8').read())
   ```
5. **按 Enter**

### 方法 2: 安装到 KLayout 宏目录

```bash
# 复制文件到 KLayout 宏目录
cp /Users/dean/Documents/git/klayout-fib-tool/src/fib_plugin.py ~/KLayout/macros/
cp /Users/dean/Documents/git/klayout-fib-tool/src/markers.py ~/KLayout/macros/
cp /Users/dean/Documents/git/klayout-fib-tool/src/config.py ~/KLayout/macros/
```

然后在 KLayout 中：Macros → fib_plugin.py → Run

## 使用方法

成功加载后，工具栏会出现三个按钮：

1. **FIB Cut** - 点击后，在布局上点击两次：
   - 第1次：设置中心位置
   - 第2次：设置方向
   - 创建在 Layer 317

2. **FIB Connect** - 点击后，在布局上点击两次：
   - 第1次：起点
   - 第2次：终点
   - 创建在 Layer 318

3. **FIB Probe** - 点击后，在布局上点击一次：
   - 创建圆形标记
   - 创建在 Layer 319

## 标记规格

- **线宽**: 0.2 μm（固定）
- **PROBE 半径**: 0.5 μm
- **图层**:
  - CUT: 317/0
  - CONNECT: 318/0
  - PROBE: 319/0

## 核心文件

- `fib_plugin.py` - 主程序（支持鼠标点击）
- `fib_tool.lym` - KLayout 宏版本（备用）
- `markers.py` - 标记类定义
- `config.py` - 配置文件

## 故障排除

### 按钮没有出现
- 确保已打开 GDS 文件
- 检查控制台错误信息

### 标记没有显示
- 检查 Layer Panel，确保 Layer 317/318/319 可见
- 使用 "Fit All" 查看整个布局

### 点击没有反应
- 确保点击了工具栏按钮激活模式
- 检查控制台的调试信息
