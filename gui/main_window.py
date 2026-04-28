import json
import random
import time
import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QFrame, QPushButton, QComboBox, QSizePolicy,
                             QDialog, QSlider, QFormLayout, QMessageBox, QLCDNumber,
                             QSplitter, QTextBrowser, QLineEdit,QFileDialog)
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer

from .editor_widget import CodePracticeCanvas
from .theme_manager import ThemeManager
from core.typing_logic import TypingMapBuilder
from core.ai_bridge import AITaskWorker

class SettingsDialog(QDialog):
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setFixedSize(350, 220)
        self.theme_manager = theme_manager
        
        layout = QFormLayout(self)
        
        # 1. 界面主题
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("浅色 (Light)", "light")
        self.combo_theme.addItem("深色 (Dark)", "dark")
        index = self.combo_theme.findData(self.theme_manager.current_theme)
        if index >= 0: self.combo_theme.setCurrentIndex(index)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        layout.addRow("界面主题:", self.combo_theme)
        
        # 2. 背景透明度
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(10, 100)
        self.slider_opacity.setValue(int(self.theme_manager.opacity * 100))
        self.slider_opacity.valueChanged.connect(self._on_opacity_changed)
        layout.addRow("背景透明度:", self.slider_opacity)

        # ... (前面保留主题和透明度的代码) ...

        # 3. API Key
        self.input_api_key = QLineEdit()
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api_key.setPlaceholderText("填入 API Key")
        self.input_api_key.setText(self.theme_manager.api_key)
        self.input_api_key.textChanged.connect(self._on_api_key_changed)
        layout.addRow("API 密钥:", self.input_api_key)

        # 4. 【新增】接口地址 (Base URL)
        self.input_base_url = QLineEdit()
        self.input_base_url.setPlaceholderText("例如: https://api.deepseek.com/v1")
        self.input_base_url.setText(self.theme_manager.api_base_url)
        self.input_base_url.textChanged.connect(self._on_base_url_changed)
        layout.addRow("接口地址:", self.input_base_url)

        # 5. 【新增】模型选择 (下拉 + 可手动编辑)
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True) # 允许用户手动输入其他厂家的模型名
        self.combo_model.addItems([
            "deepseek-chat",     # DeepSeek V3 (速度/常规)
            "deepseek-reasoner", # DeepSeek R1 (深度思考/Pro)
            "gpt-4o",            # OpenAI
            "moonshot-v1-8k"     # 月之暗面 Kimi
        ])
        self.combo_model.setCurrentText(self.theme_manager.ai_model)
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        layout.addRow("AI 模型:", self.combo_model)

        # 6. 外部代码导入按钮 ...
        self.btn_import = QPushButton("📁 选择本地文件导入...")
        self.btn_import.clicked.connect(self._import_code)
        layout.addRow("外部代码:", self.btn_import)

    def _on_base_url_changed(self, text):
        self.theme_manager.api_base_url = text.strip()
        self.theme_manager.save_config()

    def _on_model_changed(self, text):
        self.theme_manager.ai_model = text.strip()
        self.theme_manager.save_config()

    def _on_theme_changed(self, index):
        theme_id = self.combo_theme.itemData(index)
        self.theme_manager.current_theme = theme_id
        self.parent().apply_global_theme()
        self.theme_manager.save_config()

    def _on_opacity_changed(self, value):
        opacity = value / 100.0
        self.theme_manager.opacity = opacity
        self.parent().setWindowOpacity(opacity)
        self.theme_manager.save_config()

    def _on_api_key_changed(self, text):
        self.theme_manager.api_key = text.strip()
        self.theme_manager.save_config()

    def _import_code(self):
        """处理文件导入逻辑"""
        main_win = self.parent()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择练习代码", "", 
            "代码文件 (*.py *.js *.cpp *.c *.java *.go *.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                dest_dir = main_win.snippets_dir
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / Path(file_path).name
                shutil.copy2(file_path, dest_path) # 将文件复制到 assets/snippets/
                
                # 通知主窗口刷新列表并选中新文件
                main_win._scan_and_load_snippets()
                index = main_win.combo_snippet.findText(dest_path.name)
                if index >= 0:
                    main_win.combo_snippet.setCurrentIndex(index)
                    
                QMessageBox.information(self, "导入成功", f"文件 '{dest_path.name}' 成功加入练习代码！")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"无法复制文件: {e}")

