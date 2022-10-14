from enum import Enum


INTEGER = 'INTEGER'  # 整数类型
REAL = 'REAL'  # 实数类型
INTEGER_CONST = 'INTEGER_CONST'  # 整数（因子）
REAL_CONST = 'REAL_CONST'  # 实数（因子）
PLUS = 'PLUS'  # 加
MINUS = 'MINUS'  # 减
MUL = 'MUL'  # 乘
INTEGER_DIV = 'INTEGER_DIV'  # 整数除法
FLOAT_DIV = 'FLOAT_DIV'  # 浮点数除法
LPAREN = 'LPAREN'  # 左括号
RPAREN = 'RPAREN'  # 右括号
ID = 'ID'  # 变量名称
ASSIGN = 'ASSIGN'  # 赋值符号
BEGIN = 'BEGIN'  # 开始标记
END = 'END'  # 结束标记
SEMI = 'SEMI'  # 分号
DOT = 'DOT'  # 点（程序结束符）
PROGRAM = 'PROGRAM'  # 程序
VAR = 'VAR'  # 变量声明标记
COLON = 'COLON'  # 冒号
COMMA = 'COMMA'  # 逗号
EOF = 'EOF'  # 结束符号
PROCEDURE ='PROCEDURE'

class Token:
    def __init__(self,value_type,value,lineno=None,column=None) -> None:
        self.value_type=value_type
        self.value=value
        self.lineno=lineno
        self.column=column
    
    def __str__(self) -> str:
        """String representation of the class instance.

        Example:
            >>> Token(TokenType.INTEGER, 7, lineno=5, column=10)
            Token(TokenType.INTEGER, 7, position=5:10)
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.value_type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self) -> str:
        return self.__str__()

# RESERVED_KEYWORDS = {  # 保留字
#     'PROGRAM': Token('PROGRAM', 'PROGRAM'),
#     'VAR': Token('VAR', 'VAR'),
#     'DIV': Token('INTEGER_DIV', 'DIV'),
#     'INTEGER': Token('INTEGER', 'INTEGER'),
#     'REAL': Token('REAL', 'REAL'),
#     'BEGIN': Token('BEGIN', 'BEGIN'),
#     'END': Token('END', 'END'),
#     'PROCEDURE': Token('PROCEDURE', 'PROCEDURE'),  # 保留字
# }

class TokenType(Enum):
    # single-character token types
    PLUS          = '+'
    MINUS         = '-'
    MUL           = '*'
    FLOAT_DIV     = '/'
    LPAREN        = '('
    RPAREN        = ')'
    SEMI          = ';'
    DOT           = '.'
    COLON         = ':'
    COMMA         = ','
    # block of reserved words
    PROGRAM       = 'PROGRAM'  # marks the beginning of the block
    INTEGER       = 'INTEGER'
    REAL          = 'REAL'
    INTEGER_DIV   = 'DIV'
    VAR           = 'VAR'
    PROCEDURE     = 'PROCEDURE'
    BEGIN         = 'BEGIN'
    END           = 'END'      # marks the end of the block
    # misc
    ID            = 'ID'
    INTEGER_CONST = 'INTEGER_CONST'
    REAL_CONST    = 'REAL_CONST'
    ASSIGN        = ':='
    EOF           = 'EOF'


def _build_reserved_words():
    tt_list = list(TokenType)
    star_index = tt_list.index(TokenType.PROGRAM)
    end_index = tt_list.index(TokenType.END)
    reserved_keywords={
        token_type.value:Token(token_type,token_type.value)
        for token_type in tt_list[star_index:end_index+1]
    }
    return reserved_keywords


RESERVED_KEYWORDS= _build_reserved_words()