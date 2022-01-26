from selenium import webdriver
from io import BytesIO
import requests
import json
import base64
import random
import math
from yaml import load, dump, FullLoader
from robot.api import logger
import datetime
from dateutil.relativedelta import relativedelta
import getpass

username = getpass.getuser()


def info(msg: str, html: bool = True, also_console: bool = True):
    msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:{msg}"
    logger.info(msg, html, also_console)


def debug(msg: str, html: bool = True):
    logger.console(f"[DEBUG][{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:{msg}")
    logger.debug(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:{msg}", html)


def warn(msg: str, html: bool = True):
    msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:{msg}"
    logger.warn(msg, html)


def init_chrome_option_for_wx():
    """
    功能描述：配置chrome浏览器启动参数for微信H5应用
    :return: option  chrome浏览器的配置项
    """
    # 手机实例扩展参数
    mobile_emulation = {
        "deviceMetrics": {"width": 480, "height": 830, "pixelRatio": 3.2},
        "userAgent": "Mozilla/5.0 (Linux; Android 11; M2007J17C Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045617 Mobile Safari/537.36 MMWEBID/5899 MicroMessenger/8.0.6.1900(0x2800063D) Process/tools WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64"
    }
    option = webdriver.ChromeOptions()
    # 指定用户数据目录
    option.add_argument(f'--user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/UserDataForWXTest')  # 设置用户自己的数据目录
    # 设置浏览器分辨率
    option.add_argument('--window-size=480,1000')
    # 禁用GPU防止以外Bug
    option.add_argument('--disable-gpu')
    # 装载扩展参数
    option.add_experimental_option("mobileEmulation", mobile_emulation)
    return option


def init_chrome_option_for_web():
    """
    功能描述：配置chrome浏览器启动参数for普通web页面
    :return: option  chrome浏览器的配置项
    """
    option = webdriver.ChromeOptions()
    # 指定用户数据目录
    option.add_argument(f'--user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/UserDataForTest')  # 设置用户自己的数据目录
    # 最大化
    option.add_argument('start-maximized')
    # 禁用GPU防止以外Bug
    option.add_argument('--disable-gpu')
    return option


def init_chrome_option_pay():
    """
    功能描述：配置chrome浏览器启动参数for启动支付宝的H5支付页面
    :return: option  chrome浏览器的配置项
    """
    # 手机实例扩展参数
    mobile_emulation = {
        "deviceMetrics": {"width": 480, "height": 830, "pixelRatio": 3.2},
    }
    option = webdriver.ChromeOptions()
    # 指定用户数据目录
    option.add_argument(f'--user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/UserDataForPay')  # 设置用户自己的数据目录
    # 设置浏览器分辨率
    option.add_argument('--window-size=460,1000')
    # 禁用GPU防止以外Bug
    option.add_argument('--disable-gpu')
    # 装载扩展参数
    option.add_experimental_option("mobileEmulation", mobile_emulation)
    return option


def recognize_rand_code_by_base64str(base64str, url="http://127.0.0.1:6000/recognize_image",sys_type=""):
    """
    功能描述：通过传递验证码的base64字符串原始内容给后端接口，识别验证码
    :param         base64str: str  验证码的原始base64字符串
    :param               url: str  验证码识别接口的服务地址
    :return:    predict_text：str  验证码字符串
    """
    header = {"Upgrade-Insecure-Requests": "1",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
              "Accept": "application/json, text/plain, */*",
              "Accept-Encoding": "gzip, deflate",
              "Accept-Language": "zh-CN,zh;q=0.9",
              "Cookie": "JSESSIONID=4BCF08631207AB71BAAA5E9569E3E111"
              }
    if "," in base64str:
        base64str = base64str.split(",")[1]
    base64str = base64.b64decode(base64str)
    files = {'image_file': ("captcha.jpg", BytesIO(base64str), 'application')}
    sys_type = {"sys_type": sys_type}
    # 请求识别
    response_post = requests.post(url=url, data=sys_type, files=files, headers=header, timeout=30)
    predict_text = json.loads(response_post.text)["value"]
    logger.console(f"\n[DEBUG][{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:验证码 {predict_text}")
    return predict_text


def create_random_string(count=28):
    """
    功能描述: 生成指定长度的随机字符串
    :param count: int  字符串的长度
    :return:
    """
    random_string = "".join(random.sample("0123456789abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ", k=count))
    return random_string


def analyze_dictionary(dic_string, keys_list=None):
    """
    功能描述：解析字典：如果给定了keys_list参数则按照keys的顺序反馈对应的values列表，如果不给定keys则返回字典的全部keys
    :param    dic_string: str|dict   字典对象
    :param     keys_list: list       字典中的keys
    :return: values_list: list      字典中的value
    """
    # 如果是字符串对象，则转化成python对象
    if dic_string:
        convert_to_dic = ""
        if isinstance(dic_string, str):
            new_dic_str = str(dic_string).replace("'", '"')
            convert_to_dic = json.loads(new_dic_str)
        elif isinstance(dic_string, dict):
            convert_to_dic = dic_string
        keys = convert_to_dic.keys()
        if not keys_list:
            return list(keys)

        values_list = []
        for key in keys_list:
            if key in convert_to_dic:
                # 保存所有key对应的value
                values_list.append(convert_to_dic[key])
            else:
                values_list.append(None)
        if len(values_list) == 0:
            return
        elif len(values_list) == 1:
            return values_list[0]
        else:
            return values_list
    # 目标对象如果为空直接返回不处理
    return False


def get_intersection_from_lists(list_one, list_two):
    """
    功能描述：反馈两个列表的交集
    :param list_one: list  列表1
    :param list_two: list  列表2
    :return: 列表交集
    """
    intersection = [x for x in list_one if x in list_two]
    return intersection


def get_union_from_lists(list_one, list_two):
    """
    功能描述：反馈两个列表的并集
    :param list_one: list  列表1
    :param list_two: list  列表2
    :return: 列表并集
    """
    union = list(set(list_one).union(set(list_two)))
    return union


def get_difference_from_lists(list_one, list_two):
    """
    功能描述：反馈两个列表的差集
    :param list_one: list  列表1
    :param list_two: list  列表2
    :return: 列表差集
    """
    difference = list(set(list_one).difference(set(list_two)))
    return difference


def base64_encode(string):
    """
    功能描述： 将字符串进行base64编码
    :param string: str  指定字符串
    :return: 编码后的base64字符串
    """
    b64_str = base64.b64encode(string.encode())
    return b64_str


def base64_decode(string):
    """
    功能描述： 将字符串进行base64解码
    :param string: str  指定字符串
    :return: 解码后的base64字符串
    """
    return base64.b64decode(string).decode()


def read_img_to_base64str(img_path):
    """
    功能描述：读取图片并转换成base64格式的字符串
    :param img_path:  str  图片路径
    :return: 图片的base64字符串
    """
    with open(img_path, "rb") as file:
        img_base64str = base64.b64encode(file.read())
    return img_base64str


def load_yml(filepath):
    """
    功能描述：导入yml配置文件并反序列化为python对象
    :param filepath:
    :return: python对象
    """
    # 1.yaml文件规则
    # 区分大小写；
    # 使用缩进表示层级关系；
    # 缩进的空格数目不固定，只需要相同层级的元素左侧对齐；
    # 文件中的字符串不需要使用引号标注，但若字符串包含有特殊字符则需用引号标注；
    # 注释标识为  #
    # 2.yaml文件数据结构
    # 对象：键值对的集合（简称"映射或字典"）
    # 键值对用冒号 “:” 结构表示，冒号与值之间需用空格分隔
    # 数组：一组按序排列的值（简称"序列或列表"）
    # 数组前加有 “-” 符号，符号与值之间需用空格分隔
    # 纯量(scalars)：单个的、不可再分的值（如：字符串、bool值、整数、浮点数、时间、日期、等）
    # None值可用、 ~ 表示
    with open(filepath, 'r', encoding='UTF-8') as file:
        content = file.read()
        yaml_info = load(content, Loader=FullLoader)
    return yaml_info


def dump_yml(filepath, data):
    """
    功能描述： 将指定的python对象的数据序列化后存入文件
    :param filepath:
    :param data:
    :return:
    """
    # 1.yaml文件规则
    # 区分大小写；
    # 使用缩进表示层级关系；
    # 使用空格键缩进，而非Tab键缩进
    # 缩进的空格数目不固定，只需要相同层级的元素左侧对齐；
    # 文件中的字符串不需要使用引号标注，但若字符串包含有特殊字符则需用引号标注；
    # 注释标识为  #
    # 2.yaml文件数据结构
    # 对象：键值对的集合（简称"映射或字典"）
    # 键值对用冒号 “:” 结构表示，冒号与值之间需用空格分隔
    # 数组：一组按序排列的值（简称"序列或列表"）
    # 数组前加有 “-” 符号，符号与值之间需用空格分隔
    # 纯量(scalars)：单个的、不可再分的值（如：字符串、bool值、整数、浮点数、时间、日期、等）
    # None值可用、 ~ 表示
    with open(filepath, 'w', encoding='UTF-8'):
        dump(data, filepath)


def create_dict(dic_string):
    """
    功能描述：转换json字符串至python字典对象
    :param dic_string: str  json对象形式的字段字符串
    :return: python字典对象
    """
    convert_to_dic = ""
    if isinstance(dic_string, str):
        new_dic_str = str(dic_string).replace("'", '"')
        convert_to_dic: object = json.loads(new_dic_str)
    elif isinstance(dic_string, dict):
        convert_to_dic = dic_string
    return convert_to_dic


def set_dict(dic, key, value):
    """
    功能描述： 获取字典指定键的值
    :param   dic:  dict  字典对象
    :param   key:   str  字典的键
    :param value:        字典的键值
    :return:
    """
    dic[key] = value


def append_list(*args):
    """
    功能描述：已有列表追加值，或者生成新列表
    :param args: 一个参数的时候为列表的值；两个参数的时候，第一个参数为原始列表，第二个参数为该列表追加的值
    :return: 更新的列表
    """
    args_len = len(args)
    my_list = []
    # 一个参数的时候生成新的列表，并返回该列表
    if args_len == 1:
        my_list.append(args)
    # 两个参数的时候，第一个参数必须为列表，将第二个参数追加到该列表内
    elif args_len == 2:
        my_list = args[0]
        my_list.append(args[1])
    return my_list


def del_list_by_index(target_list, start="", end=""):
    """
    功能描述：根据索引删除列表的值
    :param target_list: list  目标列表
    :param start:       int|str  起始索引
    :param end:         int|str  终止索引
    :return:
    """
    if end:
        del target_list[int(start):int(end)]
    else:
        del target_list[int(start)]


# 类函数装饰器函数
def get_all_list(func):
    """
    功能描述：获取接口全部分页数据，并返回所有目标数据的全集
    :param func: str  目标接口名
    :return:
    """

    def wrapper(self, *args, **kwargs):
        result = []
        resp = func(self, *args, **kwargs)
        if "data" not in resp:
            return
        if "totalRows" in resp["data"]:
            pages = math.ceil(resp["data"]["totalRows"] / 10)
        else:
            pages = math.ceil(resp["data"]["total"] / 10)
        # print(f"pages:{pages}")
        for i in range(1, pages + 1):
            resp = func(self, page=i, **kwargs)
            # logger.console(f"resp:{resp}")
            result.extend(resp["data"]["list"])
        if func.__name__ == "inter_get_new_and_renewal_list":
            debug(f"续费名单长度:{len(result)},未检查到重复记录！")
        return result

    return wrapper


def get_now_date():
    """
    功能描述：获取当前日期
    :return:
    """
    now_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    logger.console(f"now_date:{now_date}")
    return now_date


def get_now_year():
    """
    功能描述：获取当前日期的年份
    :return:
    """
    year = datetime.datetime.strftime(datetime.datetime.now(), '%Y')
    return year


def get_now_month():
    """
    功能描述：获取当前日期的月份
    :return:
    """
    month = datetime.datetime.strftime(datetime.datetime.now(), "%m")
    return month


def get_now_day():
    """
    功能描述：获取当前日期的日
    :return:
    """
    day = datetime.datetime.strftime(datetime.datetime.now(), "%d")
    return day


def get_now_relative(year="", month="", day="", return_year=False, return_month=False):
    """
    功能描述：获取当前日期的相对偏移量
    :param           year: str|int  年份的偏移量
    :param          month: str|int  月份的偏移量
    :param            day: str|int  日的偏移量
    :param    return_year: boolean  是否返回年份
    :param   return_month: boolean  是否返回月份
    :return: 日期偏移量
    """
    year = int(year) if isinstance(year, int) else year
    month = int(month) if isinstance(month, int) else month
    day = int(day) if isinstance(day, int) else day
    now_time = datetime.datetime.now()
    # now = datetime.datetime.strptime("2021-1-20",'%Y-%m-%d')
    if year != "":
        relative = now_time + relativedelta(years=year)
        new_relative = datetime.datetime.strftime(relative, '%Y')
    elif month != "":
        relative = now_time + relativedelta(months=month)
        new_relative = datetime.datetime.strftime(relative, '%m')
    elif day != "":
        relative = now_time + relativedelta(days=day)
        new_relative = datetime.datetime.strftime(relative, '%d')
    else:
        relative = now_time
        new_relative = datetime.datetime.strftime(relative, '%Y-%m-%d')
    # logger.console(f"new_relative:{new_relative}")
    year_relative = datetime.datetime.strftime(relative, '%Y')
    month_relative = datetime.datetime.strftime(relative, '%m')
    if return_year and not return_month:
        return year_relative, new_relative
    elif return_month and not return_year:
        return month_relative, new_relative
    elif return_year and return_month:
        return year_relative, month_relative, new_relative
    else:
        return new_relative


def create_phone_number():
    # 创建手机号第二位,从这个list里面随机选择一个数字
    second = random.choice([3, 4, 5, 7, 8, 9])
    # 创建手机号第三位
    third = {
        # 从0-9之间随机生成一个整数int类型
        3: random.randint(0, 9),
        4: random.choice([5, 7, 9]),
        5: random.choice([0, 1, 2, 3, 4, 5, 7, 8]),
        7: random.choice([2, 3, 5, 6, 7, 8]),
        8: random.randint(0, 9),
        9: random.choice([1, 3, 8, 9]),
    }[second]  # third后面加上second是由于third的生成要依赖second的随机选择结果

    # 创建手机号最后八位
    suffix = "".join(random.sample("0123456789", k=8))
    # 拼接手机号
    return f"1{second}{third}{suffix}"


def public_check_image_url_filename(url, filepath):
    """
    功能描述:对比通过url下载的图片和filename的图片是否一致，并返回对比结果
    :param filepath:     str|本地图片地址
    :param url:          str|图片的网络地址
    :return:
    """
    url_image = base64.b64encode(requests.get(url, timeout=30).content)
    with open(filepath, "rb") as image_file:
        local_image = base64.b64encode(image_file.read())
    return url_image == local_image


class CustomException(Exception):
    def __init__(self, error_info):
        # 初始化父类
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


if __name__ == "__main__":
    # now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    # d1 = datetime.datetime.strptime(now, '%Y-%m-%d')
    # d2 = datetime.datetime.strptime(now, '%Y-%m-%d')
    # delta = datetime.timedelta(days=3)
    # x1 = d1 + delta
    # x2 = d2 - delta
    # x3 = d1 + relativedelta(months=3)
    # x4 = d1 - relativedelta(months=3)
    # print(x1)
    # print(x2)
    # print(x3)
    # print(x4)
    # print(x1.year, x1.month, x1.day)
    # get_now_date()
    # get_now_year()
    # get_now_month()
    # get_now_day()
    # print(get_now_relative(day=+1, return_year=True, return_month=True))
    # now = datetime.datetime.strptime(datetime.datetime.now(), '%Y-%m-%d %H')
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(now, now2)
