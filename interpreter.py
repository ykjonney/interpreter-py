
from collections import OrderedDict
import os


os.chdir('.')
print(os.getcwd())
from token import  Token,Lexer

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
PROCEDURE = 'PROCEDURE'
class AST():
    pass

class BinOperator(AST):
    def __init__(self,left,operator,right) -> None:
        self.left = left
        self.token = self.operator = operator
        self.right = right

class Num(AST):
    def __init__(self,token) -> None:
        self.token = token
        self.value = token.value

class UnaryOperator(AST):  # 定义一元运算符节点类
    def __init__(self, operator, expr):  # 初始化
        self.token = self.operator = operator  # 运算符记号和运算符节点
        self.expr = expr  # 一元运算符的子表达式

class Compound(AST):  # 添加复合语句节点
    def __init__(self) -> None:
        self.childrens = []  # 子节点列表

class Assign(AST):  # 添加赋值语句节点
    def __init__(self, left, operator, right):
        self.left = left  # 变量名称
        self.token = self.operator = operator  # 记号和赋值符号
        self.right = right  # 右侧表达式

class Variable(AST):  # 添加变量节点
    def __init__(self, token):
        self.token = token  # 记号
        self.name = token.value  # 变量值

class NoOperator(AST):  # 添加空语句节点
    pass  # 无内容

class Program(AST): # 定义程序节点
    def __init__(self,name,block) -> None: # 程序由名称和语句块组成
        self.name = name
        self.block = block

class Block(AST): # 定义语句块节点
    def __init__(self,declarations,compound_statement) -> None: # 语句块由声明和符合语句组成
        self.declarations = declarations
        self.compound_statement = compound_statement
    
class VarDecl(AST): # 定义变量声明节点
    def __init__(self,var_name,var_type) -> None:# 变量声明由变量和类型组成
        self.var_name = var_name
        self.var_type = var_type

class Type(AST):# 定义类型节点
    def __init__(self,token) -> None:
        self.token = token
        self.name = token.value
        
class ProcedureDecl(AST):  # 添加过程声明节点
    def __init__(self, name, block_node):
        self.name = name  # 名称
        self.block_node = block_node  # 块节点

