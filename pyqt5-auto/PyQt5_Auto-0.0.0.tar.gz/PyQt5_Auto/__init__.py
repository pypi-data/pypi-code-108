#By I'm_Chris
#可以引用或者修改此代码，但是不可销毁或者修改原作者信息

print("\033[044mPyQt5自动环境配置工具(By I'm_Chris)\033[000m",end="\n\n\n")

#返回值：0：正常操作、1.用户取消、2.未知错误、3.pip安装出错、4.环境变量配置出错
global flag
flag=False

import sys, os, platform, time
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    
except ImportError:
    a=input("\033[007m您未配置PyQt5环境，是否进行配置？（输入1进行配置，输入其他则退出程序）")
    if a=="1":
        flag=True
    else:
        sys.exit(1)
        
except:
    print("\n\n\033[031m\033[047m出现未知错误\033[000m")
    sys.exit(2)

if flag:
    print("\n\n\033[000m\033[045m开始安装PyQt5第三方包\033[000m\n\n")
    if os.system(f'"{sys.executable}" -m pip install pyqt5==5.15.4 -i https://pypi.doubanio.com/simple')!=0:
        print("\n\n\033[031m\033[047mpip安装出现错误，请检查您的网络或者您的Python环境中是否已经部署好了pip，详细信息可以从pip展示的日志中获取\033[000m")
        sys.exit(3)
    print("\n\n\033[045mPyQt5第三方包安装成功！\033[000m\n\n")

a=input("\033[007m您未配置PyQt5环境变量，是否进行配置？（输入1进行配置，输入其他则退出程序）")
if a=="1":
    
    print("\033[000m\033[045m开始配置PyQt5系统环境变量\033[000m\n\n")
    try:
        sysstr = platform.system()
        if sysstr=="Windows":
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']=f"{os.path.split(sys.executable)[0]}\\Lib\\site-packages\\PyQt5\\Qt5\\plugins"
        else:
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']=f"{os.path.split(sys.executable)[0]}/Lib/site-packages/PyQt5/Qt5/plugins"
    except Exeception:
        print("\033[031m\033[047m环境变量设置出现问题，错误：",Exception,"\033[000m")
        sys.exit(4)
    print("\033[045m环境变量设置成功，3秒后进入程序\033[000m")    
else:
    sys.exit(1)
    
time.sleep(3)

    
sysstr = platform.system()
if sysstr=="Windows":
    os.system("cls")
else:
    os.system("clear")
