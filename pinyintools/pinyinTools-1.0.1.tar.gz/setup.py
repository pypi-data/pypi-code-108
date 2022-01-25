import sys

from setuptools import setup
from xes import AIspeak

if __name__ == '__main__':
    sys.argv += ["sdist"]
setup(
    name='pinyinTools',
    version='1.0.1',
    packages=['pinyinTools'],
    url='https://yangguang-gongzuoshi.top/wry/',
    license='MIT License',
    author='Ruoyu Wang',
    author_email='wry2022@outlook.com',
    description='Python拼音小工具/' + AIspeak.translate('Python拼音小工具'),
    long_description="Python拼音小工具，可以解析键盘输入（适合做输入法）和拼音首字母等/" + AIspeak.translate("Python拼音小工具，可以解析键盘输入（适合做输入法）和拼音首字母等"),
    requires=["pypinyin"]
)
