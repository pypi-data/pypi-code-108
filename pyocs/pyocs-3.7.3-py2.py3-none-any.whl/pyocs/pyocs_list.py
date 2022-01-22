# from pyocs import pyocs_software
from pyocs import pyocs_demand
from pyocs.pyocs_request import PyocsRequest
import logging
from urllib.parse import urlencode
from lxml import etree
from colorama import Fore, Back, Style


class PyocsList:

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别


    def get_single_data_list(self, list_xpath, search_id):
        """
        Args:
            list_xpath: 想要获取的任意一列的数据的xpath，一般根据class这个属性可以精确定位
            search_id: ocs SearchId,主要是批量搜索订单
        Returns:
            1. 返回获取到的订单的数量
            2. 返回需要获取的数据（ocs号/客户批号/.....
        """
        url = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:'
        url += search_id
        request = PyocsRequest()
        r = request.pyocs_request_get(url)
        html = etree.HTML(r.text)
        single_data_nodes = html.xpath(list_xpath)
        single_data_list = []
        for node in single_data_nodes:
            single_data_list.append(node.text)
        return len(single_data_list), single_data_list

    def get_ocs_id_list(self, search_id):
        """
        Args:
            search_id: ocs SearchId,主要是批量搜索订单
        Retuens:
            返回搜到的ocs订单号列表
        """
        xpath = '//td[@class="Task_col_id"]'
        ocs_number, ocs_list = self.get_single_data_list(xpath, search_id)

        return ocs_number, ocs_list


    def get_ocs_customerId_list(self, search_id):
        """
        Args:
            search_id: ocs SearchId,主要是批量搜索订单
        Retuens:
            返回搜到的ocs订单号列表
        """
        xpath = '//td[@class="Contract_col_account_bno"]'
        ocs_number, ocs_list = self.get_single_data_list(xpath, search_id)
        return ocs_number, ocs_list

    def get_ocs_engineer_list(self, search_id):
        """
        Args:
            search_id: ocs SearchId,主要是批量搜索订单
        Retuens:
            返回搜到的ocs订单号列表
        """
        xpath = '//td[@class="Task_col_sw_user_id"]'
        user_number, user_list = self.get_single_data_list(xpath, search_id)
        return user_number, user_list

    def get_ocs_specific_list(self, xpath_id, search_id):
        """
        Args:
            xpath_id : xpath 具体字符
            search_id: ocs SearchId,主要是批量搜索订单
        Retuens:
            返回搜到的ocs订单号列表
        """
        xpath = '//td[@class="' + xpath_id + '"]'
        count_number, specific_list = self.get_single_data_list(xpath, search_id)
        return count_number, specific_list
