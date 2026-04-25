from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.token import Token
from typing import List, Dict, Any

class TypingMapBuilder:
    """
    打字地图生成引擎。
    负责在代码加载初期，利用 Pygments 进行词法分析，
    将目标代码降维打击成一个一维的字符属性数组（Typing Map），供 GUI 层进行 O(1) 复杂度的实时查询。
    """

    @staticmethod
    def build_map(code: str, filename: str) -> List[Dict[str, Any]]:
        """
        核心解析逻辑。
        将字符串解析为单个字符的集合，并附加语法属性。
        
        返回的数据结构示例：
        [
            {"char": "d", "is_skip": False},
            {"char": "e", "is_skip": False},
            {"char": "#", "is_skip": True}, ...
        ]
        """
        try:
            # 尝试根据文件名（如 .py, .js）获取对应的词法分析器
            lexer = get_lexer_for_filename(filename)
        except Exception:
            # 容错处理：如果是不认识的后缀，降级为纯文本解析
            lexer = TextLexer()

        # 获取 Token 流
        tokens = lexer.get_tokens(code)
        typing_map = []

        for token_type, value in tokens:
            is_comment = (token_type in Token.Comment) or (token_type in Token.String.Doc)
            
            for char in value:
                typing_map.append({
                    "expected_char": char,
                    "is_skip": is_comment,
                    "is_whitespace": char.isspace()
                })
                
        return typing_map


# ==========================================
# 引擎内部测试桩 (Test Stub)
# ==========================================
if __name__ == "__main__":
    # 模拟一段带有注释的 Python 代码
    sample_code = "def add(a, b):\n    # 这是一个加法函数\n    return a + b"
    
    print("引擎启动，开始解析...\n")
    typing_map = TypingMapBuilder.build_map(sample_code, "test.py")
    
    # 打印前 25 个字符的解析结果验证逻辑
    for i, item in enumerate(typing_map[:25]):
        char_display = repr(item['expected_char']) # 使用 repr 显示 \n 等不可见字符
        skip_flag = ">>跳过<<" if item['is_skip'] else "需输入"
        print(f"索引 {i:02d} | 字符: {char_display:<4} | 状态: {skip_flag}")