# 时间格式化
# 创建人：曾逸夫
# 创建时间：2022-01-20

import sys


# 判断时间格式
def is_time(preTime):
    if (preTime <= 0):
        print(f'时间格式不正确！程序结束！')
        sys.exit()


# 时间格式化
def time_format(preTime):
    is_time(preTime)  # 判断时间格式
    m, s = divmod(preTime, 60)  # 获取秒
    h, m = divmod(m, 60)  # 获取时、分

    if (0 < s < 1):
        time_str = f'{s:.3f}秒'
        # print(time_str)
        return time_str
    elif (h == 0 and m == 0 and s >= 1):
        time_str = f'{s:.3f}秒'
        # print(time_str)
        return time_str
    elif (h == 0 and m > 0):
        m = int(m)
        time_str = f'{m}分{s:.3f}秒'
        # print(time_str)
        return time_str
    elif (h > 0):
        if (h >= 24):
            h = int(h / 24)
            m = int(m)
            time_str = f'{h}天{m}分{s:.3f}秒'
        else:
            h = int(h)
            m = int(m)
            time_str = f'{h}时{m}分{s:.3f}秒'
        # print(time_str)
        return time_str
    else:
        print(f'时间格式化失败！程序结束！')
        sys.exit()


# if __name__ == '__main__':

#     time_format(0.52362)
#     time_format(50.52362)
#     time_format(90.52362)
#     time_format(5000.52362)
#     time_format(3600*24 + 1000.52362)
