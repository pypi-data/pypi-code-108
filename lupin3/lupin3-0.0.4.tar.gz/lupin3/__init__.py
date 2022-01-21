import pandas as pd
import datetime
import itertools
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
# pip install psycopg2-binary
import psycopg2
# pip install mysql-connector
import os
import mysql.connector
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from IPython.core.interactiveshell import InteractiveShell
import baostock as bs
InteractiveShell.ast_node_interactivity = "all"
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def str2date(strword):
    return datetime.datetime.strptime(strword, '%Y-%m-%d')


def date2str(dateword):  # only save date
    return str(datetime.datetime.strftime(dateword, '%Y-%m-%d'))


def datestr(word):
    if type(word) == datetime.datetime:
        return datetime.datetime.strftime(word, '%Y-%m-%d')
    elif type(word) == str:
        return datetime.datetime.strptime(word, '%Y-%m-%d')


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print("---  new folder...  ---")
        print("---  OK  ---")

    else:
        print("---  There is this folder!  ---")


def dateminus(startdate, daynum):
    if type(startdate) == str:
        return date2str(str2date(startdate) - datetime.timedelta(days=daynum))
    elif type(startdate) == datetime.datetime:
        return date2str(startdate - datetime.timedelta(days=daynum))


def dateplus(startdate, daynum):
    if type(startdate) == str:
        return date2str(str2date(startdate) + datetime.timedelta(days=daynum))
    elif type(startdate) == datetime.datetime:
        return date2str(startdate + datetime.timedelta(days=daynum))


def showeveryday(startday, endday):  # input string of date
    startd = str2date(startday)
    endd = str2date(endday)
    if startd > endd:
        print('startday must more than endday')
    else:
        daynum = (endd - startd).days
    outputdays = []
    for dayn in range(daynum + 1):
        newdate = dateplus(startd, dayn)
        outputdays.append(newdate)
    return outputdays


def splitlist(listsample, size=1000):
    donelist = [listsample[i:i + size] for i in range(0, len(listsample), size)]
    return donelist


def cartesian(l1, l2):
    carte = []
    for i in itertools.product(l1, l2):
        carte.append(i)
    df = pd.DataFrame(carte)
    return df


def postgreSqlconnect(host, port, user, password, database, sql):
    conn_string = "host=" + host + " port=" + port + " dbname=" + database + " user=" + user + " password=" + password
    gpconn = psycopg2.connect(conn_string)

    curs = gpconn.cursor()

    curs.execute(sql)

    data = curs.fetchall()

    gpconn.commit()

    curs.close()
    gpconn.close()
    data = pd.DataFrame(data)

    return data


class MyConverter(mysql.connector.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        row = super(MyConverter, self).row_to_python(row, fields)

        def to_unicode(col):
            if type(col) == bytearray:
                return col.decode('utf-8')
            return col

        return [to_unicode(col) for col in row]


def mySqlconnect(host, port, user, password, database, sql, ret):
    mysqlcon = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        passwd=password,
        database=database, use_unicode=False, converter_class=MyConverter
    )
    mysqlcurs = mysqlcon.cursor(buffered=True)
    # mysql

    mysqlcurs.execute(sql)

    if ret is True:

        myresult = mysqlcurs.fetchall()  # fetchall() 获取所有记录
        return myresult
        mysqlcon.close()
        mysqlcurs.close()

    elif ret is False:

        mysqlcon.commit()
        mysqlcon.close()
        mysqlcurs.close()


def find_pd(word, pd):
    index_ = []
    for num_row in range(pd.shape[0]):  # 5
        for num_col in range(pd.shape[1]):  # 4
            if pd.iloc[num_row, num_col] == word:
                # print([num_row, num_col])
                index_.append([num_row, num_col])
            else:
                pass
    return index_


