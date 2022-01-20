# -*- coding: utf-8 -*-
# @Time     : 2022/01/19 20:49:07
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : build_feature.py
# @Software : Visual Studio Code
# @WeChat   : NextB


import os
import sys
import json
import hashlib
try:
    from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
except:
    sys.exit(0)

from python_mmdt.mmdt.mmdt import MMDT
from python_mmdt.mmdt.common import mmdt_save, mmdt_std


def list_dir(root_dir):
    all_file = list()
    files = os.listdir(root_dir)
    for f in files:
        file_path = os.path.join(root_dir, f)
        all_file.append(file_path)
    return all_file

def read_lables(lable_path):
    with open(lable_path, 'r') as f:
        data = f.read()
        labels = json.loads(data)
        return labels

def check_mmdt_hash(md):
    arr_std = mmdt_std(md)
    if arr_std > 0.0:
        return True
    return False

def calc_sha1(file_name):
    with open(file_name, 'rb') as f:
        data = f.read()
        _s = hashlib.sha1()
        _s.update(data)
        return _s.hexdigest()

def work(file_list, labels):
    datas = list()
    mmdt = MMDT()
    count = 0
    for full_path in file_list:
        count += 1
        file_name = os.path.basename(full_path)
        print('process: %s, %d' % (file_name, count))
        mmdt_hash = mmdt.mmdt_hash(full_path)
        if check_mmdt_hash(mmdt_hash):
            c_sha1 = calc_sha1(full_path)
            label = labels.get(file_name, 'black')                
            data = '%s:%s:%s' % (mmdt_hash, label, c_sha1)
            datas.append(data)
    return datas

def run():
    samples_path = sys.argv[1]
    samples_label_file = sys.argv[2]
    feautre_name = sys.argv[3]
    file_list = list_dir(samples_path)
    all_labels = read_lables(samples_label_file)
    max_workers = 8
    number = len(file_list)
    dlt = int(number / max_workers)
    dlt = number if dlt < max_workers else dlt
    datas = list()
    # datas.extend(work(file_list, all_labels))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        all_task = [executor.submit(work, file_list[k:k+dlt], all_labels) for k in range(0, number, dlt)]
        wait(all_task, return_when=ALL_COMPLETED)
        for task in all_task:
            result = task.result()
            datas.extend(result)
    mmdt_save(feautre_name, datas)


if __name__ == '__main__':
    run()