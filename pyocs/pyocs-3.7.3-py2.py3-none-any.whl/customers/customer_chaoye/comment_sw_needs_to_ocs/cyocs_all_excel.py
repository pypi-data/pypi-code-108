# -*- coding: utf-8 -*-
import os
import xlrd
from pyocs.pyocs_login import PyocsLogin
from customers.customer_chaoye.comment_sw_needs_to_ocs.cy_demand_to_ocs import CyNeedsToOcs
from customers.customer_chaoye.comment_sw_needs_to_ocs.excel_deal import getRowsClosNum


rows_total_num = getRowsClosNum()
print(rows_total_num)

pyocs_login=PyocsLogin()
account_info = pyocs_login.get_account_from_json_file()
Path = account_info["chaoye_request_excel_path"]

workbook = xlrd.open_workbook(Path, formatting_info=1)
worksheet=workbook.sheet_by_index(1)

max_cols=11
#从3开始因为前两行是表头不用处理
for row_index in range(2,rows_total_num):
    for cols_index in range(1,11):
        #屏型号+软件时间变更不做处理
        if (cols_index == 6 or cols_index == 7):
            break;
        xfx = worksheet.cell_xf_index(row_index, cols_index)
        xf = workbook.xf_list[xfx]
        bgx = xf.background.pattern_colour_index

        #朝野需求表 紫色46  橙色51  黄色13 需要处理
        if bgx == 46 or bgx == 51 or bgx== 13:
            if(CyNeedsToOcs.deal_customer_excel_date_to_ocs(row_index) == "Get_num_none"):
                break;
            break;

print("处理结束，删除需求表文件!")
os.remove(Path)