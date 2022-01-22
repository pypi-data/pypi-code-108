#! /usr/bin/env python3
import logging
from lxml import etree
from pyocs import pyocs_login
from pyocs.pyocs_request import PyocsRequest

"""
# @author:zhaoxinan
# @作用：对于客户升级，库存过账，已作废更改单，系统自动移除的需求
# @KB: https://kb.cvte.com/pages/viewpage.action?pageId=190181751
# @className：OsmInventoryChangeOrder
"""


class OsmCHOrderInvalidAuotRemove:
    #未处理的更改单 软件发放人员 肖瑶 柯雅芬 莫媛媛 李丽敏 EBS更改状态已作废、更改原因库存过账、软件更改情况客户升级
    _untreated_base_url = "https://ocs-api.gz.cvte.cn/tv/StockMms/index/range:all/status:STOCK_MM_STATUS_SW/SearchId:2749251"
    #已接收
    _treated_base_url = "https://ocs-api.gz.cvte.cn/tv/StockMms/index/range:all/status:STOCK_MM_STATUS_SW_ALLOCATION/SearchId:2749251"

    _post_url = "https://ocs-api.gz.cvte.cn/tv/StockMms/process_stockmm_done_json/"

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

    def get_all_inventory_order_html_untreatedid(self):
        response = PyocsRequest().pyocs_request_get(self._untreated_base_url)
        html = etree.HTML(response.text)

        pages_xpath ='//p/text()'
        pages_str = html.xpath(pages_xpath)
        pagesnum = self.get_pages_num(str(pages_str))
        #print("一共有:"+str(pagesnum)+"页")

        #得到首页的ID list
        stockmm_id_list = []
        stockmm_id_xpath = '//a[contains(@href, "/tv/Logs/view_logs/StockMms")]/text()'
        stockmm_id_list= html.xpath(stockmm_id_xpath)
        
        #如果有多页则将其他页的id和首页ID进行一个整合
        if pagesnum >= 2:
            for i in range(2,pagesnum+1):
                _page_url = self._ocs_inventory_ch_order_url+'/page:'+str(i)
                #print(_page_url)
                pagresponse = PyocsRequest().pyocs_request_get(_page_url)
                pagehtml = etree.HTML(pagresponse.text)
                stockmm_id_list = stockmm_id_list+pagehtml.xpath(stockmm_id_xpath)
        #print(stockmm_id_list)
        return stockmm_id_list

    def get_all_inventory_order_html_treatedid(self):
        response = PyocsRequest().pyocs_request_get(self._treated_base_url)
        html = etree.HTML(response.text)

        pages_xpath ='//p/text()'
        pages_str = html.xpath(pages_xpath)
        pagesnum = self.get_pages_num(str(pages_str))
        #print("一共有:"+str(pagesnum)+"页")

        #得到首页的ID list
        stockmm_id_list = []
        stockmm_id_xpath = '//a[contains(@href, "/tv/Logs/view_logs/StockMms")]/text()'
        stockmm_id_list= html.xpath(stockmm_id_xpath)
        
        #如果有多页则将其他页的id和首页ID进行一个整合
        if pagesnum >= 2:
            for i in range(2,pagesnum+1):
                _page_url = self._ocs_inventory_ch_order_url+'/page:'+str(i)
                #print(_page_url)
                pagresponse = PyocsRequest().pyocs_request_get(_page_url)
                pagehtml = etree.HTML(pagresponse.text)
                stockmm_id_list = stockmm_id_list+pagehtml.xpath(stockmm_id_xpath)
        #print(stockmm_id_list)
        return stockmm_id_list

    def deal_all_untreated_order(self,id_list):
        
        for i in range(len(id_list)):
            data = {
                'stock_id': int(id_list[i])
            }
            ret = PyocsRequest().pyocs_request_post(self._post_url, data=data)
            print(ret)

    def start_deal_invaild_order_remove(self):
        id_list = self.get_all_inventory_order_html_untreatedid()
        self.deal_all_untreated_order(id_list)
        #print(id_list)
        print("软件更改单系统未处理自动移除完毕!")
        id_list = self.get_all_inventory_order_html_treatedid()
        self.deal_all_untreated_order(id_list)
        #print(id_list)
        print("软件更改单系统已接收自动移除完毕!")