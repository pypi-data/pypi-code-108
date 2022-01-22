
import pprint
import sys
import os
import json
import re

FILE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
PROJ_HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1,PROJ_HOME_PATH)

from pyocs import pyocs_software
from pyocs.pyocs_request import PyocsRequest
from pyocs import pyocs_demand
from pyocs import pyocs_login
from lxml import etree


headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.76 Safari/537.36",
        # 'Connection':'keep-alive',
        'Referer'   : "http://ocs-api.gz.cvte.cn/tv/pop/Tasks/create_pre_order_task/554977"
        # 'Accept': "*/*"
    }

intention_order_form_data_dict = {
        "data[model]":"PreOrder",
        "data[action]":"new",
        "data[Pname]":"",
        "data[Pvalue]":"",
        "data[req][1][account]":"",
        "data[req][1][account_id]":"",
        "data[req][1][prod_name]":"",#TP.MT5510S.PB803A<11122011.0001.0073>
        "data[req][1][product_id]":"",#415266
        "data[Task][1][Task__sw_user_id]":"",#订单软件工程师
        "data[req][1][rd_dept]":"",
        "data[req][1][rd_dept_id]":"",
        "data[Task][1][Task__subject]":"",#摘要
        "req_1__Confirmation__SW_Panel":"on",
        "data[req][1][sw][Confirmation__SW_Panel]":"",
        "req_1__Confirmation__SW_Logo":"on",
        "data[req][1][sw][Confirmation__SW_Logo]":"",
        "req_1__Confirmation__SW_RemoteControl":"on",
        "data[req][1][sw][Confirmation__SW_RemoteControl]":"",
        "req_1__Confirmation__SW_Language":"on",
        "data[req][1][sw][Confirmation__SW_Language]":"",
        "req_1__Confirmation__SW_DefaultLanguage":"on",
        "data[req][1][sw][Confirmation__SW_DefaultLanguage]":"",
        "req_1__Confirmation__SW_Country":"on",
        "data[req][1][sw][Confirmation__SW_Country]":"",
        "req_1__Confirmation__SW_DefaultCountry":"on",
        "data[req][1][sw][Confirmation__SW_DefaultCountry]":"",
        "req_1__Confirmation__SW_OptFunc":"on",
        "data[req][1][sw][Confirmation__SW_OptFunc]":"",
        "data[req][1][remark]":""
    }


def postHttpReqsToGetCustomerId(customer_name: str):
    url = "http://ocs-api.gz.cvte.cn/tv/Accounts/find_account"
    form_data_dict = {
        "accountName": customer_name
    }

    response = PyocsRequest().pyocs_request_post_with_headers(url, data = form_data_dict, headers = headers)
    if (response.status_code == 200):
        response_dict = json.loads(response.text) #将获取的内容转换成字典
        return (response_dict["Account"]["id"],response_dict["Account"]["name"])
    else:
        print("response error!!!")


def get_order_ocs_id(customer_order_id : str):
    """
    从OCS摘要中搜索客户订单号，判断相关订单是否存在
    :param customer_order_id:
    :return:
    """
    ret = pyocs_software.PyocsSoftware().get_ocs_number_from_abstract(customer_order_id)
    if len(ret) == 0:
        return 0
    else:
        return ret[0]

def create_intention_order(order_subject ='自动创建订单' ,order_customer_id = '1917',order_customer_name = '青岛海尔电子有限公司'):
    """
    创建意向订单
    :param ocs_number:
    :return:
    """
    intention_order_url = "http://ocs-api.gz.cvte.cn/tv/Reqs/submit_req_by_ajax/"
    intention_order_form_data_dict["data[Task][1][Task__subject]"] = order_subject
    intention_order_form_data_dict["data[req][1][account]"]    = order_customer_id
    intention_order_form_data_dict["data[req][1][account_id]"] = order_customer_name

    sw_user_id = pyocs_software.PyocsSoftware().get_user_id_from_account(pyocs_login.PyocsLogin().get_account_from_json_file()['Username'])
    intention_order_form_data_dict["data[Task][1][Task__sw_user_id]"] = sw_user_id

    ret = PyocsRequest().pyocs_request_post_with_headers(intention_order_url, data = intention_order_form_data_dict, headers = headers)
    if (ret.status_code == 200):
        ret_dict = json.loads(ret.text)
        return "".join(re.findall(r"\d*",ret_dict['go_to_url']))
    else:
        print("response error!!!")
    return ret


def main():
    customer_name = ''
    bom_number = ''

    if (len(sys.argv) > 2):
        customer_name = sys.argv[1]#客户名称
        bom_number = sys.argv[2]#订单客料号
    else:
        print("请输入客户名 客户料号!")
        return
    
    ocs_id = get_order_ocs_id(bom_number)
    
    #OCS上没有相关订单
    if ocs_id == 0:
        if customer_name or bom_number:
            order_subject = customer_name + " " + bom_number
        else:
            order_subject = '自动创建订单'
        order_customer_id,order_customer_name = postHttpReqsToGetCustomerId(customer_name)
        ocs_id = create_intention_order(order_subject,order_customer_id,order_customer_name)
        print("OCS上没有相关订单，已新建如下意向订单：" + ocs_id)
    else:
        ocs_request = pyocs_demand.PyocsDemand(ocs_id)
        print("OCS上已存在如下大货订单：" + ocs_id)
        print("版型："      + ocs_request.get_port_name())
        print("芯片型号："  + ocs_request.get_chip_name())
        print("占空比："    + ocs_request.get_pwm())
        print("其它应用软件："    + ocs_request.get_other_app_software())


if __name__ == '__main__':
    main()