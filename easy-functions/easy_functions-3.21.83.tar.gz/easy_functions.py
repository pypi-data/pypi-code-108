"""声明
easy_functions是一个简单但实用的Python模块，可以通过import文件里的def函数和类(class)来达到简化代码运行的效果
已经开发了许多功能，目前还在继续开发新的功能
本模块使用MIT协议
"""
import os
import sys
import time
import socket
import tempfile
cmdlist = [
    'bigfont','literally','wait','cls',
    'title','find_file','start','call',
    'Vbs','color','mode','shield',
    'choice','Cipher','mkdir','copy',
    'pause','find_suffix','help','Environment<Beta>',
    'update','getIP'
    ,'version','log'
] # 命令列表，以大写字母开头的为类(class)
__all__ = cmdlist
c = 0
d = 0
for i in cmdlist:
    if i.istitle():
        c += 1
d = len(cmdlist) - c
__version__ = str(c) + '.' + str(d) + '.' + '83' # 版本号
__author__ = 'Jerry\n我的QQ号：2711893794' # 作者
class FunctionSyntaxError(Exception): # 异常
    pass
def bigfont( name ): # 大字显示
    """
    大字显示功能
    用法：文件名或<import...as...>命令别名.bigfont('字母、空格或点')
    """
    lngth = len(name) 
    l = ""
    for x in range(0, lngth): 
        c = name[x] 
        c = c.upper()
        if (c == "A"): 
            print("..######..\n..#....#..\n..######..", end = " ") 
            print("\n..#....#..\n..#....#..\n\n") 
              
        elif (c == "B"): 
            print("..######..\n..#....#..\n..#####...", end = " ") 
            print("\n..#....#..\n..######..\n\n") 
              
        elif (c == "C"): 
            print("..######..\n..#.......\n..#.......", end = " ") 
            print("\n..#.......\n..######..\n\n") 
              
        elif (c == "D"): 
            print("..#####...\n..#....#..\n..#....#..", end = " ") 
            print("\n..#....#..\n..#####...\n\n") 
              
        elif (c == "E"): 
            print("..######..\n..#.......\n..#####...", end = " ") 
            print("\n..#.......\n..######..\n\n") 
              
        elif (c == "F"): 
            print("..######..\n..#.......\n..#####...", end = " ") 
            print("\n..#.......\n..#.......\n\n") 
              
        elif (c == "G"): 
            print("..######..\n..#.......\n..#.####..", end = " ") 
            print("\n..#....#..\n..#####...\n\n") 
              
        elif (c == "H"): 
            print("..#....#..\n..#....#..\n..######..", end = " ") 
            print("\n..#....#..\n..#....#..\n\n") 
              
        elif (c == "I"): 
            print("..######..\n....##....\n....##....", end = " ") 
            print("\n....##....\n..######..\n\n") 
              
        elif (c == "J"): 
            print("..######..\n....##....\n....##....", end = " ") 
            print("\n..#.##....\n..####....\n\n") 
              
        elif (c == "K"): 
            print("..#...#...\n..#..#....\n..##......", end = " ") 
            print("\n..#..#....\n..#...#...\n\n") 
              
        elif (c == "L"): 
            print("..#.......\n..#.......\n..#.......", end = " ") 
            print("\n..#.......\n..######..\n\n") 
              
        elif (c == "M"): 
            print("..#....#..\n..##..##..\n..#.##.#..", end = " ") 
            print("\n..#....#..\n..#....#..\n\n") 
              
        elif (c == "N"): 
            print("..#....#..\n..##...#..\n..#.#..#..", end = " ") 
            print("\n..#..#.#..\n..#...##..\n\n") 
              
        elif (c == "O"): 
            print("..######..\n..#....#..\n..#....#..", end = " ") 
            print("\n..#....#..\n..######..\n\n") 
              
        elif (c == "P"): 
            print("..######..\n..#....#..\n..######..", end = " ") 
            print("\n..#.......\n..#.......\n\n") 
              
        elif (c == "Q"): 
            print("..######..\n..#....#..\n..#.#..#..", end = " ") 
            print("\n..#..#.#..\n..######..\n\n") 
              
        elif (c == "R"): 
            print("..######..\n..#....#..\n..#.##...", end = " ") 
            print("\n..#...#...\n..#....#..\n\n") 
              
        elif (c == "S"): 
            print("..######..\n..#.......\n..######..", end = " ") 
            print("\n.......#..\n..######..\n\n") 
              
        elif (c == "T"): 
            print("..######..\n....##....\n....##....", end = " ") 
            print("\n....##....\n....##....\n\n") 
              
        elif (c == "U"): 
            print("..#....#..\n..#....#..\n..#....#..", end = " ") 
            print("\n..#....#..\n..######..\n\n") 
              
        elif (c == "V"): 
            print("..#....#..\n..#....#..\n..#....#..", end = " ") 
            print("\n...#..#...\n....##....\n\n") 
              
        elif (c == "W"): 
            print("..#....#..\n..#....#..\n..#.##.#..", end = " ") 
            print("\n..##..##..\n..#....#..\n\n") 
              
        elif (c == "X"): 
            print("..#....#..\n...#..#...\n....##....", end = " ") 
            print("\n...#..#...\n..#....#..\n\n") 
              
        elif (c == "Y"): 
            print("..#....#..\n...#..#...\n....##....", end = " ") 
            print("\n....##....\n....##....\n\n") 
              
        elif (c == "Z"): 
            print("..######..\n......#...\n.....#....", end = " ") 
            print("\n....#.....\n..######..\n\n") 
              
        elif (c == " "): 
            print("..........\n..........\n..........", end = " ") 
            print("\n..........\n\n") 
              
        elif (c == "."): 
            print("----..----\n\n")
    return
def literally(text, wait=0.1): # 逐字显示
    """
    逐字显示功能
    用法：文件名或<import...as...>命令别名.literally('文字',显示间隔时间)
    """
    try:
        wait + 1
    except TypeError as e:
        raise FunctionSyntaxError(
            '你输入的值%s不符合运行要求，请输入数字'%type(wait)
        ) from e
    sys.stdout.write("\n " + " " * 60 + "\r")
    sys.stdout.flush()
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(wait)
    return
def wait(wait=1): # 等待功能
    """
    等待功能
    用法：文件名或<import...as...>命令别名.wait(持续的时间)
    """
    try:
        time.sleep(wait)
    except TypeError as e:
        raise FunctionSyntaxError(
            '你输入的值%s不符合运行要求，请输入数字'%type(wait)
        ) from e
    return
def cls(): # 清除命令行
    """
    清除命令行功能
    用法：文件名或<import...as...>命令别名.cls()
    """
    os.system('cls')
    return
def title( title ): # 更改标题
    """
    更改命令行标题功能
    用法：文件名或<import...as...>命令别名.title('标题')
    """
    os.system("title " + title)
    return
def find_file(file, mode): # 检测文件是否存在
    """
    文件查找功能
    用法：文件名或<import...as...>命令别名.find_file('文件路径','模式')")
    共有两种模式可用：
    1."exist?"判断文件是否存在，返回布尔值
    2."import?"判断文件是否可以被导入，返回布尔值
    """
    if not type(file) == type('str'):
        raise FunctionSyntaxError(
            '需要输入字符串，而你输入的是%s'%type(file)
        )
    if mode == 'exist?':
        try:
            f = open(file,'r')
        except FileNotFoundError:
            return False
        else:
            f.close()
            return True
    elif mode == 'import?':
        try:
            __import__(file)
        except ModuleNotFoundError:
            return False
        else:
            return True
    else:
        raise FunctionSyntaxError(
            '没有模式"%s"'%mode
        )
def start( path ): # 启动
    """
    启动功能
    用法：文件名或<import...as...>命令别名.start('路径')
    此命令存在的意义是为了运行除Python文件以外的其他文件或打开一个文件夹
    """
    return os.system("start " + path)
def call( path ): # 文件调用
    """
    文件调用功能
    用法：文件名或<import...as...>命令别名.start('路径')
    start命令和call命令的区别：
    1.start命令在执行时会打开另一个窗口，而call命令不会
    2.call可以获取特定文件的返回值，例如调用.vbs文件，按下弹窗上的按钮后会返回数字
    3.此命令只能用于文件
    """
    return os.system("call " + path)
class Vbs: # 创建并调用弹窗，类用法(class)
    """
    弹窗功能
    用法：变量 = 文件名或<import...as...>命令别名.Vbs()
          变量.shownormal('标题','正文','换行文字')/warningaskcancel('标题','正文','换行文字')/erroraskcancel('标题','正文','换行文字')/...")
    如果想要换行，可以这样：
    import easy_functions as ef
    v = ef.Vbs()
    v.shownormal('a','b','c','d')
    其中，"a"为标题，"b"为正文，"c"和"d"将被换行

    它看上去应该是这样子的(弹窗位置演示)：
    标题处：      |--a------|
    正文处：      |    b    |
    换行的正文：  |    c    |
    换行的正文：  |    d    |
    按键处：      |----确定-|

    换行文字支持无限个，相当于在tkinter的弹窗中使用换行符
    注意：模块tkinter中含有的图标类型以及按键本模块不再编写，请使用模块tkinter
          用户按下Vbs提供的按键后会返回数字，可根据数字判断用户按下的按键
          请自行调试返回值，每个按键的返回值这里不予提供
          警告：标题和正文中不能含有换行符和回车符，这些字符在标题和正文出现将被忽略
    功能Vbs现接受以下图标参数：
    变量.shownormal()-无图标')
    变量.warningaskcancel()-显示警告图标并提供[确认]和[取消]
    变量.erroraskcancel()-显示错误图标并提供[确认]和[取消]
    变量.infoaskcancel()-显示信息图标并提供[确认]和[取消]
    变量.warningaskyesno()-显示警告图标并提供[是]和[否]
    变量.errorretry()-显示错误图标并提供[重试]和[取消]
    """
    def __init__( self ):
        self.path = tempfile.gettempdir() + '\\easy_functionsMSG.vbs'
    def shownormal(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): #无图标
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '0' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
    def warningaskcancel(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): #显示警告图标并提供[确认]和[取消]
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '49' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
    def erroraskcancel(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): #显示错误图标并提供[确认]和[取消]
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '17' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
    def infoaskcancel(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): # 显示信息图标并提供[确认]和[取消]
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '65' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
    def warningaskyesno(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): # 显示警告图标并提供[是]和[否]
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '52' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
    def errorretry(self, title='easy_functions msgbox', message='模块easy_functions，简单，实用', *chr13): # 显示错误图标并提供[重试]和[取消]
        title = title.replace('\n','')
        message = message.replace('\n','')
        title = title.replace('\r','')
        message = message.replace('\r','')
        true = False
        chr = ' '
        if len(chr13) != 0:
            for i in chr13:
                chr = chr + '+ chr(13) + ' + '"' + i + '"'
            true = True
        with open(self.path,'w') as f:
            f.write('wsh.quit(msgbox(')
            f.write('"' + message + '"')
            if true == True:
                f.write(chr)
            f.write(',' + '21' + ',')
            f.write('"' + title + '"')
            f.write('))')
        return call(self.path)
def color( color ): # 更改颜色
    """
    更改命令行颜色
    用法：文件名或<import...as...>命令别名.color('完整颜色编码')
    该功能现接受以下颜色编码：
    0 = 黑色       8 = 灰色
    1 = 蓝色       9 = 淡蓝色
    2 = 绿色       A = 淡绿色
    3 = 浅绿色     B = 淡浅绿色
    4 = 红色       C = 淡红色
    5 = 紫色       D = 淡紫色
    6 = 黄色       E = 淡黄色
    7 = 白色       F = 亮白色
    一个完整的颜色编码由两个颜色编码组成，第一个为背景，第二个为前景')
    你可以通过不同的组合达到不同的颜色效果')
    例如: "color 0a" 将在黑色背景上产生淡绿色字幕')
    再例如："color fc" 将在亮白色背景上产生亮红色前景等'
    """
    colorfontlist = ['0','1','2','3','4','5','6','7']
    colorbacklist = ['8','9','a','b','c','d','e','f']
    try:
        coloroutrange = color[2]
    except IndexError as e:
        try:
            coloroutrange = color[1]
        except IndexError as e:
            raise FunctionSyntaxError(
                '"%s"不是一个完整的颜色编码'%color
            ) from e
        else:
            if color[0].isupper() or color[1].isupper():
                raise FunctionSyntaxError(
                    '"%s"中含有大写字母，颜色编码必须小写'%color
                )
            elif color[0] in colorfontlist and color[1] in colorbacklist:
                os.system('color ' + color)
            elif color[0] in colorbacklist and color[1] in colorfontlist:
                os.system('color ' + color)
            elif color[0] in colorbacklist and color[1] in colorbacklist:
                os.system('color ' + color)
            elif color[0] in colorfontlist and color[1] in colorfontlist:
                os.system('color ' + color)
            else:
                raise FunctionSyntaxError(
                    '无效颜色编码"%s"'%color
                ) from e
    else:
        raise FunctionSyntaxError(
            '不支持2个以上的颜色编码"%s"'%color
        )
    return
def mode(cols, lines): # 更改cmd外框大小
    """
    更改命令行窗口大小
    用法：文件名或<import...as...>命令别名.mode(宽, 高)
    宽和高需要输入数字，也可以输入字符串，但字符串必须由数字组成
    """
    try:
        int(str(cols))
    except ValueError as e:
        raise FunctionSyntaxError(
            '请不要输入除数字外的字母，符号等'
        ) from e
    else:
        c = str(cols)
    try:
        int(str(lines))
    except ValueError as e:
        raise FunctionSyntaxError(
            '请不要输入除数字外的字母，符号等'
        ) from e
    else:
        l = str(lines)
    return os.system('mode con cols=' + c + ' lines=' + l)
def shield(words, WordsBlackList): # 词语屏蔽
    """
    词语屏蔽功能
    用法：先新建一个列表，例如blacklist
    用法：文件名或<import...as...>命令别名.shield('句子',blacklist)
    将会把句子中出现在blacklist中的词语全部替换为"*"
    """
    A_list = ['*','**','***','****','*****','******','*******','********','*********','**********','***********','************']
    try:
        WordsBlackList.append('test')
    except AttributeError as e:
        raise FunctionSyntaxError(
            '功能shield的词语黑名单需要传入列表'
        ) from e
    else:
        WordsBlackList.pop()
        for i in WordsBlackList:
            length = len(i) - 1
            words = words.replace(i, A_list[length])
    return words
def choice(choose='YN', text='Y/N', default='False', timeout='10', *, hide=False): # 按键选择功能
    """
    按键选择功能
    用法：文件名或<import...as...>命令别名.choice('用户可选的按键','显示的文字(显示的文字中不能含有空格)','默认按键选择(可填)','多少秒后默认按键生效(必须先指定默认按键，默认为0)'),'hide=True/False(是否隐藏选项列表)')
    可以写成：变量 = 文件名或<import...as...>命令别名.choice()
    如果这样写，用户所选择的按键就会变为返回值存储在变量中
    返回值是根据用户选择的按键的排序生成的
    例如('YNC')这个用户可选按键列表中，共有3个按键：<Y>、<N>和<C>
    如果用户按下<Y>，返回值为1
    如果用户按下<N>，返回值为2
    如果用户按下<C>，返回值为3
    以此类推
    但在选择按键的过程中，如果用户使用<Ctrl+Break>或<Ctrl+C>键，该功能会返回0
    如果检测到错误状态，该功能会返回255
    如果用户按下的键不是有效的选择，电脑会发出警告响声(如果在音量合成器里启用了系统声音)
    """
    choice = 'choice '
    choice = choice + ' /C '
    for i in range(len(text)):
        if text[i] == ' ':
            raise FunctionSyntaxError(
                '显示的文字中不能含有空格'
            )
    if hide is True: 
        choice = choice + choose + ' /N ' + ' /M ' + text
    else:
        choice = choice + choose + ' /M ' + text
    if default != 'False':
        if default in choose:
            choice = choice + ' /D ' + default
            choice = choice + ' /T ' + timeout
        elif default not in choose:
            raise FunctionSyntaxError(
                '按键默认值不在设置的按键中'
            )
    return os.system(choice)