# 获取ast
class Parser:
    def __init__(self,lexer:Lexer) -> None:
        self.lexer=lexer  
       
        self.current_token=lexer.get_next_token()

    # 第一个非终结符因子 
    def factor(self):
        current_token = self.current_token
        if current_token.value_type == PLUS:
            self.eat(PLUS)
            return UnaryOperator(current_token,self.expr())
        elif current_token.value_type == MINUS:
            self.eat(MINUS)
            return UnaryOperator(current_token,self.expr())
        elif current_token.value_type == INTEGER_CONST:  # 整数
            self.eat(INTEGER_CONST)
            return Num(current_token)
        elif current_token.value_type == REAL_CONST:  # 实数
            self.eat(REAL_CONST)
            return Num(current_token)
        elif current_token.value_type == LPAREN:  # 处理括号内表达式
            self.eat(LPAREN)  # 验证左括号
            result = self.expr()  # 计算括号内的表达式
            self.eat(RPAREN)  # 验证右括号
            return result  # 返回括号内表达式的值
        else:  # 新增变量因子
            node = self.variable()  # 获取变量节点
            return node  # 返回变量节点

    # 表达式
    def expr(self):
        node = self.term()
        while self.current_token.value_type in (PLUS,MINUS):
            token = self.current_token
            if self.current_token.value_type == PLUS:
                self.eat(PLUS)
                # result += self.term()
            if self.current_token.value_type  == MINUS:
                self.eat(MINUS)
                # result -= self.term()
            node = BinOperator(node,token,self.term())
        return node

    # 乘除法运算
    def term(self):
        node = self.factor()
        while self.current_token.value_type in (MUL,INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if self.current_token.value_type == MUL:
                self.eat(MUL)
            
            elif token.value_type == INTEGER_DIV:  # 整数除法
                self.eat(INTEGER_DIV)
            elif token.value_type == FLOAT_DIV:  # 浮点数除法
                self.eat(FLOAT_DIV)
            node = BinOperator(node,token,self.factor())
        return node

    def variable(self):# 添加获取变量节点的方法
        node = Variable(self.current_token) # 获取变量节点
        self.eat(ID) # 验证变量名称
        return node

    def empty(self):  # 添加获取空语句节点的方法
        return NoOperator()  # 返回空语句节点

    def assignment_statement(self): # 添加获取赋值语句节点的方法
        left = self.variable()  # 获取变量名称节点
        token =self.current_token # 获取当前记号
        self.eat(ASSIGN) # 验证赋值符
        right = self.expr() # 获取表达式节点
        node = Assign(left,token,right)  # 组成赋值语句节点
        
        return node

    def statement(self):# 添加获取语句节点的方法
        if self.current_token.value_type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.value_type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def statement_list(self):
        node = self.statement()
        nodes=[node]
        while self.current_token.value_type ==SEMI:
            self.eat(SEMI)
            nodes.append(self.statement())
        if self.current_token.value_type==ID:
            self.lexer.error()
        print(self.current_token)
        return nodes

    def compound_statement(self):
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)
        root =Compound()
        root.childrens=nodes
        return root 

    def type_spec(self): # 构造变量类型节点的方法
        token = self.current_token
        if token.value_type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node

    def variable_declaration(self):# 构造变量声明节点的方法
 
        var_nodes = [Variable(self.current_token)]
        self.eat(ID)
        while self.current_token.value_type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Variable(self.current_token))
            self.eat(ID)
        self.eat(COLON)
        type_code = self.type_spec()
        var_decalarations = [VarDecl(var_node,type_code) for var_node in var_nodes]
        return var_decalarations

    def declarations(self): # 构造声明节点的方法
        declarations = []
        while True: # 遍历声明
            if self.current_token.value_type == VAR:# 如果是变量声明
                self.eat(VAR)
                while self.current_token.value_type == ID:
                    declarations.extend(self.variable_declaration())
                    self.eat(SEMI) # 验证分号
            elif self.current_token.value_type == PROCEDURE:
                self.eat(PROCEDURE)
                procedure_name = self.current_token.value
                self.eat(ID)
                self.eat(SEMI)
                block_node = self.block()
                procedure_decl = ProcedureDecl(procedure_name, block_node)
                declarations.append(procedure_decl)
                self.eat(SEMI)
            else:  # 否则
                break  # 结束声明遍历
        return declarations

    def block(self):# 构造块节点的方法
        declarations = self.declarations() 
        compound_statement =self.compound_statement()
        node = Block(declarations,compound_statement)
        return node # 块节点由声明节点和符合语句节点组成


    def program(self):  # 添加获取程序所有节点方法
        self.eat(PROGRAM) # 验证程序开始标记
        var_node = self.variable()  # 获取变量节点
        program_name = var_node.name  # 获取程序名称
        self.eat(SEMI)  # 验证分号
        block_node = self.block()  # 获取块节点
        node = Program(program_name,block_node) # 创建程序节点
        self.eat(DOT)# 验证程序结束符号
        return node  # 返回程序节点

    # 定义辅助运算的方法，此方法用于验证记号对象的值类型是否符合运算要求。
    def eat(self,token_type):
        # print(self.current_token.value_type,token_type)
        if self.current_token.value_type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.lexer.error()

    def parser(self):  # 定义语法分析器的方法
        node = self.program()
        if self.current_token.value_type != EOF:  # 如果当前不是文件末端记号
            self.lexer.error()  # 抛出异常
        return node  # 返回树对象


class NodeVisitor():
    def visit(self,node):
        method_name = 'visit_'+type(node).__name__ # 获取节点类型名称组成访问器方法名（子类Interpreter中方法的名称）
        visitor = getattr(self,method_name,self.generic_visit)
        return visitor(node)

    def generic_visit(self,node):
        raise Exception(f'未找到“visit_{type(node).__name__}()”方法！')


class Symbol:
    def __init__(self,name,symbol_type=None) -> None:
        self.name = name
        self.symbol_type = symbol_type

class BuiltinTypeSymbol(Symbol): #内建类型
    def __init__(self, name, symbol_type=None) -> None:
        super().__init__(name, symbol_type)
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"  # 输出类名和符号名称

class VarSymbol(Symbol):
    def __init__(self, name, symbol_type=None) -> None:
        super().__init__(name, symbol_type)
    
    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}':type='{self.symbol_type}')>"  # 输出类名、符号名称和类型

    __repr__ = __str__

class SymbolTable:#符号表
    def __init__(self) -> None:
        self._symbols = OrderedDict()
        self._init_builtins()

    def _init_builtins(self):  # 定义初始化内置类型的方法
        self.insert(BuiltinTypeSymbol('INTEGER'))  # 通过insert()方法存入内置类型符号
        self.insert(BuiltinTypeSymbol('REAL'))  # 通过insert()方法存入内置类型符号

    def __str__(self) -> str:
        symtab_header = '符号表中的内容：'
        lines = [symtab_header, '-' * len(symtab_header) * 2]  # 头部标题与分割线存入打印内容的列表
        lines.extend([f'{key:8}: {value}' for key, value in self._symbols.items()])  # 符号表内容合并到打印内容列表
        s = '\n'.join(lines)  # 以换行符连接每个列表元素组成字符串
        return s  # 返回打印内容

    __repr__ = __str__

    def insert(self,symbol):
        print(f'存入:{symbol}')
        self._symbols[symbol.name] = symbol # 以符号名称为键存入符号

    def lookup(self, name):  # 添加查询方法
        print(f'查询：{name}')
        symbol = self._symbols.get(name)
        return symbol

