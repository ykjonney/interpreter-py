from keys import *
from generic_error import ErrorCode, ParserError


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
    def __init__(self,var_node,var_type) -> None:# 变量声明由变量和类型组成
        self.var_node = var_node
        self.var_type = var_type

class Type(AST):# 定义类型节点
    def __init__(self,token) -> None:
        self.token = token
        self.name = token.value
        
class ProcedureDecl(AST):  # 添加过程声明节点
    def __init__(self, name, block_node,params):
        self.name = name  # 名称
        self.block_node = block_node  # 块节点
        self.params = params #参数

class Param(AST):
    def __init__(self,var_name,var_type) -> None:
        self.var_name = var_name
        self.var_type = var_type


# 获取ast
class Parser:
    def __init__(self,lexer) -> None:
        self.lexer=lexer  
       
        self.current_token=lexer.get_next_token()
    
    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    # 第一个非终结符因子 
    def factor(self):
        current_token = self.current_token
        if current_token.value_type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOperator(current_token,self.expr())
        elif current_token.value_type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOperator(current_token,self.expr())
        elif current_token.value_type == TokenType.INTEGER_CONST:  # 整数
            self.eat(TokenType.INTEGER_CONST)
            return Num(current_token)
        elif current_token.value_type == TokenType.REAL_CONST:  # 实数
            self.eat(TokenType.REAL_CONST)
            return Num(current_token)
        elif current_token.value_type == TokenType.LPAREN:  # 处理括号内表达式
            self.eat(TokenType.LPAREN)  # 验证左括号
            result = self.expr()  # 计算括号内的表达式
            self.eat(TokenType.RPAREN)  # 验证右括号
            return result  # 返回括号内表达式的值
        else:  # 新增变量因子
            node = self.variable()  # 获取变量节点
            return node  # 返回变量节点

    # 表达式
    def expr(self):
        node = self.term()
        while self.current_token.value_type in (TokenType.PLUS,TokenType.MINUS):
            token = self.current_token
            if self.current_token.value_type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                # result += self.term()
            if self.current_token.value_type  == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                # result -= self.term()
            node = BinOperator(node,token,self.term())
        return node

    # 乘除法运算
    def term(self):
        node = self.factor()
        while self.current_token.value_type in (TokenType.MUL,TokenType.INTEGER_DIV, TokenType.FLOAT_DIV):
            token = self.current_token
            if self.current_token.value_type == TokenType.MUL:
                self.eat(TokenType.MUL)
            
            elif token.value_type == TokenType.INTEGER_DIV:  # 整数除法
                self.eat(TokenType.INTEGER_DIV)
            elif token.value_type == TokenType.FLOAT_DIV:  # 浮点数除法
                self.eat(TokenType.FLOAT_DIV)
            node = BinOperator(node,token,self.factor())
        return node

    def variable(self):# 添加获取变量节点的方法
        node = Variable(self.current_token) # 获取变量节点
        self.eat(TokenType.ID) # 验证变量名称
        return node

    def empty(self):  # 添加获取空语句节点的方法
        return NoOperator()  # 返回空语句节点

    def assignment_statement(self): # 添加获取赋值语句节点的方法
        left = self.variable()  # 获取变量名称节点
        token =self.current_token # 获取当前记号
        self.eat(TokenType.ASSIGN) # 验证赋值符
        right = self.expr() # 获取表达式节点
        node = Assign(left,token,right)  # 组成赋值语句节点
        
        return node

    def statement(self):# 添加获取语句节点的方法
        if self.current_token.value_type == TokenType.BEGIN:
            node = self.compound_statement()
        elif self.current_token.value_type == TokenType.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def statement_list(self):
        node = self.statement()
        nodes=[node]
        while self.current_token.value_type ==TokenType.SEMI:
            self.eat(TokenType.SEMI)
            nodes.append(self.statement())
        if self.current_token.value_type==TokenType.ID:
            self.lexer.error()
        return nodes

    def compound_statement(self):
        self.eat(TokenType.BEGIN)
        nodes = self.statement_list()
        self.eat(TokenType.END)
        root =Compound()
        root.childrens=nodes
        return root 

    def type_spec(self): # 构造变量类型节点的方法
        token = self.current_token
        if token.value_type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
        else:
            self.eat(TokenType.REAL)
        node = Type(token)
        return node

    def variable_declaration(self):# 构造变量声明节点的方法
 
        var_nodes = [Variable(self.current_token)]
        self.eat(TokenType.ID)
        while self.current_token.value_type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Variable(self.current_token))
            self.eat(TokenType.ID)
        self.eat(TokenType.COLON)
        type_code = self.type_spec()
        var_decalarations = [VarDecl(var_node,type_code) for var_node in var_nodes]
        return var_decalarations

    def declarations(self): # 构造声明节点的方法
        declarations = []
        while True: # 遍历声明
            if self.current_token.value_type ==TokenType.VAR:# 如果是变量声明
                self.eat(TokenType.VAR)
                while self.current_token.value_type == TokenType.ID:
                    declarations.extend(self.variable_declaration())
                    self.eat(TokenType.SEMI) # 验证分号
            elif self.current_token.value_type == TokenType.PROCEDURE:
                proc_decl = self.procedure_declaration()
                declarations.append(proc_decl)

            else:  # 否则
                break  # 结束声明遍历
        return declarations
    
    def procedure_declaration(self):
        """procedure_declaration :
            PROCEDURE ID (LPAREN formal_parameter_list RPAREN)? SEMI block SEMI
        """
        self.eat(TokenType.PROCEDURE)
        proc_name = self.current_token.value
        self.eat(TokenType.ID)
        params = []

        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            params = self.formal_parameter_list()
            self.eat(TokenType.RPAREN)

        self.eat(TokenType.SEMI)
        block_node = self.block()
        proc_decl = ProcedureDecl(proc_name, params, block_node)
        self.eat(TokenType.SEMI)
        return proc_decl

    def formal_parameter_list(self):# 添加创建参数列表节点的方法
        if self.current_token.value_type != TokenType.ID:
            return []
        param_nodes = self.formal_parameters() # 添加同类型参数节点到参数节点列表
        while self.current_token.value_type == TokenType.SEMI: # 当前记号是分号时还有更多参数
            self.eat(TokenType.SEMI)
            param_nodes.extend(self.formal_parameters()) 
        return param_nodes
        
    def formal_parameters(self): # 添加创建参数节点的方法
        '''formal_parameters：ID（COMMA ID）* COLON type_spec'''
        param_nodes=[] # 参数节点列表
        param_tokens=[self.current_token] # 参数记号列表
        self.eat(TokenType.ID) # 验证第一个参数名称
        while self.current_token.value_type == TokenType.COMMA:  # 当遇到逗号时
            self.eat(TokenType.COMMA) # 验证逗号
            param_tokens.append(self.current_token) # 添加记号到参数记号列表
            self.eat(TokenType.ID)
        self.eat(TokenType.COLON)
        var_type = self.type_spec() # 获取参数类型节点
        for param_token in param_tokens:
            param_node = Param(Variable(param_token),var_type) # 通过参数记号创建参数节点
            param_nodes.append(param_node)
        return param_nodes

    def block(self):# 构造块节点的方法
        declarations = self.declarations() 
        compound_statement =self.compound_statement()
        node = Block(declarations,compound_statement)
        return node # 块节点由声明节点和符合语句节点组成


    def program(self):  # 添加获取程序所有节点方法
        self.eat(TokenType.PROGRAM) # 验证程序开始标记
        var_node = self.variable()  # 获取变量节点
        program_name = var_node.name  # 获取程序名称
        self.eat(TokenType.SEMI)  # 验证分号
        block_node = self.block()  # 获取块节点
        node = Program(program_name,block_node) # 创建程序节点
        self.eat(TokenType.DOT)# 验证程序结束符号
        return node  # 返回程序节点

    # 定义辅助运算的方法，此方法用于验证记号对象的值类型是否符合运算要求。
    def eat(self,token_type):
        # print(self.current_token.value_type,token_type)
        if self.current_token.value_type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(
            error_code=ErrorCode.UNEXPECTED_TOKEN,
            token=self.current_token,
        )

    def parser(self):  # 定义语法分析器的方法
        node = self.program()
        if self.current_token.value_type != TokenType.EOF:  # 如果当前不是文件末端记号
            self.error(ErrorCode.ID_NOT_FOUND,self.current_token)  # 抛出异常
        return node  # 返回树对象

