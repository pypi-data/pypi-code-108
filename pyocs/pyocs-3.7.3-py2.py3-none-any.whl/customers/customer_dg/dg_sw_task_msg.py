from pyocs import pyocs_software 
from pyocs.pyocs_demand import PyocsDemand
import os
import csv
import sys
import time
confirm_task = pyocs_software.PyocsSoftware()
class DgSwTaskMsg:
    @staticmethod
    def dg_get_sw_task_msg(fileName):
        with open(fileName,"r", newline="") as csvfile:
            csvReader = csv.reader(csvfile);
            output = []
            for sw_name in csvReader:
                dst_ocs_array = confirm_task.get_all_ocs_number_from_sw(sw_name)
                print("软件版本："+str(sw_name)+"使用被引用订单有：")
                print(dst_ocs_array)
                for ocs_number in dst_ocs_array:
                    print("正在查询以下订单:"+ocs_number+"，请等待...")
                    ocs_task = PyocsDemand(ocs_number) 
                    product_name = ocs_task.get_product_name_and_version()
                    c_mach = ocs_task.get_customer_machine()
                    plan_end = ocs_task.get_plan_end_date()
                    all_batch = ocs_task.get_all_produce_batch_code()
                    for one_batch in all_batch:
                        one_record = {}
                        one_record['软件版本'] = ''.join(sw_name)
                        one_record['产品型号'] = product_name
                        one_record['客户机型'] = c_mach
                        one_record['生产批次号'] = one_batch
                        one_record['数量'] = ocs_task.get_number_by_product_batch_code(one_batch)
                        one_record['计划完成日期'] = plan_end 
                        output.append(one_record)
        time_str = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
        with open( time_str+'.csv', 'w', newline='') as csvfile:
            fieldnames = ['软件版本', '产品型号', '客户机型', '生产批次号', '数量', '计划完成日期']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for one_record in output:
                writer.writerow(one_record)

if __name__ == '__main__':
    DgSwTaskMsg.dg_get_sw_task_msg(sys.argv[1])
