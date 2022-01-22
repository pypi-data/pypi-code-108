from openpyxl import load_workbook
from openpyxl import Workbook
import os
import sys
from pyocs import pyocs_software
from lxml import etree
from pyocs.pyocs_analysis import PyocsAnalysis
from pyocs.pyocs_request import PyocsRequest

# 创建对象
ocs_communication = pyocs_software.PyocsSoftware()
#ocs_link = self._ocs_link_Prefix + ocs_number
ocs_link = 'http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/472993'
response = PyocsRequest().pyocs_request_get(ocs_link)
html = etree.HTML(response.text)
sw_name = 'CP472993_JPE_TP_RD8503_PC815_NIGERIA_ST5461B03_5_TELEFUNKEN_01201908186_E55DM1100_REF52_AT_trunk_6759d7d6_20190822_152510.tar'
#获取文本为sw_name的所有a节点的上一级节点下的span节点的text文本。/../表示去到上一级
fw_id_xpath = '//a[text()="' + sw_name + '"]/../span/text()'
#fw_id_xpath = '//td[@class]/../span/text()'#/../span/text()'
shenhezhuangtai_xpath = '//td[@class="firmware_status"]/span/text()'
#xpath要全路径？
fw_id_str_list = html.xpath(fw_id_xpath)
print(fw_id_str_list)
shenhezhuangtai_xpath = html.xpath(shenhezhuangtai_xpath)
print(shenhezhuangtai_xpath)
#ocs_fw_id=ocs_communication.get_enable_software_fw_id_from_html_by_sw_name(html,'20190917_120744')
#print(ocs_fw_id)
print(ocs_communication._upload_fw_url_prefix)
old_sw_id=ocs_communication.find_old_sw_id_by_name(sw_name)
print(old_sw_id)
result=ocs_communication.upload_old_sw_by_id('482650',old_sw_id)
print(result)


