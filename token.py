
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
    def __init__(self,value_type,value) -> None:
        self.value_type=value_type
        self.value=value
    
    def __str__(self) -> str:
        return 'Token ({},{})'.format(self.value_type,self.value)

    def __repr__(self) -> str:
        return self.__str__()

RESERVED_KEYWORDS = {  # 保留字
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
    'PROCEDURE': Token('PROCEDURE', 'PROCEDURE'),  # 保留字
}
class Lexer:
    def __init__(self,text) -> None:
        self.text=text  
        self.pos = 0
        self.current_char=self.text[self.pos]

    def error(self):
        raise Exception('输入错误的内容')

    # 获取token
    def get_next_token(self):
        while self.current_char is not None:
            char = self.current_char
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            if self.current_char.isdigit():
                return self.number()
            if self.current_char == '+':
                self.advance()
                return Token(PLUS,char)
            if self.current_char == '-':
                self.advance()
                return Token(MINUS,char)
            if self.current_char == '*':
                self.advance()
                return Token(MUL,char)
            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV,char)
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN,char)
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN,char)

            if self.current_char.isalpha():
                return  self._id()
            if self.current_char ==':' and self.peek() =='=':
                self.advance()
                self.advance()
                return Token(ASSIGN,':=')
            if self.current_char == ';':
                self.advance()
                return Token(SEMI,';')
            if self.current_char == ',':
                self.advance()
                return Token(COMMA,',')
            if self.current_char == ':':
                self.advance()
                return Token(COLON,':')
            if self.current_char == '.':
                self.advance()
                return Token(DOT,'.')
            else:
                self.error()
        return Token(EOF,None)

    def peek(self):
        pos = self.pos + 1  # 获取下一个位置
        if pos >= len(self.text):  # 如果超出文本末端
            return None  # 返回None
        else:  # 否则
            return self.text[pos]  # 返回下一位置字符

    # 获取下一个字符
    def advance(self):
        self.pos +=1
        if self.pos >=len(self.text):
            self.current_char=None
        else:
            self.current_char = self.text[self.pos]

    # 跳过空格
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()

    def number(self):  # 获取多位数字
        result = ''
        while self.current_char is not None and self.current_char.isdigit():  # 如果当前字符不是None值并且当前字符是数字
            result += self.current_char  # 连接数字
            self.advance()  # 获取下一个字符
            if self.current_char == '.':
                result += '.'
                self.advance()
                while self.current_char is not None and self.current_char.isdigit():
                    result += self.current_char
                    self.advance()
               
                return Token(REAL_CONST,float(result))
        return Token(INTEGER_CONST,int(result))  # 返回数字  

    def _id(self): # 获取保留字或赋值名称记号的方法
        result = ''
        while self.current_char is not None and self.current_char.isalnum():# 如果当前字符是字母数字
            result += self.current_char
            self.advance()
        token = RESERVED_KEYWORDS.get(result,Token(ID,result))
        
        return token