import re
from zpylib.lib import lib

class LibCollection():

    # 根据依赖到库中取出对应的索引
    def map(self, data, targetType):
        libs = self.collect(data)
        for lib_item in libs:
            lib.load(lib_item, targetType)
        if targetType == 'py':
            return lib.zpyMap
        if targetType == 'zpy':
            return lib.pyMap

    # 依赖收集
    def collect(self, data):
        pyLibs = self.collectPy(data)
        zpyLibs = self.collectZpy(data)
        return pyLibs + zpyLibs

    # python 依赖收集
    @staticmethod
    def collectPy(file):
        libs = []

        import_pattern = re.compile(r'^\s*import.+$', re.M)
        import_lib = import_pattern.findall(file)

        from_pattern = re.compile(r'^\s*from.+$', re.M)
        from_lib = from_pattern.findall(file)

        for lib_item in import_lib:
            lib_str = re.search(r'(?<=import\s).+$', lib_item).group()
            lib_list = lib_str.split(',')
            for item in lib_list:
                item = item.replace(' ', '')
                libs.append(item)

        for lib_item in from_lib:
            lib_str = re.search(r'(?<=from\s).+(?=\simport)', lib_item).group()
            lib_str = lib_str.replace(' ', '')
            libs.append(lib_str)

        return libs

    # zpy 依赖收集
    @staticmethod
    def collectZpy(file):
        libs = []

        import_pattern = re.compile(r'^\s*导入.+$', re.M)
        import_lib = import_pattern.findall(file)

        from_pattern = re.compile(r'^\s*从.+$', re.M)
        from_lib = from_pattern.findall(file)

        for lib_item in import_lib:
            lib_str = re.search(r'(?<=导入\s).+$', lib_item).group()
            lib_list = lib_str.split(',')
            for item in lib_list:
                item = item.replace(' ', '')
                libs.append(item)

        for lib_item in from_lib:
            lib_str = re.search(r'(?<=从\s).+(?=\s导入)', lib_item).group()
            lib_str = lib_str.replace(' ', '')
            libs.append(lib_str)

        return libs

    # 弃用：直接根据替换代码
    @staticmethod
    def compile(file, libs, targetType='py'):
        methodList = []
        for lib_item in libs:
            info = lib.load(lib_item, targetType)
            if info is not None:
                methodList.append(info)
        for lib_item in methodList:
            file = LibCollection.replaceKey(file, lib_item['zpy'], lib_item['name'], targetType)
            for func in lib_item['functions']:
                file = LibCollection.replaceKey(file, func['zpy'], func['name'], targetType)
                if 'args' in func:
                    for arg in func['args']:
                        file = LibCollection.replaceKey(file, arg['zpy'], arg['name'], targetType)
        return file

    # 弃用：根据传入映射替换代码
    @staticmethod
    def replaceKey(file, key, value, targetType):
        if targetType == 'zpy':
            value, key = key, value
        pattern = eval(f"f'(?<=([^\u4e00-\u9fa5\w])){key}(?=\(.*\))'")
        file = re.sub(key, value, file, count=0, flags=0)
        return file

libCollection = LibCollection()