# CodexRitual

CodexRitual 是一款专为开发者设计的代码键入练习与理解辅助工具。在 AI 辅助生成的时代，本项目提倡通过“手动键入”的方式加强对代码逻辑的深度理解，并结合大语言模型提供即时的语义解释。

## 核心特性

### 1. 语义化代码解析引擎
* **逻辑聚焦**：基于 `Pygments` 词法分析，系统能够精准识别代码中的逻辑部分与注释部分。
* **智能跳过**：自动计算缩进并支持注释、文档字符串（Docstring）的自动跳过模式，确保用户专注于核心代码逻辑的练习。

### 2. 高级语法高亮系统
* **IDE 级体验**：内置模拟 VS Code 标准的深色/浅色高亮规则，支持 Python, JavaScript, C++, Go 等多种主流编程语言。
* **状态动态反馈**：代码初始呈现暗灰色，随用户的正确键入逐字“唤醒”高亮色彩；退格时自动恢复初始状态。

### 3. AI 导师集成
* **语义注释生成**：集成 DeepSeek/OpenAI 兼容接口，可一键为当前练习的代码段生成详尽的中文逻辑注释。
* **交互式学习**：内置 AI 逻辑推演舱，支持针对代码细节进行对话探讨。

### 4. 零配置资产管理
* **动静分离架构**：程序采用资源自动释放机制。运行时自动在用户文档目录（`Documents/CodexRitual_Data`）建立独立数据区，确保配置与自定义资产（代码片段、指法图）在软件升级或迁移时不丢失。
* **多模态输入兼容**：深度优化 `inputMethodEvent`，完美兼容操作系统原生中文输入法（IME），解决中英文混输时的排版抖动问题。

## 环境要求

- **Python**: 3.8 或更高版本
- **主要依赖**:
  - `PyQt6`: 图形界面框架
  - `Pygments`: 语法高亮与词法分析
  - `openai`: AI 接口通讯（兼容 DeepSeek）

## 安装指南

### 从源码运行
1. **克隆仓库**
   ```bash
   git clone [https://github.com/your-username/CodexRitual.git](https://github.com/your-username/CodexRitual.git)
   cd CodexRitual
创建并激活虚拟环境 (推荐)

python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
安装依赖

pip install PyQt6 pygments openai
启动程序

python main.py
独立运行 (Windows .exe)
如果您使用的是打包后的 .exe 版本，请直接双击运行 CodexRitual.exe。程序会在首次启动时，自动在您的 我的文档/CodexRitual_Data 目录下生成配置文件和资源文件夹，您后续可以直接在该目录中管理您的资产。

使用教程
1. 基础练习
从顶部的“当前练习”下拉菜单选择代码文件。

按照界面提示进行键入。按下 Tab 键可快速跳过连续的缩进空格。

点击顶部右侧的 [⌨️ 侧边栏] 可呼出或隐藏不同布局的键盘指法图。

2. 激活 AI 导师
点击右上角 [⚙️ 设置]。

在“API 密钥”栏位中安全填入您的 DeepSeek 密钥 (或其他兼容的 OpenAI API Key)。

选中一段需要练习的代码，点击顶部的 [✨ 一键生成注释]。

系统将在后台调用 AI 并自动在当前目录下生成带有详细注释的新代码文件，随后自动重载高亮画布。

3. 导入自定义代码
您可以直接将代码文件放入 Documents/CodexRitual_Data/assets/snippets 目录中。

或通过主界面 [⚙️ 设置] -> [📁 选择本地文件导入...] 快速将外部文件添加至练习环境。

技术架构
CodexRitual/
├── core/                # 核心逻辑与系统引擎层
│   ├── typing_logic.py  # 词法分析与键入状态机映射
│   └── ai_bridge.py     # 异步多线程 AI 通讯模块
├── gui/                 # 界面表现层 (PyQt6)
│   ├── main_window.py   # 主窗口控制、信号路由与文件流转
│   ├── editor_widget.py # 基于 QTextCursor 的高性能渲染画布
│   └── theme_manager.py # 全局状态、QSS 样式及存储管理
├── assets/              # 静态内置资源映射
└── data/                # 提示词模板及默认配置

开发者说明
本项目具有极高的定制性：

修改 AI 行为：程序会自动读取 data/ai_skill.txt 文件中的系统提示词 (System Prompt)。您可以通过修改此文本，令 AI 输出不同口吻或不同深度的代码注释。

自定义语法颜色：可在 theme_manager.py 的字典中调整基于 Token 分类的 Hex 颜色值。

许可证
本项目基于 MIT License 协议开源。