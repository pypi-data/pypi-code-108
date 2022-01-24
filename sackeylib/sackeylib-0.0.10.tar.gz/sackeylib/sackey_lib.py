# -*- coding: utf-8 -*-
import time
import datetime
import _thread as thr
import requests
import json
import sys
import os
from pathlib import Path

__all__ = [
    'str_time_day','print_var','str_time_year','str_time_Day','str_time_Month','str_time_hour','sleep',
    'print_sys','print_msg','print_error','lib_to_do_lib','len_var','print_dict','var_name',
    'readConfig','rename_file','copy_file','str_dict','input_lib','print_function',
    'print_object','print_item']

current_path = os.path.dirname(os.path.abspath(__file__))
min_sec = 60
hou_sec = min_sec * 60
day_sec = hou_sec * 24
tasks = {
    "1": "定时提醒",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "q": "退出系统",
    "i": "查询现有任务",
    "r": "修改任务",
    "d": "del task",
    "reloading": "reloading task"
}
repeat_lib = {"1": "定时", "2": "每日", "3": "工作日", "4": "延迟N分钟", "5": "Now"}
group_lib = {
    "0": {
        "1": "项目组",
        "2": "贪吃蛇测试组",
        "3": "袁少华"
    },
    "袁少华":
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=cf6fe1e9-5bd9-42af-a518-4a7c3f609b79",
    "贪吃蛇测试组":
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2acaad96-591b-4176-9759-6cbba401855d",
    "项目组":
    "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=503a0e01-9dc6-4b98-8fc9-8980d76ac0a9"
}
models = {}
task_list = {}
task_replace = {}
debug = False
data_list = ["content", "mentioned_list", "mentioned_mobile_list"]


def str_time_day():
    return time.strftime('%m-%dT%H-%M-%S', time.localtime())


def str_time_year():
    return time.strftime('%Y-%m-%dT%H-%M-%S', time.localtime())

def str_time_Day():
    return time.strftime('%Y-%m-%d', time.localtime())


def str_time_Month():
    return time.strftime('%Y-%m', time.localtime())


def str_time_hour():
    return time.strftime('%H-%M-%S', time.localtime())


def sleep(times=None):
    if not times:
        times = 2

    for i in range(times):
        print("\r"+"wait for {}/{}s ".format(i, times),end='',flush=True)
        time.sleep(1)


def print_sys(tips=None):
    """
    :param tips:
    :return:
    """
    if tips:
        print(tips)
    print("Unexpected error:", sys.exc_info()[0], sys.exc_info()[1])


def print_msg(tips=None):
    if not tips:
        print("**" * 15 + "task" + "**" * 15)
    else:
        print("##" * 30 + "\n" + tips + "\n" + "##" * 30)


def print_var(var,i=0):
    """
    打印一个变量
    """
    print("**" * 20 + str(i))
    print('打印变量:',var_name(var))
    print(var.__str__)
    print(var)
    print(type(var))
    print("###" * 20)

def print_error(tips=""):
    tips += "输入有误，请重新输入:"
    print("**" * 15 + tips + "**" * 15)


def lib_to_do_lib(dict_lib):
    libs = {}
    do_lib = {}
    if isinstance(dict_lib, (list, tuple)):
        print(dict_lib)
        for i in range(len(dict_lib)):
            libs[str(i + 1)] = dict_lib[i]
        do_lib = libs.copy()
    elif isinstance(dict_lib, dict):
        if '0' in dict_lib.keys():
            libs = dict_lib['0']
        else:
            keys_lib = list(dict_lib.keys())
            for i in range(len(keys_lib)):
                libs[str(i + 1)] = keys_lib.pop()
        do_lib = dict_lib.copy()
        for key in libs.keys():
            if libs[key] not in do_lib.keys():
                raise 'dict_lib error:%s' % str(dict_lib)
    return libs, do_lib


def len_var(ob):
    if type(ob) == str:
        return len(ob)
    else:
        return len(str(ob))

def print_dict(dicts):
    """
    格式打印字典变量
    :param dicts:
    :return:
    """
    print(str_dict(dicts))

def var_name(var, dict_var=None):
    """
    :The function is tu return name of the variable:
    :param var:
    :param dict_var:
    :return var_name_str:
    """
    dict_var = dict_var or globals().copy()
    for key in dict_var:
        if dict_var[key] == var:
            return key


def readConfig(path=''):
    """
    读取配置文件，转成字典
    """
    res = {}
    with open(os.path.join(path,'config.txt'),'r',encoding='utf8') as cf:
        for ls in cf.readlines():
            if ls[0] == '#' : continue
            key_val = ls.replace("\n",'').split(":")
            if len(key_val) == 2:
                res[key_val[0]] = key_val[1]
    return res

def rename_file(file_name, newName, path1='',path2=None):
    """
    重命名文件
    """
    print("rename", path1 + file_name, path2 + newName)

    os.rename(os.path.join(path1,file_name),os.path.join(path2 or path1,newName))

