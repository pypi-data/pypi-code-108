# from pyocs import pyocs_software
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_software import PyocsSoftware
from pyocs.pyocs_request import PyocsRequest
import logging
from urllib.parse import urlencode
from lxml import etree
from colorama import Fore, Back, Style
import re


class PyocsEdit:

    _ocs_base_link = "https://ocs-api.gz.cvte.cn"

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    def get_key(self, dict, value):
        return list(dict.keys())[list(dict.values()).index(value)]

    def get_burn_place_hold(self, ocs_number):
        pyocsSoftware = PyocsSoftware()
        ddr_info_str = PyocsDemand(ocs_number).get_ddr_info()
        ddr_info_dict = eval(ddr_info_str)
        burn_place_hold_nums = ddr_info_str.count('refDec')
        burn_place_hold_itemNo = ddr_info_dict['categoryDescp']
        flash_list1 = ['EMMC FLASH', 'NAND FLASH']
        flash_list2 = ['NOR FLASH']
        if 1 == burn_place_hold_nums:
            burn_place_hold = '【' + ddr_info_dict['refDec'] + '】,' + ddr_info_dict['supplierNo'] + ',' + \
                              ddr_info_dict['itemNo'] + ',' + ddr_info_dict['categoryDescp'] + ',' + ddr_info_dict['capacity']
            burn_place_hold_type = ddr_info_dict['refDec']
            if burn_place_hold_itemNo in flash_list1:
                burn_type = pyocsSoftware.sw_burn_type["离线烧录"]
            elif burn_place_hold_itemNo in flash_list2:
                burn_type = pyocsSoftware.sw_burn_type["在线烧录"]
        elif 2 == burn_place_hold_nums:
            burn_place_hold = '【' + ddr_info_dict['refDec'] + '】,' + ddr_info_dict['supplierNo'] + ',' + \
                              ddr_info_dict['itemNo'] + ',' + ddr_info_dict['categoryDescp'] + ',' + ddr_info_dict['capacity']
            burn_place_hold_option = ddr_info_dict['refDec']
            burn_place_hold1 = '【' + ddr_info_dict['refDec1'] + '】,' + ddr_info_dict['supplierNo1'] + ',' + \
                               ddr_info_dict['itemNo1'] + ',' + ddr_info_dict['categoryDescp1'] + ',' + ddr_info_dict['capacity1']
            burn_place_hold_option1 = ddr_info_dict['refDec1']
            burn_place_hold_str = '请输入烧录位号选项' + '(' + burn_place_hold_option + ', ' + burn_place_hold_option1 + '): '
            burn_place_hold_type = input(burn_place_hold_str)
            burn_place_hold_type = burn_place_hold_type.upper()
            burn_type = input("请输入烧录类型选项(1,2)：")
        return burn_place_hold_type, burn_type


    def get_update_ocs_xml_list(self, ocs_number, list_xpath, filterData):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
            list_xpath: 想要获取的任意一列的数据的xpath，一般根据class这个属性可以精确定位
            filterData: 过滤器，主要是截取需要的字符串返回
        Returns:
            返回过滤器截取过的字符串列表
        """
        if len(filterData) < 1:
            return None

        url = 'https://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/'
        url += ocs_number
        request = PyocsRequest()
        r = request.pyocs_request_get(url)
        html = etree.HTML(r.text)
        single_data_nodes = html.xpath(list_xpath)
        single_data_list = []
        for node in single_data_nodes:
            if filterData[0] == 'all':
                single_data_list.append(str(node))
            elif filterData[0] in str(node) and len(filterData) >= 3:
                rr = re.compile(filterData[1] + '(.*?)' + filterData[2], re.S)
                test = rr.findall(str(node))
                single_data_list.append(test[0])

        return single_data_list

    def get_ocs_xml_update_url(self, ocs_number):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
        Returns:
            返回搜到的url列表
        """
        xpath = '//td/a[@class="btn btn-mini"]/@onclick'
        filterData = ['Attachments/view_code', '\'/tv/pop/Attachments/view_code/', '\',']
        url_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        return url_list

    def get_use_software_url(self, ocs_number, url_list):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
            url_list: 传入所有的url
        Returns:
            返回未禁用软件的url列表
        """
        ret_list = []
        xpath = '//td/a[@class="btn btn-mini new_lock_fw"]/@attachment_id'
        filterData = ['all', '', '']
        id_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        for _url in url_list:
            for _id in id_list:
                if _id in _url:
                    ret_list.append(_url)
        return ret_list

    def get_assign_software_url(self, ocs_number, sw_name, url_list):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
            sw_name: 传入指定软件名
            url_list: 传入所有的url
        Returns:
            返回未禁用软件的url列表
        """
        ret_list = []
        xpath = '//a[contains(@class, "btn btn-mini new_lock_fw") and contains(@file_name,"' + sw_name + '")]/@attachment_id'
        filterData = ['all', '', '']
        id_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        for _url in url_list:
            if len(id_list) > 0 and id_list[0] in _url:
                ret_list.append(_url)
        return ret_list

    def update_ocs_xml(self, ocs_number, xmlpath, sw_name):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
            xmlpath: 传入本地的xml文件路径
            sw_name: 默认为all，更新全部未禁用的软件xml，不为all时，指定软件名更新xml
        Returns:
            返回True或Fasle
        """
        pyocsSoftware = PyocsSoftware()
        if sw_name == 'all':
            ocs_xml_url = self.get_use_software_url(ocs_number, self.get_ocs_xml_update_url(ocs_number))
        else:
            ocs_xml_url = self.get_assign_software_url(ocs_number, sw_name, self.get_ocs_xml_update_url(ocs_number))
        ret = False
        for xml_url in ocs_xml_url:
            ret = pyocsSoftware.upload_xml_to_ocs(xml_update_url = xml_url, xml_path = xmlpath)
        return ret 

    def set_ocs_test_type_for_all(self, ocs_number, test_type):
        ret = True
        pyocsSoftware = PyocsSoftware()
        ocs_sw_list = pyocsSoftware.get_enable_software_list(ocs_number, False)
        if ocs_sw_list:
            for ocs_sw in ocs_sw_list:
                print(str(ocs_sw.name))
                ret &= pyocsSoftware.set_test_type_for_ocs(ocs_number=ocs_number, sw_name=str(ocs_sw.name), test_type=test_type)
        return ret

    def set_ocs_customer_confirm_for_all(self, ocs_number, confirm_type):
        ret = True
        pyocsSoftware = PyocsSoftware()
        ocs_sw_list = pyocsSoftware.get_enable_software_list(ocs_number, False)
        if ocs_sw_list:
            for ocs_sw in ocs_sw_list:
                print(str(ocs_sw.name))
                ret &= pyocsSoftware.set_software_confirm_for_ocs(ocs_number=ocs_number, sw_name=str(ocs_sw.name), confirm_type=confirm_type)
        return ret
        

    def update_ocs_test_type(self, ocs_number, sw_name, test_type):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的测试类型
            sw_name: 默认为all，更新全部未禁用的软件测试类型，不为all时，指定软件名更新测试类型
            test_type: 传入测试类型(N,A,B,C,D,E,F,G,BC)
        Returns:
            返回True或Fasle
        """
        pyocsSoftware = PyocsSoftware()
        if sw_name == 'all':
            ret = self.set_ocs_test_type_for_all(ocs_number=ocs_number, test_type=test_type)
        else:
            ret = pyocsSoftware.set_test_type_for_ocs(ocs_number=ocs_number, sw_name=sw_name, test_type=test_type)
        return ret

    def get_ocs_burn_type_with_sw_name(self, ocs_number, sw_name):
        """
        Args:
            ocs_number: ocs id
            sw_name: 默认为all，更新全部未禁用的软件测试类型，不为all时，指定软件名更新测试类型
        Returns:
            返回sw_name对应的烧录相关信息
        """
        xpath = '//a[contains(@file_name,"' + sw_name + '")]/../../td[9]/text()'
        filterData = ['all', '', '']
        burn_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        return burn_list

    def get_ocs_burn_id_with_sw_name(self, ocs_number, sw_name):
        """
        Args:
            ocs_number: ocs id
            sw_name: 默认为all，更新全部未禁用的软件测试类型，不为all时，指定软件名更新测试类型
        Returns:
            返回sw_name对应的烧录相关信息
        """
        xpath = '//a[contains(@file_name,"' + sw_name + '")]/../../td[9]/a/@onclick'
        filterData = ['all', '', '']
        burn_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        burn_str = burn_list[0]
        p1 = re.compile(r'[(](.*?)[)]', re.S)
        burn_id_list = re.findall(p1, burn_str)
        burn_id = burn_id_list[0].replace('\'', '')
        return burn_id

    def set_ocs_burn_type(self, ocs_number, sw_name, burn_id, burn_type):
        """
        Args:
            ocs_number: ocs id
            sw_name: 默认为all，更新全部未禁用的软件测试类型，不为all时，指定软件名更新测试类型
            burn_type: 传入烧录方式(在线烧录，离线烧录)
        Returns:
            设置烧录方式，返回True或Fasle
        """
        pyocsSoftware = PyocsSoftware()
        burn_url = self._ocs_base_link + burn_id
        ret = pyocsSoftware.set_burn_type_for_ocs(ocs_number=ocs_number, sw_name=sw_name, burn_url=burn_url, burn_type=burn_type)
        return ret

    def update_ocs_customer_confirm(self, ocs_number, sw_name, confirm_type):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的客户确认状态
            sw_name: 默认为all，更新全部未禁用的软件客户确认状态，不为all时，指定软件名更新客户确认状态
            test_type: 传入测试类型(1-未确认, 3-口头确认, 4-邮件确认, 5-不需确认)
        Returns:
            返回True或Fasle
        """
        pyocsSoftware = PyocsSoftware()
        if sw_name == 'all':
            ret = self.set_ocs_customer_confirm_for_all(ocs_number=ocs_number, confirm_type=confirm_type)
        else:
            ret = pyocsSoftware.set_software_confirm_for_ocs(ocs_number=ocs_number, sw_name=sw_name, confirm_type=confirm_type)
        return ret

    def find_emmcbin_id(self, sw_name):
        """
        Args:
            sw_name: 通过软件名获取emmc bin
        Returns:
            返回EMMCBIN的id
        """
        pyocsSoftware = PyocsSoftware()
        sw_lists = pyocsSoftware.find_old_sw_id_by_name(old_sw_name=sw_name)
        for sw_list in sw_lists.items():
            fw__id = sw_list[0]
            fw_name = sw_list[1]
            if 'EMMCBIN' in fw_name:
                return fw__id
        return None

    def find_burn_bin_id(self, sw_name):
        """
        Args:
            sw_name: 通过软件名获取 flash 烧录 bin id
        Returns:
            返回EMMCBIN的id
        """
        pyocsSoftware = PyocsSoftware()
        sw_lists = pyocsSoftware.find_old_sw_id_by_name(old_sw_name=sw_name)
        for sw_list in sw_lists.items():
            fw__id = sw_list[0]
            fw_name = sw_list[1]
            if 'EMMCBIN' in fw_name or 'NANDBIN' in fw_name:
                return fw__id
        return None

    def get_max_test_type(self, test_list):
        return min(list(map(int, test_list)))

    def copy_emmcbin_only(self, ocs_number, sw_name):
        """
        拷贝对应软件名的emmc bin到指定的ocs
        Args:
            ocs_number: ocs id,操作指定的ocs
            sw_name: 传入软件名
        returns:
            返回TRUE/FALSE
        """
        pyocsSoftware = PyocsSoftware()
        emmc_id = self.find_emmcbin_id(sw_name)
        if emmc_id:
            burn_place_hold_type, burn_type = self.get_burn_place_hold(ocs_number)
            return pyocsSoftware.upload_old_sw_by_id(ocs_num=ocs_number, old_sw_id=emmc_id, burn_place_hold=burn_place_hold_type, 
                burn_type=burn_type, disable_origin_sw=False)
        return False

    def get_test_type(self, ocs_number):
        """
        Args:
            ocs_number: ocs id,主要是更新指定ocs的xml
        Returns:
            返回最大的测试类型
        """
        pyocsSoftware = PyocsSoftware()
        xpath = '//li[contains(@class, "change_fw_property") and contains(@select, "1") and contains(@rel, "test_type")]/@test_type'
        # xpath = '//li[contains(@class, "change_fw_property") and contains(@select, "1") and contains(@rel, "test_type")]/@test_type'
        filterData = ['all', '', '']
        test_list = self.get_update_ocs_xml_list(ocs_number, xpath, filterData)
        max_test_type = self.get_max_test_type(test_list)
        return self.get_key(pyocsSoftware.sw_test_type, str(max_test_type))

    def set_engineer(self, ocs_number, user):
        """指派给指定工程师
        Args:
            ocs_number: ocs号
            user: 中文输入工程师名字

        Returns:
            成功则返回为True
        """
        pyocsSoftware = PyocsSoftware()
        return pyocsSoftware.set_engineer(ocs_number=ocs_number, user=user)
