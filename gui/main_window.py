import json
import random
import time
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QLabel, QFrame, QPushButton, QComboBox, QSizePolicy,
                             QDialog, QSlider, QFormLayout, QMessageBox, QLCDNumber)
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QTimer

from .editor_widget import CodePracticeCanvas
from .theme_manager import ThemeManager
from core.typing_logic import TypingMapBuilder

# --- 这里保留你原来的 SettingsDialog 类 ---
class SettingsDialog(QDialog):
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统设置")
        self.setFixedSize(300, 150)
        self.theme_manager = theme_manager
        
        layout = QFormLayout(self)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("浅色 (Light)", "light")
        self.combo_theme.addItem("深色 (Dark)", "dark")
        index = self.combo_theme.findData(self.theme_manager.current_theme)
        if index >= 0: self.combo_theme.setCurrentIndex(index)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        layout.addRow("界面主题:", self.combo_theme)
        
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(10, 100)
        self.slider_opacity.setValue(int(self.theme_manager.opacity * 100))
        self.slider_opacity.valueChanged.connect(self._on_opacity_changed)
        layout.addRow("背景透明度:", self.slider_opacity)

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

# --- 新增的庆祝动画弹窗类 ---
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

# --- 终极整合版主窗口 ---
class CodeRunnerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Speed Runner")
        self.resize(1200, 800)
        
        self.base_dir = Path(__file__).resolve().parent.parent
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
        
        # --- 连接画布的开始和结束信号 ---
        self.canvas.signal_started.connect(self._on_typing_started)
        self.canvas.signal_finished.connect(self._on_typing_finished)

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
        
        # --- 新增的 LCD 计时器 ---
        self.lcd_timer = QLCDNumber()
        self.lcd_timer.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd_timer.setMinimumWidth(120)
        self.lcd_timer.setStyleSheet("color: #007ACC; border: none; font-weight: bold;")
        self.lcd_timer.display("00:00")
        
        self.btn_settings = QPushButton("⚙️ 设置")
        self.btn_settings.clicked.connect(self._open_settings)
        
        self.btn_toggle_keyboard = QPushButton("⌨️ 侧边栏")
        self.btn_toggle_keyboard.clicked.connect(self._toggle_sidebar)
        
        top_bar.addWidget(label_snippet)
        top_bar.addWidget(self.combo_snippet)
        top_bar.addWidget(self.lcd_timer) # 将计时器放在下拉框旁边
        top_bar.addStretch()
        top_bar.addWidget(self.btn_settings)
        top_bar.addWidget(self.btn_toggle_keyboard)
        main_layout.addLayout(top_bar)
        
        # 2. 工作区与画布
        workspace_layout = QHBoxLayout()
        self.canvas = CodePracticeCanvas()
        workspace_layout.addWidget(self.canvas, stretch=7)
        
        # 3. 侧边栏
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
        
        main_layout.addLayout(workspace_layout)
        
        # 4. 底部栏
        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("font-family: Microsoft YaHei; font-size: 13px; font-style: italic;")
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