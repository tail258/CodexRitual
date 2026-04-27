from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation

class CodePracticeCanvas(QTextEdit):
    """
    定制化的代码输入画布 (终极形态)
    新增：打字进度保持、QPropertyAnimation平滑下滑、首字母触发/完成信号。
    """
    # 信号：通知主控室开始计时、结束计时
    signal_started = pyqtSignal()
    signal_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_canvas_settings()
        self._typing_map = []
        self._current_index = 0
        self.colors = {}
        self._has_started = False
        
        # 预备平滑滚动动画引擎
        self.scroll_anim = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.scroll_anim.setDuration(150) # 150毫秒的平滑过渡

    def _init_canvas_settings(self) -> None:
        font = QFont("Consolas", 14)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.viewport().setCursor(Qt.CursorShape.BlankCursor)
        self.setCursorWidth(0)
        self.setAcceptRichText(False)

    def apply_theme_colors(self, colors_dict: dict):
        """核心修正：切换主题时，仅重绘颜色，不重置光标和进度"""
        self.colors = colors_dict
        if not self._typing_map: return
        
        # 挂起界面刷新，进行静默重绘以防止闪烁
        self.setUpdatesEnabled(False)
        for i in range(len(self._typing_map)):
            if i < self._current_index:
                # 已敲击部分：重新应用正确/跳过的颜色
                is_skip = self._typing_map[i]["is_skip"]
                self._set_format(i, fg=self.colors["skip"] if is_skip else self.colors["correct"])
            elif i == self._current_index:
                self._render_virtual_cursor()
            else:
                # 未敲击部分：全部刷为默认灰或跳过灰
                is_skip = self._typing_map[i]["is_skip"]
                self._set_format(i, fg=self.colors["skip"] if is_skip else self.colors["default"])
        self.setUpdatesEnabled(True)

    def load_code_and_map(self, raw_code: str, typing_map: list) -> None:
        self._typing_map = typing_map
        self._current_index = 0
        self._has_started = False
        
        self.setPlainText(raw_code)
        self.selectAll()
        
        fmt = QTextCharFormat()
        fmt.setForeground(self.colors.get("default", QColor("#B0B0B0")))
        fmt.setBackground(QColor(Qt.GlobalColor.transparent))
        
        self.textCursor().mergeCharFormat(fmt)
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)
        
        self._advance_to_next_typable()

    def keyPressEvent(self, event) -> None:
        if self._current_index >= len(self._typing_map):
            return 

        if not self._has_started:
            self._has_started = True
            self.signal_started.emit()

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier: return

        key = event.key()
        text = event.text()

        if key == Qt.Key.Key_Backspace:
            self._handle_backspace()
            return

        if key == Qt.Key.Key_Tab:
            for _ in range(4): self._process_character_input(" ")
            return

        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            text = "\n"

        if not text: return

        self._process_character_input(text)

    def inputMethodEvent(self, event) -> None:
        """
        [核心修正] 中文输入法 (IME) 事件专门接管。
        剥离原生的拼音内联显示（防止破坏等宽排版），只接收最终上屏的中文字符串。
        """
        if self._current_index >= len(self._typing_map):
            return

        # 获取输入法最终确认上屏的字符串（比如选中的中文字词，或按回车输入的纯英文字母）
        commit_string = event.commitString()
        
        if commit_string:
            # 触发计时器启动（如果是第一下敲击）
            if not self._has_started:
                self._has_started = True
                self.signal_started.emit()
                
            # 将上屏的字符串拆解为单字，逐一喂给我们的打字状态机
            for char in commit_string:
                self._process_character_input(char)
        
        # 核心防御：必须 accept() 且绝对不调用 super().inputMethodEvent()。
        # 这会告诉操作系统：“我已经拿到了中文字，你不要再自作主张往画布里塞拼音下划线了！”
        event.accept()

    def _process_character_input(self, input_char: str) -> None:
        target_node = self._typing_map[self._current_index]
        expected_char = target_node["expected_char"]
        if expected_char == "\n" and input_char == "\r": input_char = "\n"

        is_correct = (input_char == expected_char)
        self._apply_char_format(self._current_index, is_correct)
        self._current_index += 1
        
        if is_correct and input_char == "\n":
            self._auto_skip_indentation()
        else:
            self._advance_to_next_typable()
            
        self._check_completion()

    def _check_completion(self):
        """检查是否敲击完毕，触发庆祝信号"""
        if self._current_index >= len(self._typing_map):
            self._reset_char_format(self._current_index - 1) # 清除最后一个光标
            self.signal_finished.emit()

    def _handle_backspace(self) -> None:
        if self._current_index <= 0: return
        self._reset_char_format(self._current_index)
        self._current_index -= 1
        while self._current_index > 0 and self._typing_map[self._current_index]["is_skip"]:
            self._reset_char_format(self._current_index)
            self._current_index -= 1
        self._reset_char_format(self._current_index)
        self._render_virtual_cursor()

    def _advance_to_next_typable(self) -> None:
        while self._current_index < len(self._typing_map) and self._typing_map[self._current_index]["is_skip"]:
            target_node = self._typing_map[self._current_index]
            category = target_node.get("category", "comment")
            syntax_color = self.colors.get("syntax", {}).get(category, self.colors.get("skip"))
            
            self._set_format(self._current_index, fg=syntax_color)
            self._current_index += 1
            
        if self._current_index < len(self._typing_map):
            self._render_virtual_cursor()
            self._ensure_cursor_visible()

    def _ensure_cursor_visible(self):
        """核心修正：计算逻辑光标的物理坐标，触发平滑滚动"""
        cursor = self.textCursor()
        cursor.setPosition(self._current_index)
        rect = self.cursorRect(cursor)
        
        viewport_height = self.viewport().height()
        # 如果光标距离底部不足 80 像素，开始滚动
        if rect.bottom() > viewport_height - 80:
            current_scroll = self.verticalScrollBar().value()
            target_scroll = current_scroll + 100 # 向下滚动步长
            
            self.scroll_anim.stop()
            self.scroll_anim.setStartValue(current_scroll)
            self.scroll_anim.setEndValue(target_scroll)
            self.scroll_anim.start()

    def _auto_skip_indentation(self) -> None:
        while self._current_index < len(self._typing_map):
            target = self._typing_map[self._current_index]
            if target["expected_char"] == " ":
                self._apply_char_format(self._current_index, True)
                self._current_index += 1
            else:
                break
        self._advance_to_next_typable()

    def _apply_char_format(self, index: int, is_correct: bool) -> None:
        if is_correct:
            # 动态获取当前字符应该显示的高亮色
            target_node = self._typing_map[index]
            category = target_node.get("category", "default")
            syntax_color = self.colors.get("syntax", {}).get(category, self.colors["correct"])
            self._set_format(index, fg=syntax_color)
        else:
            self._set_format(index, fg=self.colors["error_fg"], bg=self.colors["error_bg"])

    def _reset_char_format(self, index: int) -> None:
        if index < len(self._typing_map):
            # 只要退格，熄灭成基础预载灰色
            color = self.colors["default"]
            self._set_format(index, fg=color, bg=QColor(Qt.GlobalColor.transparent))

    def _render_virtual_cursor(self) -> None:
        if self._current_index < len(self._typing_map):
            self._set_format(self._current_index, bg=self.colors["cursor_bg"])

    def _set_format(self, index: int, fg: QColor = None, bg: QColor = None) -> None:
        cursor = self.textCursor()
        cursor.setPosition(index)
        cursor.setPosition(index + 1, QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat()
        if fg: fmt.setForeground(fg)
        if bg: fmt.setBackground(bg)
        cursor.mergeCharFormat(fmt)