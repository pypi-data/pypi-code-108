import os
import sys
import time

PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(PATH)
print(PATH)

from src.winhye_common.config.config_client import ConfigClient


def test_apollo():
    clint = ConfigClient()
    clint.init(lib_app_id='winhye_common')
    alarm = clint.get_group('alarm', "winhye_software.common")
    while True:
        print(alarm.url)
        print(alarm.isAtAll, eval(alarm.isAtAll))
        # print(clint.get_value("alarm.isAtAll", "winhye_software.common"))
        time.sleep(5)


if __name__ == '__main__':
    test_apollo()
