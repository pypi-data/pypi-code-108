import random
import time


# 打印时间
def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# 获取时间间隔
def _get_time_interval():
    time_a = time.time()
    time.sleep(3)
    time_b = time.time()
    interval = round(time_b - time_a, 2)
    print(f'时间间隔: {interval}s')
    return interval


# 生成时间戳
def get_timestamp(n=13) -> str:
    timestamp = str(time.time()).replace('.', '')[:n]
    timestamp = timestamp.ljust(n, '6')
    print(f'时间戳: {timestamp}')
    return timestamp


# 通过时间戳生成文本
def get_name(content) -> str:
    non_report_str = f'{content}-{get_timestamp()}'
    print(f'不重复的字符串: {non_report_str}')
    return non_report_str


# 通过时间戳生成手机号
def get_phone() -> str:
    # 移动手机号前几位
    cm = [134, 135, 136, 137, 138, 139, 150, 151, 152, 157, 158, 159, 182, 183, 184, 187, 188, 147, 178, 1705]
    # 联通手机号前几位
    cu = [130, 131, 132, 155, 156, 185, 186, 145, 176, 1709]
    # 手机号前几位
    ct = [133, 153, 180, 181, 189, 177, 1700]
    phone = str(random.choice(cm + cu + ct)) + get_timestamp()
    phone = phone[:11]
    print(f'手机号: {phone}')
    return phone


if __name__ == '__main__':
    # get_timestamp()
    # get_name('张三')
    # get_phone()
    _get_time_interval()



