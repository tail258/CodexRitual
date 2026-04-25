# CodexRitual: 面向编程学者的代码打字练习器

`CodexRitual` 在vibe coding的时代，古法编程已经沦为非物质文化遗产，但Ai没办法帮助学者理解代码。本项目意在通过传统的手敲代码模式，帮助学者理解每一行代码的意义，未来准备接入Ai大模型辅助生成代码的注释，辅助编程学习。

![alt text](image\1.png)

---

## 💡 项目创新点 (Innovation)

### 1. 语义化打字地图 (Semantic Typing Map)
* **创新**：系统并非将代码视为“扁平字符串”，而是通过 `Pygments` 进行词法标记。
* **价值**：能够精准识别 `Comment` 和 `Docstring`。程序会自动通过算法计算出可跳过区域，实现“只练逻辑，不练注释”的高效模式，甚至支持 Python 的三引号文档字符串跳过。

### 2. 混合输入状态机 (Hybrid IME Bypass)
* **创新**：独创的 `inputMethodEvent` 与 `keyPressEvent` 双轨并行机制。
* **价值**：彻底解决了底层按键拦截与操作系统输入法（IME）的冲突。用户可以在代码字符串中无缝切换中英文输入，且拼音输入过程不会破坏代码的等宽排版。

### 3. 智能缩进穿透 (Auto-Indent Penetration)
* **创新**：基于代码上下文的空白符预测算法。
* **价值**：在换行后，系统会自动根据下一行的缩进深度填充空格并标记为“已完成”，光标直接定位至代码起始处，还原真实的 IDE 开发手感。

### 4. 实时渲染性能优化
* **创新**：放弃 `setText` 的全量刷新，采用 `QTextCursor` 局部增量渲染。
* **价值**：即使是数千行的长代码，也能保证每一帧敲击的延迟低于 5ms，配合 `QPropertyAnimation` 实现的平滑滑动，提供丝滑的输入反馈。

---

## ✨ 核心功能 (Features)

| 功能模块 | 详细说明 |
| :--- | :--- |
| **主题引擎** | 内置浅色/深色模式，色彩配比参考 VS Code 官方标准。 |
| **透明窗口** | 支持 10%-100% 背景透明度调节，练习时可隐约透出下方的技术文档或代码参考。 |
| **指法参考** | 右侧可折叠面板，支持自定义上传多套键盘指法布局图。 |
| **动态格言** | 底部轮播展示语录，支持外部 JSON 注入。 |

image\2.png
image\3.png

---

## 🛠️ 技术架构 (Architecture)

image\4.png

---

## 快速开始 (Quick Start)

### 环境要求
- Python 3.8+
- PyQt6
- Pygments

### 安装步骤
1. **克隆并安装依赖**
   ```bash
   git clone https://github.com/your-username/CodeSpeedRunner.git
   cd CodeSpeedRunner
   pip install PyQt6 pygments
   ```
2. **准备资源**
   - 在 `assets/snippets/` 放入你的代码文件（`.py`, `.js`, `.cpp` 等）。
   - 在 `assets/animations/` 放入用于庆祝的 `.gif` 文件。
   - 在 `assets/keyboards/` 放入指法图。

image\5.png
image\6.png
image\7.png

3. **运行**
   ```bash
   python main.py
   ```

image\8.png

---

## 📅 开发路线图 (Roadmap)

- [x] 核心词法解析引擎
- [x] 中文输入法兼容支持
- [x] 多语言自动缩进跳过
- [ ] 接入 AI 大模型一键生成代码注释，辅助理解 (计划中)

## 🤝 参与贡献
如果你有更好的高亮配色方案或性能优化建议，欢迎提交 Pull Request 或 Issue。

## 📄 许可证
本项目基于 [MIT License](LICENSE) 协议开源。

---