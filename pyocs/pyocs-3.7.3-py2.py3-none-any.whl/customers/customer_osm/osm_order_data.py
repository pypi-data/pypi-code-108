import logging
import re
import time
import datetime
from pyocs import pyocs_list
from pyocs import pyocs_demand
from pyocs import pyocs_software
from pyocs import pyocs_searchid
from customers.customer_opm import opm_order_status

"""
# @author: chenfan3714
# @作用：统计OSM订单绩效数据
# @className: OsmOrderData
"""


class OsmOrderData:
    """OSM 订单数据绩效统计"""
    _logger = logging.getLogger(__name__)
    order_data_dict = {}

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    def get_release_order_data(self, search_id, t_start: str, t_end: str):
        value = 0
        cal_count = 0
        sw = pyocs_software.PyocsSoftware()
        order_status = opm_order_status.OpmOrderStatus()
        si = pyocs_searchid.PyocsSearchid(search_id)
        ocs_id_list = si.get_ocs_id_list_info()

        for ocs_id in ocs_id_list:
            count = 0
            cal_count += 1
            # print(ocs_id, cal_count)
            print("# 统计订单计数:", cal_count)
            batch_code_info_list = sw.get_enable_sw_release_info(ocs_id)
            ocs_request = pyocs_demand.PyocsDemand(ocs_id)
            release_model = ocs_request.get_ocs_project_name()
            release_stock_state = sw.get_sw_release_stock_state(ocs_id)
            xpath_id1 = '//span[contains(text(), "已发放")]/../../preceding-sibling::tr[1]/td[4]/a/text()'
            xpath_id2 = '//span[contains(text(), "已发放")]/../../preceding-sibling::tr[1]/td[4]/a/s/text()'
            release_stock_name = sw.get_sw_release_stock_state_name(ocs_id, xpath_id1) + sw.get_sw_release_stock_state_name(ocs_id, xpath_id2)
            task_comment_str, task_comment_list = order_status.get_filter_task_comment_list_spec(ocs_id)
            if release_stock_name:
                release_comment = release_stock_name
            else:
                continue
            key_str = "已发工厂生产"

            if release_model not in self.order_data_dict.keys():
                self.order_data_dict.update({release_model: {'首发': 0, '库存': 0}})

            batch_code_list = [batch_code_list for batch_code_list in batch_code_info_list if '状态' in batch_code_list]
            batch_code_list = list(set(batch_code_list))
            for batch_code in batch_code_list:
                batch_code = str(batch_code)
                batch_code.replace("状态:", '')
                if batch_code[-4].isdigit() is True:
                    print("# ocs:", ocs_id)
                    print("# batch_code:", batch_code.replace("状态：", ''))
                    print("# 库存首发状态为:", release_stock_state)
                    for signal_comment_str in task_comment_list:
                        if release_comment in signal_comment_str and key_str in signal_comment_str:
                            m = re.search("(\d{4}-\d{1,2}-\d{1,2}\d{1,2}:\d{1,2}:\d{1,2})", signal_comment_str)
                            str_date = m.group(1)
                            str_date = str_date[0:10]
                            date_release = datetime.datetime.strptime(str_date, "%Y-%m-%d")
                            date_start = datetime.datetime.strptime(t_start, "%Y-%m-%d")
                            date_end = datetime.datetime.strptime(t_end, "%Y-%m-%d")
                            X = (date_release - date_start)
                            Y = (date_end - date_release)
                            if X.days >= 0 and Y.days >= 0:
                                count += 1
                            continue
            value = self.order_data_dict[release_model][release_stock_state]
            value += count
            self.order_data_dict[release_model][release_stock_state] = value

        return self.order_data_dict



