#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/6 10:02 下午
# @Author  : lance.txl
# @Site    : 
# @File    : adb_utils.py
# @Software: PyCharm

import os

def get_serial_list():
    cmd = "adb devices"
    lines = os.popen(cmd).readlines()
    devices = [x.split("\t")[0].strip() for x in lines[1:] if re.search("device",x)]
    return devices

def adb_head(serial):
    if serial:
        return "adb -s {}".format(serial)
    else:
        return "adb"

def get_new_current_activity(topseq=0,serial=None):
    cmd = "{} shell dumpsys activity | grep -i 'Run #.: ActivityRecord'".format(adb_head(serial))
    lines = [x.strip() for x in os.popen(cmd).readlines() if x.strip()]
    if lines:
        parts = [x.strip() for x in lines[topseq].split(" ") if x.strip()]
        return parts[4] if len(parts) > 5 else ""
    return ""


if __name__ == '__main__':
    r = get_new_current_activity()
    print(r)