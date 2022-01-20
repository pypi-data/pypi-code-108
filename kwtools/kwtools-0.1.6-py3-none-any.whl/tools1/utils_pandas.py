import os
import pandas as pd
import numpy as np
import math
import collections
import pymongo
import json
import copy
import hashlib
from io import StringIO

import warnings
warnings.filterwarnings("ignore")

home_path = os.getenv("HOME")
desktop_path = f"{home_path}/Desktop"


class UtilsPandas():

    def __init__(self):
        pass

    # 1. [数据转化相关]
    # ============================================================================
    def import_data(
        self, in_file_name="in", end_index=None, field=None, is_df=True,
        in_file_path=None, encoding="gb18030", index_col=None,
    ):
        """
        in:csv文件
        out:df类型/类mongo类型
        function:  csv → df/mongo (默认转出:类mongo)

        notes: in_file_path 的优先级比 in_file_name 高。
        """
        if in_file_path:
            df = pd.read_csv(in_file_path, encoding=encoding, engine='python', index_col=index_col)
        else:
            print("[INFO]: 没有传入'in_file_path', 尝试从桌面路径读取...")
            df = pd.read_csv(desktop_path+"/{0}.csv".format(in_file_name), encoding=encoding, engine='python', index_col=index_col)
        if is_df:
            return df
        # 1.需要返回的是某个字段的lst格式
        if field:
            field_lst = df[field].values[:end_index] # 得到的是np.array格式
            return list(field_lst) # 用list数据格式来返回
        # 2.返回的是mongo支持的docs
        df = df[:end_index]
        docs = df.T.to_dict().values()
        return docs


    def output_data(
        self, in_obj, out_file_name="out", ordered_field_lst=None,
        out_file_path=None, output=True, index=False, encoding="gb18030", export_excel=False,
        ):
        """
        in:类mongo/df
        out:csv文件
        function:  1.mongo/df  → csv
                   2.mongo → df (这样output设为False即可)

        in_obj:    不管是mongo还是df,自动先转化成df,再用它来转csv

        tips: 如果需要 "mongo → df": output设置为False即可!
        notes: out_file_path 的优先级比 out_file_name 高。
        """

        # 1. 如果是 "类mongo" 类型, 先转化成df
        if isinstance(in_obj, pymongo.cursor.Cursor):
            # total_items = []
            # for doc in in_obj:
            #     # items = {i:str(j).strip() for i, j in zip(list(doc.keys()), list(doc.values()))}
            #     # 以下会按照mongo中存着的顺序进行输出!
            #     items = collections.OrderedDict({i:str(j).strip() for i, j in zip(list(doc.keys()), list(doc.values()))})
            #     total_items.append(items)
            # df = pd.DataFrame(total_items)
            df = pd.DataFrame(list(in_obj))  # 如果in_obj的数据量是上百万条, 其实这个操作很危险的!!
        elif isinstance(in_obj, pd.core.frame.DataFrame):
            df = in_obj

        # 2.确定字段的呈现顺序
        if ordered_field_lst:
            # 如果指定的df字段在df中并不存在,则把该字段remove掉.确保不报错
            for field in ordered_field_lst.copy():
                if field not in df.columns:
                    print("字段 {} 不在df中,将其抛弃!".format(field))
                    ordered_field_lst.remove(field)
            df = df[ordered_field_lst]  # 指定顺序

        # 3.看是否需要导出csv文件,如果不需要,直接返回df
        if not output:
            return df

        # 4. 最后,将df数据转成csv文件输出
        try:
            if out_file_path:
                if not export_excel:
                    df.to_csv(out_file_path, index=index, encoding=encoding)
                else:
                    df.to_excel(out_file_path, index=index, encoding=encoding)
            else:
                if not export_excel:
                    df.to_csv(desktop_path+"/{0}.csv".format(out_file_name), index=index, encoding=encoding)
                else:
                    df.to_excel(desktop_path+"/{0}.xlsx".format(out_file_name), index=index, encoding=encoding)
        except Exception as e:
            print(e)
            out_file_name = input("输出文件名出错,请重新键入文件名: ")
            df.to_csv(desktop_path+"/{0}.csv".format(out_file_name), index=index, encoding=encoding)

        return df


    # 输出excel文件
    def output_excel(self, df_lst, out_file_name="out", out_file_path=None, sheet_name_lst=None):
        from pandas import ExcelWriter
        if out_file_path is None:
            # 如果没有out_file_path: 默认放在桌面
            out_file_path = f"{desktop_path}/{out_file_name}.xlsx"
        with ExcelWriter(out_file_path) as writer:
            for i, df in enumerate(df_lst):
                if sheet_name_lst:
                    sheet_name = sheet_name_lst[i]
                else:
                    sheet_name = f"sheet_{i}"
                df.to_excel(writer, sheet_name, index=False)
            writer.save()


    def docs_to_df(self, docs, ordered_field_lst=None):
        """
        把mongo的数据转化成df
        """
        df = output_data(docs, output=False, ordered_field_lst=ordered_field_lst)
        return df


    def df_2_mongo(self, df):
        return df.T.to_dict().values() # 即：docs


    def df_to_docs(self, df):
        docs = df.to_dict("records") # 高效
        return docs


    def read_excel(self, in_file_name="in", in_file_path=None, sheet_name=None, need_to_concat=True):
        """
            params:
                sheet_name:
                    传入None: 返回一个有序字典 OrderedDict([("<sheet名字>", <df对象>)])
                            ( 需要用sheet名来按键取值)
                need_to_concat:
                    当没有指定"sheet_name"时, 默认把所有sheet合并, 返回合并后的df
                        (当need_to_concat为False时, 不自动合并sheet, 而是返回一个 'excel字典对象')
        """
        # 1. 先读取整个excel文件
        if in_file_path is not None:
            ordered_d = pd.read_excel(in_file_path, sheet_name=None)
        elif in_file_path is None:
            ordered_d = pd.read_excel(f"{desktop_path}/{in_file_name}.xlsx", sheet_name=None)

        # 2. 读取对应sheet_name (返回df)
        if sheet_name != None:
            df = ordered_d.get(sheet_name)
            del ordered_d # 释放中间过程对象的内存
            return df
        # 3. 合并多个sheet, 返回合并后的df
        elif need_to_concat == True:
            concat_df = pd.concat([sheet for sheet in ordered_d.values()], axis=0, ignore_index=True)
            del ordered_d # 释放中间过程对象的内存
            return concat_df

        # 4. 返回这个excel字典对象 (每个键值对中, 以sheet的名字作为"键", 对应的df对象作为"值")
        return ordered_d


    def sort_df(self, df, ordered_field_lst):
        # 1. 如果指定的字段在df中并不存在,则把该字段remove掉.确保不报错
        ordered_field_lst_copy = ordered_field_lst.copy()
        for field in ordered_field_lst_copy:
            if field not in df.columns:
                print("字段 {} 不在df中, 将其抛弃!".format(field))
                ordered_field_lst.remove(field)

        # 2. 把所需要保留的 "有序字段list" 作用在df上
        return df[ordered_field_lst]  # 指定顺序


    def save_df_to_mongo(sefl, collection_obj, df):
        dict_values = df.T.to_dict().values() # df的一种特殊结构? 不能直接取值?
        try:
            collection_obj.insert_many(dict_values)
        except Exception as e:
            raise Exception(f"[存储mongo异常] e:{e}")


    def read_mongo(self, collection_obj, query={}, need_to_show_dict={}, df_name="foo", need_to_convert_date=True):
        """
            params:
                need_to_convert_date: 是否需要在读取mongo数据的时候, 转化日期格式
        """
        # 不需要获取"_id"字段
        need_to_show_dict.update({"_id":0})

        # Make a query to the specific DB and Collection
        # print(query, need_to_show_dict)
        cursor = collection_obj.find(query, need_to_show_dict)

        # Expand the cursor and construct the DataFrame
        df =  pd.DataFrame(list(cursor))

        df.df_name = df_name

        if ("crawl_date" in df.columns) and (need_to_convert_date==True):
            df["crawl_date"] = pd.to_datetime(df["crawl_date"])
        if ("date" in df.columns) and (need_to_convert_date==True):
            df["date"] = pd.to_datetime(df["date"])

        return df


    def merge_df(
        self, x_name, y_name, out_file_name="out",
        is_df=None, join_field="house_id", output=True):
        """
        function: 不仅可以合并df/csv, 还附带输出csv的功能
        """
        print(">>>1")
        if not is_df:
            # 如果 不是df， 就把这个当做文件名，导入
            x_df = import_data(x_name, is_df=True)
            y_df = import_data(y_name, is_df=True)
        else:
            # 如果 是df， 就直接把传入的x、y当做 df对象来使用
            x_df = x_name
            y_df = y_name
        print(">>>2")
        # pd.merge() 返回的不是df类型，而是function类型。 但这个function可以使用to_csv导出文件
        #  ??????   什么情况？ 之前测试的时候返回的不是df对象，现在测试发现又确实是df对象了。。。见鬼！
        merged_df = pd.merge(x_df, y_df, how="left", on=join_field)
        if not output:
            return merged_df
        print(">>>3")
        merged_df.to_csv(desktop_path+"/{0}.csv".format(out_file_name), index=False, encoding="gb18030")
        print("合并成功!")



    # 2. [时间处理相关]
    # ============================================================================
    """
    常用的5个时间函数:
        两个时间对象:
            1. '时间偏移'对象;  2. '时间戳'对象
        三个时间字符串:
            1. 日期; 2. 时间; 3.日期+时间
    """
    def get_timedelta(self, arg="1d"):
        """
            function:
                - 获取一段时间的对象. (用于计算'偏移时间点')
                    类型: pandas._libs.tslibs.timedeltas.Timedelta
            arg:
                arg: 1s/10s/100s, 1m/10m/100m, 1h/10h/100h, 1d/10d/100d, 1w/10w/100w  (月份的'偏移'暂时不知道)
                        注: 也可以是 '1w3h12m34s' 的形式, 多个偏移量叠加在一起
        """
        return pd.to_timedelta(arg)


    def get_timestamp(self, arg="now", offset_flag=0, offset='1m', tz="hongkong", unit="s"):
        """
            function: 获取一个时间戳对象
            args:
                - arg: 参数类型可以是 str 或者 int/float 或者 时间戳对象:
                - offset_flag: 偏移的方向 # 0, -1, +1
                    0:  不偏移
                    -1: 向过去偏移
                    +1: 向未来偏移
                - offset: 偏移量 (参数同get_timedelta()中的arg: '1m', '1h', '1d', '1d1h'等)
            notes:
                - 这里面的'today', 也可以写成'2020-03-18'的形式
                - 使用timestamp()方法, 可以得到float型的时间戳:
                    get_timestamp("2020-03-18 23:32:12").timestamp()  # 单位是秒, 类型是float (精度是5位小数)
                - 一般情况, 传入一个数值型的时间戳, 都会把它视作是'utc', 因为时间戳的真实含义就是'格里尼治从1970年开始的秒数', 是绝对值!!不区分时区的

            return:
                - 返回一个'pandas._libs.tslibs.timestamps.Timestamp'的对象 (反正就是一个关于时间的'对象', 有很多强大的功能)


            [超级无敌巨坑]:
                - time.time(): 返回的是最真实的utc的时间戳.
                    (其实时间戳是一个'绝对值', 不管在哪个时区, 你的时间戳都是一样的!!!)
                    但是!! pandas的时间戳概念很奇怪.....(见下)
                # - pd.to_datetime("now") 或者 pd.Timestamp("now")

                - pandas的Timestamp对象:
                            (默认没有时区概念, 需要自行添加tz参数) (或者也可以把它的时区看做是'utc')
                    案例:
                        eg1:
                            pd.Timestamp("now") # Timestamp('2021-03-26 01:32:08.557217')
                            尾部没有'时区'的标记
                        eg2:
                            pd.Timestamp("now", tz="hongkong") # Timestamp('2021-03-26 01:33:39.669813+0800', tz='Hongkong')
                            尾部标记了'东八区'
                        eg3:
                            pd.Timestamp("now", tz="utc") # Timestamp('2021-03-25 17:33:55.432743+0000', tz='UTC')
                            用'now'输入, 并且传入时区, 则得到的时间戳就是'标准的当前时间戳' : 就等于 time.time()这个时间戳
                    重点:
                        - 由上面可以看出, Timestamp对象的表现形式都是 '时间', 而'时间'如果没有规定'时区', 那就是个'伪概念'
                            (没有时区的时间, 其实没啥意义!!)
                            # **我之前认知里的timestamp对象一直都是这种没有时区的'伪时间', 只有给它标注是'本地时区'或者'utc'时间, 那才有意义
                                (所以我现在把get_timestamp()优化了一下, 每生成一个时间戳, 都给它定义了一个'时区')
                        - 另外, 我发现, pandas更倾向于展示'相对值-时间'而不是'绝对值-时间戳':
                            - time.time():
                                    [先有'时间戳', 再根据'时区', 推出'时间']
                                    无论身处哪里, 打印的都是'真实唯一的时间戳'
                            - pandas.Timestamp():
                                    [先有'时间', 再根据'时区', 推出'时间戳']
                                    是先有'时间'的概念, 然后我去定义它这个时间是属于哪个时区的, 然后才能计算出对应的'时间戳'


                    提示:
                        - 打印单个时间戳, 而不是应用在series上的话, 最好用 pd.Timestamp()比较好. pd.to_datetime()的用法很迷!! 不推荐

            notes:
                - 我们东八区的tz就是"hongkong"
        """
        # 1. 如果arg是'时间字符串':
        if isinstance(arg, str):
            import datetime
            if arg == "now":
                # timestamp_obj = pd.to_datetime("today") # pandas这个函数输入'today', 返回的却是当前的时间....(醉了)
                timestamp_obj = pd.Timestamp("now", tz=tz)
            elif arg == "today":
                # timestamp_obj = pd.to_datetime(datetime.date.today())
                timestamp_obj = pd.Timestamp(datetime.date.today(), tz=tz)
            elif arg == "yesterday":
                # timestamp_obj = pd.to_datetime(datetime.date.today()) - self.get_timedelta("1d")
                timestamp_obj = pd.Timestamp(datetime.date.today(), tz=tz) - self.get_timedelta("1d")
            else:
                # timestamp_obj = pd.to_datetime(arg)
                timestamp_obj = pd.Timestamp(arg, tz=tz)
        # 2. 如果arg是'时间戳'的数值型:
        elif isinstance(arg, int) or isinstance(arg, float):
            if len(str(int(arg))) == 10: # 以's'为单位的时间戳都是10位数的
                # 该函数默认接收的时间戳单位是'ns', 这里改成's'
                # 一般情况, 传入一个数值型的时间戳, 都会把它视作是'utc', 因为时间戳的真实含义就是'格里尼治从1970年开始的秒数', 是绝对值!!不区分时区的
                timestamp_obj = pd.Timestamp(arg, unit=unit, tz="utc") # 所以此时obj是以'UTC'时区来表示时间 (比东八区晚8小时)
                # 再将这个'UTC'表示的时间对象, 转化成"hongkong"时间来表示  (时间戳的绝对值不变, 表达的时间意思不变, 就是改个呈现方式)
                timestamp_obj = timestamp_obj.tz_convert("hongkong") # 所以: 输出的时间对象都是用"Hong Kong"时间表示的!!!
            else:
                raise Exception("\n[错误]: 传入的时间戳不是以'秒'为单位, 请检查!\n")
        # 3. 其他类型(eg: 时间戳对象):
        else:
            # 如果传进来的时间戳对象已经有'tz'属性的话, 这里是不能再加'tz'参数的
            if hasattr(arg, "tz"):
                timestamp_obj = pd.Timestamp(arg)
            else:
                timestamp_obj = pd.Timestamp(arg, tz=tz)

        # 计算偏移后的结果
        if offset_flag == -1:
            timestamp_obj = timestamp_obj - self.get_timedelta(offset)
        elif offset_flag == 1:
            timestamp_obj = timestamp_obj + self.get_timedelta(offset)
        return timestamp_obj


    def get_date(self, arg="today", format="%Y-%m-%d"):
        """
            return:
                str格式的日期 # '2021-03-18'
            notice:
                - 这里得到的时间的str, 表示时间的时区统一是'Hong Kong'时区
        """
        timestamp_obj = self.get_timestamp(arg=arg)
        return timestamp_obj.strftime(format) # 转成“2019-02-28”这样的str形式


    def get_time(self, arg="now", format="%X"):
        """
            return:
                str格式的日期 # '13:23:12'
            notice:
                - 这里得到的时间的str, 表示时间的时区统一是'Hong Kong'时区
        """
        timestamp_obj = self.get_timestamp(arg=arg)
        return timestamp_obj.strftime(format) # 转成“14:13:30”这样的str形式

    def get_datetime(self, arg="now", format="%Y-%m-%d %X"):
        """
            return:
                str格式的日期 # '2021-03-18 13:23:12'
            使用案例:
                datetime = self.get_datetime(self.get_timestamp("now") - self.get_timedelta("1w3h12m34s")) # '2021-03-11 16:40:51'
                datetime = self.get_datetime(self.get_timestamp("now", -1, "3d3h"))  # '2021-03-15 17:29:22'
            notice:
                - 这里得到的时间的str, 表示时间的时区统一是'Hong Kong'时区
        """
        timestamp_obj = self.get_timestamp(arg=arg)
        return timestamp_obj.strftime(format) # 转成“2020-07-29 14:13:30”这样的str形式


    def get_yesterday_date(self, format="%Y-%m-%d"):
        " 获取昨天的'时间字符串'"
        return self.get_date(arg="yesterday", format=format)


    def get_delta_days(self, start_date, end_date):
        """获取两个时间点之间的'天数'."""
        start_date_obj = self.get_timestamp(arg=start_date)
        end_date_obj = self.get_timestamp(arg=end_date)
        delta_days = (end_date_obj - start_date_obj).days
        return delta_days


    def get_this_month_first_date(self, date_str="today"):
        " 本月第一天的日期"
        timestamp_obj = self.get_timestamp(date_str) # 今天的时间戳对象
        firstday_timestamp_obj = self.get_timestamp(timestamp_obj.strftime("%Y-%m")) # 这个月第一天的时间戳对象
        return self.get_date(firstday_timestamp_obj)


    def get_datetime_us(self, arg='now', format='%Y-%m-%d %X.%f'):
        return self.get_datetime(arg=arg, format=format)


    def get_time_us(self, arg='now', format='%X.%f'):
        return self.get_time(arg=arg, format=format)


    def get_period_df(start_date=None, end_date=None, is_crawl_date=False):
        " 获取一段时间内的 <日期扩充表> "
        if start_date is None:
            this_month_first_date = self.get_this_month_first_date()
            start_date = this_month_first_date
        if end_date is None:
            end_date = self.get_date()

        # 两种方式截取 "日期范围"
        datetime_index = pd.date_range(start_date, end_date, freq="1d")
        if is_crawl_date: # 用"crawl_date"来选择 "日期范围"
            df = pd.DataFrame({"crawl_date":datetime_index})
            df["true_date"] = df.crawl_date - self.get_timedelta("1d")
        else: # 用"true_date"来选择 "日期范围"
            df = pd.DataFrame({"true_date":datetime_index})
            df["crawl_date"] = df.true_date + self.get_timedelta("1d")

        # 生成4中 str格式的日期  (用于后期透视)
        df["日期"] = df.true_date.dt.strftime("%Y-%m-%d")
        df["日期-年"] = df.true_date.dt.strftime("%Y") # series类型正常来说是不能直接strftime成str类型的, 必须要用.dt 方法才行
        df["日期-月"] = df.true_date.dt.strftime("%Y-%m")
        # 计算"日期-周"这个 '周度日期 '
        weekly_date_lst = []
        for count, date_str in enumerate(df["日期"][-1::-1]): # 对'日期'的series逆序
            if count % 7 == 0:
                tmp = date_str
            weekly_date_lst.append(tmp)
        df["日期-周"] = weekly_date_lst[-1::-1] # 上面逆序了, 现在逆序回来
        df["sim_true_date"] = df.true_date.dt.strftime("%m%d")
        df["sim_crawl_date"] = df.crawl_date.dt.strftime("%m%d")
        return df



    # 3. [其他数据处理]
    # ============================================================================
    def avg(self, lst, round_digit=2):
        """
            function: 求一个数字序列中的均值
            args:
                lst: 序列 (可以是list, 也可以是series类)
                round_digit: 返回值要四舍五入的位数
        """
        # 1. 如果是list类
        if isinstance(lst, list):
            if len(lst) <1:
                raise Exception("元素小于1!")
            else:
                sum = 0
                for count, e in enumerate(lst):
                    sum += float(e)
                lst_avg = sum/(count+1)
                return round(lst_avg, round_digit)

        # 2. 如果是series类
        elif isinstance(lst, type(pd.Series())):
            if lst.size <1:
                raise Exception("元素小于1!")
            else:
                return round(lst.sum()/len(lst), round_digit)
        # 3. 其他类型都报错
        else:
            raise Exception(f"传入的lst类型错误: {type(lst)}")


    def k_divide(self, lst, piece=5):
        """
        function: 按lst从小到大的顺序, 等分成piece份 小lst 返回
        return: 返回等分节点的lst (即:按照这几个值去截取, 就是5等分了)
        """
        if isinstance(lst, list):
            if len(lst) <1:
                # raise Exception("元素小于1!")
                return 0
        elif isinstance(lst, type(pd.Series())):
            if lst.size <1:
                # raise Exception("元素小于1!")
                return 0

        lst = sorted(lst)
        # 1. 打印原lst
        print(lst)
        node_order_lst = []
        node_lst = []
        for count in range(1, piece):
            node_order_value = round(len(lst) * (1/piece) * count) - 1 # 减一别忘了 (另外,这里返回的是顺序值,不是真实值)
            node_order_lst.append(node_order_value)
            node_lst.append(lst[node_order_value])
        # 2. 打印分好piece后的, 节点的顺序
        print(node_order_lst) # 是顺序
        print("值的lst: {}".format(node_lst)) # 是值

        piece_dict = {}
        count = 0
        while True:
            if count == piece:
                break
            elif count == 0:
                piece_dict.update({count+1 : lst[ : node_order_lst[count]+1]})
            elif count == piece-1:
                piece_dict.update({count+1 : lst[node_order_lst[count-1]+1 : ]})
            else:
                piece_dict.update({count+1 : lst[node_order_lst[count-1]+1 : node_order_lst[count]+1]})
            count += 1
        # 3. 打印根据上面的顺序, piece等拆分了lst后的dict
        print(piece_dict)
        return node_lst


    def is_notnan_numeric(self, x):
        """
            numeric: 指所有数值: int/float (包括np.nan) (不包括None) (不包括'可以转成float的str')
            notnan_numeric: 指所有'非nan'的数值: int/float (不包括np.nan, 不包括None)
        """
        # 1. 若是数据集, 则直接返回False
        if isinstance(x, list) or isinstance(x, dict) or isinstance(x, set) or isinstance(x, tuple) or isinstance(x, np.ndarray):
            return False
        # 2. 是否为 None
        if x is None:
            return False
        # 3. 是否为 np.nan
        elif pd.isnull(x):
            return False
        # 4. 是否为 str
        elif isinstance(x, str):
            ### 注意: 这里防止x为可以被转成float的str, 先对str类型单独处理 (避免下一步造成错误判断)
            return False
        else:
            try:
                # 4. 如果可以被float()转化成float, 则x是为数值型, 返回True
                return isinstance(float(x), float)
            except:
                # 5. 不能转化, 则说明不是数值型
                return False


    def safely_to_int(self, x, need_to_print=False):
        """
            save: 表示可以'安全'转化成'int'. 如果x为不能转化成int的数据, 则保留原样
            notice: 该函数是以'四舍五入'的方式转成int
        """
        # 如果是'非nan数值型', 则直接round()
        if is_notnan_numeric(x):
            ### 为了保证转成int, 需要先四舍五入, 再转成int
            ### 注意: 如果x=np.float(3.5000) , round(x, 0)  >>> 4.0 (还是会带个小数点,很烦,所以干脆转成int是最省心/最干净的)
            return int(round(x, 0))
        # 否则: 原样return回去
        else:
            if need_to_print:
                print(f"x: {x}, 类型为: {type(x)}, 不能保留整数!\n")
            return x


    def round_df(self, df, round_digit=0, inplace=False, included_columns=[], excluded_columns=[]):
        """
            params:
                round_digit: 保留的小数位数
                inplace: 是否在原df上操作?
                excluded_columns: 排除某些不需要转化的列
                included_columns: 只有这些列 需要被转化


            默认:
                1. 四舍五入到整数
                2. 列名为"xx率"的, 一律以附带"百分号", 以str的形式呈现
        """
        if inplace is False:
            df = copy.deepcopy(df)

        for column, dtype in df.dtypes.items():
            # 1. 有些'率'是需要转化成'百分数'的
            if "率" in column:
                df[column] = df[column].apply(lambda x: format(x, ".2%"))
            # 2. 若发现df中的某列是 int型或者float型, 则按照round_digit四舍五入
            else:
                # 1. 当仅仅需要某几个列需要转化时:
                if included_columns:
                    if column in included_columns:
                        if dtype == np.dtype(np.float64) or dtype == np.dtype(np.int64):
                            df[column] = df[column].round(round_digit)
                # 2. 当某几个列 一定不能转化时:
                elif excluded_columns:
                    if column not in excluded_columns: # 只有'不被排除列'才需要保留两位小数
                        if dtype == np.dtype(np.float64) or dtype == np.dtype(np.int64):
                            df[column] = df[column].round(round_digit)
                # 3. 当都没有限制条件时:
                else:
                    if dtype == np.dtype(np.float64) or dtype == np.dtype(np.int64):
                        df[column] = df[column].round(round_digit)
        return df


    def get_random_num(self, min_digital=3):
        "获取一个 [0.0, 1.0) 的随机数"
        random_num = np.random.rand(1)[0]
        random_num = round(random_num, min_digital)
        return random_num


    def get_random_df(self, df):
        "对df的每一行打乱顺序"
        random_df = pd.DataFrame(np.random.permutation(df), columns=df.columns)
        return random_df



class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for np types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)





utils_pandas = UtilsPandas()



if __name__ == '__main__':
    pass
