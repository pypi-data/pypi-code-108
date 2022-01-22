import logging
from pyocs import pyocs_edit
from pyocs.pyocs_software import PyocsSoftware
from pyocs import pyocs_searchid
from pyocs.pyocs_demand import PyocsDemand
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
"""
# @author: chenfan3714
# @作用：FAE在设置订单烧录方式时经常出错，此脚本用来定期检测并自动校正
# @className: SampleOrderStock
"""


class SampleOrderStock:
    """校正OSM订单烧录方式"""
    _logger = logging.getLogger(__name__)

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

    def get_ocs_data(self, ocs_number):
        pd = PyocsDemand(ocs_number=ocs_number)
        product_name = pd.get_product_name() if pd.get_product_name() else ""
        hw_port = pd.get_port_info() if pd.get_port_info() else ""
        flash_size = pd.get_flash_info() if pd.get_flash_info() else ""
        duty = str(pd.get_pwm()) + "%" if pd.get_pwm() else ""
        hw_tunner = pd.get_tuner_type() if pd.get_tuner_type() else ""
        chip_type = pd.get_chip_name() if pd.get_chip_name() else ""
        wifi_bt = pd.get_wifi_bluetooth_info() if pd.get_wifi_bluetooth_info() else ""
        return product_name, hw_port, flash_size, duty, hw_tunner, chip_type, wifi_bt

    def get_sample_stock_searchid(self, ocs_number):
        product_name, hw_port, flash_size, duty, hw_tunner, chip_type, wifi_bt = self.get_ocs_data(ocs_number)
        advanced_search = {
                    "0": {"search_field_name": "Req.name", "search_field_id": "1206", "search_field_type": "5",
                         "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC", "input1": product_name,
                         "input2": "null", "offset": "null"},
                    "1": {"search_field_name": "Req.product_id.HW_BasicFunc", "search_field_id": "4450",
                         "search_field_type": "22", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": hw_port,
                         "input2": "null", "offset": "null"},
                    "2": {"search_field_name": "Req.product_id.HW_FlashSize", "search_field_id": "7475",
                         "search_field_type": "22", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": flash_size, "input2": "null", "offset": "null"},
                    "3": {"search_field_name": "Req.rel_obj_id.power_change_opt", "search_field_id": "7095",
                         "search_field_type": "5", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": duty, "input2": "null", "offset": "null"},
                    "4": {"search_field_name": "Req.product_id.HW_Tunner", "search_field_id": "4888",
                         "search_field_type": "22", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": hw_tunner, "input2": "null", "offset": "null"},
                    "5": {"search_field_name": "Req.product_id.HW_ChipSeries", "search_field_id": "4886",
                         "search_field_type": "22", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": chip_type, "input2": "null", "offset": "null"},
                    "6": {"search_field_name": "Req.product_id.HW_TV_WIFIandBT", "search_field_id": "11617",
                         "search_field_type": "22", "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC",
                         "input1": wifi_bt, "input2": "null", "offset": "null"},
        }
        condition = "1 and 2 and 3 and 4 and 5 and 6 and 7"
        searchid = PyocsSoftware().get_sample_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def auto_operate_stock_sw(self, ocs_number):
        _sample_ocs_link_Prefix = 'https://ocs-api.gz.cvte.cn/tv/Reqs/sample_order_index/sort:SampleOrder.status/direction:asc/range:all/SearchId:'

        psw = PyocsSoftware()
        search_id = self.get_sample_stock_searchid(ocs_number)
        pid = pyocs_searchid.PyocsSearchid(search_id, link_prefix=_sample_ocs_link_Prefix)
        ocs_list = pid.get_ocs_id_list_info(xpath='//td[@class="resizable Product_col_name"]/../td[4]')
        if ocs_list:
            for ocs in ocs_list:
                sw_list = psw.get_sample_enable_software_list(ocs, exclude_bin=0)
                if sw_list:
                    try:
                        psw.reuse_old_sw_from_src_to_dst(src_ocs=ocs, dst_ocs=ocs_number, workspace='/')
                    except NoSoftwareError:
                        click.echo("Fail:源订单上无软件")
                    except ReviewExcelError:
                        click.echo("Fail:客户批号信息不匹配，请检查并重新上传Excel")
                    finally:
                        return True
        return False