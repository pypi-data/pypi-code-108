
'''
版本号管理
'''

import re


class CIVersionManager(object):

    '''
    判断传入的字符串是否符合版本号结构
    '''
    @staticmethod
    def isVersion(version):
        rule = "\.{2,10}"
        rule2 = "^\d+(\.\d+){0,10}$"
        res = re.search(rule, version)
        if (res == None):
            result = re.search(rule2, version)
            if (result):
                return True
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    isversion = CIVersionManager.isVersion('1.1.2')
    print(isversion)