# -*- coding: utf-8 -*-

__author__ = "Wang Lin"

import re
import subprocess


def get_ios_device_list():
    """
    Returns: the ios device list on Mac OS
    """

    ios_device_list = []

    system_info = subprocess.check_output("xcrun simctl list devices", shell=True, universal_newlines=True)
    arrived_ios_tag = False

    for info in system_info.splitlines():
        if info.startswith("-- iOS"):
            print("start get the ios device name list...")
            arrived_ios_tag = True
        elif arrived_ios_tag is True and info.startswith("--"):
            break
        else:
            if "iPhone" in info or "iPad" in info:
                info = re.split(r'[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+-[0-9a-zA-Z]+', info)[0]
                info = info[:-1]
                ios_device_list.append(info.strip())

    return ios_device_list


if __name__ == "__main__":
    print(get_ios_device_list())