# --- 庆祝动画弹窗类 ---
class CompletionDialog(QDialog):
    def __init__(self, time_spent: float, base_dir: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎉 练习完成！")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")
        layout = QVBoxLayout(self)
        
        # 动画标签
        self.lbl_anim = QLabel()
        self.lbl_anim.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_anim)
        
        # 加载随机动画
        anim_dir = base_dir / "assets" / "animations"
        if anim_dir.exists():
            gifs = [f for f in anim_dir.iterdir() if f.suffix.lower() == '.gif']
            if gifs:
                gif_path = random.choice(gifs)
                self.movie = QMovie(str(gif_path))
                # 调整动画大小以适应窗口
                self.movie.setScaledSize(self.size() * 0.6) 
                self.lbl_anim.setMovie(self.movie)
                self.movie.start()
            else:
                self.lbl_anim.setText("⭐ Excellent! ⭐\n(可在 assets/animations 放入 gif 动画)")
        else:
            self.lbl_anim.setText("⭐ Excellent! ⭐\n(可在 assets/animations 放入 gif 动画)")
            
        # 统计文本
        lbl_stats = QLabel(f"耗时: {time_spent:.2f} 秒\n\n继续保持，肌肉记忆正在形成！")
        lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_stats.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        layout.addWidget(lbl_stats)

