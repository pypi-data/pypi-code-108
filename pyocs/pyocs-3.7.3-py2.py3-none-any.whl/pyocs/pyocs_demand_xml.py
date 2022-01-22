from pyocs.pyocs_request import PyocsRequest
from pyocs.pyocs_exception import *
from lxml import etree
import logging


class PyocsDemand:
    _ocs_link_Prefix = 'http://ocs-api.gz.cvte.cn/tv/pop/Tasks/compare_request/'
    _logger = logging.getLogger(__name__)

    SAMPLE_ORDER = "样品订单"
    FORMAL_ORDER = "正式订单"

    def __init__(self, ocs_number):
        self.order_type = self.FORMAL_ORDER
        self.ocs_number = ocs_number
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        ocs_link = self._ocs_link_Prefix + ocs_number + "/5d3eec77-3058-4a1f-83bc-106aac11527a"  # XML对比页
        ocs_url_response = PyocsRequest().pyocs_request_get(ocs_link, False)

        if ocs_url_response.status_code == 302:
            sample_order_link = ocs_url_response.headers["Location"]
            if "sample_order_view" in sample_order_link:
                self.order_type = self.SAMPLE_ORDER
                ocs_url_response = PyocsRequest().pyocs_request_get(sample_order_link, False)
                self.html = etree.HTML(ocs_url_response.text)
        elif ocs_url_response.status_code == 200:
            self.html = etree.HTML(ocs_url_response.text)
        else:
            raise OcsSystemError('OCS访问存在问题')

    def xml_chipseries(self):
        # 芯片型号
        chipseries_xpath = '//*[@id="main"]//th[contains(text(),"芯片型号")]/../td[1]/ul/li/span/text()'
        chipseries_list = self.html.xpath(chipseries_xpath)
        self.chipseries_str = "".join(chipseries_list).strip() if chipseries_list else ""
        return self.chipseries_str

    def xml_tuner(self):
        # 高频头 Tuner
        tuner_xpath = '//*[@id="main"]//th[contains(text(),"高频头")]/../td[1]/ul/li/span//text()'
        tuner_list = self.html.xpath(tuner_xpath)
        self.tuner_str = ", ".join(tuner_list)
        return self.tuner_str

    def xml_flashsize(self):
        # flash大小 flash_size
        flash_size_xpath = '//*[@id="main"]//th[contains(text(),"FlashSize")]/../td[1]/ul/li/span//text()'
        flash_size_list = self.html.xpath(flash_size_xpath)
        self.flash_size_str = "".join(flash_size_list)
        return self.flash_size_str

    def xml_inputsource(self):
        # 通道功能
        inputsource_xpath = '//*[@id="main"]//th[contains(text(),"通道")]/../td[1]/ul/li/span//text()'
        inputsource_list = self.html.xpath(inputsource_xpath)
        self.inputsource_str = ", ".join(inputsource_list)
        return self.inputsource_str

    def xml_panel(self):
        # 配屏
        panel_xpath = '//*[@id="main"]//th[contains(text(),"配屏")]/../td[1]/ul/li/span/a/text()'
        panel_list = self.html.xpath(panel_xpath)
        self.panel_str = ", ".join(panel_list) if panel_list else ""
        return self.panel_str

    def xml_CI(self):
        ci_xpath = '//*[@id="main"]//th[contains(text(),"CI 功能")]/../td[1]/ul/li/span/text()'
        ci_list = self.html.xpath(ci_xpath)
        self.ci_str = ", ".join(ci_list) if ci_list else ""
        if self.ci_str != '1':
            self.ci_str = '0'
        return self.ci_str

    def xml_key(self):
        # 按键类型
        key_xpath = '//*[@id="main"]//th[contains(text(),"按键类型")]/../td[1]/ul/li/span/text()'
        key_list = self.html.xpath(key_xpath)
        self.key_str = ", ".join(key_list) if key_list else ""
        return self.key_str

    def xml_wifi(self):
        # 按键类型
        wifi_xpath = '//*[@id="main"]//th[contains(text(),"WIFI模块名称")]/../td[1]/ul/li/span/text()'
        wifi_list = self.html.xpath(wifi_xpath)
        self.wifi_str = ", ".join(wifi_list) if wifi_list else ""
        return self.wifi_str
