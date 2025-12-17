# FIB Tool - Release Checklist

## 发布前检查清单

### 1. 代码准备

- [ ] 所有功能已完成并测试
- [ ] 代码已清理（移除调试代码、TODO 注释）
- [ ] 所有文件使用 UTF-8 编码
- [ ] 路径使用相对路径（不要硬编码绝对路径）
- [ ] 双重初始化保护已测试

### 2. 文档更新

- [ ] `README.md` 更新版本号和功能列表
- [ ] `INSTALL.md` 包含所有安装方式
- [ ] `salt.xml` 版本号正确
- [ ] `fib_tool/__init__.py` 版本号正确
- [ ] 所有文档中的 URL 已更新（替换 `yourusername`）
- [ ] 添加 CHANGELOG.md（如果有）

### 3. SALT 包配置

- [ ] `salt.xml` 信息完整
  - [ ] name: `fib-tool`
  - [ ] version: `1.0.0`
  - [ ] api-version: `0.28`
  - [ ] title 和 description 准确
  - [ ] author 和 license 正确
  - [ ] url 指向正确的 GitHub 仓库
  
- [ ] `klayout_package.py` 正确初始化
  - [ ] 导入 `fib_plugin`
  - [ ] 双重初始化保护
  - [ ] 错误处理完善

### 4. 测试

#### 4.1 本地测试

- [ ] **方式 1: SALT 手动安装**
  ```bash
  cp -r fib_tool ~/.klayout/salt/
  # 重启 KLayout，检查是否正常加载
  ```

- [ ] **方式 2: exec() 加载**
  ```python
  import sys; sys.path.insert(0, '/path/to/fib_tool')
  exec(open('/path/to/fib_tool/fib_plugin.py', encoding='utf-8').read())
  ```

- [ ] **方式 3: 双重加载测试**
  - 先通过 SALT 安装
  - 再执行 exec() 加载
  - 确认没有重复按钮或错误

#### 4.2 功能测试

- [ ] 工具栏按钮显示正常
  - [ ] FIB Cut
  - [ ] FIB Connect
  - [ ] FIB Probe

- [ ] 图层自动创建
  - [ ] 打开没有 317/318/319 层的 GDS
  - [ ] 加载插件
  - [ ] 检查图层是否自动创建

- [ ] 标记创建
  - [ ] CUT 标记（2 点）
  - [ ] CONNECT 标记（2 点）
  - [ ] PROBE 标记（1 点）
  - [ ] 多点 CUT（3+ 点，右键完成）
  - [ ] 多点 CONNECT（3+ 点，右键完成）

- [ ] FIB Panel
  - [ ] Panel 正常显示
  - [ ] 标记列表更新
  - [ ] 右键菜单功能
  - [ ] 坐标跳转功能

- [ ] 导出功能
  - [ ] 截图导出（3 级缩放）
  - [ ] HTML 报告生成
  - [ ] PDF 导出（如果可用）

#### 4.3 兼容性测试

- [ ] KLayout 0.28 测试
- [ ] KLayout 0.29 测试（如果可用）
- [ ] macOS 测试
- [ ] Linux 测试（如果可用）
- [ ] Windows 测试（如果可用）

### 5. GitHub 准备

#### 5.1 仓库设置

- [ ] 仓库名称：`klayout-fib-tool`
- [ ] 描述：简短准确的项目描述
- [ ] Topics 标签：
  - `klayout`
  - `klayout-plugin`
  - `fib`
  - `ic-design`
  - `eda`
  - `python`

- [ ] README.md 在仓库首页显示正常
- [ ] LICENSE 文件存在（MIT）

#### 5.2 文件检查

- [ ] 所有必需文件已提交
  ```
  fib_tool/
  ├── klayout_package.py
  ├── __init__.py
  ├── fib_plugin.py
  ├── fib_panel.py
  ├── markers.py
  ├── multipoint_markers.py
  ├── config.py
  ├── layer_manager.py
  ├── screenshot_export.py
  ├── marker_menu.py
  ├── storage.py
  ├── report.py
  ├── smart_counter.py
  ├── utils.py
  └── file_dialog_helper.py
  
  docs/
  ├── SALT_INSTALLATION.md
  ├── LAYER_AUTO_CREATION_TEST.md
  └── ...
  
  salt.xml
  README.md
  INSTALL.md
  LICENSE
  ```

- [ ] 不要提交的文件已在 .gitignore
  - `__pycache__/`
  - `*.pyc`
  - `.DS_Store`
  - `outputs/`（如果是临时文件）

### 6. 创建 Release

#### 6.1 版本标签

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Initial SALT package release"
git push origin v1.0.0
```

#### 6.2 GitHub Release

1. **创建 Release**
   - 进入 GitHub 仓库
   - 点击 "Releases" → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `FIB Tool v1.0.0`

2. **Release 描述**
   ```markdown
   # FIB Tool v1.0.0
   
   Initial SALT package release for KLayout FIB marker tool.
   
   ## Features
   - ✅ CUT, CONNECT, PROBE markers
   - ✅ Multi-point marker support
   - ✅ Automatic layer creation (317, 318, 319)
   - ✅ PDF export with 3-level screenshots
   - ✅ Coordinate jump and display
   - ✅ Right-click menu operations
   
   ## Installation
   
   ### Via SALT Package Manager (Recommended)
   1. Open KLayout
   2. Tools → Manage Packages
   3. Install New Packages → Add Package Source
   4. Enter URL: `https://github.com/yourusername/klayout-fib-tool/releases/download/v1.0.0/klayout-fib-tool-1.0.0.zip`
   5. Click Install
   
   ### Via Manual Copy
   ```bash
   cp -r fib_tool ~/.klayout/salt/
   ```
   
   ## Requirements
   - KLayout >= 0.28
   - Python 3.8+ (included in KLayout)
   
   ## Documentation
   - [Installation Guide](INSTALL.md)
   - [SALT Installation](docs/SALT_INSTALLATION.md)
   - [Usage Guide](fib_tool/README.md)
   
   ## Known Issues
   - None
   
   ## Changelog
   - Initial release
   ```

3. **上传资产**
   - 自动生成的 Source code (zip) 和 Source code (tar.gz) 已足够
   - 可选：上传预打包的 `fib-tool-1.0.0.zip`（只包含 fib_tool/ 和 salt.xml）

#### 6.3 SALT 包 URL

Release 创建后，SALT 安装 URL 为：
```
https://github.com/yourusername/klayout-fib-tool/releases/download/v1.0.0/klayout-fib-tool-1.0.0.zip
```

或使用 GitHub 自动生成的：
```
https://github.com/yourusername/klayout-fib-tool/archive/refs/tags/v1.0.0.zip
```

### 7. 发布后验证

- [ ] **SALT 安装测试**
  1. 在干净的 KLayout 环境中
  2. 使用 Salt Package Manager
  3. 输入 Release URL
  4. 安装并测试所有功能

- [ ] **文档链接检查**
  - [ ] README.md 中的链接可访问
  - [ ] INSTALL.md 中的 URL 正确
  - [ ] docs/ 中的交叉引用正确

- [ ] **Issue 模板**（可选）
  - 创建 `.github/ISSUE_TEMPLATE/bug_report.md`
  - 创建 `.github/ISSUE_TEMPLATE/feature_request.md`

### 8. 宣传（可选）

- [ ] 在 KLayout 论坛发布
- [ ] 在相关社区分享
- [ ] 更新个人网站/博客

---

## 快速发布命令

```bash
# 1. 确保所有更改已提交
git status

# 2. 更新版本号
# 编辑 salt.xml, fib_tool/__init__.py

# 3. 提交版本更新
git add .
git commit -m "Bump version to 1.0.0"
git push

# 4. 创建标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. 在 GitHub 上创建 Release
# 访问 https://github.com/yourusername/klayout-fib-tool/releases/new
```

---

## 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR.MINOR.PATCH** (例如 1.0.0)
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

示例：
- `1.0.0` - 初始发布
- `1.0.1` - Bug 修复
- `1.1.0` - 新增功能
- `2.0.0` - 重大变更

---

## 常见问题

### Q: SALT 安装失败怎么办？

A: 检查：
1. URL 是否正确
2. Release 是否已发布
3. salt.xml 格式是否正确
4. KLayout 版本是否 >= 0.28

### Q: 如何更新已发布的版本？

A: 
1. 修复问题
2. 更新版本号（如 1.0.1）
3. 创建新的 tag 和 release
4. 用户通过 Salt Package Manager 更新

### Q: 如何撤回错误的 Release？

A:
1. 在 GitHub 上删除 Release
2. 删除 tag：`git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
3. 修复问题后重新发布

---

**准备好了就发布吧！🚀**