def copy_file(file_name, newName, path1='',path2=None):
    print("copy",  path1 + file_name, path2 or path1 + newName)
    import os
    import shutil
    shutil.copy(os.path.join(path1,file_name),os.path.join(path2 or path1,newName))

def str_dict(dicts, str1=''):
    """
    把字典格式的变量格式化为字符串
    :param dicts:
    :param str1:
    :return:
    """
    str_dicts = "{%s}"
    if type(dicts) == dict:
        str_item = ""
        for key in dicts:
            if type(dicts[key]) == dict and len(dicts[key]) >= 1:
                str_item += '\n' + str1 + key + ":"
                str_item += str_dict(dicts[key], str1 + "  ") + ','
            else:
                str_item += '\n' + str1 + key + ":" + str(dicts[key]) + ','
                continue
        # print('str_item', str_item)
        return str_dicts % str_item[0:-1]
    elif type(dicts) == list or type(dicts) == tuple:
        str_list = '\n' + str1 + 'item:'
        for item in dicts:
            str_list += '\n  ' + str1 + item
        return str_list
    else:
        return '\n' + str1 + "value:\n  " + str1 + str(dicts)

def input_lib(tips, dict_lib):
    """
    输入一个需要选择的字典
    """
    print_msg()
    times = 1
    libs, do_lib = lib_to_do_lib(dict_lib)

    while 1:
        print(tips)
        str_len = 100 // max([len_var(ob) for ob in libs.values()]) or 1
        line_num = str_len if str_len < 5 else 5
        index_en = 1
        for key in libs.keys():
            en = ";  " if index_en % line_num != 0 else ";\n"
            index_en += 1
            if libs[key]:
                print(key, libs[key], end=en)
        a_input = input("\ntips:如果没有需要的选项，输入“add”;退出输入“q“\n请选择:")
        if a_input in libs.keys():
            return libs[a_input]
        elif a_input == "q":
            return False
        elif a_input == "add":
            if isinstance(dict_lib, list):
                print(dict_lib)
                dict_lib.append(input("输入你需要的选项:"))
                libs, do_lib = lib_to_do_lib(dict_lib)
            elif isinstance(dict_lib, dict):
                key_name = input("输入你需要的选项:")
                if '0' in dict_lib.keys():
                    if key_name not in dict_lib.values():
                        dict_lib["0"][str(len(libs) + 1)] = key_name
                dict_lib[key_name] = input("输入对应参数:")
                key_name = input("输入你需要的选项:")
                if key_name not in libs.values():
                    libs["0"][str(len(libs) + 1)] = key_name
                libs[key_name] = input("输入对应参数:")
            else:
                print_error("该选择不能添加选项")
        else:
            times += 1
            print_error()
        if times >= 5:
            print("输入错误次数过多，退出")
            return False



# from itertools import *
def print_function(function):
    """
    打印一个模块的信息
    """
    print("++++"*10)
    functions = {}
    others = []
    for i in function.__dict__:
        # functions.append(str(i)+":"+str(function.__dict__[i].__doc__))
        # functions.append(function.__dict__[i].__doc__)
        if "_" != i[0]:
            if function.__dict__[i].__doc__:
                functions[i] = function.__dict__[i].__doc__
        else:
            others.append(i)
    print("functionName:", function.__name__)
    print("function is :", function.__class__)
    print("function doc :", function.__doc__)
    try:
        print("function in the module:", function.__module__)
    except Exception as es:
        print(es)
    print("function have :", "".join("\n" + key for key in functions.keys()),"\n" , "\n*************\n".join([""] + list(j+":\n    "+functions[j] for j in functions.keys())))
    print("function have others :\n", "\n".join(others))


def print_object(ob):
    """
    打印一个变量的信息
    """
    print("++++"*10)
    print(ob.__dir__())
    # for i in ob.__dir__:
    #     functions.append(i+":"+ob.__dir__[i].__doc__)
    #     functions.append(ob.__dir__[i].__doc__)
    #     # if "_" not in i:
        #     if function.__dict__[i].__doc__:
        #         functions.append(i+":"+function.__dict__[i].__doc__)
    # print("object name:", ob.__name__)
    print("object is :", ob.__class__)
    print("object doc :", ob.__doc__)
    print("object have :\n", ob.__dir__())
    for i in ob.__dir__():
        print(i)
        # print(i, eval("ob.%s()" % i))
        try:
            print(i,eval("ob.%s()"%i))
        except Exception as es:
            print("error class:",es.__doc__, "\nerror str:", es.__str__())


def print_item(item):
    """
    打印一个目标的信息
    item:modle，int,str,list,dict... ect
    """
    try:
        print(item.__str__())
        print("begin:", item.__name__)
    except Exception as es:
        print("begin:", repr(item))
        print(es.__str__())

    if type(item) in (int,str,list,dict):
        print_object(item)
    else:
        try:
            for i in item:
                if type(i) == str:
                    print(i)
                else:
                    try:
                        print_function(i)
                    except Exception as es:
                        print(es.__str__())
        except Exception as es:
            print(es.__str__())
            print_function(item)



if __name__ == "__main__":
    a = {"12":12312}
    print_var(a)
    
