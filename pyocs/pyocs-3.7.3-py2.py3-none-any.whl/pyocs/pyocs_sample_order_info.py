# coding: UTF-8

import logging
import re
from lxml import etree
from pyocs.pyocs_request import PyocsRequest


class SampleOrderInfo:
    _ocs_base_link = 'https://ocs-api.gz.cvte.cn'
    _ocs_link_Prefix = _ocs_base_link + '/tv/Tasks/sample_order_view/'
    _logger = logging.getLogger(__name__)

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    def get_ocs_sample_html(self, ocs_number):
        ocs_link = self._ocs_link_Prefix + str(ocs_number)
        response = PyocsRequest().pyocs_request_get(ocs_link)
        html = etree.HTML(response.text)
        return html

    def get_is_sample_ocs(self, html):
        ocs_type_xpath = r'//*[@id="main"]//th[contains(text(),"样品类型")]/following-sibling::td/text()'
        text_list = html.xpath(ocs_type_xpath)
        for i in range(0, len(text_list)):
            text = text_list[i]
            if len(text):
                if ('样机' in text) or ('测试' in text) or ('确认' in text) or ('认证' in text) or ('封样' in text):
                    return True
        return False

    def get_customer_info(self, html):
        title_xpath = r'//span[@class="notice-title"]/text()'
        text = html.xpath(title_xpath)[0]
        customer = re.findall(r'[\[|\【](.*?)[\]|\】]', text)[0]
        return customer

    def get_power_info(self, html):
        power_xpath = r'//*[@id="main"]//th[contains(text(),"电源背光备注")]/following-sibling::td/text()'
        text_list = html.xpath(power_xpath)
        power_info = ""
        for i in range(0, len(text_list)):
            text = text_list[i]
            if "1路" in text:
                power_info = text.split('1路')[0] + "1路"
            elif "2路" in text:
                if "串联" in text:
                    power_info = text.split('2路')[0] + "2路串联"
                elif "并联" in text:
                    power_info = text.split('2路')[0] + "2路并联"
                else:
                    power_info = "【警告】：电源背光信息错误，请确认！！！"
        power_info = power_info.replace(" ", "")
        power_info = power_info.replace("\n", "")
        return power_info

    def get_duty_info(self, html):
        duty_xpath = r'//*[@id="main"]//th[contains(text(),"电源规格及修改项")]/following-sibling::td/text()'
        text_list = html.xpath(duty_xpath)
        duty_info = ""
        for i in range(0, len(text_list)):
            text = text_list[i]
            if len(text) and ("%" in text):
                duty_info = text.split('%')[0]
                if len(duty_info):
                    duty_info = duty_info + "%"

        duty_info = duty_info.replace("\n", "")
        duty_info = duty_info.replace(" ", "")
        return duty_info

    def get_flash_size(self, html):
        flashsize_xpath = r'//*[@id="main"]//th[contains(text(),"FlashSize")]/following-sibling::td/strong/text()'
        text = html.xpath(flashsize_xpath)[0]
        flash_size = re.findall(r'使用([\d]+[G|M]Byte)', text)[0]
        return flash_size

    def get_board_subtype(self, html):
        board_subtype_xpath = r'//*[@id="main"]//th[contains(text(),"端子功能")]/following-sibling::td/p[1]/text()'
        text = html.xpath(board_subtype_xpath)[0]
        board_subtype = text.split('_')[1]
        return board_subtype

    def get_DDR_info(self, html):
        internal_ddr_xpath = r'//*[@id="main"]//th[contains(text(),"主芯片")]/following-sibling::td/p[2]/text()'
        internal_ddr_text_list = html.xpath(internal_ddr_xpath)
        internal_ddr = ''
        if len(internal_ddr_text_list):
            internal_ddr_text = internal_ddr_text_list[0]
            internal_ddr_list = re.findall(r'内置([\d]+[G|M]B)', internal_ddr_text)
            if len(internal_ddr_list):
                internal_ddr = internal_ddr_list[0]

        external_ddr_xpatp = r'//*[@id="main"]//th[contains(text(),"External DDR")]/following-sibling::td/strong/text()'
        external_ddr_text_list = html.xpath(external_ddr_xpatp)
        external_ddr = ''
        if len(external_ddr_text_list):
            external_ddr_text = external_ddr_text_list[0]
            external_ddr_list = re.findall(r'使用([\d]+[G|M]Byte)', external_ddr_text)
            if len(external_ddr_list):
                external_ddr = external_ddr_list[0]

        if len(internal_ddr) and len(external_ddr):
            return external_ddr + '+内置' + internal_ddr
        elif len(internal_ddr):
            return '内置' + internal_ddr
        elif len(external_ddr):
            return external_ddr
        else:
            return ''

    def print_ocs_sample_info(self, ocs_number):
        html = self.get_ocs_sample_html(ocs_number)

        if self.get_is_sample_ocs(html):
            print('样品：不可用于大货')

        customer_info = self.get_customer_info(html)
        if len(customer_info):
            print(str(ocs_number) + '    ' + customer_info)
        else:
            print(str(ocs_number))

        power_info = self.get_power_info(html)
        if len(power_info):
            print(power_info)

        duty_info = self.get_duty_info(html)
        board_subtype = self.get_board_subtype(html)
        if len(duty_info) and len(board_subtype):
            print(duty_info + "       " + board_subtype)
        elif len(duty_info):
            print(duty_info)
        elif len(board_subtype):
            print(board_subtype)

        flash_size = self.get_flash_size(html)
        if len(flash_size):
            print('Flash: ' + flash_size)

        ddr_info = self.get_DDR_info(html)
        if len(ddr_info):
            print('DDR: ' + ddr_info)


'''
if __name__ == '__main__':
    ocs_number = 531738
    sample_order_info = SampleOrderInfo()
    sample_order_info.print_ocs_sample_info(ocs_number)
'''
