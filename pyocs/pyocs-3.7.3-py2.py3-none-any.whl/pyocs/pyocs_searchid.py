from pyocs import pyocs_demand
from pyocs.pyocs_request import PyocsRequest
import logging
from urllib.parse import urlencode
from lxml import etree
from colorama import Fore, Back, Style
from pyocs.pyocs_exception import *
import re
from bs4 import BeautifulSoup

class PyocsSearchid:
    _logger = logging.getLogger(__name__)

    def __init__(self, search_id='', link_prefix='https://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:'):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        self.search_id = search_id
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        self.ocs_link = link_prefix + search_id
        ocs_url_response = PyocsRequest().pyocs_request_get(self.ocs_link, False)

        if ocs_url_response.status_code == 200:
            self.html = etree.HTML(ocs_url_response.text)
            self.res = ocs_url_response
        else:
            raise OcsSystemError('OCS访问存在问题')

    def get_single_searchid_info(self, xpath_str, url_str):
        """
        Args:
            list_xpath: 想要获取的任意一列的数据的xpath，一般根据class这个属性可以精确定位
            search_id: ocs SearchId,主要是批量搜索订单
        Returns:
            1. 返回获取到的订单的数量
            2. 返回需要获取的数据（ocs号/客户批号/.....
        """
        request = PyocsRequest()
        r = request.pyocs_request_get(url_str)
        xhtml = etree.HTML(r.text)
        single_data_nodes = xhtml.xpath(xpath_str)
        single_data_list = []
        for node in single_data_nodes:
            single_data_list.append(node.text)
        return single_data_list

    def get_searchid_page_index(self):
        """
        Return:
            返回搜到的ocs订单列表的页面数量
        """
        page_index_xpath = \
            '//div[@class="data-layout"]/p/text()'
        page_index_list = self.html.xpath(page_index_xpath)
        page_index_str = "".join(page_index_list).strip().strip('\r\n') if page_index_list else ""
        index_list = str(page_index_str).split('，')
        index_str = index_list[0].split('/')
        page_index_number = index_str[1].rstrip()
        return page_index_number

    def get_searchid_ocs_number(self):
        """
        Return:
            返回搜到的ocs订单列表的页面数量
        """
        page_index_xpath = \
            '//div[@class="data-layout"]/p/text()'
        page_index_list = self.html.xpath(page_index_xpath)
        page_index_str = "".join(page_index_list).strip().strip('\r\n') if page_index_list else ""
        page_index_str = page_index_str.replace(" ", "")
        begin = page_index_str.find('（总共')
        end = page_index_str.find('项）')
        page_ocs_number = page_index_str[begin + 3:end]
        page_ocs_number = int(page_ocs_number)
        return page_ocs_number

    def get_ocs_id_list_info(self, xpath='//td[@class="Task_col_id"]'):
        """
        Args:
            search_id: ocs SearchId,主要是批量搜索订单
        Retuens:
            返回搜到的ocs订单号列表
        """
        i = 1
        ocs_list = []
        page_index = self.get_searchid_page_index()
        while i <= int(page_index):
            url = self.ocs_link + '/page:' + str(i)
            i += 1
            ocs_add_list = self.get_single_searchid_info(xpath, url)
            ocs_list.extend(ocs_add_list)
        return ocs_list

    def get_sample_ocs_id_list(self):
        ocs_list = []
        soup = BeautifulSoup(self.res.text, 'html.parser')
        items = soup.find_all('td', class_='resizable Req_col_owner_user_id')
        for i in items:
            tag = i.find_previous()
            ocs_id = tag.text
            ocs_list.append(ocs_id)
        return ocs_list
