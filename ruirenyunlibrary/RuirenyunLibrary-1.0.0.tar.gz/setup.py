from setuptools import find_packages, setup

setup(
    name='RuirenyunLibrary',
    version='1.0.0',
    author='tangyi',
    description="瑞人科技自动化测试框架核心库",
    url="http://team.ruirenyun.tech/",
    license="LGPL",
    packages=find_packages(),
    author_email='314666979@qq.com',
    py_modules=["RuirenyunLibrary.MysqlDB","RuirenyunLibrary.PublicLibrary"],
    install_requires = ["selenium==3.141.0","requests==2.25.1","robotframework==4.1.1"],
    package_dir  = {'.': 'RuirenyunLibrary'},
    package_data = {'RuirenyunLibrary': ["*.robot"]},
)