import os
import sys
PROJ_HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(1,PROJ_HOME_PATH)

import json
import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from lxml import etree

from pyocs.pyocs_request import PyocsRequest

url = 'http://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/index'
submit_url_prefix = 'http://ocs-api.gz.cvte.cn/tv/TaskRelForecastWarms/submit_audit_info_json/'
submit_url_suffix = '/batch_audit_owner'
order_id_xpath = '//*[@id="main"]/div[3]/div[1]/table/tbody/tr'
response = PyocsRequest().pyocs_request_get(url)
html = etree.HTML(response.text)
xpath_value_list = html.xpath(order_id_xpath)

order_id_list = []
for content in xpath_value_list:
    for name, value in content.attrib.items():
        content_dict = json.loads(value)
        order_id_list.append(content_dict['TaskRelForecastWarm']['id'])
print(order_id_list)


# order_id_list = ['88840','88832']
now_time = datetime.datetime.now()
estimated_confirm_time = now_time + relativedelta(weeks=+1)#预估确认时间默认设置为1周后
estimated_confirm_time_str = estimated_confirm_time.strftime('%Y-%m-%d')

'''
[abnormal_sort]:'50'
[abnormal_situation]:'客户需求未确定'

[abnormal_sort]: '90',
[abnormal_situation]: '终端未确认软件'
'''

data = {}
for id in order_id_list:
    data.update({
        'data[TaskRelForecastWarm][' + id + '][abnormal_sort]': '50',
        'data[TaskRelForecastWarm][' + id + '][abnormal_situation]': '客户需求未确定',
        'data[TaskRelForecastWarm][' + id + '][sw_estimated_confirm_date]': estimated_confirm_time_str
    })

pprint(data)

submit_url = submit_url_prefix + ','.join(order_id_list) + submit_url_suffix
ret = PyocsRequest().pyocs_request_post(submit_url,data)
print(ret)

