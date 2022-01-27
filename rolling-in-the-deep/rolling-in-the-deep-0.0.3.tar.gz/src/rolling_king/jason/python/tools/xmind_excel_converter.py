# -*- coding: utf-8 -*-
# ---
# @File: xmind_excel_converter.py
# @Author: gaoxiang.404
# @Time: 4月 29, 2021
# ---

import xmind
import csv
import time

source = xmind.load('/Users/admin/Documents/Checklist/Checklist-应用代码位管理API删除聚合属性代码位限制.xmind')

case_base = source.getData()[0]['topic']['topics']


def xmind2excel():
    output_filename = 'testcase_{}.cvs'.format(str(time.time())[-5:])
    with open(output_filename, 'w', newline='') as csvfile:
        fieldname = ['Node', 'Case', 'Status', 'Tester']
        writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldname)
        writer.writeheader()

        for node in case_base:
            row_node = node['title']
            for case in node['topics']:
                row_case = case['title']
                writer.writerow({'Node':row_node,'Case':row_case,'Status': 'NOT RUN', 'Tester': 'QA'})


if __name__ == '__main__':
    # print(source.getData()[0]['topic']['topics'])
    # print(source.to_prettify_json())
    xmind2excel()
