# pip install opencc-python-reimplemented



# 作者只有11岁！



import sys
import opencc
trandic = {
    "遍历": "for",
    "在": "in",
    "定义": "def",
    "类": "class",
    "继承": "extends",
    "如果": "if",
    "返回": "return",
    "退出循环": "break",
    "跳过": "continue",
    "触发异常": "raise",
    "导入": "import",
    "从": "from",
    "到": "to",
    "结束": "end",
    "当": "as",
    "等于": "==",
    "不等于": "!=",
    "大于": ">",
    "小于": "<",
    "大于等于": ">=",
    "小于等于": "<=",
    "与": "and",
    "或": "or",
    "非": "not",
    "和": "and",
    "缩进": "   ",
    "所有": "*",
    "如果循环": "while",
}
replace_trandic = {
    "”": '"',
    "“": '"',
    "‘": "'",
    "’": "'",
    "（": "(",
    "）": ")",
    "，": ",",
    "：": ":",
    "；": ";",
    "【": "[",
    "】": "]",
    "。": ".",
    "输出": "print",
    "输入": "input",
    "转整数": "int",
    "转浮点数": "float",
    "转字符串": "str",
    "转布尔": "bool",
    "转列表": "list",
    "转元组": "tuple",
    "转字典": "dict",
    "转集合": "set",
    "转比特": "bytes",
    "转字节": "bytearray",
    "真": "True",
    "假": "False",
    "无": "None",
    "范围": "range",
    "请求网页": "get__.urlopen",
    "获取内容": "read()",
    "随机数": "random.randint",
    "占位符": "pass",
    "加": "+",
    "减": "-",
    "乘": "*",
    "除": "/",
    "取余": "%",
    "取整": "//",
    "次方": "**",
    "等待": "time.sleep",
}

guicode = '''from tkinter import *
window=Tk()
def 图形化标题(title):
    window.title(title)
def 图形化窗口大小(width,height):
    window.geometry(str(width)+"x"+str(height))
def 显示窗口():
    window.mainloop()
def 显示文本(text,x=0,y=0):
    Label(window,text=text).place(x=x,y=y)
def 显示文本框(text,x=0,y=0,width=None,height=None):
    Entry(window,text=text,width=width,height=height).place(x=x,y=y)
def 显示按钮(text,command,x=0,y=0,width=None,height=None):
    Button(window,text=text,width=width,height=height,command=command).place(x=x,y=y)
def 当窗口关闭时(command):
    def func():
        command()
        try:
            window.destroy()
        except:pass
    window.protocol("WM_DELETE_WINDOW",func)
def 图形化窗口位置(x,y):
    window.geometry("+"+str(x)+"+"+str(y))
def 刷新窗口():
    window.update()
'''
custom_keywords = [['多线程', 2, 'Thread(None,%s,None,%s).start()', 'threading']]
keywords = ['多线程']
cc = opencc.OpenCC('t2s')
def tran_code_f(codefile,encodefile):
    decodecode = ''
    code = []
    libusedict = {'urllib_request': [False, 'import urllib.request as get__'],
                'random': [False, 'import random'],
                'time': [False, 'import time'],
                'threading': [False, 'from threading import Thread'],
                '_': [False, ''],
                }
    with open(codefile, encoding="utf-8") as f:
        _code = f.readlines()
        for i in _code:
            code.append(cc.convert(i))
    for linenum in range(len(code)):
        line=code[linenum]
        lines = line.split()
        tab = ''
        while True:
            if line.startswith("    "):
                tab += "    "
                line = line[4:]
                _ = line == line[:]
            else:
                break
        if lines[0] not in keywords:
            if len(lines) == 0:
                continue
            if len(lines) == 1 and lines[0] == "导入图形化界面":
                usegui = True
                for guicodeline in guicode.split("\n"):
                    decodecode += (tab+guicodeline+"\n")
                continue
            for i in range(len(lines)):
                if "请求网页" in lines[i]:
                    libusedict["urllib_request"][0] = True
                if "随机数" in lines[i]:
                    libusedict["random"][0] = True
                if "等待" in lines[i]:
                    libusedict["time"][0] = True
                if lines[i] in trandic:
                    lines[i] = trandic[lines[i]]
                    continue
        else:
            for i in custom_keywords:
                if i[0] == lines[0]:
                    input__ = lines[1:]
                    if len(input__) != i[1]:
                        print(f"编译失败，请检查输入参数。\n行数：{linenum}\n错误代码内容：\n\n{tab+line}\n\n错误信息：输入参数个数不符合要求。")
                        exit(0)
                    input__ = ' '.join(input__)
                    for key, value in replace_trandic.items():
                        input__ = input__.replace(key, value)
                    input__ = input__.split()
                    for _a_b_ in input__:
                        _a_b_s = _a_b_.split(" ")
                        for _a_b_s_ in _a_b_s:
                            if _a_b_s_ in trandic:
                                _a_b_s_ = trandic[_a_b_s_]
                    input__ = list(map(str, input__))
                    libusedict[i[3]][0] = True
                    decodecode += tab+(i[2] % tuple(input__))+"\n"
                    break
            continue
        replace_line = (' '.join(lines)+'\n')
        for key, value in replace_trandic.items():
            replace_line = replace_line.replace(key, value)
        decodecode += tab+replace_line
    with open(encodefile, mode="w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("#!python3"+"\n"*3)
        for lib, info in libusedict.items():
            if info[0]:
                f.write(info[1]+'\n')
        f.write(decodecode)
        f.write("\n"*2)
    print("编译完成！\n输出文件："+encodefile)
