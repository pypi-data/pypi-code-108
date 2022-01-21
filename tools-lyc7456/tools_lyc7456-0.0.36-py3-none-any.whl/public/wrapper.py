import time
from functools import wraps

# Write by lyc at 2020.9.4

def wrapper_retry(retry_count=3, sleep_second=3):
    '''
    函数装饰器：异常捕获，间隔重试
    retry_count: 重试次数，默认值 3
    sleep_second: 重试间隔，默认值 3（单位秒）
    '''
    def wrapper_outer_retry(func):
        @wraps(func)
        def wrapper_inner_retry(*args, **kwargs):
            count = 1   # 重试次数
            while count <= retry_count:     # 若接口返回异常，间隔3s重试3次
                try:        # 异常捕获
                    ret = func(*args, **kwargs)
                    if ret == False:    # 接口返回值是False，也认为是异常，sleep后continue
                        count += 1
                        time.sleep(sleep_second)
                        continue
                    else:
                        break       # 没有发生异常，break跳出重试循环
                except Exception as err:  # 捕获到程序异常，sleep后继续下一循环
                    print(err)
                    count += 1
                    time.sleep(sleep_second)

            return ret
        return wrapper_inner_retry
    return wrapper_outer_retry
