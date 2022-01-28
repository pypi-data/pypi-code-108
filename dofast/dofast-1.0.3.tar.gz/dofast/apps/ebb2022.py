from collections import defaultdict
from itertools import takewhile
import codefast as cf
from authc import get_redis_cn
from datetime import datetime

rkey = 'ebb2022'


def fib():
    a, b = 1, 2
    while True:
        yield a
        a, b = b, a + b


def is_repeat_required(first_date: str, repeat_time: int):
    # is it time to repeat the task?
    days_elapsed = (datetime.now() -
                    datetime.strptime(first_date, '%Y%m%d')).days
    return cf.fplist(takewhile(lambda x: x <= days_elapsed,
                               fib())).length > repeat_time


def fetch():
    redis = get_redis_cn()
    resp = redis.get(rkey).decode('utf-8')
    cf.io.write(resp, '/tmp/ebb2022.txt')
    resp = resp.split('\n')
    dates = defaultdict(list)
    for line in resp:
        dt = line.split(',')
        for x in dt[2:]:
            begin, end = x.split('-') if '-' in x else (x, x)
            begin, end = int(begin), int(end)
            for i in range(begin, 1 + end):
                dates[i].append((dt[0], dt[1]))
    wip = []
    complete = {}
    for page_number, v in dates.items():
        first_date: str = v[0][1]
        task_type = v[0][0]
        if is_repeat_required(first_date, len(v)):
            wip.append((task_type, page_number))
        else:
            complete[page_number] = (len(v), task_type)
    complete = sorted(complete.items(), key=lambda x: x[1][0])
    for record in complete:
        repeat_time, task_type = record[1]
        print(f"{task_type} {record[0]} : {repeat_time}")
    if wip:
        print('-' * 80)
        print(f"wip: {wip}")


def push(data_file: str):
    t = cf.io.reads(data_file).strip()
    redis = get_redis_cn()
    resp = redis.set(rkey, t, ex=60 * 60 * 24 * 30)
    if resp:
        cf.info('update to redis success')


if __name__ == '__main__':
    # fetch('/tmp/ebb2022.txt')
    push('/tmp/ebb2022.txt')