class Cipher: # 加密英文
    """
    加密英文
    用法：变量 = 文件名或<import...as...>命令别名.Cipher()
          变量.lock('明文')/unlock('密文')
    本功能有一套自己的独立加密算法，可以把输入的字母转换成不可阅读的文字
    类Cipher现接受以下参数：
    变量.lock()-加密文字
    变量.unlock()-解密文字
    注意：本功能只能加密英文
          本功能的加密算法是独立的，所以只有本功能的unlock()才能解密
    """
    def __init__( self ):
        self.WordsComparison = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        self.NumberComparison = ['а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','Я','Ч','Ш','Щ','ц','ю','э']
        self.WordsCapsComparison = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        self.NumberCapsComparison = ['α','β','Φ','ε','Λ','γ','Ω','σ','υ','δ','Ъ','×','Γ','Σ','Ψ','Υ','ψ','μ','ω','ξ','Œ','Ð','□','○','∷','θ']
    def lock(self, text):
        for i in range(26):
            text = text.replace(self.WordsComparison[i], self.NumberComparison[i])
        for i in range(26):
            text = text.replace(self.WordsCapsComparison[i], self.NumberCapsComparison[i])
        return text
    def unlock(self, text):
        for i in range(26):
            text = text.replace(self.NumberComparison[i], self.WordsComparison[i])
        for i in range(26):
            text = text.replace(self.NumberCapsComparison[i], self.WordsCapsComparison[i])
        return text
def mkdir( path ): # 新建文件夹
    """
    新建文件夹
    用法：文件名或<import...as...>命令别名.mkdir('文件夹路径')
    如不填写路径，只填写名称，那么默认在同级文件夹下新建
    """
    return os.system('mkdir ' + path)
def copy(filein, fileout): # 文件复制功能
    """
    复制文件
    用法：文件名或<import...as...>命令别名.copy('被复制的文件路径','复制出来的文件路径')")
    注意：需要完整后缀
          你可以更改复制出来的文件的后缀名，但这只限于纯文本')
          对于非纯文本的文件，例如docx，ppt等，因更改后缀而造成的文件损坏、编码缺失等问题，作者概不负责
    """
    if not find_file(filein,'exist?'):
        raise FileNotFoundError(
            '没有名为%s的文件'%filein
        )
    return os.system('copy ' + filein + ' ' + fileout + ' ' + '>nul')
def pause(text='请按任意键继续...'): # 暂停功能
    """
    暂停命令行
    用法：文件名或<import...as...>命令别名.pause('显示的文字')
    这个命令和使用input('显示的文字')的区别是pause()只需要按下键盘上的任意按键，而input()需要按下回车
    """
    print(text)
    os.system('pause >nul')
    return
def find_suffix(path, suffix): # 查找指定后缀的文件
    """
    查找指定后缀的文件
    用法：文件名或<import...as...>命令别名.find_suffix('文件夹路径','后缀')
    将遍历文件夹中所有指定后缀的文件，以列表形式返回
    """
    bat = tempfile.gettempdir() + '\\make_file_list.bat'
    tmp = tempfile.gettempdir() + '\\maker.tmp'
    file_list = []
    for i in path:
        if i == ' ':
            raise FunctionSyntaxError(
                '\n路径\n"%s"\n中含有空格'%path
            )
    for i in suffix:
        if i == ' ':
            raise FunctionSyntaxError(
                '后缀"%s"中含有空格'%suffix
            )
    if not suffix[0] == '.' or '.' in suffix[1:]:
        raise FunctionSyntaxError(
            '你的后缀"%s"无效，请输入例如".py"一类的后缀'%suffix
        )
    with open(bat,'w',encoding='ansi') as f:
        f.write('@echo off\n')
        f.write('for /r ' + path + ' %%r in (*' + suffix + ') do (\n')
        f.write('    echo %%r>>%tmp%\maker.tmp\n')
        f.write(')')
    call('%s >nul'%bat)
    os.remove(bat)
    with open(tmp,'r') as f:
        for i in f.readlines():
            file_list.append(i.replace('\n',''))
    os.remove(tmp)
    return file_list
def update(): # 更新本模块
    """
    更新本模块
    用法：文件名或<import...as...>命令别名.update()
    将自动检测模块的更新，有则更新
    """
    if not os.system("pip --version") == 0:
        print("pip.exe似乎出现了一些问题\n请检查环境变量以及pip.exe是否损坏")
        return
    if os.system("pip install --upgrade easy_functions") == 0:
        print("已是最新版本")