# --- 整合版主窗口 ---
class CodeRunnerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodexRitual") # 顺手把名字也统一了
        self.resize(1200, 800)
        
        # 1. 探明真身：确定内部资源路径 (处理 PyInstaller 打包为 exe 的情况)
        if getattr(sys, 'frozen', False):
            self.internal_dir = Path(sys._MEIPASS)
        else:
            self.internal_dir = Path(__file__).resolve().parent.parent
            
        # 2. 锁定外部领地：用户数据路径
        self.user_data_dir = Path.home() / "Documents" / "CodexRitual_Data"
        
        # 3. 首次运行：释放资源到外部领地
        self._init_user_directory()
        
        # 4. 外置工作路径的指针
        self.base_dir = self.user_data_dir
        self.keyboard_dir = self.base_dir / "assets" / "keyboards"
        self.snippets_dir = self.base_dir / "assets" / "snippets"
        self.quotes_file = self.base_dir / "data" / "quotes.json"
        
        self.theme_manager = ThemeManager()
        self.quotes_list = []
        
        # --- 计时器状态初始化 ---
        self.start_time = 0.0
        self.timer_running = False
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._update_timer_display)
        
        self._init_ui()
        self.apply_global_theme()
        self.setWindowOpacity(self.theme_manager.opacity)
        
        self._load_quotes()
        self._scan_and_load_keyboards()
        self._scan_and_load_snippets()
        
        self.quote_timer = QTimer(self)
        self.quote_timer.timeout.connect(self._rotate_quote)
        self.quote_timer.start(30000)
        
        self.canvas.signal_started.connect(self._on_typing_started)
        self.canvas.signal_finished.connect(self._on_typing_finished)

    def _init_user_directory(self):
        """核心本能：如果用户文档里没有数据文件夹，自动释放内置的 assets 和 data"""
        if not self.user_data_dir.exists():
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            
            for folder in ["assets", "data"]:
                src = self.internal_dir / folder
                dst = self.user_data_dir / folder
                if src.exists():
                    shutil.copytree(src, dst, dirs_exist_ok=True)

    def apply_global_theme(self):
        self.setStyleSheet(self.theme_manager.get_stylesheet())
        self.canvas.apply_theme_colors(self.theme_manager.get_canvas_colors())
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. 顶部栏
        top_bar = QHBoxLayout()
        label_snippet = QLabel("当前练习:")
        label_snippet.setStyleSheet("font-weight: bold; font-family: Microsoft YaHei; font-size: 14px;")
        
        self.combo_snippet = QComboBox()
        self.combo_snippet.setMinimumWidth(200)
        self.combo_snippet.currentIndexChanged.connect(self._on_snippet_changed)
        
        self.lcd_timer = QLCDNumber()
        self.lcd_timer.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd_timer.setMinimumWidth(120)
        self.lcd_timer.setStyleSheet("color: #007ACC; border: none; font-weight: bold;")
        self.lcd_timer.display("00:00")
        
        self.btn_toggle_timer = QPushButton("隐藏计时")
        self.btn_toggle_timer.clicked.connect(self._toggle_timer_visibility)

        self.btn_ai_gen = QPushButton("✨ 一键生成注释")
        self.btn_ai_gen.setStyleSheet("color: #4EC9B0; font-weight: bold;")
        self.btn_ai_gen.clicked.connect(self._generate_ai_comments)
        
        # --- 【新增】AI 面板切换按钮 ---
        self.btn_toggle_ai = QPushButton("隐藏 AI")
        self.btn_toggle_ai.clicked.connect(self._toggle_ai_panel)
        
        self.btn_toggle_keyboard = QPushButton("⌨️ 侧边栏")
        self.btn_toggle_keyboard.clicked.connect(self._toggle_sidebar)

        self.btn_settings = QPushButton("⚙️ 设置")
        self.btn_settings.clicked.connect(self._open_settings)
        
        # 组装顶部栏 (将三个视图控制按钮放在右侧)
        top_bar.addWidget(label_snippet)
        top_bar.addWidget(self.combo_snippet)
        top_bar.addWidget(self.lcd_timer) 
        top_bar.addWidget(self.btn_toggle_timer)
        top_bar.addWidget(self.btn_ai_gen) 
        top_bar.addStretch() # 把后面的按钮推到最右边
        top_bar.addWidget(self.btn_toggle_ai)      # 新增的 AI 切换按钮
        top_bar.addWidget(self.btn_toggle_keyboard)
        top_bar.addWidget(self.btn_settings)
        main_layout.addLayout(top_bar)
        
        # 2. 工作区与画布 (使用 QSplitter 进行左右分割)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧 AI 对话区
        self.ai_panel = QWidget()
        ai_layout = QVBoxLayout(self.ai_panel)
        ai_layout.setContentsMargins(0, 0, 10, 0)
        
        self.chat_display = QTextBrowser()
        self.chat_display.setStyleSheet("font-family: Microsoft YaHei; font-size: 13px;")
        self.chat_display.append("<b>[系统]</b> CodexRitual AI 已上线。")
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Enter and discuss with AI ...")
        self.chat_input.returnPressed.connect(self._send_chat_message)
        
        ai_layout.addWidget(QLabel("Communicate With AI"))
        ai_layout.addWidget(self.chat_display, stretch=1)
        ai_layout.addWidget(self.chat_input)
        
        self.main_splitter.addWidget(self.ai_panel)
        
        # 右侧：原有的代码区 + 指法图侧边栏
        right_panel = QWidget()
        workspace_layout = QHBoxLayout(right_panel)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = CodePracticeCanvas()
        workspace_layout.addWidget(self.canvas, stretch=7)
        
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(350)
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.combo_keyboard = QComboBox()
        self.combo_keyboard.currentIndexChanged.connect(self._on_keyboard_changed)
        sidebar_layout.addWidget(self.combo_keyboard)
        self.img_keyboard = QLabel("暂无指法图")
        self.img_keyboard.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_keyboard.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sidebar_layout.addWidget(self.img_keyboard, stretch=1)
        workspace_layout.addWidget(self.sidebar_frame, stretch=3)
        
        self.main_splitter.addWidget(right_panel)
        self.main_splitter.setSizes([300, 900]) 
        
        # --- 【核心修复】加上 stretch=1，强制分割器填满多余的垂直空间 ---
        main_layout.addWidget(self.main_splitter, stretch=1)
        
        # 4. 底部栏
        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("font-family: Microsoft YaHei; font-size: 13px; font-style: italic; margin-top: 10px;")
        main_layout.addWidget(self.footer_label)

    # --- 计时器与完成动画逻辑 ---
    def _on_typing_started(self):
        """画布发出首次击键信号时触发"""
        self.start_time = time.time()
        self.timer_running = True
        self.ui_timer.start(100) # 每100ms刷新一次界面显示

    def _update_timer_display(self):
        """实时更新 LCD 数字"""
        if not self.timer_running: return
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        self.lcd_timer.display(f"{mins:02d}:{secs:02d}")

    def _on_typing_finished(self):
        """画布发出完成信号时触发"""
        self.timer_running = False
        self.ui_timer.stop()
        total_time = time.time() - self.start_time
        
        # 弹出庆祝框
        dialog = CompletionDialog(total_time, self.base_dir, self)
        dialog.exec()

    # --- 外部数据扫描与加载逻辑 ---
    def _load_quotes(self):
        if self.quotes_file.exists():
            try:
                with open(self.quotes_file, 'r', encoding='utf-8') as f:
                    self.quotes_list = json.load(f)
            except Exception:
                pass
        if not self.quotes_list:
            self.quotes_list = [{"text": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"}]
        self._rotate_quote()

    def _rotate_quote(self):
        quote_data = random.choice(self.quotes_list)
        self.footer_label.setText(f"{quote_data.get('text', '')} —— {quote_data.get('author', '佚名')}")

    def _scan_and_load_snippets(self):
        self.combo_snippet.blockSignals(True)
        self.combo_snippet.clear()
        
        if not self.snippets_dir.exists():
            self.snippets_dir.mkdir(parents=True, exist_ok=True)
            
        snippet_files = [f for f in self.snippets_dir.iterdir() if f.is_file() and f.suffix in {'.py', '.js', '.txt', '.cpp', '.java', '.go'}]
        
        if not snippet_files:
            self.combo_snippet.addItem("无可用代码 (请放入 snippets)", "")
        else:
            for file_path in snippet_files:
                self.combo_snippet.addItem(file_path.name, str(file_path))
                
        self.combo_snippet.blockSignals(False)
        if self.combo_snippet.count() > 0:
            self._on_snippet_changed(0)

    def _on_snippet_changed(self, index: int):
        if index < 0: return
        file_path_str = self.combo_snippet.itemData(index)
        if not file_path_str: return
            
        # 切换代码时，重置计时器
        self.timer_running = False
        self.ui_timer.stop()
        self.lcd_timer.display("00:00")
            
        file_path = Path(file_path_str)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_code = f.read()
            typing_map = TypingMapBuilder.build_map(raw_code, file_path.name)
            self.canvas.load_code_and_map(raw_code, typing_map)
        except Exception as e:
            QMessageBox.warning(self, "读取失败", f"无法加载代码文件:\n{e}")

    # --- 侧边栏与设置相关逻辑 ---
    def _open_settings(self):
        dialog = SettingsDialog(self.theme_manager, self)
        dialog.exec()

    def _toggle_sidebar(self):
        self.sidebar_frame.setVisible(not self.sidebar_frame.isVisible())

    def _toggle_sidebar(self):
        self.sidebar_frame.setVisible(not self.sidebar_frame.isVisible())

    def _toggle_ai_panel(self):
        """控制左侧 AI 对话舱的显示与隐藏"""
        if self.ai_panel.isVisible():
            self.ai_panel.setVisible(False)
            self.btn_toggle_ai.setText("显示 AI")
        else:
            self.ai_panel.setVisible(True)
            self.btn_toggle_ai.setText("隐藏 AI")

    def _toggle_timer_visibility(self):
        if self.lcd_timer.isVisible():
            self.lcd_timer.setVisible(False)
            self.btn_toggle_timer.setText("显示计时")
        else:
            self.lcd_timer.setVisible(True)
            self.btn_toggle_timer.setText("隐藏计时")

    def _scan_and_load_keyboards(self):
        self.combo_keyboard.clear()
        if not self.keyboard_dir.exists(): return
        image_files = [f for f in self.keyboard_dir.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg"}]
        for img_path in image_files:
            self.combo_keyboard.addItem(img_path.name, str(img_path))

    def _on_keyboard_changed(self, index: int):
        if index < 0: return
        pixmap = QPixmap(self.combo_keyboard.itemData(index))
        if not pixmap.isNull():
            self.img_keyboard.setPixmap(pixmap.scaled(320, 800, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    # =============== AI链路逻辑 ================
    def _generate_ai_comments(self):
        """一键触发 AI 注释生成"""
        current_code = self.canvas.toPlainText()
        if not current_code.strip():
            QMessageBox.warning(self, "无法施法", "当前画布为空，没有可供分析的代码！")
            return
            
        # 1. 加载提示词技能
        skill_path = self.base_dir / "data" / "ai_skill.txt"
        system_prompt = "请为代码添加详尽中文注释，只输出代码本身。"
        if skill_path.exists():
            with open(skill_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                
        # 2. 动态读取 API Key
        api_key = self.theme_manager.api_key
        
        if not api_key:
            QMessageBox.warning(self, "缺少魔力源泉", "请先点击右上角的「⚙️ 设置」，填入你的 AI API 密钥！")
            return
            
        # 3. 锁定按钮与 UI 状态
        self.btn_ai_gen.setEnabled(False)
        self.btn_ai_gen.setText("⏳ AI 灵魂注入中...")
        self.chat_display.append("<br><b>[系统]</b> 正在向 DeepSeek 传输代码结构，请稍候...")
        
        # 4. 启动异步后台神经元
        # 在 _generate_ai_comments 中找到这一行并修改：
        self.ai_worker = AITaskWorker(
            provider_type="openai_compatible", # 统一改为兼容模式
            api_key=api_key, 
            base_url=self.theme_manager.api_base_url, # 传入动态 URL
            model_name=self.theme_manager.ai_model,   # 传入动态模型
            context_code=current_code, 
            prompt_text=system_prompt,
            task_type="comment"
        )

        self.chat_worker = AITaskWorker(
            provider_type="openai_compatible",
            api_key=api_key, 
            base_url=self.theme_manager.api_base_url, 
            model_name=self.theme_manager.ai_model, 
            context_code=current_code, 
            prompt_text=user_text, 
            task_type="chat"
        )

    def _on_ai_success(self, new_code: str):
        """AI 处理成功，执行文件流转"""
        self.btn_ai_gen.setEnabled(True)
        self.btn_ai_gen.setText("✨ 一键生成注释")
        
        # 构建新文件名 (在原文件后加上 _AI_Commented)
        original_name = self.combo_snippet.currentText()
        if not original_name: original_name = "practice.py"
        parts = original_name.rsplit('.', 1)
        base_name = parts[0]
        ext = parts[1] if len(parts) > 1 else "py"
        new_filename = f"{base_name}_AI_Commented.{ext}"
        
        # 写入物理文件
        save_path = self.snippets_dir / new_filename
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
            
        # 重新扫描文件夹并强制跳转到新生成的代码上
        self._scan_and_load_snippets()
        index = self.combo_snippet.findText(new_filename)
        if index >= 0:
            self.combo_snippet.setCurrentIndex(index)
            
        self.chat_display.append("<br><span style='color:#4EC9B0;'><b>[系统]</b> 注入完成！新代码已自动加载，高亮引擎已就绪。</span>")

    def _on_ai_error(self, error_msg: str):
        """处理网络或环境异常"""
        self.btn_ai_gen.setEnabled(True)
        self.btn_ai_gen.setText("✨ 一键生成注释")
        QMessageBox.critical(self, "AI 连接断开", error_msg)
        self.chat_display.append(f"<br><span style='color:#FF8080;'><b>[错误]</b> {error_msg}</span>")

    def _send_chat_message(self):
        """处理左侧对话框的用户输入并发送给大模型"""
        user_text = self.chat_input.text().strip()
        if not user_text: return
        
        # 1. 显示用户消息，并锁定输入框防止连续发送
        self.chat_display.append(f"<br><b>🧑‍💻 你:</b> {user_text}")
        self.chat_input.clear()
        self.chat_input.setEnabled(False)
        
        api_key = self.theme_manager.api_key
        if not api_key:
            self.chat_display.append("<br><span style='color:#FF8080;'><b>[错误]</b> 缺少魔力源泉，请先在右上角「设置」中填入 API 密钥！</span>")
            self.chat_input.setEnabled(True)
            return

        self.chat_display.append("<i>🤖 正在结合代码上下文推演逻辑，请稍候...</i>")
        
        # 2. 提取当前画布代码作为上下文，启动聊天神经元
        current_code = self.canvas.toPlainText()
        self.chat_worker = AITaskWorker(
            provider_type="openai_compatible",
            api_key=api_key, 
            base_url=self.theme_manager.api_base_url, 
            model_name=self.theme_manager.ai_model, 
            context_code=current_code, 
            prompt_text=user_text, 
            task_type="chat"
        )
        self.chat_worker.signal_finished.connect(self._on_chat_success)
        self.chat_worker.signal_error.connect(self._on_chat_error)
        self.chat_worker.start()

    def _on_chat_success(self, reply_text: str):
        """AI 回复成功"""
        # 将返回的换行符替换为 HTML 换行，保证排版美观
        formatted_reply = reply_text.replace("\n", "<br>")
        self.chat_display.append(f"<br><b>🤖 AI:</b> {formatted_reply}")
        
        # 解锁输入框，光标重新聚焦，并将滚动条拉到最底
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus()
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_chat_error(self, error_msg: str):
        """AI 连接失败"""
        self.chat_display.append(f"<br><span style='color:#FF8080;'><b>[错误]</b> 脑波连接断开: {error_msg}</span>")
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus()