import json
from pathlib import Path
from PyQt6.QtGui import QColor

class ThemeManager:
    """
    全局主题与配置管理器。
    采用单例模式的数据结构，统筹 QSS 样式表、Pygments 高亮配色映射及用户偏好持久化。
    """
    
    THEMES = {
        "light": {
            "name": "浅色主题",
            "app_bg": "#F0F2F5",
            "app_fg": "#333333",
            "canvas_bg": "#FFFFFF",
            "colors": {
                "default": QColor("#B0B0B0"),
                "correct": QColor("#007ACC"),
                "error_bg": QColor("#FFCCCC"),
                "error_fg": QColor("#FF0000"),
                "skip": QColor("#E0E0E0"),
                "cursor_bg": QColor("#D0D0D0")
            }
        },
        "dark": {
            "name": "深色主题",
            "app_bg": "#1E1E1E",
            "app_fg": "#D4D4D4",
            "canvas_bg": "#252526",
            "colors": {
                "default": QColor("#666666"),
                "correct": QColor("#4EC9B0"), # VS Code 深色主题经典的青色
                "error_bg": QColor("#5A1D1D"),
                "error_fg": QColor("#FF8080"),
                "skip": QColor("#3A3A3A"),
                "cursor_bg": QColor("#4A4A4A")
            }
        }
    }

    def __init__(self):
        self.config_path = Path(__file__).resolve().parent.parent / "data" / "config.json"
        self.current_theme = "light"
        self.opacity = 1.0  # 1.0 为完全不透明，0.1 为极度透明
        self._load_config()

    def _load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "light")
                    self.opacity = data.get("opacity", 1.0)
            except Exception:
                pass

    def save_config(self):
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({"theme": self.current_theme, "opacity": self.opacity}, f, indent=4)

    def get_canvas_colors(self) -> dict:
        return self.THEMES[self.current_theme]["colors"]

    def get_stylesheet(self) -> str:
        theme = self.THEMES[self.current_theme]
        return f"""
            QMainWindow, QDialog {{ background-color: {theme['app_bg']}; }}
            QLabel {{ color: {theme['app_fg']}; }}
            QFrame {{ background-color: {theme['app_bg']}; border: 1px solid {theme['canvas_bg']}; border-radius: 5px; }}
            QTextEdit {{ 
                background-color: {theme['canvas_bg']}; 
                color: {theme['app_fg']};
                border: 1px solid #444; 
                border-radius: 5px; 
                padding: 10px; 
            }}
            QPushButton {{
                background-color: {theme['canvas_bg']};
                color: {theme['app_fg']};
                border: 1px solid #666;
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{ background-color: #007ACC; color: white; }}
            /* 核心修正：修复下拉菜单展开后的背景色，防止黑底黑字 */
            QComboBox QAbstractItemView {{
                background-color: { '#333333' if self.current_theme == 'dark' else '#FFFFFF' };
                color: {theme['app_fg']};
                selection-background-color: #007ACC;
            }}
        """