def getIP(): # 获取本机IP
    """
    用法：文件名或<import...as...>命令别名.getIP()
    将返回本机IP
    """
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    return IP
class Environment: # 操作环境变量
    def __init__(self, value): # 输入环境变量
        self.value = value
        self.bat_path = tempfile.gettempdir() + "\\get_environment.bat"
        self.key_path = tempfile.gettempdir() + "\\key.log"
    def set(self, key): # 修改环境变量
        os.system("setx %s %s"%(self.value, key))
    def get(self): # 获取环境变量的值
        with open(self.bat_path, "w") as f:
            f.write("")
        with open(self.bat_path, "a") as f:
            f.write("@echo off \n")
            f.write("echo %s>%s"%(self.value, self.key_path))
            f.flush()
        call(self.bat_path)
        wait(0.5)
        with open(self.key_path, "r") as f:
            key = f.read().strip("\n")
        os.remove(self.bat_path)
        os.remove(self.key_path)
        return key
    def delete(self): # 删除环境变量
        os.system("setx %s """%self.value)
def log(): # 更新日志
    """
    本模块更新日志
    用法：文件名或<import...as...>命令别名.log()
    """
    print('')
    print('[2021-3-21] [3条更新]')
    print('1.增加log()函数，可用于查看本模块的更新日志，日志从2021-3-21开始记录')
    print('2.在功能Vbs中添加了warningaskyesno()函数')
    print('3.在功能Vbs中添加了errorretry()函数')
    print('')
    print('[2021-3-22] [1条更新]')
    print('1.更改功能Vbs位置参数的名称text为message，并调换了两个参数的顺序')
    print('')
    print('[2021-3-24] [1条更新]')
    print("1.修改了功能Vbs的使用方法，不再强制需要使用(title='标题',text='正文')的写法了，同时该功能的语法发生改变，具体请使用helpcmd()功能查看")
    print('')
    print('[2021-3-28] [2条更新]')
    print('1.修改了功能Cipher的用法，具体请使用helpcmd()查看')
    print('2.添加了在用户直接打开文件而不是调用文件的时候，将运行help()')
    print('')
    print('[2021-4-3] [1条更新]')
    print('1.对shield功能进行了微调，现在shield返回的结果可以被存储在变量中')
    print('')
    print('[2021-4-7] [1条更新]')
    print('1.将所有的警告文本由print()抛出改为raise()抛出，类型为FunctionSyntaxError')
    print('')
    print('[2021-4-10] [2条更新]')
    print('1.将所有的警告文本由raise()抛出改为<raise() + from>抛出')
    print('2.修改了版本算法，现在可以准确计算出有几个函数、类、微调')
    print('')
    print('[2021-4-15] [1条更新]')
    print('1.增加了mkdir功能，具体请使用helpcmd()查看')
    print('')
    print('[2021-4-25] [2条更新]')
    print('1.更改命令名称"testfor"为"find_file"')
    print('2.对功能find_file进行了更改，现在调用文件时不会再生成ErrorOutPut.log文件，而是返回布尔值，可以直接储存在变量中')
    print('')
    print('[2021-4-30] [1条更新]')
    print('1.在功能choice中添加了位置参数hide，需要输入布尔值来操作')
    print('')
    print('[2021-5-1] [1条更新]')
    print('1.将功能choice中的位置参数hide由位置参数改为命名关键字')
    print('')
    print('[2021-5-4] [1条更新]')
    print('1.更新了功能choice的帮助文字')
    print('')
    print('[2021-5-5] [1条更新]')
    print('1.在功能choice中增加了一条检测语句，现在显示的文字中含有空格将会报错')
    print('')
    print('[2021-5-6] [1条更新]')
    print('1.因为PyPi官网的重名，本模块由pymod更名为SimpleFunctions')
    print('')
    print('[2021-5-7] [1条更新]')
    print('1.对功能start进行了微调')
    print('')
    print('[2021-5-8] [1条更新]')
    print('1.在功能choice中增加了一条检测语句，现在按键默认值不在设置的按键中将会报错')
    print('')
    print('[2021-5-9] [1条更新]')
    print('1.更改了功能choice中位置参数default和time的默认值')
    print('')
    print('[2021-5-18] [1条更新]')
    print('1.增加了功能copy，具体请使用helpcmd()查看')
    print('')
    print('[2021-5-19] [1条更新]')
    print('1.在功能literally中增加了一条检测语句，在用户没有赋值位置参数wait为数字时将会报错')
    print('')
    print('[2021-5-20] [3条更新]')
    print('1.因为某种原因，本模块由SimpleFunctions更名为easy_functions')
    print('2.对功能literally和功能wait中的检测语句进行了微调')
    print('')
    print('[2021-5-21] [1条更新]')
    print('1.对功能literally中的检测语句进行了微调')
    print('')
    print('[2021-5-29] [1条更新]')
    print('1.在功能Vbs中添加了4条检测语句，使得标题和正文中的换行符和回车符被忽略')
    print('')
    print('[2021-6-13] [4条更新]')
    print('1.对功能Vbs在helpcmd()中的解释进行了微调')
    print('2.对功能call在helpcmd()中的解释进行了微调')
    print('3.对功能color的bug进行了修复')
    print('4.对所有的报错进行了优化')
    print('')
    print('[2021-6-18] [2条更新]')
    print('1.在功能copy中增加了一条检测语句，使文件不存在时报错')
    print('2.增加了pause功能，具体请使用helpcmd()查看')
    print('')
    print('[2021-6-19] [1条更新]')
    print('1.对功能color的报错进行了优化')
    print('')
    print('[2021-6-20] [1条更新]')
    print('1.升级了功能find_file，使得此功能可以判断文件是否可以被导入')
    print('2.在功能find_file中增加了一个位置参数，使得此功能拥有两个模式，具体请使用helpcmd()查看')
    print('')
    print('[2021-6-21] [2条更新]')
    print('1.在功能find_file中添加了一条if语句，使用户没有输入字符串时报错')
    print('2.对功能wait和功能literally的报错进行了优化')
    print('')
    print('[2021-7-1] [1条更新]')
    print('1.增加了find_suffix功能，具体请使用helpcmd()查看')
    print('')
    print('[2021-7-3] [1条更新]')
    print('1.对功能find_suffix的报错进行了优化')
    print('')
    print('[2021-7-4] [1条更新]')
    print('1.修复了功能copy因功能find_file的语法改变而不可使用的bug')
    print('')
    print('[2021-7-5] [1条更新]')
    print('1.功能Vbs的弹窗正文现在支持换行，不过不是用换行符，具体请使用helpcmd()查看')
    print('')
    print('[2021-7-7] [1条更新]')
    print('1.修复了功能mode的一些bug')
    print('')
    print('[2021-7-16] [1条更新]')
    print('1.优化了功能mode，使其参数可以传入数字或由数字组成的字符串')
    print('')
    print('[2021-8-13] [GitHub] [1条更新]')
    print('1.增加了GitHub页面')
    print('')
    print('[2021-8-18] [1条更新]')
    print('1.修复了功能Vbs因临时文件夹路径的问题而无法使用的bug')
    print('')
    print('[2021-8-28] [1条更新]')
    print('1.修复了功能find_suffix因临时文件夹路径的问题而无法使用的bug')
    print('')
    print('[2021-9-29] [1条更新]')
    print('1.修复了功能find_suffix关于批处理的bug')
    print('')
    print("[2021-10-26] [1条更新]")
    print("[Beta]1.增加了update功能，具体请使用helpcmd()查看")
    print("")
    print("[2021-10-27] [1条更新]")
    print("1.修复了函数update的帮助文字的问题")
    print("")
    print("[2021-11-1] [2条更新]")
    print("1.增加了getIP功能，具体请使用helpcmd()查看")
    print("2.update命令更新至正式版")
    print("")
    print("[2021-11-13] [1条更新]")
    print("1.对部分帮助文字进行了微调")
    print("")
    print("[2021-12-19] [1条更新]")
    print("1.将功能Code更名为Cipher")
    print("")
    print("[2022-1-23] [2条更新]")
    print("1.将所有功能的帮助文字移至功能内部，删除helpcmd功能，请使用Python内置的help()命令")
    print("[Beta]2.增加了Environment功能，具体请使用")
    print("")
    return
def version(): # 版本
    """
    显示本模块版本
    用法：文件名或<import...as...>命令别名.version()
    """
    global __version__
    print('easy_functions版本:%s'%__version__)
    print('%s个函数'%(__version__[2] + __version__[3]))
    print('%s个类'%__version__[0])
    print('%s个微调'%(__version__[5] + __version__[6]))
    return
def help(): # 文件命令功能列表
    """
    命令列表功能
    用法：文件名或<import...as...>命令别名.help()
    """
    print('easy_functions版本:', __version__)
    print('内含%s个函数，%s个类'%(__version__[2] + __version__[3], __version__[0]))
    print('模块easy_functions可使用的功能为%s'%cmdlist)
    print('列表中以大写字母开头的为类(class)')
    return
if __name__ == '__main__':
    help()