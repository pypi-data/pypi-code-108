import setuptools
import sys
import xes.AIspeak

if __name__ == '__main__':
    sys.argv += ["sdist"]
setuptools.setup(
    packages=setuptools.find_packages(),
    name="PyQt5_Auto",
    author="Ruoyu Wang",
    author_email="wry2022@outlook.com",
    description="自动配置PyQt5环境/setup PyQt5 environment automatically",
    long_decription="""首先，各位下载该包后在我们写好的PyQt5程序的开头使用import导入便可，例如：
import PyQt5_Auto
或者：
from PyQt5_Auto import *
⚠注意事项：由于该工具使用的是临时的“sys.path += ”语句，该工具配置的环境变量，仅针对于当前进程，所以是临时环境变量而非全局，不可以通过除上述两种方式外的其他方式引用，也不能单独运行。/""" +
                    xes.AIspeak.translate("""首先，各位下载该包后在我们写好的PyQt5程序的开头使用import导入便可，例如：
import PyQt5_Auto
或者：
from PyQt5_Auto import *
⚠注意事项：由于该工具使用的是临时的“sys.path += ”语句，该工具配置的环境变量，仅针对于当前进程，所以是临时环境变量而非全局，不可以通过除上述两种方式外的其他方式引用，也不能单独运行。""")
)
