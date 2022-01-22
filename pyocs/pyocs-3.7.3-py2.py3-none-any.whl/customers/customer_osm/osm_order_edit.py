import logging
from pyocs import pyocs_edit
from pyocs import pyocs_software
from pyocs import pyocs_searchid
from pyocs import pyocs_demand
from pyocs import pyocs_email
from pyocs import pyocs_confluence
from pyocs.pyocs_filesystem import PyocsFileSystem
from pathlib import Path
import platform
import os
import json
import xlrd
import time
import datetime
from dateutil.relativedelta import relativedelta
from customers.customer_common.common_database import commonDataBase
"""
# @author: chenfan3714
# @作用：FAE在设置订单烧录方式时经常出错，此脚本用来定期检测并自动校正
# @className: OsmOrderEdit
"""


class OsmOrderEdit:
    """校正OSM订单烧录方式"""
    _logger = logging.getLogger(__name__)
    _ocs_id_base_link = 'https://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/'
    sender = 'chenfan3714@cvte.com'
    cc = 'xiaoyao3553@cvte.com,lilimin@cvte.com,moyuanyuan@cvte.com,keyafen@cvte.com,hesiting@cvte.com,likeyu@cvte.com'

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
        self.file_path = self.workspace + '/osm_order_edit_searchid_date.json'

    def read_searchid_date_as_dict(self):
        file = Path(self.file_path)
        # 如果文件不存在，下载文件
        if file.exists() is False:
            db = commonDataBase()
            map_list = db.get_osm_distribute_mapping_info_by_user("osm_order_edit_searchid_date")
            download_link = map_list[0]
            file_location = PyocsFileSystem.get_file_from_nut_driver(download_link, self.workspace)
        with open(file, 'r', encoding='utf8')as fp:
            date_dict = json.load(fp)
        return date_dict

    def write_searchid_date_to_json(self, add_dict):
        file = Path(self.file_path)
        with open(file, "w") as f:
            json.dump(add_dict, f)

    def send_mail_for_exception_ocs(self, ocs, subject, content):
        mail = pyocs_email.PyocsEmail()
        sw = pyocs_software.PyocsSoftware()
        ocs_request = pyocs_demand.PyocsDemand(ocs)
        sw_engineer = ocs_request.get_ocs_software_engineer()
        receivers = sw.get_email_addr_from_ocs(sw_engineer)
        mail.send_email(self.sender, receivers, self.cc, subject, content)

    def get_the_date(self, days):
        the_day = datetime.datetime.now() + relativedelta(days=days)
        the_day = datetime.datetime.strftime(the_day, '%Y-%m-%d')
        return the_day

    def get_search_id(self, td_input_6):
        sw = pyocs_software.PyocsSoftware()
        search_id = sw.get_searchid_with_advanced_search_filter("2", td_input_6)
        today = time.strftime("%Y-%m-%d")
        today_md = time.strftime("%m-%d")
        today_d = time.strftime("%d")
        whatday = datetime.datetime.strptime(today, '%Y-%m-%d').strftime("%w")
        if today_md == "09-30" or whatday == "5":
            date_dict = self.read_searchid_date_as_dict()
            if today not in date_dict.keys():
                add_dict = {
                    today: search_id
                }
                date_dict.update(add_dict)
                self.write_searchid_date_to_json(date_dict)

        if today_md >= "10-01" and today_md <= "10-07":
            date_dict = self.read_searchid_date_as_dict()
            days = eval(today_d)
            search_id = date_dict[self.get_the_date(days=-days)]
        elif whatday == "6":
            date_dict = self.read_searchid_date_as_dict()
            search_id = date_dict[self.get_the_date(days=-1)]
        elif whatday == "0":
            date_dict = self.read_searchid_date_as_dict()
            search_id = date_dict[self.get_the_date(days=-2)]

        return search_id

    def update_order_burn_type(self, td_input_6):
        sw = pyocs_software.PyocsSoftware()
        ed = pyocs_edit.PyocsEdit()
        search_id = self.get_search_id(td_input_6)
        si = pyocs_searchid.PyocsSearchid(search_id)
        ocs_id_list = si.get_ocs_id_list_info()
        for ocs_id in ocs_id_list:
            demand = pyocs_demand.PyocsDemand(ocs_id)
            customer = demand.get_ocs_customer()
            if customer == "视睿":
                continue
            sw_list = sw.get_enable_software_list(ocs_id, exclude_bin=0)
            if sw_list:
                for sw_pack in sw_list:
                    sw_name = sw_pack.name
                    burn_type_list = ed.get_ocs_burn_type_with_sw_name(ocs_id, sw_name)
                    if ('EMMCBIN' in sw_name or 'NANDBIN' in sw_name) and "离线烧录" not in burn_type_list:
                        flash_id = ed.get_ocs_burn_id_with_sw_name(ocs_id, sw_name)
                        ed.set_ocs_burn_type(ocs_id, sw_name, flash_id, "2")
                        product = demand.get_product_name()
                        title = ocs_id + ',' + customer + ',' + product
                        subject = "烧录方式设置异常单：" + title
                        ocs_id_link = self._ocs_id_base_link + ocs_id
                        content = "烧录设置异常订单超链接：" + ocs_id_link
                        self.send_mail_for_exception_ocs(ocs_id, subject, content)

