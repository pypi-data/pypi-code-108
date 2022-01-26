import os
from zpylib.compiler import compiler

# 传入文件名和目标格式，通过编译器编译后返回
class Build(object):

    def __init__(self, filename, targetType=None):
        self.cwd = os.getcwd()
        self.filename = filename
        self.targetType = targetType
        self.fileType = self.getFileType()
        self.file = self.readFile()
        self.code = None
        self.build()

    def getFileType(self):
        return self.filename.split('.')[1]

    def readFile(self):
        try:
            with open(self.filename) as raw:
                script = raw.read()
                raw.close()
            return script
        except Exception as e:
            raise Exception(f"错误: 找不到文件 {self.filename}\n目录: {self.cwd}")

    def build(self):
        if self.targetType and self.targetType not in ['py', 'zpy']:
            raise Exception(f"错误: 目标格式 {self.targetType} 只能是 py 或 zpy")
            return
        elif self.fileType not in ['py', 'zpy']:
            raise Exception(f"错误: 文件格式 {self.fileType} 只能是 py 或 zpy")
            return
        elif self.targetType == self.fileType:
            print("警告: 原格式与目标格式相同")
            return
        elif self.targetType is None:
            if self.fileType == 'zpy': self.targetType ='py'
            elif self.fileType == 'py': self.targetType ='zpy'
            else: raise Exception(f"错误: 文件格式 {self.fileType} 只能是 py 或 zpy")

        self.code = compiler.compile(self.file, self.targetType)
        return self.code
