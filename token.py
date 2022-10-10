from keys import *

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
        upper_result = result.upper()
        token = RESERVED_KEYWORDS.get(upper_result,Token(ID,result))
        return token