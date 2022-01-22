#! /usr/bin/env python3
import logging
from lxml import etree
from pyocs import pyocs_login
from pyocs.pyocs_request import PyocsRequest

"""
# @author:zhaoxinan
# @作用：软件更改单系统自动点击ERP同步的需求
# @KB: https://kb.cvte.com/pages/viewpage.action?pageId=190181702
# @className：OsmInventoryChangeOrder
"""


class OsmOrderErpSync:
    _process_data_base_url = "https://ocs-api.gz.cvte.cn/tv/ERPWsClients/processStockMmToEBS/"
    _ocs_inventory_ch_order_url = "https://ocs-api.gz.cvte.cn/tv/StockMms/index/range:all/status:STOCK_MM_STATUS_SW/SearchId:2748517"
    _ocs_inventory_ch_order_url_allocation_ = "http://ocs-api.gz.cvte.cn/tv/StockMms/index/range:all/status:STOCK_MM_STATUS_SW_ALLOCATION/SearchId:2748517"
    _logger = logging.getLogger(__name__)
    _instance = None

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别


    def get_pages_num(self,pages_string):
        pagesstr_list = pages_string.split()
        for i in range (len(pagesstr_list)):
            if pagesstr_list[i] == "页面":
                temp_list = pagesstr_list[i+1].split('/')
                return int(temp_list[1])

    def get_all_inventory_order_html_erpid_untreatedid(self):
        response = PyocsRequest().pyocs_request_get(self._ocs_inventory_ch_order_url)
        html = etree.HTML(response.text)

        pages_xpath ='//p/text()'
        pages_str = html.xpath(pages_xpath)
        pagesnum = self.get_pages_num(str(pages_str))
        #print("一共有:"+str(pagesnum)+"页")

        stockmm_id_list = []
        stockmm_id_xpath = '//a[contains(@href, "/tv/Logs/view_logs/StockMms")]/text()'
        stockmm_id_list= html.xpath(stockmm_id_xpath)
        
        if pagesnum >= 2:
            for i in range(2,pagesnum+1):
                _page_url = self._ocs_inventory_ch_order_url+'/page:'+str(i)
                #print(_page_url)
                pagresponse = PyocsRequest().pyocs_request_get(_page_url)
                pagehtml = etree.HTML(pagresponse.text)
                stockmm_id_list = stockmm_id_list+pagehtml.xpath(stockmm_id_xpath)
        #print(stockmm_id_list)
        return stockmm_id_list

    def get_all_inventory_order_html_erpid_treatedid(self):
        response = PyocsRequest().pyocs_request_get(self._ocs_inventory_ch_order_url_allocation_)
        html = etree.HTML(response.text)

        pages_xpath ='//p/text()'
        pages_str = html.xpath(pages_xpath)
        pagesnum = self.get_pages_num(str(pages_str))
        #print("一共有:"+str(pagesnum)+"页")

        stockmm_id_list = []
        stockmm_id_xpath = '//a[contains(@href, "/tv/Logs/view_logs/StockMms")]/text()'
        stockmm_id_list= html.xpath(stockmm_id_xpath)
        
        if pagesnum >= 2:
            for i in range(2,pagesnum+1):
                _page_url = self._ocs_inventory_ch_order_url_allocation_+'/page:'+str(i)
                #print(_page_url)
                pagresponse = PyocsRequest().pyocs_request_get(_page_url)
                pagehtml = etree.HTML(pagresponse.text)
                stockmm_id_list = stockmm_id_list+pagehtml.xpath(stockmm_id_xpath)
        #print(stockmm_id_list)
        return stockmm_id_list

    def deal_all_erp_sync(self,erpid_list):
        
        for i in range(len(erpid_list)):
            _process_erp_url = self._process_data_base_url+erpid_list[i]
            #print(_process_erp_url)
            response = PyocsRequest().pyocs_request_get(_process_erp_url)
            #print(response.text)

    def start_deal_erp_sync(self):
        erpid_list = self.get_all_inventory_order_html_erpid_untreatedid()
        self.deal_all_erp_sync(erpid_list)
        print("软件更改单系统自动点击ERP未处理的同步处理完毕!")
        erpid_list = self.get_all_inventory_order_html_erpid_treatedid()
        self.deal_all_erp_sync(erpid_list)
        print("软件更改单系统自动点击ERP已接收的同步处理完毕!")