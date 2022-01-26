import os
import json


class Lib():

    def __init__(self, stdlibs, level='warn'):
        self.level = level # none | log | warn | strict
        self.path = self.getPath()
        self.pyLibs = {}
        self.zpyLibs = {}
        self.pyMap = {}
        self.zpyMap = {}
        self.stdLoad(stdlibs)
    
    # 导入标准库和内置函数到映射
    def stdLoad(self, stdlibs):
        for lib in stdlibs:
            libInfo = self.loadFile(lib['path'])
            self.full(lib, libInfo)
    
    # 把根据库声明读取到的库信息写入到映射
    def full(self, lib, libInfo):
        self.fill(libInfo, lib['path'])
        for func in libInfo['functions']:
            self.fill(func, lib['path'])
        for arg in libInfo['args']:
            self.fill(arg, lib['path'])
    
    # 库信息的name，functions，args字段全部写入到映射
    def fill(self, libItem, path):
        libName = libItem['name']
        libZpy = libItem['zpy']
        if libName in self.pyMap and self.pyMap[libName] != libZpy:
            self.log(f'Python变量名映射冲突 {path} {self.pyMap[libName]} - {libZpy}')
            return
        elif libZpy in self.zpyMap and self.zpyMap[libZpy] != libName:
            self.log(f'Zpy变量名映射冲突 {path} {self.zpyMap[libZpy]} - {libName}')
            return
        self.pyMap[libName] = libZpy
        self.zpyMap[libZpy] = libName
        
    # 当前所在路径
    def getPath(self):
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dir = '/lib'
        path = project + dir
        return path

    # 导入依赖库
    def use(self, libs):
        # 构建pyLibs, 构建zpyLibs
        for lib in libs:
            # 库重复
            if lib['name'] in self.pyLibs or lib['zname'] in self.zpyLibs:
                self.log('已经存在库: ', lib)
                continue
            self.pyLibs[lib['name']] = lib
            self.zpyLibs[lib['zname']] = lib
        return self

    # 导出依赖项映射表
    def load(self, libName, targetType='py'):
        if targetType == 'py':
            if libName in self.zpyLibs:
                lib = self.zpyLibs[libName]
                libInfo = self.loadFile(lib['path'])
                self.full(lib, libInfo)
            else:
                self.log(f'找不到库 - {libName}')
        elif targetType == 'zpy':
            if libName in self.pyLibs:
                lib = self.pyLibs[libName]
                libInfo = self.loadFile(lib['path'])
                self.full(lib, libInfo)
            else:
                self.log(f'找不到库 - {libName}')
        else:
            raise Exception(f'错误: 目标格式 {self.targetType} 只能是 py 或 zpy')

    # 导出json文件内容到字典格式
    def loadFile(self, filename):
        content = self.readFile(filename)
        return json.loads(content)

    # 读取文件内容
    def readFile(self, filename):
        try:
            with open(self.path + '/' + filename) as file:
                content = file.read()
                file.close()
            return content
        except Exception as e:
            raise Exception(f'错误: 找不到文件 {filename}\n目录: {self.path}')

    # 输出
    def log(self, msg):
        if self.level == 'log':
            print(f'日志: {msg}')
        elif self.level == 'warn':
            print(f'警告: {msg}')
        elif self.level == 'strict':
            raise Exception(f'错误: {msg}')
        else:
            pass

    # 反转字典
    @staticmethod
    def invert_dict(d):
        return dict(zip(d.values(), d.keys()))
