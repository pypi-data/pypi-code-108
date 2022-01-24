from .parse import config_parse
from .setup import config_setup, strconfig, get_attrs
'''
如果要从json 或者 dict 初始化参数，调用本脚的类

'''

class Config:
    '''
    初始化配置，接受三种参数:
    1. 类
    2. json 文件
    3. dict 参数字典
    '''
    def __init__(self, config, add_parse= True) -> None:
        '''
        接收参数配置，并合并
        '''
        config = config_setup(config)
        attr_dict = get_attrs(config)
        for name, value in attr_dict.items():
            setattr(self, name, value)

        if add_parse:
            self.parse()

    def parse(self):
        '''
        调用argparse，使得可以与用户进行交互
        '''
        config_parse(self)

    def __str__(self):
        '''
        打印配置信息
        '''
        return strconfig(self)