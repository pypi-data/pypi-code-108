'''
Podfile 中的组件转为对象Model
'''


class CIComponentModel(object):
    # 组件名
    name = ''
    # 版本号
    version = ''
    # git地址
    git = ''
    # 分支名
    branch = ''
    # configurations
    configurations = ''
    # other
    other = ''

    def __init__(self, name='', version='', git='', branch='', configurations='', other=''):
        self.name = name
        self.version = version
        self.git = git
        self.branch = branch
        self.configurations = configurations
        self.other = other

    def logInfo(self):
        print('---------------------------------------------')
        print("name:", self.name)
        print("version:", self.version)
        print("git:", self.git)
        print("branch:", self.branch)
        print("configurations:", self.configurations)
        print("other:", self.other)

if __name__ == '__main__':
    model = CIComponentModel(name='YYModel', version='1.1.0', git='https://gitlab.com/YYModel.git', configurations='configurations')
    model.logInfo()