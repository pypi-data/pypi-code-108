import requests
from bs4 import BeautifulSoup
from pyocs import pyocs_login
from atlassian import Confluence
import json
import pandas as pd


class PyocsAtlassian:
    dg_use_statistics_link = "https://kb.cvte.com/pages/viewpage.action?pageId=156311985"

    def __init__(self):
        self.account = pyocs_login.PyocsLogin().get_account_from_json_file()
        self.confluence = Confluence(url='https://kb.cvte.com', username=self.account['Username'],
                                     password=self.account['Password'])

    def update_count(self, page_id, clear=False):
        user = self.account['Username']
        count = 0
        total_num = 0
        title = "代工新单软件工具使用数据统计（自动生成，请勿编辑）"
        exist = False
        dg_count_page_content = requests.get(self.dg_use_statistics_link,
                                             auth=(self.account['Username'], self.account['Password']))
        soup = BeautifulSoup(dg_count_page_content.text, features="lxml")
        user_list = soup.find_all('td', class_="user confluenceTd")
        count_list = soup.find_all('td', class_="count confluenceTd")
        int_count_list = list()
        total_user = soup.find_all('td', class_="total user confluenceTd")
        total_count = soup.find_all('td', class_="total count confluenceTd")
        body = ""
        if not clear:
            body += '<table border="1">'
            body += '<tr><td>用户</td><td>使用次数</td></tr>'
            if user_list and count_list:
                for idx, us in enumerate(user_list):
                    if user in str(us.string):
                        count = int(count_list[idx].string) + 1
                        int_count_list.append(count)
                        body += '<tr><td class="user">' + user + '</td><td class="count">' + str(count) + '</td></tr>'
                        exist = True
                    else:
                        int_count_list.append(int(count_list[idx].string))
                        body += '<tr><td class="user">' + str(us.string) + '</td><td class="count">' + str(count_list[idx].string) + '</td></tr>'
            if not exist:
                count += 1
                int_count_list.append(count)
                body += '<tr><td class="user">' + user + '</td><td class="count">' + str(count) + '</td></tr>'
            if total_user and total_count:
                tc = int(total_count[0].string) + 1
                body += '<tr><td class="total user">' + "total" + '</td><td class="total count">' + str(tc) + '</td></tr>'
            else:
                for int_count in int_count_list:
                    total_num = total_num + int_count
                body += '<tr><td class="total user">' + "total" + '</td><td class="total count">' + str(total_num) + '</td></tr>'
            body += '</table>'
        self.confluence.update_page(page_id=page_id, title=title, body=body,
                                    type='page', representation='storage')

    team_list = ['BT1', 'BT2', 'BT3', 'BT4', 'BT5', 'BT6', 'BT7', 'BT8', 'BIT4', '平台', 'PT', 'PQ', 'HFAE']

    def list_content(self):
        info_list_List = list()
        all_child_page_id_list = list()
        page_link_prefix = 'https://kb.cvte.com/pages/viewpage.action?pageId='
        child_page_id_list = self.confluence.get_child_id_list(page_id=166451422, limit=20)  # 技术支持微创新
        for child_page_id in child_page_id_list:
            all_child_page_id_list.extend(self.confluence.get_child_id_list(page_id=child_page_id, limit=80))
        print(all_child_page_id_list)
        print(len(all_child_page_id_list))
        for child in all_child_page_id_list:
            page = self.confluence.get_page_by_id(child)
            isOk = False
            for team in self.team_list:
                if team in page['title']:
                    isOk = True
                    if "已完成" in page['title']:
                        info_list = [team, page['title'], page_link_prefix + child, "已完成",
                                     page['history']['createdDate']]
                    else:
                        info_list = [team, page['title'], page_link_prefix + child, "未完成",
                                     page['history']['createdDate']]
                    info_list_List.append(info_list)
            if not isOk:
                print(page['title'])

        name = ['部分', '标题', '链接', '是否完成(模糊)', '创建日期']
        content = pd.DataFrame(columns=name, data=info_list_List)
        content.to_csv('微创新.csv', encoding='utf-8')


