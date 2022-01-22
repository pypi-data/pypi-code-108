import re
import requests
from bs4 import BeautifulSoup
from pyocs import pyocs_login


class PyocsConfluence:

    kb_page_link_prefix = 'https://kb.cvte.com/pages/viewpage.action?pageId='
    project_region_mapping_table_kb_pageid = '138102551'
    osm_distribute_mapping_table_kb_pageid = '177887289'
    customer_software_confirm_table_kb_link = 'https://kb.cvte.com/pages/viewpage.action?pageId=225598992'

    #以下连接已经转移到数据库
    project_code_mapping_table_kb_pageid = '139470654'
    customer_dt_mapping_table_kb_link = 'https://kb.cvte.com/pages/viewpage.action?pageId=139478158'
    engineer_tcl_dt_mapping_table_kb_link = 'https://kb.cvte.com/pages/viewpage.action?pageId=140906075'

    def __init__(self):
        self.account = pyocs_login.PyocsLogin().get_account_from_json_file()

    def get_kb_table_page_content(self, page_id):
        """获取单一表格的KB页面的表格内容
        Args:
            page_id: KB链接的id号
        Returns:
            返回对应表格的内容，类型为dict
        """
        table_dict = {}
        kb_page_link = self.kb_page_link_prefix + page_id
        kb_page_content = requests.get(kb_page_link, auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(kb_page_content.text, features="lxml")
        find_soup = soup.find('div',attrs={"class":"table-wrap"})
        if find_soup is None:
            return None
        trs = find_soup.find_all('tr')
        for tr in trs:
            ui = []
            for td in tr:
                ui.append(td.string)
            table_dict.update({ui[0]: ui[1:len(ui)]})
        return table_dict

    def get_kb_tables_page_content(self, page_id, title: str):
        """获取多个表格的KB页面主题为title的表格内容
        Args:
            page_id: KB链接的id号
            title: KB页面主题，如表格一，表格二...
        Returns:
            返回主题为title的表格的内容，类型为dict
        """
        table_dict = {}
        kb_page_link = self.kb_page_link_prefix + page_id
        kb_page_content = requests.get(kb_page_link, auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(kb_page_content.text, features="lxml")
        find_soup = soup.find('h1',attrs={"id":re.compile(title)})
        if find_soup is None:
            return None
        trs = find_soup.find_parents('tbody')
        # <bs4.element.ResultSet>转<class 'bs4.element.Tag>
        trs = trs[0].find_all('tr')
        for tr in trs:
            ui = []
            for td in tr:
                ui.append(td.string)
            table_dict.update({ui[0]: ui[1:len(ui)]})
        return table_dict

    def get_key_value_list_from_kb_table(self, match_name, page_id):
        """获取单一表格的指定key的value
        Args:
            match_name: 指定key
            kb_pageid: KB页面主题，如表格一，表格二...
        Returns:
            返回指定key的value，类型为list
        """
        map_list = list()
        kb_table = self.get_kb_table_page_content(page_id)
        for key in kb_table:
            if match_name in key:
                map_list = kb_table[key]
        return map_list

    def get_region_mapping_info_by_country(self, country):
        """获取自动编译国家制式映射表KB页面指定国家的value
        KB链接：
            https://kb.cvte.com/pages/viewpage.action?pageId=138102551
        """
        map_list = self.get_key_value_list_from_kb_table(country, self.project_region_mapping_table_kb_pageid)
        return map_list

    def get_code_mapping_info_by_project(self, project):
        """获取自动编译方案映射表KB页面指定项目组的value
        KB链接：
            https://kb.cvte.com/pages/viewpage.action?pageId=139470654
        """
        map_list = self.get_key_value_list_from_kb_table(project, self.project_code_mapping_table_kb_pageid)
        return map_list

    def get_download_link_of_dt_by_customer(self, customer_name: str):
        dt_download_link = ''
        country_page_content = requests.get(self.customer_dt_mapping_table_kb_link,
                                            auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(country_page_content.text, features="lxml")
        customer_list = soup.find_all('td', class_="confluenceTd")
        for customer_str in customer_list:
            if customer_name in str(customer_str.string):
                dt_download_link = customer_str.next_sibling.string if customer_str.next_sibling else ''
        return dt_download_link

    def get_download_link_of_tcl_dt_by_engineer(self, engineer_name: str):
        dt_download_link = ''
        country_page_content = requests.get(self.engineer_tcl_dt_mapping_table_kb_link,
                                            auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(country_page_content.text, features="lxml")
        engineer_list = soup.find_all('td', class_="confluenceTd")
        for engineer_str in engineer_list:
            if engineer_name in str(engineer_str.string):
                dt_download_link = engineer_str.next_sibling.string if engineer_str.next_sibling else ''
        return dt_download_link

    def get_osm_distribute_mapping_info_by_user(self, user):
        """获取自动编译方案映射表KB页面指定项目组的value
        KB链接：
            https://kb.cvte.com/pages/viewpage.action?pageId=177887289
        """
        map_list = self.get_key_value_list_from_kb_table(user, self.osm_distribute_mapping_table_kb_pageid)
        return map_list

    def get_download_link_software_confirm_table_by_customer(self, customer_name: str):
        dt_download_link = ''
        country_page_content = requests.get(self.customer_software_confirm_table_kb_link,
                                            auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(country_page_content.text, features="lxml")
        customer_list = soup.find_all('td', class_="confluenceTd")
        for customer_str in customer_list:
            if customer_name in str(customer_str.string):
                dt_download_link = customer_str.next_sibling.string if customer_str.next_sibling else ''
        return dt_download_link
