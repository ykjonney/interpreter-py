from collections import OrderedDict

from . import _SHOULD_LOG_SCOPE

from generic_error import ErrorCode, SemanticError




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


class ProcedureSymbol(Symbol):  # 添加过程符号类
    def __init__(self, name, params=None):  # 过程包含名称与形式参数信息
        super().__init__(name)
        self.params = params if params is not None else []  # 获取形式参数，如果未传入则为空列表。

    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}',parameters={self.params})>"  # 过程的信息

    __repr__ = __str__

class ScopedSymbolTable:#符号表
    def __init__(self,scope_name,scope_level,enclosing_scope) -> None:
        self._symbols = OrderedDict()
        self.scope_name = scope_name #添加作用域名称
        self.scope_level =scope_level #添加作用于级别
        self.enclosing_scope = enclosing_scope  # 添加外围作用域
        # self._init_builtins()

    def _init_builtins(self):  # 定义初始化内置类型的方法
        self.insert(BuiltinTypeSymbol('INTEGER'))  # 通过insert()方法存入内置类型符号
        self.insert(BuiltinTypeSymbol('REAL'))  # 通过insert()方法存入内置类型符号

    def __str__(self) -> str:
        scope_header = '作用域符号表：'
        lines = ['\n', scope_header, '=' * len(scope_header) * 2]
        for header_name, header_value in (
                ('作用域名称', self.scope_name),
                ('作用域级别', self.scope_level),
                ('外围作用域', self.enclosing_scope.scope_name if self.enclosing_scope else None)  # 如果不存在外围作用域则为None
        ):  # 遍历作用域名称和级别以及外围作用域
            lines.append(f'{header_name:15}:{header_value}')
            symtab_header = '符号表中的内容：'
            lines.extend(['\n', symtab_header, '-' * len(symtab_header) * 2])
            lines.extend([f'{key:8}: {value}' for key, value in self._symbols.items()])
            s = '\n'.join(lines)
        return s  # 返回打印内容

    __repr__ = __str__

    def insert(self,symbol):
        # print(f'存入:{symbol}')
        self._symbols[symbol.name] = symbol # 以符号名称为键存入符号

    def lookup(self, name,current_scope_only=False):  # 添加查询方法
        # print(f'查询：{name}(作用域：{self.scope_name})')
        symbol = self._symbols.get(name)
        # print(symbol)
        if symbol:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope : # 如果当前作用域没有找到符号并且存在外围作用域
            return self.enclosing_scope.lookup(name) # 递归方式在外围作用域进行查找

    


# class SemanticAnalyzer(NodeVisitor):
class SourceToSourceCompiler(NodeVisitor):# 修改语义分析器为源到源编译器
    def __init__(self) -> None:
        self.current_scope = None
        self.output = None  # 添加输出内容变量
    
    def error(self, error_code, token):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def log(self, msg):
        if _SHOULD_LOG_SCOPE:
            print(msg)

    def visit_BinOperator(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f'{left} {node.operator.value} {right}'

    def visit_Assign(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f'{left} := {right}'

    def visit_Num(self, node):
        return node.value

    def visit_Program(self, node):  # 添加与访问变量声明相关的访问方法
        # print('>>>>进入作用域：global')
        result_str = f'program {node.name}0\n' # 添加程序声明到输出内容
        global_scope = ScopedSymbolTable(scope_name='global', scope_level=1,enclosing_scope=self.current_scope)
        global_scope._init_builtins() # 初始化内置类型
        self.current_scope = global_scope  #  将创建的符号表对象存入指定变量，对符号表的查询与插入将通过此变量进行。
        result_str += self.visit(node.block)
        result_str +=(f'.{{END OF {node.name} }}') # 添加程序结束信息到输出内容
        self.output = result_str
        # print(global_scope)  # 显示输出符号表信息
        self.current_scope = self.current_scope.enclosing_scope
        # print('<<< 离开作用域：global')  # 显示输出离开作用域的信息

    def visit_ProcedureDecl(self,node):
        proc_name = node.name # 获取过程节点名称
        proc_symbol = ProcedureSymbol(proc_name) # 创建过程符号
        self.current_scope.insert(proc_symbol) # 过程符号添加到当前作用域
        # print(f'>>>>进入作用域：{proc_name}') # 显示输出进入过程作用域
        proc_scope = ScopedSymbolTable(scope_name=proc_name,scope_level=self.current_scope.scope_level+1,
                                        enclosing_scope=self.current_scope)# 创建过程的作用域符号表
        self.current_scope = proc_scope # 当前作用域设置为过程作用域
        result_str=f'procedure {proc_name}{self.current_scope.scope_level}' # 添加过程声明到输出内容
        if node.params:
            result_str +='(' # 添加左括号到输出内容
        formal_params = []  # 形参列表
        for param in node.params: # 遍历过程的形式参数列表
            param_type = self.current_scope.lookup(param.var_type.name) # 获取参数类型
            param_name = param.var_name.name # 获取参数名称
            param_symbol = VarSymbol(param_name,param_type) # 创建参数符号
            self.current_scope.insert(param_symbol) # 将参数符号添加到当前作用域
            proc_symbol.params.append(param_symbol) # 为过程符号参数列表添加参数符号
            formal_params.append(f'{param_name}{self.current_scope.scope_level} : {param_type}')  # 参数信息添加到形参列表
        result_str += ';'.join(formal_params)
        if node.params:
            result_str += ')'
        result_str +=';\n'
        result_str +=self.visit(node.block_node) # 访问过程中的块节点
        result_str +=f';{{END OF {proc_name}}}' # 添加过程结束信息到输出内容
        result_str = '\n'.join('   '+line for line in result_str.splitlines()) # 过程代码每行添加3个空格
        # print(proc_scope)
        self.current_scope = self.current_scope.enclosing_scope
        # print(f'<<< 离开作用域：{proc_name}')  # 显示输出离开过程作用域
        return result_str

    def visit_Block(self, node):  # 添加与访问变量声明相关的访问方法
        results = []
        for declaration in node.declarations:
            result = self.visit(declaration)
            results.append(result)
        results.append('begin')
        result = self.visit(node.compound_statement)
        result = '   '+result
        results.append(result)
        results.append('end')
        return '\n'.join(results)

    def visit_Variable(self,node):
        var_name = node.name
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:  # 如果变量未声明
            self.error(error_code=ErrorCode.ID_NOT_FOUND, token=node.token)  # 抛出语义错误
        return f'<{var_name}{self.current_scope.scope_level}:{var_symbol.symbol_type}>'  # 返回变量信息内容

    def visit_VarDecl(self, node):  # 添加访问变量声明的方法
        symbol_type = node.var_type.name
        self.current_scope.lookup(symbol_type)  # 从符号表查询内置类型符号
        var_name = node.var_node.name
        if self.current_scope.lookup(var_name,current_scope_only=True) is not None:  # 查询变量名称，如果存在变量信息
            self.error(ErrorCode.DUPLICATE_ID,node.var_node.token)   # 抛出异常
        var_symbol = VarSymbol(var_name, symbol_type)
        self.current_scope.insert(var_symbol)
        return f'   var {var_name}{self.current_scope.scope_level} : {symbol_type}' # 返回变量声明信息

    def visit_Compound(self, node):  # 添加与访问复合语句相关的访问方法
        results = []
        for child in node.childrens:
            
            result = self.visit(child)
            if result:
                results.append(result)
        return '\n'.join(results)

    def visit_NoOperator(self, node):  # 添加与访问变量声明相关的访问方法
        pass
    
    def visit_UnaryOp(self, node):
        pass
    