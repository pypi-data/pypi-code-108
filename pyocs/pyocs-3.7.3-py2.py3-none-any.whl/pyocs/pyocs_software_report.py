import logging
from lxml import etree
from pyocs.pyocs_request import PyocsRequest
from pyocs import pyocs_demand
from pyocs import pyocs_list
"""
# @author:chenfan3714
# @作用：OCS上的软件相关的功能
# @className：PyocsSoftwareReport
"""


class PyocsSoftwareReport:
    _instance = None
    _ocs_base_link = 'https://ocs-api.gz.cvte.cn'
    _sw_info_report_prefix = _ocs_base_link + '/tv/Tasks/view_task_sw_info_report/'
    _sw_info_report_suffix = '/P:erp_batch_no%3D'

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    def get_ocs_html(self, url):
        response = PyocsRequest().pyocs_request_get(url)
        html = etree.HTML(response.text)
        return html

    # @PyocsAnalysis.print_run_time
    def get_sw_report_info_url_link(self, ocs_number):
        """从OCS搜索软件的页面（http://ocs-api.gz.cvte.cn/tv/Attachments/search_firmwares）搜索软件
        Args:
             sw_info: 软件名、软件版本号、或者软件名中的部分信息
        Returns:
             返回搜索到的软件(类型@Software，包含软件名和attachment id)列表，筛除烧录bin，筛除库存重复软件
        """
        url_list = list()
        ocs_request = pyocs_demand.PyocsDemand(ocs_number)
        produce_batch_code_list = ocs_request.get_produce_batch_code()
        for batch in produce_batch_code_list:
            report_url_link = self._sw_info_report_prefix + ocs_number + self._sw_info_report_suffix + batch
            url_list.append(report_url_link)
        return url_list

    def get_mac_addr_info(self, ocs_number):
        """从OCS搜索软件的页面（http://ocs-api.gz.cvte.cn/tv/Attachments/search_firmwares）搜索软件
        Args:
             sw_info: 软件名、软件版本号、或者软件名中的部分信息
        Returns:
             返回搜索到的软件(类型@Software，包含软件名和attachment id)列表，筛除烧录bin，筛除库存重复软件
        """
        url_list = self.get_sw_report_info_url_link(ocs_number)
        mac_addr_list = list()
        for url in url_list:
            html = self.get_ocs_html(url)
            mac_address_xpath = '//th[contains(text(),"MAC地址：")]/following-sibling::td/p/text()'
            mac_address_original_list = html.xpath(mac_address_xpath)
            mac_address_original_str = "".join(mac_address_original_list).strip() if mac_address_original_list else ""
            mac_address_original_str = "" if mac_address_original_str == '无' else mac_address_original_str
            self._logger.info("MAC地址范围：" + str(mac_address_original_str))
            mac_address_list = mac_address_original_str.split( )
            for mac_address_str in mac_address_list:
                if '~' in mac_address_str:
                    mac_addr_list.append(mac_address_str)
        return mac_addr_list

    def ocs_mac_addr_dict(self, searchid):
        ocs_mac_addr_dict = {}
        ocs_list = pyocs_list.PyocsList()
        ocs_id_number, ocs_id_list = ocs_list.get_ocs_id_list(searchid)
        if ocs_id_number:
            for ocs in ocs_id_list:
                mac_addr_list = self.get_mac_addr_info(ocs)
                ocs_mac_addr_dict[ocs] = mac_addr_list
        return ocs_mac_addr_dict

    def find_ocs_match_mac_addr(self, searchid, addr: str):
        ocs_mac_addr_dict = self.ocs_mac_addr_dict(searchid)
        for ocs in ocs_mac_addr_dict.keys():
            mac_addr_list = ocs_mac_addr_dict[ocs]
            if mac_addr_list:
                for mac_addr_str in mac_addr_list:
                    mac_address_list = mac_addr_str.split('~')
                    range_min = mac_address_list[0]
                    range_max = mac_address_list[1]
                    if addr >= range_min and addr <= range_max:
                        return ocs
                    else:
                        continue
            else:
                continue
        return ''

