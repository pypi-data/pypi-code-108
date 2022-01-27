"""
this is used to verify the specified process is running or not.

@author: Wang Lin
"""
import psutil


def process_exists(name):
    for proc in psutil.process_iter():
        p_name = str(proc.name)
        if p_name.__contains__("name=u'"):
            p_name = p_name.split("name=u'")[1]
            p_name = p_name.split("')")[0]
        if p_name == name:
            return True
    return False
