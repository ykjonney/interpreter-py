
# -*- coding: utf-8 -*-  
# from __future__ import absolute_import
import os
from keys import *

os.chdir('.')

from token import  Lexer
from symbol_table import NodeVisitor, SourceToSourceCompiler
from ast_parser import Parser




class Interpreter(NodeVisitor):
    GLOBAL_SCOPE={}
    def __init__(self,parser):
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
    program Main;
   var b, x, y : real;
   var z : integer;

   procedure AlphaA(a : integer);
      var b : integer;

      procedure Beta(c : integer);
         var y : integer;

         procedure Gamma(c : integer);
            var x : integer;
         begin { Gamma }
            x := a + b + c + x + y + z+5;
         end;  { Gamma }

      begin { Beta }

      end;  { Beta }

   begin { AlphaA }

   end;  { AlphaA }

   procedure AlphaB(a : integer);
      var c : real;
   begin { AlphaB }
      c := a + b;
   end;  { AlphaB }

begin { Main }
end.  { Main }
    '''
    lexer = Lexer(text)
    parser = Parser(lexer)
    semantic = SourceToSourceCompiler()
    semantic.visit(parser.parser())
    print(semantic.output)
    # interpreter = Interpreter(parser)
    # interpreter.interpret()
    # print(interpreter.GLOBAL_SCOPE)  # 显示输出符号表


if __name__ == '__main__':
    main()