#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import logging
from src.rolling_king.jason import ExcelUtil

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置

logger = logging.getLogger("ExcelTest")


def func_excel_val_change(excel_path, excel_sheet, col):
    excel_operator = ExcelUtil(excel_path, excel_sheet)
    logger.info(excel_operator.rows)
    total_row = excel_operator.rows
    day_val = 0
    for curr_row in range(2, total_row+1): # 因为range不包括total_row，所以为了包括而+1
        val = excel_operator.get_cell_value(curr_row, col)
        print(val)
        if val.endswith("秒"):
            sec_val = val.split(" ")[0]
            day_val = int(sec_val)/24/60/60
            set_val = str(round(float(day_val), 2)) + " 天"
            excel_operator.set_cell_value(curr_row, col, set_val)
            logger.info("设置{0}行{1}列的值为{2}".format(curr_row, col, set_val))
        elif val.endswith("分钟"):
            min_val = val.split(" ")[0]
            day_val = int(min_val)/24/60
            set_val = str(round(float(day_val), 2)) + " 天"
            excel_operator.set_cell_value(curr_row, col, set_val)
            logger.info("设置{0}行{1}列的值为{2}".format(curr_row, col, set_val))
        elif val.endswith("小时"):
            hour_val = val.split(" ")[0]
            day_val = int(hour_val)/24
            set_val = str(round(float(day_val), 2))+" 天"
            excel_operator.set_cell_value(curr_row, col, set_val)
            logger.info("设置{0}行{1}列的值为{2}".format(curr_row, col, set_val))

    excel_operator.save("/Users/admin/Downloads/缺陷导出.xlsx")


if __name__ == "__main__":
    func_excel_val_change("/Users/admin/Downloads/缺陷导出-商业产品 (9).xlsx", "缺陷导出-商业产品", 12)

