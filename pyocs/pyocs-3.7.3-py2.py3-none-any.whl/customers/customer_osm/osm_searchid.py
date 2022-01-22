import logging
from pyocs import pyocs_software

"""
# @author:chenfan3714
# @作用：OCS上的软件相关的功能
# @className：OsmSearchid
"""


class OsmSearchid:
    """OSM脚本需要设置很多过滤器，特增加此文件用以添加各种过滤器使用"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARN)  # 控制打印级别

    def get_searchid_with_advanced_search_filter(self, period, td_input_6):
        advanced_search = {
            "0": {"search_field_name": "Task.plan_end_date", "search_field_id": "548", "search_field_type": "9",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": period, "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
             "1": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                   "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_GT_EQUAL", "input1": "软件待审核", "input2": "null",
                   "offset": "null"},
             "2": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                   "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_NOT_INC",
                   "input1": "已代测发放", "input2": "null", "offset": "null"},
             "3": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                   "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_NOT_INC",
                   "input1": "已最终发放", "input2": "null", "offset": "null"},
             "4": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_NOT_INC", "input1": "虚拟", "input2": "null",
                   "offset": "null"},
             "5": {"search_field_name": "Task.rd_dept_id", "search_field_id": "546", "search_field_type": "19",
                   "search_field_rel_obj": "Depts", "search_opr": "TDD_OPER_INC",
                   "input1": td_input_6,
                   "input2": "null", "offset": "null"}
         }
        condition = "1 and 2 and 3 and 4 and 5 and 6"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def get_ocs_assign_searchid_type1(self):
        advanced_search = {
               "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                     "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL", "input1": "待录入需求", "input2": "null",
                     "offset": "null"},
               "1": {"search_field_name": "Task.account_id", "search_field_id": "560", "search_field_type": "19",
                     "search_field_rel_obj": "Accounts", "search_opr": "TDD_OPER_EQUAL", "input1": "合肥长虹",
                     "input2": "null", "offset": "null"},
               "2": {"search_field_name": "Task.rd_dept_id", "search_field_id": "546", "search_field_type": "19",
                     "search_field_rel_obj": "Depts", "search_opr": "TDD_OPER_NOT_INC",
                     "input1": "V69D VST69T HV35XDG TCON T972LHE MT5510DG MT9255(DG)", "input2": "null", "offset": "null"},
               "3": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                     "search_field_rel_obj": "null", "search_opr": "TDD_OPER_NOT_INC", "input1": "7.01.1 17.11.",
                     "input2": "null", "offset": "null"},
               "4": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                     "search_field_rel_obj": "null", "search_opr": "TDD_OPER_TODAY", "input1": "", "input2": "null",
                     "offset": "null"}
        }
        condition = "1 and 2 and 3 and 4 and 5"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def get_ocs_assign_searchid_type11(self):
        advanced_search = {
                "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                   "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL", "input1": "待录入需求", "input2": "null",
                   "offset": "null"},
                "1": {"search_field_name": "Task.account_id", "search_field_id": "560", "search_field_type": "19",
                   "search_field_rel_obj": "Accounts", "search_opr": "TDD_OPER_EQUAL", "input1": "合肥长虹", "input2": "null",
                   "offset": "null"},
                "2": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC", "input1": "7.01.1", "input2": "null",
                   "offset": "null"},
                "3": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_TODAY", "input1": "", "input2": "null",
                   "offset": "null"}
         }
        condition = "1 and 2 and 3 and 4"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def get_ocs_assign_searchid_type12(self):
        advanced_search = {
                "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                   "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL", "input1": "待录入需求", "input2": "null",
                   "offset": "null"},
                "1": {"search_field_name": "Task.account_id", "search_field_id": "560", "search_field_type": "19",
                   "search_field_rel_obj": "Accounts", "search_opr": "TDD_OPER_EQUAL", "input1": "合肥长虹", "input2": "null",
                   "offset": "null"},
                "2": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC", "input1": "17.11", "input2": "null",
                   "offset": "null"},
                "3": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_TODAY", "input1": "", "input2": "null",
                   "offset": "null"}
         }
        condition = "1 and 2 and 3 and 4"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid


    def get_ocs_assign_searchid_type2(self):
        advanced_search = {
            "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                 "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL", "input1": "待录入需求", "input2": "null",
                 "offset": "null"},
            "1": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_TODAY", "input1": "", "input2": "null",
                 "offset": "null"},
            "2": {"search_field_name": "Task.rd_dept_id", "search_field_id": "546", "search_field_type": "19",
                 "search_field_rel_obj": "Depts", "search_opr": "TDD_OPER_EQUAL", "input1": "单电源", "input2": "null",
                 "offset": "null"}
        }
        condition = "1 and 2 and 3"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def get_ocs_assign_searchid_type31(self):
        advanced_search = {
          "0": {
            "search_field_name": "Task.account_id",
            "search_field_id": "560",
            "search_field_type": "19",
            "search_field_rel_obj": "Accounts",
            "search_opr": "TDD_OPER_EQUAL",
            "input1": "广东海信",
            "input2": "null",
            "offset": "null"
          },
          "1": {
            "search_field_name": "Task.status",
            "search_field_id": "584",
            "search_field_type": "19",
            "search_field_rel_obj": "Enums",
            "search_opr": "TDD_OPER_EQUAL",
            "input1": "待录入需求",
            "input2": "null",
            "offset": "null"
          },
          "2": {
            "search_field_name": "Task.rd_dept_id",
            "search_field_id": "546",
            "search_field_type": "19",
            "search_field_rel_obj": "Depts",
            "search_opr": "TDD_OPER_EQUAL",
            "input1": "MS6683",
            "input2": "null",
            "offset": "null"
          },
          "3": {
            "search_field_name": "Task.create_time",
            "search_field_id": "585",
            "search_field_type": "10",
            "search_field_rel_obj": "null",
            "search_opr": "TDD_OPER_TODAY",
            "input1": "",
            "input2": "null",
            "offset": "null"
          }
        }
        condition = "1 and 2 and 3 and 4"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def get_ocs_assign_searchid_type4(self):
        advanced_search = {
          "0": {
            "search_field_name": "Task.rel_obj_id.product_id.pcb_id.biz_id",
            "search_field_id": "5836",
            "search_field_type": "19",
            "search_field_rel_obj": "Bizs",
            "search_opr": "TDD_OPER_INC",
            "input1": "厦门部件",
            "input2": "null",
            "offset": "null"
          },
          "1": {
            "search_field_name": "Task.rd_dept_id",
            "search_field_id": "546",
            "search_field_type": "19",
            "search_field_rel_obj": "Depts",
            "search_opr": "TDD_OPER_INC",
            "input1": "RK3399 MSD3393 MT5510 MT9632 T960 RK3368 MS3663 MS3553 MS3683 厦门办",
            "input2": "null",
            "offset": "null"
          },
          "2": {
            "search_field_name": "Task.create_time",
            "search_field_id": "585",
            "search_field_type": "10",
            "search_field_rel_obj": "null",
            "search_opr": "TDD_OPER_TODAY",
            "input1": "",
            "input2": "null",
            "offset": "null"
          }
        }
        condition = "1 and 2 and 3"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid
		
    def get_ocs_assign_searchid_type5(self):
        advanced_search = {
          "0": {
            "search_field_name": "Task.rd_dept_id",
            "search_field_id": "546",
            "search_field_type": "19",
            "search_field_rel_obj": "Depts",
            "search_opr": "TDD_OPER_EQUAL",
            "input1": "视睿小板",
            "input2": "null",
            "offset": "null"
          },
          "1": {
            "search_field_name": "Task.create_time",
            "search_field_id": "585",
            "search_field_type": "10",
            "search_field_rel_obj": "null",
            "search_opr": "TDD_OPER_TODAY",
            "input1": "",
            "input2": "null",
            "offset": "null"
          },
          "2": {
            "search_field_name": "Task.status",
            "search_field_id": "584",
            "search_field_type": "19",
            "search_field_rel_obj": "Enums",
            "search_opr": "TDD_OPER_EQUAL",
            "input1": "待录入需求",
            "input2": "null",
            "offset": "null"
          },
        }
        condition = "1 and 2 and 3"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid