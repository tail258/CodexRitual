import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import CodeRunnerWindow

def main():
    """
    程序主入口。初始化 PyQt 应用事件循环并拉起主窗口。
    """
    app = QApplication(sys.argv)
    
    # 强制在 Windows 下使用现代风格
    app.setStyle("Fusion")
    
    window = CodeRunnerWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()