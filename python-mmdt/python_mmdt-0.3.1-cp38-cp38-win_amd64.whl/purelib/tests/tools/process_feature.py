# -*- coding: utf-8 -*-
# @Time     : 2022/01/20 11:50:44
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : process_feature.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import os
import sys
import datetime
from python_mmdt.mmdt.common import mmdt_load, mmdt_std, mmdt_save


def dist_filter():
    input_feature_file = sys.argv[1]
    features = mmdt_load(input_feature_file)
    new_features = list()
    for feature in features:
        tmp = feature.strip().split(":")
        md_hash = ':'.join(tmp[:2])
        tag = tmp[2]
        if tag == 'None' or mmdt_std(md_hash) < 10.0:
            print(feature)
            continue
        new_features.append(feature)

    now_time = datetime.datetime.now().strftime('%Y_%M_%D_%H_%m_%S')
    base_path = r"C:\Users\dadav\Features_mmdt\feature_dist"
    base_name = "mmdt_feature_{}".format(now_time)
    out_feature_file = os.path.join(base_path, base_name)
    mmdt_save(out_feature_file, new_features)


if __name__ == '__main__':
    dist_filter()
