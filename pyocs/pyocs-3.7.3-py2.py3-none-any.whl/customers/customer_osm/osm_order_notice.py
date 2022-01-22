import logging
from pyocs import pyocs_demand
from pyocs import pyocs_software
from pyocs import pyocs_searchid
from pyocs import pyocs_email
from pyocs import pyocs_request
from lxml import etree
import platform
import os

"""
# @author: chenfan3714
# @作用：多版软件只是部分软件包需要提交测试的订单，订单状态会显示不用测试，生产测试不能及时发现这部分订单，需要系统提醒给到生产测试
# @className: OsmOrderNotice
"""


class OsmOrderNotice:
    """多版本软件OCS订单异常设置提醒"""
    _logger = logging.getLogger(__name__)
    _ocs_id_base_link = 'https://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/'
    mul_ver_sender = 'chenfan3714@cvte.com'
    mul_ver_receivers = "luoshimei@cvte.com"
    mul_ver_cc = 'xiaoyao3553@cvte.com'
    mul_ver_subject = '多版本软件测试类型异常订单'

    sw_lock_sender = 'chenfan3714@cvte.com'
    sw_lock_cc = 'luchengfan@cvte.com'
    sw_lock_subject = 'TCON订单禁用软件提醒'

    mul_uploader_sender = 'chenfan3714@cvte.com'
    mul_uploader_receivers = 'luchengfan@cvte.com'
    mul_uploader_cc = 'xiaoyao3553@cvte.com'
    mul_uploader_subject = '多人协同订单邮件提醒-成帆处理软件-OSM更改项目组'

    def __init__(self):
        workspace = '/'
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            self.workspace = home_dir + workspace
            self._logger.info("linux环境")
        else:
            self.workspace = workspace
            self._logger.info("windows环境")

    def send_mail_for_ocs_with_mul_ver(self, searchid):
        ocs_notice_list = list()
        mail = pyocs_email.PyocsEmail()
        sw = pyocs_software.PyocsSoftware()
        # 获取当前 search id 过滤器的订单列表 ocs list
        si = pyocs_searchid.PyocsSearchid(searchid)
        ocs_list = si.get_ocs_id_list_info()
        ocs_number = si.get_searchid_ocs_number()
        if 0 == ocs_number:
            return
        for ocs in ocs_list:
            sw_list = sw.get_enable_software_list(ocs, exclude_bin=0)
            if sw_list:
                if len(sw_list) > 1:
                    for sw_id in sw_list:
                        test_type = sw.get_enable_software_test_type_from_by_sw_name(ocs, sw_id.name)
                        if test_type != "不用测试":
                            ocs_notice_list.append(ocs)
                            break
            else:
                continue
        if len(ocs_notice_list) >= 1:
            ocs_link_notice_list = [self._ocs_id_base_link + ocs_id for ocs_id in ocs_notice_list]
            content = "测试类型异常订单超链接：\n" + "\r\n".join(ocs_link_notice_list)
            mail.send_email(self.mul_ver_sender, self.mul_ver_receivers, self.mul_ver_cc, self.mul_ver_subject, content)

    def send_mail_for_ocs_with_sw_lock(self, searchid):
        ocs_notice_list = list()
        mail = pyocs_email.PyocsEmail()
        ps = pyocs_software.PyocsSoftware()
        pr = pyocs_request.PyocsRequest()
        # 获取当前 search id 过滤器的订单列表 ocs list
        si = pyocs_searchid.PyocsSearchid(searchid)
        ocs_list = si.get_ocs_id_list_info()
        ocs_number = si.get_searchid_ocs_number()
        if 0 == ocs_number:
            return
        for ocs in ocs_list:
            src_ocs_link = 'https://ocs-api.gz.cvte.cn/tv/Tasks/view/' + ocs
            res = pr.pyocs_request_get(src_ocs_link)
            html = etree.HTML(res.text)
            enable_software_name_list = ps.get_en_sw_list_from_html(html)
            if enable_software_name_list:
                for sw_name in enable_software_name_list:
                    lock_status = ps.is_sw_locked(sw_name=sw_name, html=html)
                    if lock_status:
                        ocs_request = pyocs_demand.PyocsDemand(ocs)
                        sw_engineer = ocs_request.get_ocs_software_engineer()
                        sw_lock_receivers = ps.get_email_addr_from_ocs(sw_engineer)
                        content = "以下订单全部禁用，请及时处理：\n" + self._ocs_id_base_link + ocs
                        mail.send_email(self.sw_lock_sender, sw_lock_receivers, self.sw_lock_cc, self.sw_lock_subject, content)
                        break

    def send_mail_for_ocs_with_mul_uploader(self, searchid):
        ocs_notice_list = list()
        mail = pyocs_email.PyocsEmail()
        sw = pyocs_software.PyocsSoftware()
        # 获取当前 search id 过滤器的订单列表 ocs list
        si = pyocs_searchid.PyocsSearchid(searchid)
        ocs_list = si.get_ocs_id_list_info()
        ocs_number = si.get_searchid_ocs_number()
        if 0 == ocs_number:
            return
        for ocs in ocs_list:
            ocs_notice_list.append(ocs)
        if len(ocs_notice_list) >= 1:
            ocs_link_notice_list = [self._ocs_id_base_link + ocs_id for ocs_id in ocs_notice_list]
            content = "多人协同处理订单链接：\n" + "\r\n".join(ocs_link_notice_list)
            mail.send_email(self.mul_uploader_sender, self.mul_uploader_receivers, self.mul_uploader_cc, self.mul_uploader_subject, content)
