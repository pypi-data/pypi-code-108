from distutils.core import setup

setup(
    name='fzyfirstModel',  # 对外我们模块的名字
    version='1.0',  # 版本号
    description='这是第一个对外发布的模块，测试',  # 描述
    author='fzy',  # 作者
    author_email='f335125303@163.com',
    py_modules=['fzyfirstModel.demo1', 'fzyfirstModel.demo2']  # 要发布的模块
)
