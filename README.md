<<<<<<< HEAD
# klayout-fib-tool
fib tool for klayout
=======
# KLayout FIB Tool

**简单、实用的 FIB 标注工具。遵循 Linus Torvalds 编程哲学：零废话，直接能用。**

## 项目状态

✅ **MVP 已完成** - 1028 行代码，8 个核心文件

## 快速开始

### 安装

```bash
cp -r src ~/.klayout/pymacros/fib_tool
```

重启 KLayout，按 `Ctrl+Shift+F` 启动工具。

详细安装说明：[INSTALL.md](INSTALL.md)

### 使用

1. 打开 GDS 文件
2. 按 `Ctrl+Shift+F` 启动 FIB Tool
3. 点击 Cut/Connect/Probe 按钮
4. 在版图上点击创建标记
5. 保存为 XML 或生成 HTML 报告

详细使用说明：[src/README.md](src/README.md)

## 项目结构

```
klayout-fib-tool/
├── src/                    # 源代码（核心实现）
│   ├── __init__.py         # 插件注册入口
│   ├── plugin.py           # 核心逻辑（鼠标事件）
│   ├── markers.py          # 3 种标记类
│   ├── storage.py          # XML 序列化
│   ├── ui.py               # Qt 界面
│   ├── report.py           # HTML 报告生成
│   ├── config.py           # 配置管理
│   └── test_markers.py     # 测试脚本
│
├── docs/                   # 设计文档
│   ├── requirements.md     # 技术需求
│   ├── prd.md              # 产品需求
│   ├── mvp_plan.md         # MVP 详细规划
│   ├── mvp_checklist.md    # 执行清单
│   └── klayout_api_research.md  # KLayout API 研究
│
├── INSTALL.md              # 安装指南
├── MVP_SUMMARY.md          # 实现总结
├── VERIFICATION.md         # 验证清单
└── LinusTorvalds.md        # 编程哲学
```

## 已实现功能

- **CUT 标注**：X 符号 + 方向箭头
- **CONNECT 标注**：连线 + 端点圆圈
- **PROBE 标注**：向下箭头符号
- **删除标记**：选中后删除
- **保存/加载**：XML 文件持久化
- **生成报告**：HTML 报告 + 截图

## 设计哲学

遵循 **Linus Torvalds** 的编程原则：

1. **数据结构优先**：好的数据结构让代码自然简洁
2. **消除特殊情况**：用多态，不用 if/else
3. **扁平优于嵌套**：早返回，最多 2 层缩进
4. **实用主义**：解决真实问题，不过度设计

详细哲学：[LinusTorvalds.md](LinusTorvalds.md)

## 代码质量

```
总代码行数：1028 行
平均每文件：114 行
最大文件：plugin.py (250 行)
缩进层次：最多 2 层
函数长度：最长 45 行
```

**符合 Linus 标准：简洁、直接、无废话**

## 文档

- **用户文档**
  - [安装指南](INSTALL.md)
  - [使用说明](src/README.md)
  - [验证清单](VERIFICATION.md)

- **开发文档**
  - [技术需求](docs/requirements.md)
  - [产品需求](docs/prd.md)
  - [MVP 规划](docs/mvp_plan.md)
  - [实现总结](MVP_SUMMARY.md)

- **参考文档**
  - [KLayout API 研究](docs/klayout_api_research.md)
  - [编程哲学](LinusTorvalds.md)

## 测试

```bash
# 在 KLayout Macro Development 窗口运行
python src/test_markers.py
```

手动测试清单：[VERIFICATION.md](VERIFICATION.md)

## 下一步

### v1.0 MVP（当前）
- 基本标注功能
- XML 保存/加载
- HTML 报告生成

### v1.1 增强版（规划中）
- 分组管理
- PDF 报告
- 三级视图截图
- 撤销/重做
- 快捷键支持

## 许可证

MIT License

## 致谢

遵循 Linus Torvalds 的编程哲学：
> "Talk is cheap. Show me the code."

---

**简单、实用、零废话。代码说话。** for klayout
>>>>>>> d8690d6 (feat: implement KLayout FIB Tool MVP)
