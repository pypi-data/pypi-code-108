from .tokenhandler import TokenHandler

# 编译器
class Compiler(object):

    # 编译
    def compile(self, file, targetType):
        self.file = file
        self.targetType = targetType
        self.result = ''
        if self.targetType == 'zpy':
            return self.pyToZpy(self.file)
        elif self.targetType == 'py':
            return self.zpyToPy(self.file)
        else:
            raise Exception(f"错误: 目标格式 {self.targetType} 只能是 py 或 zpy")

    # python 编译到 zpy
    @staticmethod
    def pyToZpy(file):
        pyFile = file
        # TODO py to zpy
        tokenHandler = TokenHandler(pyFile, 'zpy')
        zpyFile = tokenHandler.tokenize()
        return zpyFile

    # zpy 编译到 py
    @staticmethod
    def zpyToPy(file):
        zpyFile = file
        # TODO py to py
        tokenHandler = TokenHandler(zpyFile, 'py')
        pyFile = tokenHandler.tokenize()
        return pyFile
