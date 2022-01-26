import zpylib.ast.lexer as lex
from zpylib.grammar.token import tokens, keywords
from zpylib.grammar.type import *
from zpylib.grammar.keyword import py_invert_RESERVED, zpy_invert_RESERVED
from zpylib.grammar.builtin import builtInFunctions, invertBuiltInFunctions
from zpylib.compiler.libcollect import libCollection


# 将代码解析成一个个token，并根据token类型进行相应处理
class TokenHandler():
    def __init__(self, data, targetType):
        self.targetType = targetType
        if self.targetType not in ['py', 'zpy']: # 格式错误
            raise Exception(f"错误: 目标格式 {self.targetType} 只能是 py 或 zpy")
        self.lexer = lex.lex() # 构建 lexer
        self.lexer.input(data) # 向 lexer 传入需要分析的代码
        self.data = data
        self.positionOffset = 0 #原代码与编译后代码的指针偏移量
        self.varMap = self.variableMap()


    # 返回一个包含所有zpy与py映射关系的字典
    def variableMap(self):
        varMap = {}
        libMap = libCollection.map(self.data, self.targetType)
        if self.targetType == 'py':
            builtInMap = builtInFunctions
        elif self.targetType == 'zpy':
            builtInMap = invertBuiltInFunctions
        varMap.update(libMap)
        varMap.update(builtInMap)
        return varMap

    # 分析每个token
    def tokenize(self):
        # Tokenize
        while True:
            token = self.lexer.token()
            if token:
                self.update(token)
            else:
                break # 分析完成后退出循环
        return self.data

    # 根据token更新代码
    def update(self, token):

        # 出现 import 关键字
        if token.type == 'IMPORT':
            # TODO perf import dependency libs
            pass

        # token类型是关键字
        if token.type in keywords:
            if self.targetType == 'py':
                reservedValue = py_invert_RESERVED[token.type]
            elif self.targetType == 'zpy':
                reservedValue = zpy_invert_RESERVED[token.type]
            self.subData(token.value, reservedValue, token.lexpos)

        # token类型是英文变量名
        if token.type == 'NAME': 
            if token.value in self.varMap:
                newValue = self.varMap[token.value]
                self.subData(token.value, newValue, token.lexpos)
            else:
                # TODO feature do some thing
                newValue = token.value

        # token类型是中文变量名
        if token.type == 'ZNAME':
            if token.value in self.varMap:
                newValue = self.varMap[token.value]
                self.subData(token.value, newValue, token.lexpos)
            else:
                # TODO feature do some thing
                # parse some args and translate something
                newValue = token.value

    # 传入新数据，旧数据，在原代码中指针索引，进行数据替换
    def subData(self, oldStr, newStr, index):
        start = index + self.positionOffset
        end = start + len(oldStr)
        self.data = self.data[:start] + newStr + self.data[end:]
        self.positionOffset = self.positionOffset - (len(oldStr) - len(newStr))
