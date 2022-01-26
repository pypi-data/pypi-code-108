from exectools.tools_basic import *
from time import time


if __name__ == '__main__':
    print(datetime.now())
    print(TimeSection.nowstamp_point(time_type='hours', time_delta=1))
    print(TimeSection.timestamp_point(time(), "hours"))
