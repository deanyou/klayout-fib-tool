# FIB Tool - 快速开始（SALT 版）

## 🚀 三种安装方式

### 1️⃣ SALT Package Manager（推荐）

```
Tools → Manage Packages → Install from URL
输入：https://github.com/yourusername/klayout-fib-tool/releases/download/v1.0.0/klayout-fib-tool-1.0.0.zip
```

### 2️⃣ 手动复制

```bash
cp -r fib_tool ~/.klayout/salt/
```

### 3️⃣ exec() 加载（开发）

```python
import sys; sys.path.insert(0, '/path/to/fib_tool')
exec(open('/path/to/fib_tool/fib_plugin.py', encoding='utf-8').read())
```

---

## ✅ 验证安装

### 检查工具栏

应该看到三个按钮：
- **FIB Cut** - 创建切断标记
- **FIB Connect** - 创建连接标记  
- **FIB Probe** - 创建探测标记

### 检查控制台（F5）

应该看到：
```
=== FIB Tool Initialization ===
✓ FIB layers verified/created successfully
✓ Plugin factories created successfully
✓ FIB Panel created and docked successfully
```

---

## 🎯 快速使用

### 创建标记

1. **打开 GDS 文件**
2. **点击工具栏按钮**（Cut/Connect/Probe）
3. **在版图上点击**
   - CUT/CONNECT: 点击 2 次
   - PROBE: 点击 1 次
   - 多点模式: 左键添加点，右键完成

### 导出 PDF

1. **打开 FIB Panel**
2. **点击 "Export PDF"**
3. **选择保存位置**
4. **查看生成的 PDF 报告**

---

## 📚 完整文档

- [README.md](README.md) - 项目概述
- [INSTALL.md](INSTALL.md) - 详细安装
- [docs/SALT_INSTALLATION.md](docs/SALT_INSTALLATION.md) - SALT 指南
- [SALT_PACKAGE_READY.md](SALT_PACKAGE_READY.md) - 改造总结

---

## 🐛 遇到问题？

### 运行测试脚本

```python
# 在 KLayout Macro Development (F5) 中执行
exec(open('/path/to/test_salt_package.py', encoding='utf-8').read())
```

### 常见问题

**Q: 工具栏没有按钮？**
- 检查 KLayout 版本 >= 0.28
- 查看控制台错误信息（F5）
- 确认 `fib_tool/` 在 `~/.klayout/salt/`

**Q: 图层未创建？**
- 图层会自动创建（317/318/319）
- 检查控制台的图层创建日志
- 确保 GDS 文件可编辑

**Q: 按钮重复？**
- 不要同时使用 SALT 和 exec() 加载
- 重启 KLayout 清除状态

---

## 🎉 开始使用

安装完成后，打开一个 GDS 文件，点击工具栏按钮，开始创建 FIB 标记！

**简单、实用、零废话。** 🎯
