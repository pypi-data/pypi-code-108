import logging
from pyocs import pyocs_software

"""
# @author:chenfan3714
# @作用：OCS上的软件相关的功能
# @className：TclSearchid
"""


class TclSearchid:
    """OSM脚本需要设置很多过滤器，特增加此文件用以添加各种过滤器使用"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARN)  # 控制打印级别

    def get_searchid_with_tcl(self, customer, engineer):
        advanced_search = {
            "0": {"search_field_name": "Task.account_id", "search_field_id": "560", "search_field_type": "19",
                 "search_field_rel_obj": "Accounts", "search_opr": "TDD_OPER_EQUAL", "input1": customer,
                 "input2": "null", "offset": "null"},
            "1": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                 "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_GT_EQUAL", "input1": "待录入需求",
                 "input2": "null", "offset": "null"},
            "2": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                 "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_LE_EQUAL", "input1": "待上传软件",
                 "input2": "null", "offset": "null"},
            "3": {"search_field_name": "Task.task_type", "search_field_id": "544", "search_field_type": "19",
                 "search_field_rel_obj": "Dics", "search_opr": "TDD_OPER_EQUAL", "input1": "生产软件任务", "input2": "null",
                 "offset": "null"},
            "4": {"search_field_name": "Task.sw_user_id", "search_field_id": "555", "search_field_type": "19",
                 "search_field_rel_obj": "Users", "search_opr": "TDD_OPER_INC", "input1": engineer, "input2": "null",
                 "offset": "null"}
        }
        condition = "1 and 2 and 3 and 4 and 5 and 6"
        searchid = pyocs_software.PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid
