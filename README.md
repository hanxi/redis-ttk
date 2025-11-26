# Redis-TTK

一个基于 Python 和 ttkbootstrap 开发的现代化 Redis 客户端应用程序，提供直观易用的图形界面来管理 Redis 数据库。

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![ttkbootstrap](https://img.shields.io/badge/GUI-ttkbootstrap-orange.svg)

## ✨ 功能特性

### 🔗 连接管理
- **多连接支持**: 保存和管理多个 Redis 连接配置
- **连接测试**: 实时测试连接状态和服务器可用性
- **自动重连**: 支持连接断开后的自动重连机制
- **数据库切换**: 支持在不同 Redis 数据库间快速切换

### 📊 数据操作
- **全类型支持**: 完整支持 Redis 所有数据类型（String、List、Set、ZSet、Hash）
- **键值管理**: 新增、编辑、删除、重命名 Redis 键
- **TTL 管理**: 设置和移除键的过期时间
- **批量操作**: 支持批量删除和导入导出功能

### 🎨 用户界面
- **现代化设计**: 基于 ttkbootstrap 的美观现代界面
- **多主题支持**: 内置多种视觉主题可供选择
- **响应式布局**: 自适应不同屏幕尺寸和分辨率
- **双面板设计**: 左侧键浏览器 + 右侧值编辑器的高效布局

### ⚙️ 高级功能
- **语法高亮**: JSON 数据的语法高亮显示
- **搜索过滤**: 快速搜索和过滤 Redis 键
- **服务器信息**: 查看 Redis 服务器详细信息和统计数据
- **设置管理**: 丰富的个性化设置选项

## 🚀 快速开始

### 环境要求
- **Python**: 3.14 或更高版本
- **操作系统**: Windows、macOS、Linux

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd redis-ttk
```

2. **安装依赖**
```bash
# 使用 PDM（推荐）
pdm install

# 或使用 pip
pip install -r requirements.txt
```

3. **运行应用**
```bash
# 使用 PDM
pdm run python main.py

# 或直接运行
python main.py
```

## 📁 项目结构

```
redis-ttk/
├── main.py                 # 应用程序入口
├── redis_client.py         # Redis 连接和操作模块
├── config/                 # 配置管理
│   ├── __init__.py
│   └── settings.py         # 设置管理器
├── gui/                    # 图形界面模块
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── connection_dialog.py # 连接对话框
│   ├── key_browser.py      # 键浏览器
│   ├── value_editor.py     # 值编辑器
│   ├── settings_dialog.py  # 设置对话框
│   └── custom_dialogs.py   # 自定义对话框
├── pyproject.toml          # 项目配置
└── README.md              # 项目文档
```

## 🛠️ 技术栈

### 核心技术
- **Python 3.14**: 现代 Python 运行环境
- **ttkbootstrap**: 现代化的 Tkinter 主题库
- **redis-py**: Redis Python 客户端库

### 开发工具
- **PDM**: 现代化的 Python 依赖管理工具
- **Ruff**: 快速的 Python 代码检查和格式化工具

### 主要依赖
```toml
[project.dependencies]
ttkbootstrap = ">=1.19.0"
redis = ">=7.1.0"
```

## 📖 使用指南

### 连接 Redis
1. 点击工具栏的"连接"按钮
2. 填写 Redis 服务器信息（主机、端口、密码等）
3. 点击"测试连接"验证配置
4. 保存连接配置以便后续使用

### 管理数据
- **浏览键**: 在左侧面板查看所有 Redis 键
- **编辑值**: 在右侧面板编辑选中键的值
- **新增键**: 使用工具栏的"新增键"按钮
- **删除键**: 右键菜单或使用 Delete 键

### 个性化设置
- 通过"工具 → 设置"访问设置面板
- 自定义主题、字体、编辑器行为等
- 设置会自动保存并在下次启动时恢复

## 🎯 开发特色

### 代码质量
- **类型注解**: 全面使用 Python 类型提示
- **代码规范**: 遵循 PEP 8 和现代 Python 最佳实践
- **模块化设计**: 清晰的模块分离和职责划分

### 用户体验
- **响应式设计**: 流畅的用户交互体验
- **错误处理**: 完善的异常处理和用户提示
- **设置持久化**: 用户设置和连接配置的自动保存

### 性能优化
- **异步操作**: 避免界面冻结的异步数据加载
- **内存管理**: 高效的数据结构和内存使用
- **连接池**: 优化的 Redis 连接管理

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd redis-ttk

# 安装开发依赖
pdm install --dev

# 运行代码检查
pdm run lint

# 运行代码格式化
pdm run format
```

### 代码规范
- 使用 Ruff 进行代码检查和格式化
- 遵循 Python 类型注解规范
- 编写清晰的文档字符串

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) - 现代化的 Tkinter 主题库
- [redis-py](https://github.com/redis/redis-py) - Redis Python 客户端
- [PDM](https://pdm.fming.dev/) - 现代化的 Python 依赖管理工具

---

**Redis-TTK** - 让 Redis 管理变得简单而优雅 ✨

