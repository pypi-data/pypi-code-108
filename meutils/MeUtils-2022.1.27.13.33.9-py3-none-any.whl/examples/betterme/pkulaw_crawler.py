#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : pkulaw_crawler
# @Time         : 2021/9/1 上午11:30
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.date_utils import date_difference
from meutils.request_utils.xpath import get_dom_tree
from meutils.notice.wecom import Wecom

date_1 = date_difference('%Y.%m.%d', days=1)
url = "http://www.pkulaw.cn/cluster_form.aspx?Db=news&menu_item=law&EncodingName=&keyword=&range=name&"

xpath = """//*[starts-with(@id, 'a_ft_')]/@href"""
urls = get_dom_tree(url, xpath)
urls = [f'http://www.pkulaw.cn/{url}' for url in urls]

# xpath = """//*[starts-with(@id, 'a_ft_')]//text()"""
xpath = """//*[@id="dir_sub_div"]//tr//text()"""
ts = get_dom_tree(url, xpath)
title2url = list(zip([t for t in ''.join(ts).replace(' ', '').split() if t.endswith(date_1)], urls))

if __name__ == '__main__':
    wecom = Wecom("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b1424470-f377-4d13-a2c8-b2c4014687c1")

    wecom.send_markdown(f"> # [北大法宝]({url})", [f"[{title}]({url})" for title, url in title2url[:6]])