def chineseloto(N=1000):
    def rand_num():
        n_l, e_l = [], []
        while len(n_l) < 5:
            t = random.randint(1, 35)
            if t in n_l:
                pass
            else:
                n_l.append(t)
        n_l.sort()
        while len(e_l) < 2:
            t = random.randint(1, 12)
            if t in e_l:
                pass
            else:
                e_l.append(t)
        e_l.sort()
        l = n_l + e_l
        return l

    sum_ = []
    for n in range(N):
        sum_.append(str(rand_num()))

    dict_ = {}
    for key in sum_:
        dict_[key] = dict_.get(key, 0) + 1

    def top_n_scores(n, score_dict):
        lot = [(k, v) for k, v in dict_.items()]  # make list of tuple from scores dict
        nl = []
        while len(lot) > 0:
            nl.append(max(lot, key=lambda x: x[1]))
            lot.remove(nl[-1])
        return nl[0:n]

    return top_n_scores(4, dict_)


def Stackedbar(titlename, xlabel, label, botV, cenV, topV):
    plt.title(titlename)
    N = len(xlabel)
    ind = np.arange(N)  # [ 0  1  2  3  4  5  6  7  8 ]
    plt.xticks(ind, xlabel)

    # plt.ylabel('Scores')
    Bottom, Center, Top = botV, cenV, topV

    d = []
    for i in range(0, len(Bottom)):
        sum = Bottom[i] + Center[i]
        d.append(sum)

    colors = list(mcolors.TABLEAU_COLORS.keys())

    p1 = plt.bar(ind, Bottom, color=colors[0])
    p2 = plt.bar(ind, Center, bottom=Bottom, color=colors[1])
    p3 = plt.bar(ind, Top, bottom=d, color=colors[2])

    plt.legend((p1[0], p2[0], p3[0]), label, loc=2)

    plt.show()


def multiplebar(n=2, total_width=0.5, size=5):
    print('待修改')
    x = np.arange(size)
    a = np.random.random(size)
    b = np.random.random(size)
    c = np.random.random(size)

    # total_width, n = 0.8, 3
    width = total_width / n
    x = x - (total_width - width) / 2

    plt.bar(x, a, width=width, label='a')
    plt.bar(x + width, b, width=width, label='b')
    plt.bar(x + 2 * width, c, width=width, label='c')
    plt.legend()

    plt.plot(x, a)
    plt.plot(x + width, b)
    plt.plot(x + 2 * width, c)
    # plt.plot(x, y, "r", marker='*', ms=10, label="a")
    # plt.xticks(rotation=45)
    # plt.legend(loc="upper left")

    plt.show()


def ML_LogisticRegression(data, label, size=0.2, penalty='l2', showcoef=False, showmatch=False, **kwargs):
    X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=size)

    # 标准化处理
    transfer = StandardScaler()
    X_train = transfer.fit_transform(X_train)
    X_test = transfer.transform(X_test)

    # 模型训练
    # 创建一个逻辑回归估计器
    estimator = LogisticRegression(penalty=penalty)
    # 训练模型，进行机器学习
    estimator.fit(X_train, y_train)
    # 得到模型，打印模型回归系数，即权重值
    if showcoef is True:
        print("logist回归系数为:\n", estimator.coef_)
    else:
        pass
    # return estimator
    # 模型评估
    y_predict = estimator.predict(X_test)
    if showmatch is True:
        print("预测值为:\n", y_predict)
        print("真实值与预测值比对:\n", y_predict == y_test)
    else:
        pass
    rate = estimator.score(X_test, y_test)
    print("直接计算准确率为:\n", rate)

    # 打印精确率、召回率、F1 系数以及该类占样本数
    print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=[0, 1]))

    # ###模型评估
    # #ROC曲线与AUC值
    print("AUC值:\n", roc_auc_score(y_test, y_predict))


def getstockdata(code,startdate,enddate,frequency):
    print("code sample:\"sh.600001\" ")
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    # print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(code,
                                      "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                      start_date=startdate, end_date=enddate,
                                      frequency=str(frequency), adjustflag="3")
    # print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    # result.to_csv("history_A_stock_k_data.csv", index=False)
    # print(result.head(10))
    return result

