from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.token import Token
from typing import List, Dict, Any

class TypingMapBuilder:
    
    @staticmethod
    def _get_token_category(token_type) -> str:
        if token_type in Token.Comment or token_type in Token.String.Doc: return "comment"
        if token_type in Token.Keyword: return "keyword"
        if token_type in Token.String: return "string"
        if token_type in Token.Number: return "number"
        if token_type in Token.Name.Function: return "function"
        if token_type in Token.Name.Class: return "class"
        if token_type in Token.Name.Tag: return "tag" # 适配 HTML
        if token_type in Token.Name.Attribute: return "attribute"
        if token_type in Token.Name.Builtin: return "function" # 很多内置函数按 function 标色
        return "default"

    @staticmethod
    def build_map(code: str, filename: str) -> List[Dict[str, Any]]:
        try:
            lexer = get_lexer_for_filename(filename)
        except Exception:
            lexer = TextLexer()

        tokens = lexer.get_tokens(code)
        typing_map = []

        for token_type, value in tokens:
            is_comment = (token_type in Token.Comment) or (token_type in Token.String.Doc)
            # 获取当前词汇的高亮分类
            category = TypingMapBuilder._get_token_category(token_type)
            
            for char in value:
                typing_map.append({
                    "expected_char": char,
                    "is_skip": is_comment,
                    "is_whitespace": char.isspace(),
                    "category": category  # 【新增】将语法基因刻入每一个字符
                })
                
        return typing_map