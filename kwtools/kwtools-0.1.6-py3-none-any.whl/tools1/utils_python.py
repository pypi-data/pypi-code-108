import os
import time
import functools
import logging
import sys
import random
import traceback
import json
import gc
import pandas as pd
import numpy as np



class UtilsPython():
    def __init__(self):
        pass


    # 个人用于记录报错内容的log装饰器
    def log_error(self, log_directory=f"{os.getcwd()}/log", throw_error=False):
        """
            params:
                log_directory: 你要存储log的目录路径 (默认是当前路径)

        """
        # 作为装饰器时, 一定要加上(); 否则就不会返回内部的decorate函数了
        # 如果没有传入log的存放目录, 默认使用上述目录
        def decorate(func):
            def record_error(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    module_name = get_this_module_name()
                    func_name = func.__name__
                    kkprint(module_name=module_name, func_name=func_name)
                    tb_txt = traceback.format_exc(limit=5) # limit参数: 表示traceback最多到第几层
                    if not os.path.exists(log_directory): # 如果没有这个log的目录路径, 则创建这个文件夹
                        os.mkdir(log_directory)
                    log_file_path = f"{log_directory}/{module_name}_error.log"
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        print(f"\n【捕获到异常】\n{tb_txt}\n【异常存储路径】: {log_file_path}\n")
                        log_msg = tb_txt
                        this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        f.write(f"{this_time}\n{log_msg}\n\n\n")
                    # 有时候需要把错误内容抛出, 在更外层捕获 (通过'消费者多线程池'来捕获,让其url进入到error_queue)
                    if throw_error:
                        raise Exception(tb_txt)
            return record_error
        return decorate


    def timer(self, func):
        """装饰器：记录并打印函数耗时"""
        def decorated(*args, **kwargs):
            st = time.time()
            ret = func(*args, **kwargs)
            module_name = get_this_module_name()
            func_name = func.__name__
            # kkprint(module_name=module_name, func_name=func_name)
            print(f'\n[计时器]: \n模块"{module_name}" -- 函数"{func_name}": 执行时长: {time.time() - st} 秒\n')
            return ret
        return decorated


    # python官网的例子
    def logged(self, level, name=None, message=None):
        """
        这是python cookbook 中官方写写的log案例
        Add logging to a function. level is the logging
        level, name is the logger name, and message is the
        log message. If name and message aren't specified,
        they default to the function's module and name.

        可以看到, 如果你想要给装饰器传参, 就需要在decorate外面再嵌套一层函数: 总共3层

        # Example use
        # @logged(logging.DEBUG)
        # def add(x, y):
        #     return x + y
        #
        # @logged(logging.CRITICAL, 'example')
        # def spam():
        #     print('Spam!')

        """
        def decorate(func): # 此处一定只有一个func形参
            logname = name if name else func.__module__
            log = logging.getLogger(logname)
            logmsg = message if message else func.__name__

            @functools.wraps(func) # 这里的装饰器可以修改__name__的问题(其实没啥用, 反正写上更好就对了, 管他呢)
            def wrapper(*args, **kwargs):  # 此处的形参一定是(*args, **kwargs), 并且与下面return中传入的参数一致!!
                log.log(level, logmsg)
                return func(*args, **kwargs) # 一定要记得return
            return wrapper  # 返回的函数名称一定和上面定义(warpper)的一致!!
        return decorate


    def get_this_function_name(self):
        function_name = sys._getframe().f_code.co_name


    def get_this_module_name(self):
        "获取本函数所在脚本的模块名称"
        argv_str = sys.argv[-1]
        return argv_str.split("/")[-1][:-3]


    def sprint(self, **kwargs):
        """
            主要使用场景: 调试bug时候, 经常要打印某个变量名, 是否正确得到, 每次手动写print, 烦的一批!!!
                        遂, 写成了通用接口
            tips:
                与kprint的区别:  sprint只显示一行, 更加简洁   (意为: simply print)
        """
        "kwargs就是一个dict类型"
        for k, v in kwargs.items():
            print(f"\n变量'{k}'--({type(v)})----> {v}\n")


    def kprint(self, **kwargs):
        """
            主要使用场景: 调试bug时候, 经常要打印某个变量名, 是否正确得到, 每次手动写print, 烦的一批!!!
                        遂, 写成了通用接口
        """
        "kwargs就是一个dict类型"
        for k, v in kwargs.items():
            # print(f"\n【变量'{k}'】: {v}, {type(v)}\n\n")

            # int型是没有len()方法的, 所以做了一个判断....(麻烦)
            if hasattr(v, "__len__"): # 是否有__len__魔法方法 (用于测算长度用的)
                print(f"\n【变量'{k}'】:\n    类型: {type(v)}\n    长度: {len(v)}\n    值: {v} \n\n")
            else:
                print(f"\n【变量'{k}'】:\n    类型: {type(v)}\n    长度: NAN\n    值: {v} \n\n")


    def kkprint(self, **kwargs):
        """
            主要使用场景: 当爬虫接口中的json太长时候, 为了美化打印用的.
        """
        "方便打印出某些变量的值(测试使用); 需要使用关键字传参"
        json_ = json.dumps(kwargs, indent=4, ensure_ascii=False)
        print(json_)


    def k_update(self, dic, key, value):
        "添加一个'k-v'对的同时, 返回这个添加后的dict对象!! (python默认是没有返回值的, 有些时候不方便) [下同]"
        dic[str(key)] = value
        return dic


    def k_append(self, lst, element):
        lst.append(element)
        return lst


    def k_extend(self, lst, lst2):
        lst.extend(lst2)
        return lst


    def k_memory(self, obj, accuracy=False):
        """
            params:
                obj: 需要计算内存大小的对象
                accuracy: 是否需要精细测算内存大小 (使用递归的方法,把列表/字典中的元素全部遍历出来计算)

            return:
                memory_usage, unit

            note:
                getsizeof函数默认返回bytes(字节/大B)

            tips:
                比 df["<col>"].memory_usage(deep=True) 要稍大一丢丢 (但可以认为是相同的)
        """

        def recur_cal_memory(obj):
            "递归函数: 计算有深度的对象的内存"

            # 1. 列表对象
            if type(obj) == list:
                total_memory = 0
                for e in obj:
                    memory_of_e = recur_cal_memory(e)
                    total_memory += memory_of_e
                return total_memory

            # 2. 字典对象
            elif type(obj) == dict:
                total_memory = 0
                for k, v in obj.items():
                    memory_of_k = sys.getsizeof(k)
                    memory_of_v = recur_cal_memory(v)
                    total_memory = total_memory + memory_of_k + memory_of_v
                return total_memory

            # 3. 其他
            else:
                # [递归的'原子条件': 当数据类型不为"list"和"dict"时]
                memory_usage = sys.getsizeof(obj)
                return memory_usage



        # 1. 需要精准计算
        if accuracy:
            memory_usage = recur_cal_memory(obj)

        # 2. 粗略计算即可
        else:
            memory_usage = sys.getsizeof(obj)

        # 以一种更"human"的方式呈现 '内存大小'
        if memory_usage < 1024:
            return round(memory_usage, 2), "Bytes"
        elif memory_usage < 1024*1024:
            return round(memory_usage/1024, 2), "KB"
        elif memory_usage < 1024*1024*1024:
            return round(memory_usage/1024/1024, 2), "MB"
        elif memory_usage < 1024*1024*1024*1024:
            return round(memory_usage/1024/1024/1024, 2), "GB"


    def get_df_deep_memory(self, df):
        show_dict = {}
        columns = list(df.columns)
        for col in columns:
            # df[col].memory_usage(deep=True)
            memory_usage_tuple = k_memory(df[col])
            show_dict.update({col:memory_usage_tuple})
        kprint(show_dict=show_dict)
        return show_dict


    def get_top(self, df, field_1, field_2, top_num=5, ascending=True):
        """
            function: 计算"某"个分类的"某"个字段的"前5名"
            params:
                df: 所需df
                field_1: 按它分类
                field_2: 按它排名
                top_num: 取前几名
        """
        # 先对df的 "field_2" 进行排序
        df = df.sort_values(field_2, ascending=ascending)

        # 用于计数的dict
        d = {}
        def foo(row):
            # nonlocal d
            """
                row: 是df中的一行
            """
            _key = row.get(field_1)
            if d.get(_key, 0) == 0:
                d.update({_key : 1})
                return row
            elif d.get(_key) < top_num:
                d.update({_key : d.get(_key) + 1})
                return row

        # 使用apply, 应用上面的函数
        df2 = df.apply(foo, axis=1)
        _ = df2.columns[0]
        df3 = df2.query(f"{_} == {_}")

        output_data(df3, f"top5_{field_2}")

        return df3




utils_python = UtilsPython()




if __name__ == "__main__":
    pass