class SemanticAnalyzer(NodeVisitor):
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()

    def visit_BinaryOperator(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Assign(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Program(self, node):  # 添加与访问变量声明相关的访问方法
        self.visit(node.block)

    def visit_Block(self, node):  # 添加与访问变量声明相关的访问方法
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_Variable(self,node):
        var_name = node.name
        var_symbol = self.symbol_table.lookup(var_name)
        if var_symbol is None:  # 如果变量未声明
            raise NameError(f'引用了不存在的标识符：{repr(var_name)}')  # 抛出语义错误

    def visit_VarDecl(self, node):  # 添加访问变量声明的方法
        symbol_type = node.type_node.name
        self.symbol_table.lookup(symbol_type)  # 从符号表查询内置类型符号
        var_name = node.var_node.name
        if self.symbol_table.lookup(var_name) is not None:  # 查询变量名称，如果存在变量信息
            raise Exception(f'错误：发现重复的标识符：{var_name}')  # 抛出异常
        var_symbol = VarSymbol(var_name, symbol_type)
        self.symbol_table.insert(var_symbol)

    def visit_Compound(self, node):  # 添加与访问变量声明相关的访问方法
        for child in node.childrens:
            self.visit(child)

    def visit_NoOperator(self, node):  # 添加与访问变量声明相关的访问方法
        pass

class Interpreter(NodeVisitor):
    GLOBAL_SCOPE={}
    def __init__(self,parser) -> None:
        self.parser = parser

    def visit_BinOperator(self,node):
        if node.operator.value_type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator.value_type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator.value_type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator.value_type == INTEGER_DIV:  # 如果是整数除法
            return self.visit(node.left) // self.visit(node.right)  # 返回整数除法运算结果
        elif node.operator.value_type == FLOAT_DIV:  # 如果是浮点数除法
            return self.visit(node.left) / self.visit(node.right)  # 返回浮点数除法运算结果
    
    def visit_Num(self, node):
        return node.value

    def visit_UnaryOperator(self,node):
        if node.operator.value_type == PLUS:  # 如果运算符类型是加号
            return +self.visit(node.expr)  # 返回正的访问子节点的结果
        if node.operator.value_type == MINUS:  # 如果运算符类型是减号
            return -self.visit(node.expr)  # 返回负的访问子节点的结果

    def visit_Compound(self,node):# 访问复合语句节点
        for child in node.childrens:  # 遍历复合语句节点的子节点
            self.visit(child) # 访问子节点

    def visit_Assign(self,node):# 访问赋值语句节点
        var_name = node.left.name # 获取变量名称
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right) # 以变量名称为键添加变量值到符号表
    
    def visit_Variable(self,node):# 访问变量节点
        var_name = node.name
        value = self.GLOBAL_SCOPE.get(var_name)
        if value is None:
            raise NameError(f'错误的标识符：{repr(var_name)}')
        else:
            return value
    
    def visit_NoOperator(self,node):
        pass

    def visit_VarDecl(self, node):  # 添加访问变量声明的方法
        pass  # 无需处理

    def visit_Type(self, node):  # 添加访问类型的方法
         pass  # 无需处理

    def visit_Program(self,node):
        self.visit(node.block)

    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def interpret(self): # 执行解释的方法
        tree = self.parser.parser() # 获取语法分析器分析后的树对象
        return self.visit(tree) # 返回访问树对象的计算结果

def main():
    # while True:  # 循环获取输入
    #     try:
    #         text = input('>>>')  # 获取用户输入
    #     except EOFError:  # 捕获到末端错误时退出
    #         break
    #     if not text:  # 如果未输入时继续提示输入
    #         continue
    #     lexer = Lexer(text)
    #     parser = Parser(lexer)
    #     interpreter = Interpreter(parser)  # 实例化解释器对象
    #     result = interpreter.interpreter()  # 执行运算方法获取运算结果
    #     print(text, '=', result)  # 
    text = '''
    PROGRAM Part10AST;
    VAR
        a, b : INTEGER;
        y    : REAL;

    BEGIN {Part10AST}
        a := 2;
        b := 10 * a + 10 * a DIV 4;
        y := 20 / 7 + 3.14;
    END.  {Part10AST}
    '''
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()
    print(interpreter.GLOBAL_SCOPE)  # 显示输出符号表


if __name__ == '__main__':
    main()