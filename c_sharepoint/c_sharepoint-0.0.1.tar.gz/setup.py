from setuptools import setup, find_packages  

with open("c_sharepoint\README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

# print(long_description)
long_description="""
from c_sharepoint import Share_Point
share_point=Share_Point(base_url,username,password,site)
"""
setup(  
    name = 'c_sharepoint',  
    version = '0.0.1',
    # keywords = ('chinesename',),  
    description = 'c_sharepoint',  
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = 'MIT tencent_message',  
    install_requires = ["requests_ntlm","requests"],  
    packages = ['c_sharepoint'],  # 要打包的项目文件夹
    include_package_data=True,   # 自动打包文件夹内所有数据
    author = 'evanyang',  
    author_email = 'lightyiyi@qq.com',
    url = 'https://www.cnblogs.com/Evan-fanfan/',
    # packages = find_packages(include=("*"),),  
)  


# python setup.py check #检查写的有没有问题，有问题就直接报错了
# python setup.py sdist upload #压缩、并打包上传到pip源上，会在当前目录下产生一个dist文件夹
# #里面就是打好的压缩包
 
# python setup.py sdist #只压缩不上传，就是打成tar.gz这种安装包，给别人用的话直接给他安装包就可以了