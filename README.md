<p align="center">
  <img src="logo.ico" alt="CodexRitual Logo" width="120"/>
</p>

<h1 align="center">CodexRitual</h1>
<p align="center">
  <em>代码键入练习与理解辅助工具</em>
  <br>
  通过“手动键入”加深代码逻辑理解，结合大语言模型提供即时语义解释
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/github/license/your-username/CodexRitual?style=flat-square&color=6366f1" />
  <img src="https://img.shields.io/github/v/release/your-username/CodexRitual?style=flat-square&color=10b981" />
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" />
</p>

<br>

## ✨ 核心特性

### 🧠 语义化代码解析引擎
- **逻辑聚焦**：基于 Pygments 词法分析，精准区分代码逻辑与注释部分
- **智能跳过**：自动计算缩进，支持注释、文档字符串（Docstring）的一键跳过，确保你只练习核心逻辑

### 🎨 高级语法高亮系统
- **IDE 级体验**：内置模拟 VS Code 标准的深色/浅色高亮规则，支持 Python、JavaScript、C++、Go 等主流语言
- **逐字唤醒**：初始呈暗灰色，随你的正确键入逐渐“点亮”高亮色彩，退格时自动还原

### 🤖 AI 导师集成
- **语义注释生成**：对接 DeepSeek / OpenAI 兼容接口，一键为当前代码段生成详尽的中文逻辑注释
- **交互式学习**：内置 AI 逻辑推演舱，支持针对代码细节进行对话式探讨

### 📦 零配置资产管理
- **动静分离**：程序采用资源自动释放机制，首次运行时在 `Documents/CodexRitual_Data` 建立独立数据区，升级或迁移不丢失配置与自定义资产
- **多模态输入**：深度优化 `inputMethodEvent`，完美兼容操作系统原生中文输入法（IME），消除中英文混输排版抖动

<details>
<summary>📸 点击展开截图 (深色/浅色模式)</summary>
<br>
<p align="center">
  <img src="assets/screenshots/demo-light.png#gh-light-mode-only" width="700" alt="浅色模式界面" />
  <img src="assets/screenshots/demo-dark.png#gh-dark-mode-only" width="700" alt="深色模式界面" />
  <br>
  <sub>自适应深色 / 浅色主题</sub>
</p>
</details>

## 🚀 环境要求

| 环境 / 依赖 | 版本 / 说明 |
|-------------|-------------|
| Python      | ≥ 3.8       |
| PyQt6       | 图形界面框架 |
| Pygments    | 语法高亮与词法分析 |
| openai      | AI 接口通讯（兼容 DeepSeek） |

## 📥 安装指南

### 🔧 从源码运行

```bash
# 克隆仓库
git clone https://github.com/your-username/CodexRitual.git
cd CodexRitual

# 创建并激活虚拟环境（推荐）
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# 安装依赖
pip install PyQt6 pygments openai

# 启动程序
python main.py
```

### 📦 独立运行 (Windows .exe)

如果你使用的是打包后的 `CodexRitual.exe`，直接双击运行即可。  
首次启动时，程序会自动在你的 `我的文档\CodexRitual_Data` 目录下生成配置与资源文件夹，后续可直接在该目录管理你的自定义资产。

## 📖 使用教程

### ⌨️ 基础练习
1. 从顶部“当前练习”下拉菜单选择代码文件
2. 按照界面提示逐字键入，按下 `Tab` 键可快速跳过连续缩进空格
3. 点击右侧 [⌨️ 侧边栏] 可呼出或隐藏不同布局的键盘指法图

### 🤖 激活 AI 导师
1. 点击右上角 [⚙️ 设置]
2. 在 “API 密钥” 栏位中填入你的 DeepSeek 密钥（或其他兼容的 OpenAI API Key）
3. 选中一段练习代码，点击顶部 [✨ 一键生成注释]
4. 系统将在后台调用 AI，并在当前目录生成带有详细注释的新代码文件，随后自动重载高亮画布

### 📁 导入自定义代码
- **直接放入**：将代码文件放入 `Documents/CodexRitual_Data/assets/snippets` 目录即可
- **界面导入**：通过主界面 [⚙️ 设置] → [📁 选择本地文件导入...] 快速添加外部文件

## 🧱 技术架构

```
CodexRitual/
├── core/                    # 核心逻辑与系统引擎层
│   ├── typing_logic.py      # 词法分析与键入状态机映射
│   └── ai_bridge.py         # 异步多线程 AI 通讯模块
├── gui/                     # 界面表现层 (PyQt6)
│   ├── main_window.py       # 主窗口控制、信号路由与文件流转
│   ├── editor_widget.py     # 基于 QTextCursor 的高性能渲染画布
│   └── theme_manager.py     # 全局状态、QSS 样式及存储管理
├── assets/                  # 静态内置资源映射
└── data/                    # 提示词模板及默认配置
```

## 🛠️ 开发者说明

本项目具有极高的定制性，你可以轻松调整以下内容：

- **修改 AI 行为**  
  打开 `data/ai_skill.txt`，修改系统提示词（System Prompt）即可让 AI 输出不同口吻或深度的代码注释。

- **自定义语法颜色**  
  在 `gui/theme_manager.py` 的字典中，按 Token 类型自由调整 Hex 颜色值，打造属于你自己的主题。

> 欢迎提交 Issue 和 PR！更多开发细节请参考 [贡献指南](./CONTRIBUTING.md)（如果你有的话）。

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 协议开源。
```
