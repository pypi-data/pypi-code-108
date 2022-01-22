import logging
import datetime
from lxml import etree
import mimetypes
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs.pyocs_analysis import PyocsAnalysis
from pyocs.pyocs_request import PyocsRequest
from requests_toolbelt import MultipartEncoder
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_exception import *
from customers.customer_dg.dg_database import dgDataBase
import os
import re
import xlrd
import requests
import json
from pyocs import pyocs_login
from bs4 import BeautifulSoup
from customers.customer_common.common_database import commonDataBase
from pyocs import faas_api

"""
# @author:zhubowen3432
# @作用：OCS上的软件相关的功能
# @className：PyocsSoftware
"""


class PyocsSoftware:
    _instance = None
    _ocs_base_link = 'https://ocs-api.gz.cvte.cn'
    _search_url = _ocs_base_link + '/tv/Attachments/search_firmwares'
    _ocs_link_Prefix = _ocs_base_link + '/tv/Tasks/view/'
    _sample_ocs_link_Prefix = _ocs_base_link + '/tv/Tasks/sample_order_view/'
    _master_url = _ocs_base_link + "/tv/FirmwareAttachmentRelInfos/set_fw_is_master_json/"
    _auto_bin_url_prefix = _ocs_base_link + "/tv/Tasks/auto_sw_bin_json/"  # 410430/5c275e6d-987c-4b6f-a60a-1ab6ac11527a/NULL/NULL
    _upload_fw_url_prefix = _ocs_base_link + "/tv/pop/Tasks/upload_fw_attachment/"
    _update_xml_url_prefix = _ocs_base_link + "/tv/pop/Attachments/upload_xml/"
    find_cps_sw_link = _ocs_base_link + "/tv/pop/Attachments/search_cps_firmwares"

    _ocs_add_contact_link_url = _ocs_base_link + "/tv/UserPrefDatas/add_contact_json"
    _ocs_delete_contact_link_url = _ocs_base_link + "/tv/UserPrefDatas/delete_pref_user_contacts_json"
    _ocs_save_task_url = _ocs_base_link + "/tv/Tasks/save_task_date/"
    _ocs_change_status_url = '/tv/Tasks/change_status_json/'
    _ocs_confirm_url = _ocs_base_link + "/tv/Tasks/change_fw_property_json/"
    _ocs_comment_url = _ocs_base_link + "/tv/TaskComments/save_task_comment_json/"
    _ocs_comment_top_url = _ocs_base_link + "/tv/TaskComments/edit_task_comment_is_top_json"
    _ocs_cus_sw_request_remark_url = _ocs_base_link+"/tv/Tasks/save_cus_sw_request_remark_json/"
    _ocs_find_old_sw_url = _ocs_base_link + "/tv/pop/selectors/common_view/Controller:FirmwareAttachments/" \
                                            "Parameters:accountId/input_id:old_fw_id/input_name:old_fw_name/inputtype:1"
    sw_test_type = {'N': '100', 'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5', 'F': '6', 'G': '7', 'BC': '8'}
    sw_burn_type = {'在线烧录': '1', '离线烧录': '2'}
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    # 单例模式
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(PyocsSoftware, cls).__new__(cls, *args, **kw)
        return cls._instance

    class SoftwareDownloadlink:
        def __init__(self):
            self.name = ''  # 软件名
            self.download_link = ''  # 软件下载链接
            self.deadline = ''  # 链接截止日期

    class Software:
        def __init__(self):
            self.name = ''  # 软件名
            self.attachment_id = ''  # 软件attachment id
            self.fw_id = ''  # 软件fw_id

    # 无依赖OCS
    @staticmethod
    def is_burn_bin(sw_name):
        """
        检查是否是烧录bin
        :param sw_name:
        :return:
        """
        return "EMMCBIN" in sw_name or "NANDBIN" in sw_name

    # 无依赖OCS
    @staticmethod
    def is_cvte_spec_sw(sw_name):
        """
        检查是否符合CVTE软件命名规范
        :return:
        """
        return "CP" in sw_name or "CS" in sw_name

    def get_ocs_html(self, ocs_number):
        ocs_link = self._ocs_link_Prefix + ocs_number
        response = PyocsRequest().pyocs_request_get(ocs_link)
        html = etree.HTML(response.text)
        return html

    def get_ocs_from_board_code(self,product_code):
        search_form_data = dict()
        search_form_data['_method'] = 'POST'
        search_form_data['link_id'] = product_code
        search_response = PyocsRequest().pyocs_request_post(self._ocs_link_Prefix, data=search_form_data, allow_redirects=True)
        return search_response.url

    def get_bom_num_by_ocs(self,ocs_url):
        r = PyocsRequest().pyocs_request_get(ocs_url)
        html = etree.HTML(r.text)
        bom_num = html.xpath('//a[contains(@href, "/tv/Products/view/")]/parent::*/following-sibling::*[1]/text()')
        return bom_num

    # 无依赖OCS
    def get_refresh_software_download_link_by_sw_info(self, sw_info):
        """根据软件局部信息更新软件外网下载链接和链接更新日期
        Args:
            sw_info: 软件名、软件版本号、或者软件名中的部分信息
        Returns:
            返回软件刷新后的下载链接和下载链接有效期
        """
        sdl_list = list()
        sw_list = faas_api.refresh_software_link_by_sw_info(sw_info)
        if not sw_list:
            return None
        for sw in sw_list:
            sdl = self.SoftwareDownloadlink()
            sdl.download_link = sw['download_link']
            sdl.deadline = sw['deadline']
            sdl.name = sw['name']
            sdl_list.append(sdl)
        return sdl_list

    # 无依赖OCS
    def get_download_link_by_software_name(self, sw_name):
        """根据软件全名获取软件外网下载链接和链接更新日期
        Args:
            sw_name: 软件的全名
        Returns:
            返回软件下载链接和下载链接有效期
        """
        split_str = sw_name.split('_')
        if "CONFIG" in split_str:
            ocs_number = split_str[1].lstrip('CP').lstrip('CS')
        else:
            ocs_number = split_str[0].lstrip('CP').lstrip('CS')
        sdl = self.get_software_download_link(ocs_number=ocs_number, sw_name=sw_name)
        return sdl

    def get_my_ocs_order(self):
        order_list = list()
        ocs_url = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:my/'
        r = PyocsRequest().pyocs_request_get(ocs_url)
        html = etree.HTML(r.text)
        ocs_list = html.xpath('//td[@class="Task_col_id"]')
        for i in range(len(ocs_list)):
            order_list.append(ocs_list[i].text)

        return order_list

    # 无依赖OCS
    def get_download_link_by_ocs(self, ocs_number, exclude_bin=True, use_cache=True):
        """根据软件OCS订单号,获取软件外网下载链接和链接有效期
        Args:
            ocs_number: OCS订单号
            use_cache: 使用redis缓存
        Returns:
            返回软件下载链接和下载链接有效期
        """
        sw_download_link_list = list()
        sw_list = faas_api.get_software_list(ocs_number=ocs_number, exclude_disable=False, exclude_bin=exclude_bin, use_cache=use_cache)
        if not sw_list:
            return sw_download_link_list
        for sw in sw_list:
            sdl = self.SoftwareDownloadlink()
            sdl.download_link = sw["external_link"]["link"]
            sdl.deadline = sw["external_link"]["expiration"]
            sdl.name = sw["name"]
            sw_download_link_list.append(sdl)
        return sw_download_link_list

    # 无依赖OCS
    def get_software_download_link(self, ocs_number, sw_name, exclude_bin=True, use_cache=True):
        """根据软件全名获取软件外网下载链接和链接更新日期
        Args:
            ocs_number:订单号
            sw_name: 软件的全名
            use_cache: 使用redis缓存
        Returns:
            返回软件下载链接和下载链接有效期
        """
        sdl_list = self.get_download_link_by_ocs(ocs_number=ocs_number, exclude_bin=exclude_bin, use_cache=use_cache)
        for sdl in sdl_list:
            if sw_name == sdl.name:
                return sdl
        return None

    def get_en_sw_list_from_html(self, html):
        """获取订单上的启用状态下的软件列表，包含被锁定的软件
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的软件列表
        """
        enable_software_list = []
        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)
        self._logger.info("启用状态的软件:" + str(enable_software_name_list))
        for sw_name in enable_software_name_list:
            enable_software_list.append(sw_name)
        if enable_software_list:
            return enable_software_list
        else:
            return None

    def get_enable_software_list_from_html(self, html, exclude_lock_sw = True):
        """获取订单上的启用状态下的软件列表
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的软件列表
        """
        enable_software_list = []
        # enable_software_name_xpath = '//strong[text()="同时停用以下软件包"]/../../..//input[@type="checkbox"]/..//label/text()'  # '//a[@title="停用软件"]/@file_name'
        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)
        self._logger.info("启用状态的软件:" + str(enable_software_name_list))
        if not exclude_lock_sw and enable_software_name_list:
            return enable_software_name_list
        for sw_name in enable_software_name_list:
            if not self.is_sw_locked(sw_name=sw_name, html=html):
                enable_software_list.append(sw_name)
        if enable_software_list:
            return enable_software_list
        else:
            return None

    def get_enable_software_info_from_html(self, html, exclude_bin=True):
        """获取订单上的启用状态下的软件以及对应的信息字典
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的非烧录 bin 或者不符合 CVTE 规范的软件以及对应的信息字典
        """
        active_software_name_list = []
        active_software_info_list = []

        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)

        self._logger.info("启用状态的软件:" + str(enable_software_name_list))

        for sw_name in enable_software_name_list:
            if not self.is_sw_locked(sw_name=sw_name, html=html):
                if exclude_bin and self.is_burn_bin(sw_name=sw_name):
                    continue
                if exclude_bin and not self.is_cvte_spec_sw(sw_name=sw_name):
                    continue
                enable_software_info_list = html.xpath('//*[text()=$val]/../following-sibling::td[5]/text()', val=str(sw_name))
                sw_info = ','.join(enable_software_info_list)
                active_software_name_list.append(sw_name)
                active_software_info_list.append(sw_info)

        enable_software_dict = dict(zip(active_software_name_list, active_software_info_list))
        return enable_software_dict

    def get_enable_software_test_type_with_ocs(self, ocs, exclude_bin=True):
        """获取订单上的启用状态下的软件以及对应的信息字典
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的非烧录 bin 或者不符合 CVTE 规范的软件以及对应的信息字典
        """
        active_software_info_list = []

        src_ocs_link = self._ocs_link_Prefix + ocs
        response = PyocsRequest().pyocs_request_get(src_ocs_link)
        html = etree.HTML(response.text)
        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)

        self._logger.info("启用状态的软件:" + str(enable_software_name_list))

        for sw_name in enable_software_name_list:
            if not self.is_sw_locked(sw_name=sw_name, html=html):
                if exclude_bin and self.is_burn_bin(sw_name=sw_name):
                    continue
                if exclude_bin and not self.is_cvte_spec_sw(sw_name=sw_name):
                    continue
                enable_software_info_list = html.xpath('//*[text()=$val]/../following-sibling::td[@class="firmware_status"]/span/text()', val=str(sw_name))
                sw_info = ','.join(enable_software_info_list)
                active_software_info_list.append(sw_info)

        if active_software_info_list:
            enable_software_test_type = active_software_info_list[0]
            return enable_software_test_type
        else:
            return None

    def get_enable_software_test_status_with_ocs(self, ocs, exclude_bin=True):
        """获取订单上的启用状态下的软件以及对应的信息字典
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的非烧录 bin 或者不符合 CVTE 规范的软件以及对应的信息字典
        """
        active_software_info_list = []

        src_ocs_link = self._ocs_link_Prefix + ocs
        response = PyocsRequest().pyocs_request_get(src_ocs_link)
        html = etree.HTML(response.text)
        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)

        self._logger.info("启用状态的软件:" + str(enable_software_name_list))

        for sw_name in enable_software_name_list:
            if not self.is_sw_locked(sw_name=sw_name, html=html):
                if exclude_bin and self.is_burn_bin(sw_name=sw_name):
                    continue
                if exclude_bin and not self.is_cvte_spec_sw(sw_name=sw_name):
                    continue
                enable_software_info_list = html.xpath('//*[text()=$val]/../following-sibling::td[@class="firmware_status"]/span/text()', val=str(sw_name))
                sw_info = ','.join(enable_software_info_list)
                active_software_info_list.append(sw_info)

        if active_software_info_list:
            enable_software_test_status = active_software_info_list[0]
            return enable_software_test_status
        else:
            return None

    def get_enable_software_reuse_ocs_with_ocs(self, ocs, exclude_bin=True):
        """获取订单上的启用状态下的软件以及对应的信息字典
        Args:
            html: 某个ocs订单的html页面
        Returns:
            启用状态下的非烧录 bin 或者不符合 CVTE 规范的软件以及对应的信息字典
        """
        active_software_info_list = []

        src_ocs_link = self._ocs_link_Prefix + ocs
        response = PyocsRequest().pyocs_request_get(src_ocs_link)
        html = etree.HTML(response.text)
        enable_software_name_xpath = \
            '//a[contains(@href, "/tv/Attachments/download_attachment")]/text()'
        enable_software_name_list = html.xpath(enable_software_name_xpath)

        self._logger.info("启用状态的软件:" + str(enable_software_name_list))

        for sw_name in enable_software_name_list:
            if not self.is_sw_locked(sw_name=sw_name, html=html):
                if exclude_bin and self.is_burn_bin(sw_name=sw_name):
                    continue
                if exclude_bin and not self.is_cvte_spec_sw(sw_name=sw_name):
                    continue
                enable_software_info_list = html.xpath('//*[text()=$val]/..//strong[@class="label"]/text()', val=str(sw_name)) + html.xpath('//*[text()=$val]/..//strong/a/text()', val=str(sw_name))
                sw_info = ','.join(enable_software_info_list)
                active_software_info_list.append(sw_info)

        enable_reuse_software_info = active_software_info_list[0]
        enable_reuse_ocs_list = re.findall(r'\d+', enable_reuse_software_info)
        return enable_reuse_ocs_list

    @staticmethod
    def is_sw_locked(sw_name, html):
        tmp_xpath = '//strong[text()="软件包"]/../../..//a[text()="' + sw_name + '"]/../a[@data-locktype="LOCK"]/i/@class'
        tmp_list = html.xpath(tmp_xpath)
        is_locked = True if 'icon-eye-close' in tmp_list else False
        return is_locked

    def get_enable_software_attachment_id_from_html_by_sw_name(self, html, sw_name):
        """获取订单上的特定启用状态下软件的attachment_id，非启用状态的软件，返回为空
        Args:
            html: 某个ocs订单的html页面
            sw_name: 需要获取attachment_id的软件名（软件全名）
        Returns:
            软件的attachment id，没有找到则返回为空
        """
        attachment_id_xpath = '//a[text()="' + sw_name + '"]/@href'
        attachment_id_str_list = html.xpath(attachment_id_xpath)
        self._logger.info("attachment_id_str_list:" + str(attachment_id_str_list))
        if attachment_id_str_list:
            attachment_id_split_list = attachment_id_str_list[0].split('/')
            attachment_id = attachment_id_split_list[-1]
            self._logger.info("attachment id:" + attachment_id)
            return attachment_id
        else:
            return None

    def get_enable_software_test_type_from_by_sw_name(self, ocs, sw_name):
        """获取订单上的特定启用状态下软件的测试状态，非启用状态的软件，返回为空
        Args:
            ocs: 订单ocs号
            sw_name: 需要获取attachment_id的软件名（软件全名）
        Returns:
            软件的测试状态，没有找到则返回为空
        """
        ocs_link = self._ocs_link_Prefix + ocs
        response = PyocsRequest().pyocs_request_get(ocs_link)
        html = etree.HTML(response.text)
        test_type_xpath = '//a[text()="' + sw_name + '"]/@href/../../../td[7]/text()'
        test_type_str_list = html.xpath(test_type_xpath)
        self._logger.info("test_type_str_list:" + str(test_type_str_list))

        if test_type_str_list:
            test_type_split_list = test_type_str_list[0].split('/')
            test_type = test_type_split_list[-1]
            self._logger.info("attachment id:" + test_type)
            return test_type
        else:
            return None

    def get_enable_software_attachment_id_from_html_by_fuzzy_sw_name(self, html, sw_name):
        """获取订单上的特定启用状态下软件的attachment_id，非启用状态的软件，返回为空
        Args:
            html: 某个ocs订单的html页面
            sw_name: 需要获取attachment_id的软件名（使用模糊匹配的方式，可以不包含OTA等前缀）
        Returns:
            软件的attachment id，没有找到则返回为空
        """
        attachment_id_xpath = '//a[contains(text(),"' + sw_name + '")]/@href'
        attachment_id_str_list = html.xpath(attachment_id_xpath)
        self._logger.info("attachment_id_str_list:" + str(attachment_id_str_list))
        if attachment_id_str_list:
            attachment_id_split_list = attachment_id_str_list[0].split('/')
            attachment_id = attachment_id_split_list[-1]
            self._logger.info("attachment id:" + attachment_id)
            return attachment_id
        else:
            return None

    def get_enable_software_fw_id_from_html_by_sw_name(self, html, sw_name):
        """获取订单上的特定启用状态下软件的fw_id，非启用状态的软件，返回为空
        Args:
            html: 某个ocs订单的html页面
            sw_name: 需要获取fw id的软件名（软件全名）
        Returns:
            软件的fw id，没有找到则返回为空
        """
        fw_id_xpath = '//a[text()="' + sw_name + '"]/../span/text()'
        fw_id_str_list = html.xpath(fw_id_xpath)
        if fw_id_str_list:
            fw_id = fw_id_str_list[0].strip()
            self._logger.info("fw_id:" + fw_id)
            return fw_id
        else:
            return None

    # 无依赖OCS
    @PyocsAnalysis.print_run_time
    def get_enable_software_list(self, ocs_number, exclude_bin=True, exclude_lock_sw=True):
        """
        获取订单中启用状态下的软件列表，以Software对象列表返回
        """
        sw_list = list()
        s_list = faas_api.get_software_list(ocs_number=ocs_number, exclude_bin=exclude_bin,
                                            exclude_lock=exclude_lock_sw)
        if not s_list:
            return None
        for s in s_list:
            sw = self.Software()
            sw.name = s['name']
            sw.attachment_id = s['attachment_id']
            sw.fw_id = s['fw_id']
            sw_list.append(sw)
        self._logger.info("软件名和attchment id的字典 ：" + str(sw_list))
        return sw_list

    # 无依赖OCS
    @PyocsAnalysis.print_run_time
    def get_sw_lock_status(self, ocs_number, build_time):
        ret = faas_api.get_software_list(ocs_number=ocs_number, exclude_bin=False, exclude_lock=False,
                                         exclude_disable=False)
        if not ret:
            return "no_found"
        for sw in ret:
            if build_time in sw['name']:
                if not sw['is_lock']:
                    return "unlock"
                else:
                    return "lock"
        return "no_found"

    # 无依赖OCS
    @PyocsAnalysis.print_run_time
    def get_sample_enable_software_list(self, ocs_number, exclude_bin=True):
        """
        获取样品订单中启用状态下的软件列表，以Software对象列表返回
        """
        sw_list = self.get_enable_software_list(ocs_number=ocs_number, exclude_bin=exclude_bin, exclude_lock_sw=False)
        if sw_list:
            return sw_list
        else:
            return None

    @PyocsAnalysis.print_run_time
    def set_master_sw(self, fw_id):
        """根据fw_id，设置主程序，常用于做bin
        """
        self._logger.info('fw_id：' + str(fw_id))
        data = {
            'data[fw_id]': int(fw_id),
            'data[action]': 'master',
            'data[is_master]': 1
        }
        ret = PyocsRequest().pyocs_request_post(self._master_url, data=data)
        self._logger.info(ret.text)
        ret_dict = ret.json()
        self._logger.info(ret_dict['success'])
        if ret_dict['success'] is True:
            return True
        else:
            return False

    def auto_make_bin(self, ocs_number, attachment_id):
        _auto_bin_url = self._auto_bin_url_prefix + ocs_number + '/' + attachment_id
        response = PyocsRequest().pyocs_request_post(_auto_bin_url, data=None)
        ret_dict = response.json()
        self._logger.info(ret_dict['success'])
        if ret_dict['success'] is True:
            return True
        else:
            return False

    def auto_make_bin_by_sw_name(self, sw_name: str):
        ocs_number_str = re.search("C[PS][0-9]*", sw_name).group(0).lstrip('CP').lstrip('CS')
        ocs_link = self._ocs_link_Prefix + ocs_number_str
        response = PyocsRequest().pyocs_request_get(ocs_link)
        html = etree.HTML(response.text)
        sw_attachment_id = self.get_enable_software_attachment_id_from_html_by_sw_name(html, sw_name)
        sw_fw_id = self.get_enable_software_fw_id_from_html_by_sw_name(html, sw_name)
        self.set_master_sw(sw_fw_id)
        return self.auto_make_bin(ocs_number_str, sw_attachment_id)

    def set_master_sw_by_ocs_and_sw_name(self, ocs_number, sw_name: str):
        ret = ""
        data_list = faas_api.get_software_list(ocs_number=ocs_number)
        for d in data_list:
            if d["name"] == sw_name:
                ret = self.set_master_sw(d["fw_id"])
        return ret

    def add_comment_to_ocs(self, ocs_number, message):

        strlist = message.split('\n')
        comment = ""
        for value in strlist:
            comment = comment + '<p style="margin: 2px;">' + value + "</p>"

        data = {
            'task_id': int(ocs_number),
            'comment': comment,
            'comment_text': str(message),
            'parent_id': 0,
            'url': " "
        }

        ret = PyocsRequest().pyocs_request_post(self._ocs_comment_url, data=data)
        self._logger.info("ocs 备注message：" + comment)
        return ret

    def _set_comment_top(self, commit_id):

        data = {
            'comment_id': commit_id,
            'is_comment_top': 'true'
        }

        ret = PyocsRequest().pyocs_request_post(self._ocs_comment_top_url, data=data)

        if(ret.status_code == 200):
            return True
        else:
            return False

    def _add_cus_sw_request_remark(self, ocs_number, message):
        """
        # 编辑ocs页面的"客户需求备注"信息
        """
        data = {
            'TaskId': int(ocs_number),
            'CusSwRequestRemark': str(message)
        }

        ret = PyocsRequest().pyocs_request_post(self._ocs_cus_sw_request_remark_url, data=data)

        if(ret.status_code == 200):
            return True
        else:
            return False
    """
       # 根据订单号特性转换
    """

    def order_info_transfer(slef, order_info):
        # 可能出现在摘要中的订单号 X19026 X-19026 X219026 X2-19026
        order_info_list = [order_info]
        order_sign = "-"
        order_type = order_info[:-5]
        order_number = order_info[-5:]
        order_info_list.append(order_type + order_sign + order_number)  # CHAOYE X-19026形式
        return order_info_list

    """
    # 根据sw_name和order_info，获取对应OCS号
    """

    @PyocsAnalysis.print_run_time
    def get_ocs_number_from_sw(self, sw_name, order_info):
        ocs_number = str()
        search_form_data = dict()
        search_form_data['_method'] = 'POST'
        search_form_data['AttachmentName'] = sw_name
        search_response = PyocsRequest().pyocs_request_post(self._search_url, data=search_form_data)
        html = etree.HTML(search_response.text)
        str_ocs_number_xpath = '//strong[@class="label"]/text()'
        ocs_number_list = html.xpath(str_ocs_number_xpath)
        order_info_list = self.order_info_transfer(order_info)
        for ocs_number_index in set(ocs_number_list):
            tmp_ocs_number = ocs_number_index.strip("#")
            str_ocs_abstract_xpath = '//a[contains(@href,"/tv/Tasks/view/' + tmp_ocs_number + '")]/text()'
            ocs_abstract_info = html.xpath(str_ocs_abstract_xpath)
            for order_info_index in order_info_list:
                if order_info_index in str(ocs_abstract_info):
                    ocs_number = tmp_ocs_number
        if ocs_number:
            return ocs_number
        else:
            self._logger.info("ocs_number not found")

    def get_flash_burn_hold_place_from_ocs(self, ocs):
        ddr_info_str = PyocsDemand(ocs).get_ddr_info()
        ddr_info_dict = eval(ddr_info_str)
        burn_place_hold_nums = ddr_info_str.count('refDec')
        burn_place_hold_dst = ' '
        for i in range(0, burn_place_hold_nums):
            if i == 0:
                refDec = 'refDec'
                categoryDescp = 'categoryDescp'
            else:
                refDec = 'refDec' + str(i)
                categoryDescp = 'categoryDescp' + str(i)
            flash_list = ['EMMC FLASH', 'NAND FLASH', 'NOR FLASH']
            if ddr_info_dict[categoryDescp] in flash_list:
                burn_place_hold_dst = ddr_info_dict[refDec]
                break
        return burn_place_hold_dst

    def reuse_old_sw_from_src_to_dst(self, src_ocs, dst_ocs, workspace):
        """
        引用库存软件，如果此单上已经引用了同名的库存软件，则不做引用
        :param src_ocs:
        :param dst_ocs:
        :return:
        """
        reuse_sw_name_list = faas_api.copy_software(src=src_ocs, dst=dst_ocs)
        if not reuse_sw_name_list:
            return True
        pd = PyocsDemand(ocs_number=dst_ocs)
        customer = pd.get_ocs_customer()
        engineer = pd.get_ocs_software_engineer()
        project = pd.get_ocs_project_name()
        if customer in ["TCL海外", "TCL王牌", "深圳TCL新技术"] and self.is_dg_software(pd=pd):
            db = dgDataBase()
            if engineer == "赵壮洪":
                download_link = db.get_download_link_of_tcl_dt_by_engineer(engineer + project)
            else:
                download_link = db.get_download_link_of_tcl_dt_by_engineer(engineer)
            if not download_link:
                return
            excel_file_location = PyocsFileSystem.get_file_from_nut_driver(url=download_link, workspace=workspace)
            for sw_name in reuse_sw_name_list:
                self.upload_tcl_special_excel(ocs_num=dst_ocs, sw_name=sw_name,
                                              excel_file_location=excel_file_location, pd=pd)
                if ("TCL王牌" in customer or "TCL海外" in customer) and "赵壮洪" not in engineer:
                    self.set_software_confirm_for_ocs(ocs_number=dst_ocs, sw_name=sw_name)
            if ("TCL王牌" in customer or "TCL海外" in customer) and "赵壮洪" not in engineer:
                self.comment_tcl_software_info(excel_file_location=excel_file_location,
                                               customer_batch=pd.get_customer_batch_code(), ocs_number=dst_ocs)

    def is_dg_software(self, pd: PyocsDemand):
        product_name_prefix = pd.get_product_name().split(".")[0]
        if "D" in product_name_prefix:
            return True
        return False

    def comment_tcl_software_info(self, excel_file_location, customer_batch, ocs_number):
        workbook = xlrd.open_workbook(filename=excel_file_location)
        table = workbook.sheet_by_index(0)
        batch_code_list = table.col_values(0)
        row_index = None
        row_numbers = table.nrows
        for index, col_value in enumerate(reversed(batch_code_list)):
            if col_value.strip() == customer_batch:
                row_index = row_numbers - index - 1
                break
        html_table = '<table border="1">'
        header = '<tr>'
        message = '<tr>'
        for index, info in enumerate(table.row_values(row_index)):
            if info:
                header += '<td>' + table.cell(0, index).value + '</td>'
                info_str = str(int(info)) if type(info) == float else str(info)
                message += '<td>' + info_str + '</td>'
        message += '</tr>'
        header += '</tr>'
        html_table += header + message + '</table>'
        # print(html_table)
        self.add_comment_to_ocs(ocs_number=ocs_number, message=html_table)

    def upload_tcl_special_excel(self, ocs_num, sw_name, excel_file_location, pd: PyocsDemand):
        headers = dict()
        compare_url = 'http://ocs-api.gz.cvte.cn/tv/pop/Tasks/compare_request/' + ocs_num + '/'
        html = pd.get_ocs_html()
        fw_id = self.get_enable_software_fw_id_from_html_by_sw_name(html=html, sw_name=sw_name)
        attachment_id = self.get_enable_software_attachment_id_from_html_by_sw_name(html=html, sw_name=sw_name)
        print(attachment_id)
        compare_url += attachment_id
        upload_url = 'http://ocs-api.gz.cvte.cn/Attachments/upload_attachment_json/63/' + \
                     fw_id + "/230/xmlexcel"
        headers.update({
            'Referer': compare_url
        })
        files = {'attach_file': ("tcl_xml_excel.xls", open(excel_file_location, 'rb'),
                                 '%s' % self.get_content_type(excel_file_location))}
        ret = PyocsRequest().pyocs_request_post_file(upload_url, file=files, header=headers)
        if ret.json()['success']:
            return True
        else:
            raise ReviewExcelError("异常信息：" + ret.json()['message'])

    @staticmethod
    def get_content_type(filepath):
        return mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

    def set_software_confirm(self, sw_name, order_info, confirm_type=4):
        """
        # 根据sw_name和order_info，确认软件
        """
        ocs_number = self.get_ocs_number_from_sw(sw_name, order_info)
        if ocs_number is None:
            pass
        else:
            sw_list = self.get_enable_software_list(ocs_number=ocs_number,exclude_bin=False)

            if sw_list is None:
                return None
            else:
                for sw in sw_list:
                    fw_id = sw.fw_id
                    data = {
                        'task_id': int(ocs_number),
                        'field': "account_firmware_status",
                        'firmware_id': int(fw_id),
                        'data': confirm_type,
                        'confirm_reason': 1,
                        'first_confirm_reason': str(ocs_number),
                        'second_confirm_reason': str(sw_name)
                    }
                    ret = PyocsRequest().pyocs_request_post(self._ocs_confirm_url, data=data)
                confirm_result = ret.text
                self._logger.info(confirm_result)
                if int(confirm_result) > 0:
                    return True
                else:
                    self._logger.info("confirm failed")

    def set_software_confirm_for_ocs(self, ocs_number: str, sw_name: str, confirm_type=4):
        """
            确认软件
        :param ocs_number:
        :param sw_name:
        :param confirm_type: 1-未确认，3-口头确认，(default)4-邮件确认，5-不需确认
        :return:
        """
        html = self.get_ocs_html(ocs_number=ocs_number)
        fw_id = self.get_enable_software_fw_id_from_html_by_sw_name(html=html, sw_name=sw_name)
        data = {
            'task_id': int(ocs_number),
            'field': "account_firmware_status",
            'firmware_id': int(fw_id),
            'data': confirm_type,
            'confirm_reason': 1,
            'first_confirm_reason': str(ocs_number),
            'second_confirm_reason': str(sw_name)
        }
        ret = PyocsRequest().pyocs_request_post(self._ocs_confirm_url, data=data)
        return ret.status_code == 200

    def set_enable_software_confirm_for_ocs(self, ocs_number: str, sw_name: str, confirm_type=4):
        """
            通过ocs和软件时间。让软件+烧录bin能够一起确认
        :param ocs_number:
        :param sw_name:
        :param confirm_type: 1-未确认，3-口头确认，(default)4-邮件确认，5-不需确认
        :return:
        """
        sw_list = self.get_enable_software_list(ocs_number=ocs_number, exclude_bin=False)
        if sw_list is None:
            return None
        else:
            for sw in sw_list:
                fw_id = sw.fw_id
                print("fw_id = "+fw_id)
                data = {
                    'task_id': int(ocs_number),
                    'field': "account_firmware_status",
                    'firmware_id': int(fw_id),
                    'data': confirm_type,
                    'confirm_reason': 1,
                    'first_confirm_reason': str(ocs_number),
                    'second_confirm_reason': str(sw_name)
                }
                ret = PyocsRequest().pyocs_request_post(self._ocs_confirm_url, data=data)
            return ret.text

    def set_ocs_status(self, ocs_number: str, status_type=20):
        """
            修改OCS订单状态
        :param ocs_number:
        :param status_type: 10-待录入需求 20-待上传软件 30-软件待审核 40-软件审核不通过
        ：                  50-软件待测试 60-软件测试不通过 70-待发放 80-已完成
        :return:
        """
        _ocs_status_url = self._ocs_base_link + self._ocs_change_status_url + ocs_number + '/' + str(status_type)
        data = {}
        ret = PyocsRequest().pyocs_request_post(_ocs_status_url, data=data)
        return ret.status_code == 200

    def set_test_type_for_ocs(self, ocs_number: str, sw_name: str, test_type: str):
        """
            设置OCS软件的测试类型
        :param ocs_number: ocs id
        :param sw_name: 软件名
        :param test_type: N,A,B,C,D,E,F,G,BC
        :return:true/false
        """
        html = self.get_ocs_html(ocs_number=ocs_number)
        fw_id = self.get_enable_software_fw_id_from_html_by_sw_name(html=html, sw_name=sw_name)
        test = self.sw_test_type[test_type]
        data = {
            'task_id': int(ocs_number),
            'firmware_id': int(fw_id),
            'field': "test_type",
            'data': test,
        }
        ret = PyocsRequest().pyocs_request_post(self._ocs_confirm_url, data=data)
        return ret.status_code == 200

    def set_burn_type_for_ocs(self, ocs_number: str, sw_name: str, burn_url: str, burn_type: str):
        """
            设置OCS软件的烧录方式
        :param ocs_number: ocs id
        :param sw_name: 软件名
        :param burn_type: 在线烧录，离线烧录
        :return:true/false
        """
        src_ocs_link = self._ocs_link_Prefix + ocs_number
        response = PyocsRequest().pyocs_request_get(src_ocs_link)
        html = etree.HTML(response.text)
        sw_dict = self.get_enable_software_info_from_html(html, exclude_bin=False)
        burn_info = sw_dict[sw_name]

        if burn_info:
            burn_place_hold = burn_info.split(",")[0]

        data = {
            'data[burn_place_hold][]': '',
            'data[burn_place_hold][]': burn_place_hold,
            'data[burn_type]': burn_type,
        }
        ret = PyocsRequest().pyocs_request_post(burn_url, data=data)
        return ret.status_code == 200

    def get_test_type_from_ocs(self, ocs_number: str):
        """
            获取OCS软件的测试类型
        :param ocs_number:
        :return:test type str
        """
        test_type_xpath = '//*[@id="current_test_type_text"]/text()'
        html = self.get_ocs_html(ocs_number=ocs_number)
        test_type_list = html.xpath(test_type_xpath)
        self._logger.info(test_type_list)
        if len(test_type_list) < 1:
            return None
        else:
            test_type_str = str(test_type_list[0]).replace(" ", "").replace("\n", "").replace("\r", "")
            return test_type_str

    def get_test_burn_from_ocs(self, ocs_number: str):
        """
            获取OCS软件的测试类型
        :param ocs_number:
        :return:test type str
        """
        test_type_xpath = '//*[@id="current_test_type_text"]/text()'
        html = self.get_ocs_html(ocs_number=ocs_number)
        test_type_list = html.xpath(test_type_xpath)
        self._logger.info(test_type_list)
        if len(test_type_list) < 1:
            return None
        else:
            test_type_str = str(test_type_list[0]).replace(" ", "").replace("\n", "").replace("\r", "")
            return test_type_str

    def get_test_level_from_ocs(self, ocs_number: str):
        """
            获取OCS软件的当前测试级别
        :param ocs_number:
        :return:test level str
        """
        test_level_xpath = '//*[@id="current_test_level_text"]/text()'
        html = self.get_ocs_html(ocs_number=ocs_number)
        test_level_list = html.xpath(test_level_xpath)
        self._logger.info(test_level_list)
        if len(test_level_list) < 1:
            return None
        else:
            test_level_str = str(test_level_list[0]).replace(" ", "").replace("\n", "").replace("\r", "")
            return test_level_str

    def get_enable_sw_audit_link(self, ocs_number: str):
        """
            获取OCS里使能软件自动审核不通过的审核页链接
        :param ocs_number:
        :return:test type str
        """
        #audit_link_xpath = '//a[@title="自动审核失败" or @title="自动审核通过" ]/./@onclick'
        #audit_link_xpath = '//a[@title="自动审核失败"]/./@onclick'
        audit_link_xpath = '//a[@title="停用软件"]/../a[@title="自动审核失败"]/./@onclick'
        html = self.get_ocs_html(ocs_number=ocs_number)
        tmp_link = html.xpath(audit_link_xpath)
        if len(tmp_link) < 1:
            return None
        else:
            link_str = str(tmp_link).split(",")[0].split("'")[-2].rstrip("\\")
            return link_str

    def get_self_audit_msg(self, audit_link_str: str):
        """
            获取OCS软件审核页的不匹配信息
        :param audit_link_str:
        :return:self audit not pass msg
        """
        audit_pass_xpath = '//tr[@class="row_impoarant class_ab_row " \
                            or @class="row_impoarant class_ab_row row_compare-diff"]/th/text()'
        if audit_link_str is None:
            return None
        else:
            audit_link = self._ocs_base_link + audit_link_str
            self._logger.info(audit_link)
            response = PyocsRequest().pyocs_request_get(audit_link)
            html = etree.HTML(response.text)
            audit_msg_ret = html.xpath(audit_pass_xpath)
            return audit_msg_ret

    def find_old_sw_id_by_name(self, old_sw_name):
        """根据 old_sw_name 查找库存软件 old_sw_id
        Args:
            old_sw_name: 软件名
        Returns:
            查找到的软件字典
        """
        old_sw_dict = dict()
        self._logger.info(old_sw_name)
        data = {
            'data[autocomplete]': str(old_sw_name)
        }
        search_response = PyocsRequest().pyocs_request_post(self._ocs_find_old_sw_url, data=data, allow_redirects=True)
        soup = BeautifulSoup(search_response.text, 'html.parser')
        items = soup.find_all('tr', class_='tr_select')
        for i in items:
            tag1 = i.find('td', class_='FirmwareAttachment_col_id')
            old_sw_id_str = tag1.text
            tag2 = i.find('td', class_='FirmwareAttachment_col_attachment_id MainField')
            sw_name = tag2.text
            old_sw_dict[old_sw_id_str] = sw_name
        self._logger.info("ocs 库存软件查找：" + str(old_sw_dict))
        return old_sw_dict

    def upload_old_sw_by_id(self, ocs_num, old_sw_id, burn_place_hold, burn_type, disable_origin_sw=True):
        """根据ocs_num 和old_sw_name， 上传库存软件
        """
        fields = {'data[fw_Attach][file][]': '(binary)',
                  'data[fw_Attach][old_fw_id][]': str(old_sw_id),
                  'data[fw_Attach][ab_sw_name][]': '',
                  'data[fw_Attach][ab_sw_id][]': '',
                  'data[fw_Attach][ab_xml_name][]': '',
                  'data[fw_Attach][ab_xml_id][]': '',
                  'data[fw_Attach][autobuild_bill_no][]': '',
                  'data[fw_Attach][fileXML][]': '(binary)',
                  'data[fw_Attach][test_type][]': "100",  # 默认不用测试
                  'data[fw_Attach][fw_cfm_type]': '',
                  'data[fw_Attach][soft_remark]': '',
                  'data[fw_Attach][burn_place_hold][]': burn_place_hold,
                  'data[fw_Attach][burn_type]': burn_type,
                  'data[fw_Attach][function_description]': '',
                  'data[fw_Attach][result_of_modified]': '',
                  'data[fw_Attach][note][]': "引用库存软件",
                  'data[change_task_status]': 'on'
                  }
        if disable_origin_sw:
            sw_list = self.get_enable_software_list(ocs_number=ocs_num, exclude_bin=False)
            if sw_list:
                for sw in sw_list:
                    fields.update({'data[fw_Attach][fileList][' + sw.attachment_id + ']': 'on'})
        ret = PyocsRequest().pyocs_request_post(self._upload_fw_url_prefix + str(ocs_num), data=fields)
        return ret.status_code == 200

    def upload_cps_sw_by_id(self, ocs_num, cps_sw_name, cps_sw_id, cps_xml_name, cps_xml_id, build_id,  burn_place_hold, burn_type, disable_origin_sw, Test_type):
        """根据ocs_num 和cps_sw_name， 上传库存软件
                    test_type:
                0 未知
                1 A类 - 全面测试
                2 B类 - 针对遥控器的测试
                3 C类 - 局部修改针对性测试
                4 D类 - 测配屏
                5 E类 - 首测，无任何功能及BUG的修改
                6 F类 - 过硬件首测，只要求匹配硬件
                7 G类 - 仅测试BOOT
                8 B+C - 新遥控器测试，局部功能修改/添加
                100 不用测试
        """
        test_type_dict = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'BC': 8, 'N': 100}
        fields = {'data[fw_Attach][file][]': '(binary)',
                  'data[fw_Attach][old_fw_id][]':'' ,
                  'data[fw_Attach][ab_sw_name][]': str(cps_sw_name),
                  'data[fw_Attach][ab_sw_id][]': str(cps_sw_id),
                  'data[fw_Attach][ab_xml_name][]': str(cps_xml_name),
                  'data[fw_Attach][ab_xml_id][]': str(cps_xml_id),
                  'data[fw_Attach][autobuild_bill_no][]': str(build_id),
                  'data[fw_Attach][fileXML][]': '(binary)',
                  'data[fw_Attach][test_type][]': str(test_type_dict[Test_type]),
                  'data[fw_Attach][fw_cfm_type]': '',
                  'data[fw_Attach][soft_remark]': '',
                  'data[fw_Attach][burn_place_hold][]': burn_place_hold,
                  'data[fw_Attach][burn_type]': burn_type,
                  'data[fw_Attach][function_description]': '',
                  'data[fw_Attach][result_of_modified]': '',
                  'data[fw_Attach][note][]': "引用CPS软件",
                  'data[change_task_status]': 'on'
                  }
        if disable_origin_sw:
            sw_list = self.get_enable_software_list(ocs_number=ocs_num, exclude_bin=False, exclude_lock_sw=False)
            if sw_list:
                for sw in sw_list:
                    fields.update({'data[fw_Attach][fileList][' + sw.attachment_id + ']': 'on'})
        ret = PyocsRequest().pyocs_request_post(self._upload_fw_url_prefix + str(ocs_num), data=fields)
        return ret.status_code == 200

    def find_cps_id_by_name(self, cps_sw_name):
        fields = {
            '_method': 'POST',
            'AttachmentName':str(cps_sw_name)
        }
        result = list()
        xml_id_list = list()
        xml_name_list = list()
        response = PyocsRequest().pyocs_request_post(self.find_cps_sw_link, data=fields)
        html = etree.HTML(response.text)
        build_id_list = html.xpath('//div[@class="clearfix"]//input[@class="mark"]/@value')
        sw_id_list = html.xpath('//div[@class="clearfix"]//input/@attachment_id')
        sw_name_list = html.xpath('//div[@class="clearfix"]//a/@modal_title')
        result.append(sw_name_list)
        result.append(sw_id_list)

        for i in range(len(build_id_list)):
            xml_fileds = {
                'AutoBuildBillBo': str(build_id_list[i]),
                'AttachmentId': str(sw_id_list[i])
            }
            response = PyocsRequest().pyocs_request_post("http://ocs-api.gz.cvte.cn/tv/Tasks/get_autobuild_sw_info_json/", data=xml_fileds)
            response_dict = json.loads(response.text)
            xml_id_list.append(response_dict["datas"]["xml_id"])
            xml_name_list.append(response_dict["datas"]["xml_name"])

        result.append(xml_name_list)
        result.append(xml_id_list)
        result.append(build_id_list)
        return result

    def upload_software_to_ocs(self, ocs_num, zip_path, xml_path, test_type, burn_place_hold, burn_type, message: str, disable_origin_sw=True):
        """根据ocs_num 和sw_path， 上传软件
        Args:
            ocs_num: 订单号
            zip_path: 软件包地址
            xml_path: xml地址
            test_type:
                0 未知
                1 A类 - 全面测试
                2 B类 - 针对遥控器的测试
                3 C类 - 局部修改针对性测试
                4 D类 - 测配屏
                5 E类 - 首测，无任何功能及BUG的修改
                6 F类 - 过硬件首测，只要求匹配硬件
                7 G类 - 仅测试BOOT
                8 B+C - 新遥控器测试，局部功能修改/添加
                100 不用测试
            burn_place_hold: 选项从OCS订单自动获取
            burn_type:
                1 在线烧录
                2 离线烧录
            message: 上传软件备注

        Returns:
            成功则返回为True
        """
        headers = dict()
        data_fields = dict()
        test_type_set = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '100'}
        if test_type not in test_type_set:
            return False

        encoded_sw_name = 'sw_name'  # 此举是为了解决中文的问题，MultipartEncoder 存在中文方面的BUG
        encoded_xml_name = 'xml_name'
        data_fields.update({
            'data[fw_Attach][file][]': (encoded_sw_name,
                                        open(zip_path, 'rb'), self.get_content_type(zip_path)),
            'data[fw_Attach][old_fw_id][]': '',
            'data[fw_Attach][ab_sw_name][]': '',
            'data[fw_Attach][ab_sw_id][]': '',
            'data[fw_Attach][ab_xml_name][]': '',
            'data[fw_Attach][ab_xml_id][]': '',
            'data[fw_Attach][autobuild_bill_no][]': '',
            'data[fw_Attach][fileXML][]': (encoded_xml_name,
                                           open(xml_path, 'rb'), self.get_content_type(xml_path)),
            'data[fw_Attach][test_type][]': test_type,
            'data[fw_Attach][fw_cfm_type]': '0',
            'data[fw_Attach][soft_remark]': '',
            'data[fw_Attach][burn_place_hold][]': burn_place_hold,
            'data[fw_Attach][burn_type]': burn_type,
            'data[fw_Attach][function_description]': '',
            'data[fw_Attach][result_of_modified]': '',
            'data[fw_Attach][note][]': message,
            'data[change_task_status]': 'on'
        }
        )
        if disable_origin_sw:  # 停用/不停用
            sw_list = self.get_enable_software_list(ocs_number=ocs_num, exclude_bin=False)
            if sw_list:
                for sw in sw_list:
                    data_fields.update({'data[fw_Attach][fileList][' + sw.attachment_id + ']': 'on'})

        data = MultipartEncoder(
            fields=data_fields
        )
        data_str = data.to_string()
        data_str = data_str.replace(encoded_sw_name.encode('utf-8'), os.path.basename(zip_path).encode('utf-8'))
        data_str = data_str.replace(encoded_xml_name.encode('utf-8'), os.path.basename(xml_path).encode('utf-8'))
        headers.update({
            'Referer': self._upload_fw_url_prefix + ocs_num
        })
        headers['Content-Type'] = data.content_type
        self._logger.info(headers)
        ret = PyocsRequest().pyocs_request_post_with_headers(self._upload_fw_url_prefix + ocs_num,
                                                             data=data_str, headers=headers)
        self._logger.info(ret.text)
        return ret.status_code == 200

    def upload_attachments_to_ocs(self, ocs_num, file_path):
        """根据ocs_num 和 file_path， 上传附件文件
        Args:
            ocs_num: OCS id
            file_path: 附件路径

        Returns:
            成功则返回为True
        """
        headers = dict()
        data_fields = dict()

        encoded_sw_name = 'sw_name'  # 此举是为了解决中文的问题，MultipartEncoder 存在中文方面的BUG
        data_fields.update({
            'data[Attach][file][]': (encoded_sw_name,
                                     open(file_path, 'rb'), self.get_content_type(file_path))
        }
        )

        data = MultipartEncoder(
            fields=data_fields
        )
        data_str = data.to_string()
        data_str = data_str.replace(encoded_sw_name.encode('utf-8'), os.path.basename(file_path).encode('utf-8'))
        headers.update({
            'Referer': self._ocs_link_Prefix + ocs_num
        })
        headers['Content-Type'] = data.content_type
        self._logger.info(headers)
        ret = PyocsRequest().pyocs_request_post_with_headers(self._ocs_link_Prefix + ocs_num,
                                                             data=data_str, headers=headers)
        self._logger.info(ret.text)
        return ret.status_code == 200


    def upload_xml_to_ocs(self, xml_update_url, xml_path):
        """根据ocs_num 和sw_path， 上传软件
        Args:
            xml_update_url: xml的url路径
            xml_path: xml地址

        Returns:
            成功则返回为True
        """
        headers = dict()
        data_fields = dict()

        encoded_xml_name = 'xml_name'
        data_fields.update({
            'data[fileXML]': (encoded_xml_name,
                                           open(xml_path, 'rb'), self.get_content_type(xml_path)),
            'data[delete_reason]': '0',
        }
        )

        data = MultipartEncoder(
            fields=data_fields
        )
        data_str = data.to_string()
        data_str = data_str.replace(encoded_xml_name.encode('utf-8'), os.path.basename(xml_path).encode('utf-8'))
        headers.update({
            'Referer': self._update_xml_url_prefix + xml_update_url,
        })
        headers['Content-Type'] = data.content_type
        self._logger.info(headers)
        ret = PyocsRequest().pyocs_request_post_with_headers(self._update_xml_url_prefix + xml_update_url,
                                                             data=data_str, headers=headers)
        self._logger.info(ret.text)
        return ret.status_code == 200

    def set_engineer(self, ocs_number, user):
        """指派给指定工程师
        Args:
            ocs_number: ocs号
            user: 中文输入工程师名字

        Returns:
            成功则返回为True
        """
        pd = PyocsDemand(ocs_number=ocs_number)
        cur_engineer = pd.get_ocs_software_engineer()
        if cur_engineer != user:
            headers = dict()
            headers.update({
                'Referer': self._ocs_link_Prefix + 'range:all/' + ocs_number,
                })
            self._logger.info('ocs_number : ' + ocs_number +'  set engineer : ' + user)
            ret = PyocsRequest().pyocs_request_post_with_headers(self._ocs_save_task_url + ocs_number + '/Task.sw_user_id/' + user,
                                                                 data='', headers=headers)
            self._logger.info(ret.text)
            return ret.text == '1'
        return True

    def set_sw_audit_user(self, ocs_number, user):
        """指派给订单软件审核人员
        Args:
            ocs_number: ocs号
            user: 中文输入工程师名字

        Returns:
            成功则返回为True
        """
        pd = PyocsDemand(ocs_number=ocs_number)
        cur_engineer = pd.get_ocs_software_engineer()
        if cur_engineer != user:
            headers = dict()
            headers.update({
                'Referer': self._ocs_link_Prefix + 'range:all/' + ocs_number,
                })
            self._logger.info('ocs_number : ' + ocs_number +'  set reviewer : ' + user)
            ret = PyocsRequest().pyocs_request_post_with_headers(self._ocs_save_task_url + ocs_number + '/Task.sw_audit_user_id/' + user,
                                                                 data='', headers=headers)
            self._logger.info(ret.text)
            return ret.text == '1'
        return True

    def comment_factory_test_info(self, ocs_num: str, message: str):
        factory_test_url_pre = "http://ocs-api.gz.cvte.cn/Tasks/add_task_test_remark/"
        factory_test_url = factory_test_url_pre + ocs_num
        message_list = message.split(";")
        data_fields = dict()
        for idx, mess in enumerate(message_list):
            data_fields.update({'data[TestRemark' + str(idx + 1) + ']': mess})
        # print(data_fields)
        ret = PyocsRequest().pyocs_request_post(factory_test_url, data=data_fields)
        return ret.status_code == 302

    def get_audit_failed_link(self, ocs, sw_name):
        # html = self.get_ocs_html(ocs_number=ocs)
        pd = PyocsDemand(ocs)
        html = pd.html
        is_audit_failed = pd.is_audit_failed(sw_name)
        compare_url = 'http://ocs-api.gz.cvte.cn/tv/pop/Tasks/compare_request/' + ocs + '/'
        if is_audit_failed:
            attachment_id = self.get_enable_software_attachment_id_from_html_by_fuzzy_sw_name(html, sw_name)
            link = compare_url + attachment_id
            return link
        else:
            return None

    def set_software_customer_chaoye_needs_to_ocs(self, customer_name, order_info, customer_bom, board_type, customer_needs):
        #order_info：M-19117
        #customer_bom：17B5-S520-SC86E56A
        #board_type：TP.MT5510S.PB803
        #1、通过以上信息高级搜索获得ocs号
        #ocs_number = self.get_ocs_number_from_sw(sw_name, order_info)
        #2、通过OCS号将制定的客户需求str = customer_needs 填写到ocs评论区

        # 1、通过以上信息高级搜索 获取高级搜索的searchID
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        advanced_search = {
            "0":{
                "search_field_name":"Task.account_id",
                "search_field_id":"560",
                "search_field_type":"19",
                "search_field_rel_obj":"Accounts",
                "search_opr":"TDD_OPER_INC",
                "input1":customer_name+"", #客户
                "input2":'null',
                "offset":'null'
            },
             "1":{
                 "search_field_name": "Task.subject",
                 "search_field_id": "554",
                 "search_field_type": "5",
                 "search_field_rel_obj": "null",
                 "search_opr": "TDD_OPER_INC",
                 "input1": board_type + "",  # 板型
                 "input2": 'null',
                 "offset": 'null'
                },
            "2":{
                "search_field_name":"Task.subject",
                "search_field_id":"554",
                "search_field_type":"5",
                "search_field_rel_obj":"null",
                "search_opr":"TDD_OPER_INC",
                "input1":order_info+"", #客户订单
                "input2":'null',
                "offset":'null'
            },
            "3":{
                "search_field_name":"Task.subject",
                "search_field_id":"554",
                "search_field_type":"5",
                "search_field_rel_obj":"null",
                "search_opr":"TDD_OPER_INC",
                "input1":customer_bom+"", #客户料号
                "input2":'null',
                "offset":'null'
            }
        } 
        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': '1 and 2 and 3 and 4',
            'unknownModel': '9'
        }
        # 2、通过SearchID 获取对应订单的ocs号
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        ordurl = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:'+ret.text
        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        ocslist = html.xpath('//td[@class="Task_col_id"]')
        if ocslist:
            ocsnum = ocslist[0].text
            #print(ocsnum)
            # 3、通过ocs号将customer needs 特殊需求备注在ocs评论区
            # 解析customer_needs
            needlist = customer_needs.split('@')
            language = needlist[0]
            logo = needlist[1]
            specialneed = needlist[2]

            html_table = '<table border="1">'
            header = '<tr>'
            message = '<tr>'

            header += '<td colspan="6" height=30 bgcolor="#F5DEB3" align="center">' + '朝野客户'+order_info+'订单特殊需求--如果一个订单有多个不同需求需和工程师确认' + '</td>'
            message += '<td>' + language + '</td>'
            message += '</tr>'
            message += '<tr>'
            message += '<td>' + logo + '</td>'
            message += '</tr>'
            message += '<tr>'
            message += '<td>' + specialneed + '</td>'
            message += '</tr>'
            message += '</tr>'
            header += '</tr>'
            html_table += header + message + '</table>'
            # print(html_table)
            self.add_comment_to_ocs(ocs_number=ocsnum, message=html_table)

            # print(ocs_num[0])

            infotext = "success:"+order_info+"   "+board_type+"   OCS = "+ocsnum+"\n"
        else:
            infotext = "error  :"+order_info+"   "+board_type+"   "+customer_bom+"  无法查到对应ocs，请确认料号板卡是否正确!\n"
        return infotext
		
    def get_ocs_number_from_customer_order(self, customer_name, customer_order):
        '''OCS高级搜索
        从摘要搜索得到一个OCS号列表'''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        ocs_list = list()
        status_list = list()
        advanced_search = {
            "0": {
                "search_field_name": "Task.account_id",
                "search_field_id": "560",
                "search_field_type": "19",
                "search_field_rel_obj": "Accounts",
                "search_opr": "TDD_OPER_INC",
                "input1": customer_name + "",  # 客户
                "input2": 'null',
                "offset": 'null'
            },
            "1": {
                "search_field_name": "Task.rel_obj_id.rel_obj_id.account_bno",
                "search_field_id": "4289",
                "search_field_type": "5",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_INC",
                "input1": customer_order,  # 客户批号
                "input2": 'null',
                "offset": 'null'
            }
        }

        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': '1 and 2',
            'unknownModel': '9'
        }
        # 2、通过SearchID 获取对应订单的ocs号
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        ordurl = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:' + ret.text

        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        original_ocs_list = html.xpath('//td[@class="Task_col_id"]')
        original_status_list = html.xpath('//td[@class="Task_col_status"]')

        for ocs in original_ocs_list:
            ocs_list.append(ocs.text)

        for status in original_status_list:
            status_list.append(status.text)

        return status_list,ocs_list

    def get_ocs_number_from_customer_name_bom(self, customer_name, customer_bom):
        '''OCS高级搜索
        从摘要搜索得到一个OCS号列表'''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        ocs_list = list()
        status_list = list()
        advanced_search = {
            "0": {
                "search_field_name": "Task.account_id",
                "search_field_id": "560",
                "search_field_type": "19",
                "search_field_rel_obj": "Accounts",
                "search_opr": "TDD_OPER_INC",
                "input1": customer_name + "",  # 客户
                "input2": 'null',
                "offset": 'null'
            },
            "2":{
                "search_field_name":"Task.subject",
                "search_field_id":"554",
                "search_field_type":"5",
                "search_field_rel_obj":"null",
                "search_opr":"TDD_OPER_INC",
                "input1":customer_bom+"", #摘要的方式去搜索客户料号
                "input2":'null',
                "offset":'null'
            }
        }

        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': '1 and 2',
            'unknownModel': '9'
        }
        # 2、通过SearchID 获取对应订单的ocs号
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        ordurl = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:' + ret.text

        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        original_ocs_list = html.xpath('//td[@class="Task_col_id"]')

        for ocs in original_ocs_list:
            ocs_list.append(ocs.text)

        return ocs_list

    def get_searchid_from_advanced_search(self, advanced_search, condition):
        '''OCS高级搜索
        从摘要搜索得到一个OCS号列表'''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'

        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': condition,
            'unknownModel': '9'
        }
        # 2、通过SearchID 获取对应订单的ocs号
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        return ret.text

    def get_sample_searchid_from_advanced_search(self, advanced_search, condition):
        "样品单OCS高级搜索从摘要搜索得到一个OCS号列表"
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'

        form_data = {
            'controller': 'Reqs',
            'data': json.dumps(advanced_search),
            'srch_textarea': condition,
            'unknownModel': '103'
        }
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        return ret.text

    def get_ocs_number_from_abstract(self, abstract):
        '''OCS高级搜索
        从摘要搜索得到一个OCS号列表'''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        ocs_list = list()
        advanced_search = {
            "0": {
                "search_field_name": "Task.subject",
                "search_field_id": "554",
                "search_field_type": "5",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_INC",
                "input1": abstract + "",  # 客户
                "input2": 'null',
                "offset": 'null'
            }
        }
        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': '',
            'unknownModel': '9'
        }
        # 2、通过SearchID 获取对应订单的ocs号
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        ordurl = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:' + ret.text
        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        original_ocs_list = html.xpath('//td[@class="Task_col_id"]')
        for ocs in original_ocs_list:
            ocs_list.append(ocs.text)
        return ocs_list

    def get_chinese_name_from_account(self,account_name):
        '''
        通过用户账号，获取用户中文名称
        '''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        advanced_search = {
            "0":{
                "search_field_name":"User.email",
                "search_field_id":"48",
                "search_field_type":"15",
                "search_field_rel_obj":"null",
                "search_opr":"TDD_OPER_INC",
                "input1":account_name,
                "input2":'null',
                "offset":'null'
                }
        }

        form_data = {
            'controller': 'Users',
            'data': json.dumps(advanced_search),
            'srch_textarea': ''
        }

        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        url_part1 = 'http://ocs-api.gz.cvte.cn/tv/pop/selectors/common_view/Controller:Users/Parameters:biz_id=1&alias=all&type=Task.sw_user_id&SearchId='
        url_part2 = '/input_id:input_2/input_name:input_2/inputtype:1'
        ordurl = url_part1 + ret.text + url_part2

        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        tmp_text = html.xpath('//td[@class="User_col_realname  MainField"]/text()')
        user_chinese_name = tmp_text[0] if tmp_text else ''

        return user_chinese_name

    def get_user_id_from_account(self,account_name):
        '''
        通过用户账号，获取用户OCS 账号的id
        '''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        advanced_search = {
            "0":{
                "search_field_name":"User.email",
                "search_field_id":"48",
                "search_field_type":"15",
                "search_field_rel_obj":"null",
                "search_opr":"TDD_OPER_INC",
                "input1":account_name,
                "input2":'null',
                "offset":'null'
                }
        }

        form_data = {
            'controller': 'Users',
            'data': json.dumps(advanced_search),
            'srch_textarea': ''
        }

        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        url_part1 = 'http://ocs-api.gz.cvte.cn/tv/pop/selectors/common_view/Controller:Users/Parameters:biz_id=1&alias=all&type=Task.sw_user_id&SearchId='
        url_part2 = '/input_id:input_2/input_name:input_2/inputtype:1'
        ordurl = url_part1 + ret.text + url_part2

        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        tmp_text = html.xpath('//td[@class="User_col_id  "]/text()')
        user_id = tmp_text[0] if tmp_text else ''

        return user_id

    def get_overdue_21d_older(self):
        '''OCS高级搜索
        从摘要搜索得到一个OCS号列表'''
        searchurl = 'http://ocs-api.gz.cvte.cn/tv/Searches/advance_search_json/'
        order_info = {
            'ocs_id':'',
            'update_time':''
        }
        order_list = list()
        user_account = pyocs_login.PyocsLogin().get_account_from_json_file()['Username']
        user_chinese_name = self.get_chinese_name_from_account(user_account)

        advanced_search = {
            "0": {
                "search_field_name": "Task.status",
                "search_field_id": "584",
                "search_field_type": "19",
                "search_field_rel_obj": "Enums",
                "search_opr": "TDD_OPER_LE",
                "input1": "已完成",
                "input2": 'null',
                "offset": 'null'
            },
            "1": {
                "search_field_name": "Task.sw_user_id",
                "search_field_id": "555",
                "search_field_type": "19",
                "search_field_rel_obj": "Users",
                "search_opr": "TDD_OPER_INC",
                "input1": user_chinese_name,
                "input2": 'null',
                "offset": 'null'
            },
            "2": {
                "search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status",
                "search_field_id": "1637",
                "search_field_type": "19",
                "search_field_rel_obj": "Enums",
                "search_opr": "TDD_OPER_EQUAL",
                "input1": "已代测发放",
                "input2": 'null',
                "offset": 'null'
            },
            "3": {
                "search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status",
                "search_field_id": "1637",
                "search_field_type": "19",
                "search_field_rel_obj": "Enums",
                "search_opr": "TDD_OPER_EQUAL",
                "input1": "已最终发放",
                "input2": 'null',
                "offset": 'null'
            },
            "4": {
                "search_field_name": "Task.plan_end_date",
                "search_field_id": "548",
                "search_field_type": "9",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_RECENT",
                "input1": "18",#超期X天，这里默认设置为18天，宁愿多捞点订单出来梳理，也不要少捞
                "input2": 'null',
                "offset": "TDD_OFFSET_DAY"
            },
            "5": {
                "search_field_name": "Task.plan_end_date",
                "search_field_id": "548",
                "search_field_type": "9",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_FUTURE",
                "input1": "1000",
                "input2": 'null',
                "offset": "TDD_OFFSET_DAY"
            },
            "6": {
                "search_field_name": "Task.subject",
                "search_field_id": "554",
                "search_field_type": "5",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_INC",
                "input1": "虚拟",
                "input2": 'null',
                "offset": 'null'
            },
            "7": {
                "search_field_name": "Task.rel_obj_id.create_time",
                "search_field_id": "1226",
                "search_field_type": "10",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_RECENT",
                "input1": "20",
                "input2": 'null',
                "offset": "TDD_OFFSET_DAY"
            },
            "8": {
                "search_field_name": "Task.rel_obj_id.create_time",
                "search_field_id": "1226",
                "search_field_type": "10",
                "search_field_rel_obj": "null",
                "search_opr": "TDD_OPER_FUTURE",
                "input1": "1000",
                "input2": 'null',
                "offset": "TDD_OFFSET_DAY"
            }
        }
        form_data = {
            'controller': 'Tasks',
            'data': json.dumps(advanced_search),
            'srch_textarea': '1 and 2 and (((3 or 4) and (not 5 and not 6)) or (7 and not 8 and not 9))',
            'unknownModel': '9'
        }
        p = PyocsRequest()
        ret = p.pyocs_request_post(searchurl, data=form_data)
        self._logger.info(ret.text)

        ordurl = 'http://ocs-api.gz.cvte.cn/tv/Tasks/index/range:all/SearchId:' + ret.text
        r = p.pyocs_request_get(ordurl)
        html = etree.HTML(r.text)
        original_ocs_list = html.xpath('//td[@class="Task_col_id"]')
        original_ocs_update_time_list = html.xpath('//td[@class="Task_col_update_time"]')
        for i in range(len(original_ocs_list)):
            order_info['ocs_id']=original_ocs_list[i].text
            order_info['update_time']=original_ocs_update_time_list[i].text
            order_list.append(order_info.copy())

        return order_list

    def get_overdue_7d_older(self,time_day):
        order_list = self.get_overdue_21d_older()
        ret = list()
        for order_dict in order_list:
            order_update_time = order_dict['update_time'].split(' ')[0]
            y = datetime.datetime.strptime(order_update_time, '%Y-%m-%d')
            z = datetime.datetime.now()
            diff = (z - y).days
            if diff >= int(time_day):
                ret.append(order_dict['ocs_id'])
        return ret


    def get_software_file_from_ocs(self, ocs_number, workspace: str):
        """根据软件链接获取软件包
        Args:
            ocs_number: 订单号
            workspace : 软件包存放地址
        Returns:
            file_location: 文件存放地址
        """
        result_list = self.get_download_link_by_ocs(ocs_number)
        print("result_list: ", result_list)
        if len(result_list) == 0:
            print("无可用软件信息,请确认当前订单是否软件被锁定")
        for result in result_list:
            sw_name = result.name
            sw_download_link_str = result.download_link
            sw_download_link = sw_download_link_str.split(' ')[0]
            ret = requests.get(sw_download_link)
            file_location = os.path.join(workspace, sw_name)
            with open(file_location, 'wb') as f:
                for chunk in ret.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        return file_location

    def get_email_addr_from_ocs(self, name):
        """根据名字从OCS获取邮件地址
        Args:
            name: 名字,str类型
        Returns:
            email_addr: 邮箱地址，str类型
        """
        data = {
            'item_id': int(3),
            'contact_name': str(name),
            'pref_def_id': int(2)
        }
        response = PyocsRequest().pyocs_request_post(self._ocs_add_contact_link_url, data=data)
        response_dict = json.loads(response.text) #将获取的内容转换成字典
        if response_dict['retValue'] == -1: #不存在该名字
            print("======="+name+" 名称不存在,请确认输入是否正确"+"=======")
        elif response_dict['retValue'] == 0: #名字已经重复
            None #有无痕查找机制暂不需对重复进行处理
        else:
            pref_id = response_dict['user_pref_data_id'] #记录本次添加的pref_id用于擦除
            email_addr = response_dict['pref_user_email'] #获取的email_addr
            #擦除本次的添加查找记录
            data = {
                'pref_data_id': int(pref_id)
            }
            response = PyocsRequest().pyocs_request_post(self._ocs_delete_contact_link_url,data)
            if "1" not in response.text:
                print("擦除失败")
            return email_addr

    def get_enable_sw_release_state(self, ocs_number: str):
        """
            获取OCS里使能软件自动审核不通过的审核页链接
            :param ocs_number:
            :return:test type str
        """
        html = self.get_ocs_html(ocs_number=ocs_number)
        state_xpath = '//span[contains(text(), "已发放")]/../../preceding-sibling::tr[1]/td[2]/a/@title'
        state_list = html.xpath(state_xpath)
        if state_list:
            if "停用软件" in state_list:
                return True
            else:
                return False
        else:
            return False

    def get_enable_sw_release_info(self, ocs_number: str):
        """
            获取OCS里使能软件自动审核不通过的审核页链接
            :param ocs_number:
            :return:test type str
        """
        html = self.get_ocs_html(ocs_number=ocs_number)
        state_xpath = '//span[contains(text(), "已发放")]/../text()'
        state_info = html.xpath(state_xpath)
        return state_info

    def get_sw_release_stock_state(self, ocs_number: str):
        """
            获取OCS里使能软件自动审核不通过的审核页链接
            :param ocs_number:
            :return:test type str
        """
        html = self.get_ocs_html(ocs_number=ocs_number)
        release_test_xpath = '//span[contains(text(), "已发放")]/../../preceding-sibling::tr[1]/td[7]/text()'
        release_test_list = html.xpath(release_test_xpath)
        if "不用测试" in release_test_list:
            return "库存"
        else:
            return "首发"

    def get_sw_release_stock_state_name(self, ocs_number: str, xpath_id):
        """
            获取OCS里使能软件自动审核不通过的审核页链接
            :param ocs_number:
            :return:test type str
        """
        sw_name = ''
        html = self.get_ocs_html(ocs_number=ocs_number)
        release_sw_list = html.xpath(xpath_id)
        if release_sw_list:
            sw_name = release_sw_list[0]
        return sw_name

    def get_all_ocs_number_from_sw(self, sw_name):
        ocs_number = str()
        search_form_data = dict()
        search_form_data['_method'] = 'POST'
        search_form_data['AttachmentName'] = sw_name
        search_response = PyocsRequest().pyocs_request_post(self._search_url, data=search_form_data)
        html = etree.HTML(search_response.text)
        str_ocs_number_xpath = '//strong[@class="label"]/text()'
        ocs_number_list = html.xpath(str_ocs_number_xpath)
        ocs_number_array = []
        for ocs_number_index in set(ocs_number_list):
            ocs_number = ocs_number_index.strip("#")
            ocs_number_array.append(ocs_number)
        return ocs_number_array

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
        searchid = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def report_mac_address_for_gaia(self, tag: int, mac: str):
        """GAIA mac地址报备
        Args:
            tag: GAIA TYPE
            mac: mac地址

        Returns:
            成功则返回为执行结果
        """
        user = os.environ['USER']
        mac_report_url = "http://tvweb.cvtapi.com/tvweb-rest/api/v1/busbase/tag/update"
        headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/son'
        }
        data_dict = {
            'tagId': tag,
            'macAddr': mac,
            'crtUser': user,
        }
        ret = PyocsRequest().pyocs_request_post_with_headers(mac_report_url, headers=headers, data=str(data_dict))
        ret_dict = json.loads(ret.text)
        return ret_dict

    def reuse_old_sw_for_boe(self, ocs, workspace):
        """
        根据待上传OCS上的客料号，从BOE出海信软件确认表中找到已确认的软件包名，并上传。
        """
        pd = PyocsDemand(ocs_number=ocs)
        customer_info = pd.get_ocs_customer()
        passenger_number = pd.get_passenger_number()
        passenger_number = passenger_number.strip()
        print("OCS订单上的客料号：" + passenger_number)

        db = commonDataBase()
        download_link = db.get_download_link_software_confirm_table_by_customer(customer_info)
        excel_file_location = PyocsFileSystem.get_file_from_nut_driver(url=download_link, workspace=workspace)

        #从Excel表中由OCS上的客料号获取到客户确认的软件名称
        workbook = xlrd.open_workbook(filename=excel_file_location)
        table = workbook.sheet_by_index(0)
        board_type_list = table.col_values(0) #料号在确认表中的第0列
        sw_name_column = 1 #客户确认的软件名在表中的第1列
        customer_confirm_sw_name = None
        for index in range(len(board_type_list)):
            board_type_name = board_type_list[index].strip()
            if passenger_number in board_type_name:
                customer_confirm_sw_name = table.cell_value(index, sw_name_column)
                break

        #用客户确认的软件包名在OCS中查找已使用的OCS，并上传到目标OCS上
        if customer_confirm_sw_name:
            customer_confirm_sw_name = customer_confirm_sw_name.strip()
            print("客户已确认的软件包: " + customer_confirm_sw_name)
            search_form_data = dict()
            search_form_data['_method'] = 'POST'
            search_form_data['AttachmentName'] = customer_confirm_sw_name
            search_response = PyocsRequest().pyocs_request_post(self._search_url, data=search_form_data)
            html = etree.HTML(search_response.text)
            sw_used_ocs_list = html.xpath('//td/strong/text()')
            if sw_used_ocs_list != [] :
                sw_used_ocs = sw_used_ocs_list[0].strip("#")
                self.reuse_old_sw_from_src_to_dst(sw_used_ocs, ocs, workspace)
        else:
            raise NoConfirmSoftwareError("确认表中没有找到客户确认的软件！")
