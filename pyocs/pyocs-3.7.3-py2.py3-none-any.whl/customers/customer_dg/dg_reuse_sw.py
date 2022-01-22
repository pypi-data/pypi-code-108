from customers.customer_dg.excelManager import ExcelManager
from pyocs import pyocs_software
from customers.customer_dg.cfgManager import work_dir
import os
confirm_task = pyocs_software.PyocsSoftware()
class DGReuseSw:
    @staticmethod
    def dg_reuse_software(cus_name, file_path, workspace):
        count = 1
        if cus_name == "CHANGHON":
            excelm_d = ExcelManager(file_path)
            abstract_list = excelm_d.get_rule_value(['长虹批号'])
            line_list = ExcelManager.get_line_number_from_excel_for_changhon(cus_name, file_path)
            for line in line_list:
                if len(line) > 1:
                    print("==ERROR==冻结书中第 %s 项在映射表中不止找到一项，请确认映射表正确性" % count)
                    continue
                elif line == []:
                    print("==冻结书中第 %s 项在映射表中找不到匹配项==" % count)
                else:
                    src_ocs = ExcelManager.get_ocs_number_from_excel(work_dir + '/KB信息对照表.xlsx', line[0])
                    dst_ocs = confirm_task.get_ocs_number_from_abstract(abstract_list[0][count - 1])
                    if len(dst_ocs) > 1:
                        print("==ERROR==冻结书中第%s项的摘要匹配了不止一个订单，请确认映射表正确性" % count)
                        continue
                    else:
                        print("OCS: %s >>>>>>>>>> OCS: %s" % (src_ocs, dst_ocs))
                        print("引用软件中......")
                        confirm_task.reuse_old_sw_from_src_to_dst(str(src_ocs), str(dst_ocs[0]), workspace=workspace)
                count += 1
        elif cus_name == "TCL":
            excelm_tcl = ExcelManager(file_path)
            line_list = excelm_tcl.get_line_number_from_excel_for_TCL()
            for line in line_list:
                if line == []:
                    print("==第 %s 项在表中找不到匹配项==" % count)
                else:
                    src_ocs = ExcelManager.get_ocs_number_from_excel(file_path, line[0])
                    dst_ocs = ExcelManager.get_ocs_number_from_excel(file_path, excelm_tcl.min_sign_ret + count)
                    print("OCS: %s >>>>>>>>>> OCS: %s" % (src_ocs, dst_ocs))
                    print("引用软件中......")
                    confirm_task.reuse_old_sw_from_src_to_dst(str(src_ocs), str(dst_ocs), workspace=workspace)
                count += 1
        else:
            print("您所输入的客户没有对应的规则，请确认您的输入信息，或者联系管理员添加")
            exit(2)

    @staticmethod
    def make_res_dir():
        if os.path.exists(work_dir) == False:
            os.system("mkdir %s" % work_dir)

if __name__ == "__main__":
    DGReuseSw.make_res_dir()






