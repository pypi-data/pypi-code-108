import os
import re
import readline
import click
import datetime
import time
import requests
from customers.customer_osm import cps_upload_key
from customers.customer_osm import osm_order_assign
from customers.customer_osm import osm_order_data
from customers.customer_opm import opm_order_status
from customers.customer_osm import osm_order_edit
from customers.customer_osm import osm_order_notice

from customers.customer_sample import sample_order_stock
from customers.customer_tcl import tcl_order
from pyocs import pyocs_jenkins
from pyocs import pyocs_jenkins_status
from pyocs import pyocs_jira
from pyocs import pyocs_software
from pyocs import __version__
from pyocs import pyocs_list
from pyocs import pyocs_edit
from pyocs import pyocs_software_report
from pyocs import pyocs_appjson
from pyocs import pyocs_confluence
from pyocs import pyocs_gerrit
from pyocs import pyocs_jira_func
from pyocs import pyocs_searchid
from pyocs.pyocs_rsa import PyocsRsa
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_auto_config import PyocsAutoConfig
from pyocs.pyocs_filesystem import PyocsFileSystem
import pprint
from pyocs.pyocs_exception import *
from customers.customer_dg import dg_reuse_sw
from customers.customer_dg import dg_sw_task_msg 
from customers.customer_chaoye.comment_sw_needs_to_ocs.cy_demand_to_ocs import CyNeedsToOcs
from customers.customer_sqy.create_intention_order import create_intention_order
from pyocs.pyocs_confluence import PyocsConfluence
from pyocs.pyocs_maxhubshare_report import *

STYLE = {
    'fore':
    {   # 前景色
     'black'    : 30,   #  黑色
     'red'      : 31,   #  红色
     'green'    : 32,   #  绿色
     'yellow'   : 33,   #  黄色
     'blue'     : 34,   #  蓝色
     'purple'   : 35,   #  紫红色
     'cyan'     : 36,   #  青蓝色
     'white'    : 37,   #  白色
     },

    'back' :
    {   # 背景
     'black'     : 40,  #  黑色
     'red'       : 41,  #  红色
     'green'     : 42,  #  绿色
     'yellow'    : 43,  #  黄色
     'blue'      : 44,  #  蓝色
     'purple'    : 45,  #  紫红色
     'cyan'      : 46,  #  青蓝色
     'white'     : 47,  #  白色
     },

    'mode' :
    {   # 显示模式
     'mormal'    : 0,   #  终端默认设置
     'bold'      : 1,   #  高亮显示
     'underline' : 4,   #  使用下划线
     'blink'     : 5,   #  闪烁
     'invert'    : 7,   #  反白显示
     'hide'      : 8,   #  不可见
     },

    'default' :
    {
        'end' : 0,
    },
}
# pyocs命令行使用场景较多，使用linux中USER环境变量传递当前用户，虽然并非100%准确，但是具备统计意义
user = os.environ['USER']
statistics_url_prefix = "http://tsc.gz.cvte.cn/v1/statistics/"

def use_style(string, mode='', fore='', back=''):
    mode = '%s' % STYLE['mode'][mode] if mode in STYLE['mode'] else ''
    fore = '%s' % STYLE['fore'][fore] if fore in STYLE['fore'] else ''
    back = '%s' % STYLE['back'][back] if back in STYLE['back'] else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)


# 使用样式输出
# print(use_style("hello world!", mode="bold"))
# print(use_style("hello world!", back="green"))


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__.version)
    ctx.exit()


@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="打印Pyocs的版本信息")
def cli():
    """ Pyocs命令行工具，使用介绍：https://kb.cvte.com/pages/viewpage.action?pageId=135433093"""
    pass


@click.command()
def update():
    """更新Pyocs版本"""
    os.system("pip3 install --upgrade pyocs --user")


@click.command()
@click.option('--ocs', help='OCS订单号')
@click.option('--test', default='F', help='测试类型N、A、B、C、D、E、F')
@click.option('--message', default='Jenkins Auto Config System', help='OCS备注')
@click.option('--bin', default='False', help='是否做bin(True/False)')
def autoconf(ocs, test, message, bin):
    """获取OCS订单需求,生成配置，自动提交,返回model id"""
    try:
        obj = PyocsAutoConfig()
        para = obj.auto_config_by_ocs(ocs_number=ocs, test=test, message=message, is_make_bin=bin)
        click.echo(para)
    except ProjectNoSupportError:
        click.echo("Fail:暂不支持此方案，请勿重复提交")
    except CustomerNoSupportError:
        click.echo("Fail:暂不支持此客户，请勿重复提交")
    except NoRegionError:
        click.echo("Fail:订单无区域信息，请确认推动解决区域问题")
    except OcsRegionError:
        click.echo("Fail:订单区域错误，请推动解决区域问题")
    except ReadPwmError:
        click.echo("Fail:占空比错误，请检查订单占空比格式是否正确")
    except No358GaiaAI:
        click.echo("Fail:358 没有导入GAIA AI，请确认")
    except OcsSystemError:
        click.echo("Fail:无法访问OCS系统，请确认")
    except GitError:
        click.echo("Fail:代码服务器存在问题，请确认")
    except RuntimeError:
        raise


@click.command()
@click.option('--ocs', help='OCS订单号')
@click.option('--excel', help='excel参数')
@click.option('--workspace', help='工作路径')
@click.option('--test', default='F', help='测试类型N、A、B、C、D、E、F')
@click.option('--message', default='Jenkins Auto Config System', help='OCS备注')
@click.option('--bin', default='False', help='是否做bin(True/False)')
@click.option('--check', default='False', help='预检资源')
def autodt(ocs, excel, workspace, test, message, bin, check):
    """获取OCS订单需求,生成配置，自动提交,返回model id"""
    obj = PyocsAutoConfig()
    if check == 'False':
        para = obj.auto_config_by_excel(ocs_num=ocs, excel_para=excel, workspace=workspace, test=test,
                                        message=message, is_make_bin=bin)
        click.echo(para)
    else:
        ret = obj.pre_check_for_customer_demand_excel_resource(ocs_num=ocs, excel_para=excel, workspace=workspace)
        click.echo(ret)


@click.command()
@click.option('--ocs', default="", help='OCS订单号')
@click.option('--batch', default="", help='通过生产批次号进行订单查询生产数量')
@click.option('--content', default='demand', help='需要从订单上获取内容类型：例如：title(订单摘要)、demand(订单需求)，默认为demand')
def require(ocs, batch, content):
    """获取OCS订单的简化信息"""
    if ocs == "" and batch != "":
        product_number = PyocsDemand().get_number_by_product_batch_code(batch)
        print("生产批次号:" + batch + "\n生产数量:" + product_number)
    else:
        if content == 'title':
            title = PyocsDemand(ocs).get_ocs_title()
            click.echo(title)
        elif content == 'demand':
            ret = PyocsDemand(ocs).get_request()
            pprint.PrettyPrinter(indent=4).pprint(ret)
        elif content == 'project':
            project = PyocsDemand(ocs).get_ocs_project_name()
            click.echo(project)
        elif content == 'customer_batch_code':
            customer_batch_code = PyocsDemand(ocs).get_customer_batch_code()
            click.echo(customer_batch_code)
        elif content == 'flash_description':
            flash_descriptrion = PyocsDemand(ocs).get_flash_model()
            click.echo(flash_descriptrion)
        elif content == 'customer_model':
            customer_model = PyocsDemand(ocs).get_customer_machine()
            click.echo(customer_model)


@click.command()
@click.option('--content', default='ocs_id', help='获取ocs list的内容指定,例如：ocs_id(获取ocs id)、customer_id(获取客户批号)、engineer_id(获取工程师)')
@click.option('--search_id', help='通过search id获取ocs的ID')
def mid_ocs_list(search_id, content):
    """获取OCS订单的简化信息"""
    j = pyocs_list.PyocsList()
    if content == 'ocs_id':
        project = j.get_ocs_id_list(search_id)
    elif content == 'customer_id':
        project = j.get_ocs_customerId_list(search_id)
    elif content == 'engineer_id':
        project = j.get_ocs_engineer_list(search_id)
    elif content == 'sample_ocs_id':
        si = pyocs_searchid.PyocsSearchid(search_id, 'https://ocs-api.gz.cvte.cn/tv/Reqs/sample_order_index/range:all/SearchId:')
        project = si.get_sample_ocs_id_list()
    click.echo(project)

@click.command()
@click.option('--ocs', help="传入ocs id")
@click.option('--content', help="修改内容：test(修改测试类型), confirm(修改客户确认状态), xml(修改xml), copy_emmc(只使用库存的emmc bin), \
    get_test(获取测试类型，传入ocs，获取最大的测试类型), engineer(设置软件工程师)")
@click.option('--sw', default='all', help='需要修改的软件， 默认为all（全部未禁用软件的信息更新）')
@click.option('--data', help="传入数据，test(传入测试类型：N,A,B,C,D,E,F,G,BC)，confirm（传入客户确认状态：1-未确认, 3-口头确认, 4-邮件确认, 5-不需确认), \
    xml(传入本地xml的路径), copy_emmc(传入软件的压缩包名字, 然后去查找emmc), engineer(传入中文的软件工程师名字)")
def edit(ocs, content, sw, data):
    """修改已传的ocs"""
    edit_task = pyocs_edit.PyocsEdit()
    if content == 'test':
        project = edit_task.update_ocs_test_type(ocs_number=ocs, sw_name=sw, test_type=data)
    elif content == 'confirm':
        project = edit_task.update_ocs_customer_confirm(ocs_number=ocs, sw_name=sw, confirm_type=data)
    elif content == 'xml':
        project = edit_task.update_ocs_xml(ocs_number=ocs, xmlpath=data, sw_name=sw)
    elif content == 'copy_emmc':
        project = edit_task.copy_emmcbin_only(ocs_number=ocs, sw_name=sw)
    elif content == 'get_test':
        project = edit_task.get_test_type(ocs_number=ocs)
    elif content == 'engineer':
        project = edit_task.set_engineer(ocs_number=ocs, user=data)
    else:
        project = 'The content is null'
    click.echo(project)


@click.command()
@click.argument('models', nargs=-1)
@click.option('--mail',type=str,help='客户邮件地址(多个地址请用英文冒号" ; "分隔)')#不定量参数，tuple类型参数 #
@click.option('--mail_cc',type=str,help='抄送人邮件地址(多个地址请用英文冒号" ; "分隔)，默认抄送自己，不填写则不抄送客户')#不定量参数，tuple类型参数 #
@click.option('--mail_title', type=str, help='邮件主题，不填写则使用OCS订单上的摘要作为主题')#不定量参数，tuple类型参数
@click.option('--cmd',type=click.Choice(['make ocs','make differ','make fast_upgrade_ota','make debug','make config',\
                                         'make config EN_CFG_CHECK=0']), default='make ocs',help='编译命令，默认 make ocs')
@click.option('--ota_url',type=str,help='make differ 参数')
@click.option('--cherry_pick',type=str,help='多个提交ID请用空格分隔')
@click.option('--other_ocs',type=str,help='上传到指定的OCS，批量请用空格隔开')
def jenkins(models,cmd,mail,mail_cc,mail_title,cherry_pick,ota_url,other_ocs):
    """向Jenkins FAE软件云编译提交编译请求"""

    build_cmd_param_dict = {}
    if cmd == 'make ocs':
        build_cmd_param_dict['BUILD_CMD']='make ocs'

    elif cmd == 'make differ':
        build_cmd_param_dict['BUILD_CMD']='make differ'
        if ota_url :
            build_cmd_param_dict['OTA_URL'] = ota_url
        else:
            print('请输入make differ 参数:')
            build_cmd_param_dict['OTA_URL'] = input("OTA_URL:")
        # print("OTA_URL = "+build_cmd_param_dict['OTA_URL'] )

        while 1:
            ret = input("OTA_SKIP_REF（Y,N），默认为N:")
            if not ret:
                build_cmd_param_dict['OTA_SKIP_REF'] = 'False'
                break
            elif ret is 'Y' or ret is 'y':
                build_cmd_param_dict['OTA_SKIP_REF'] = 'True'
                break
            elif ret is 'N' or ret is 'n':
                build_cmd_param_dict['OTA_SKIP_REF'] = 'False'
                break
            else:
                print('输入错误，请重新输入！！！')
        # print("OTA_SKIP_REF = "+build_cmd_param_dict['OTA_SKIP_REF'] )

    elif cmd == 'make fast_upgrade_ota':
        build_cmd_param_dict['BUILD_CMD']='make fast_upgrade_ota'
    # print( 'BUILD_CMD = ' + build_cmd_param_dict['BUILD_CMD'])

    elif cmd == 'make debug':
        build_cmd_param_dict['BUILD_CMD']='make debug'

    elif cmd == 'make config':
        build_cmd_param_dict['BUILD_CMD']='make config'

    elif cmd == 'make config EN_CFG_CHECK=0':
        build_cmd_param_dict['BUILD_CMD']='make config EN_CFG_CHECK=0'

    if mail :
        build_cmd_param_dict['SEND_CUSTOMER_EMAIL'] = mail
        # print('SEND_CUSTOMER_EMAIL = ' + build_cmd_param_dict['SEND_CUSTOMER_EMAIL'])

    if mail_cc :
        build_cmd_param_dict['EMAIL_CC'] = mail_cc
        # print('EMAIL_CC = ' + build_cmd_param_dict['EMAIL_CC'])

    if mail_title :
        build_cmd_param_dict['EMAIL_TITLE'] = mail_title
        # print('EMAIL_TITLE = ' + build_cmd_param_dict['EMAIL_TITLE'] )
    
    if cherry_pick:
        build_cmd_param_dict['CHERRY_PICK'] = cherry_pick
        # print('CHERRY_PICK = ' + build_cmd_param_dict['CHERRY_PICK'] )

    if other_ocs:
        build_cmd_param_dict['UPLOAD_SPECIFIC_OCS'] = other_ocs
        print('UPLOAD_SPECIFIC_OCS = ' + build_cmd_param_dict['UPLOAD_SPECIFIC_OCS'] )


    if models != ():
        for model in models:
            print("\n提交编译 MODEL_ID: %s" % model)
            j = pyocs_jenkins.PyocsJenkins()
            j.create_jenkins_job(model,build_cmd_param_dict)
    else:
        while 1:
            model = input(" 请输入model_id（输入E结束提交）: ")
            if(model == 'e' or model == 'E'):
                exit(0)
            j = pyocs_jenkins.PyocsJenkins()
            j.create_jenkins_job(model,build_cmd_param_dict)
            print("======已提交编译model_id: %s ======" % model)

@click.command()
@click.argument('model_id', nargs=-1)
def updatesw(model_id):
    """编译指定model ID软件，并创建新意向订单，用以上传软件"""
    if model_id == ():
        print("请输入model ID")
        exit(0)
    new_ocs_id = create_intention_order()
    if new_ocs_id:
        build_cmd_param_dict = {}
        build_cmd_param_dict['UPLOAD_SPECIFIC_OCS'] = new_ocs_id
        j = pyocs_jenkins.PyocsJenkins()
        j.create_jenkins_job(model_id[0],build_cmd_param_dict)
    else:
        print("Error：创建意向订单失败")

@click.command()
@click.argument('model')
def status(model):
    """从Jenkins 获取软件编译状态"""
    j = pyocs_jenkins_status.PyocsJenkinsStatus()
    print("查询中...\n")
    j.require_jenkins_build_status(model)

@click.command()
@click.option('-n',type=str,help='指定捞取超n天的订单,不指定则默认捞取超7天订单')
def checkocs(n):
    """查询超期订单"""
    sw_module = pyocs_software.PyocsSoftware()
    n = n if n else 7
    ocs_order_list = sw_module.get_overdue_7d_older(n)
    if len(ocs_order_list)>0:
        for order in ocs_order_list:
            print("超" + str(n) + "天订单：" + order)
    else:
        print("未查询到超"+str(n) + "天订单")


@click.command()
@click.option('--sw', type=str, help='需要获取下载链接的软件全名')
@click.option('--ocs', type=str, help='需要获取下载链接的OCS订单号')
def download(sw, ocs):
    """获取软件外网下载链接"""
    _search_task = pyocs_software.PyocsSoftware()
    if ocs:
        print("当前OCS订单号：" + ocs)
        result_list = _search_task.get_download_link_by_ocs(ocs)
        if len(result_list) == 0:
            print("---------------------")
            print("无可用软件信息,请确认当前订单是否软件被锁定")
        for result in result_list:
            print("---------------------")
            print("软件包名：" + result.name)
            print("下载链接：" + result.download_link + " 有效截止时间：" + result.deadline)
    elif sw:
        result = _search_task.get_download_link_by_software_name(sw)
        print("软件包名：" + result.name)
        print("下载链接：" + result.download_link + " 有效截止时间：" + result.deadline)


@click.command()
@click.option('--sw', type=str, help='需要刷新的版本')
@click.option('--txt', type=str, help='批量刷新的txt文件')
def refresh(txt, sw):
    """刷新软件下载链接"""
    refresh_task = pyocs_software.PyocsSoftware()
    if txt and ".txt" in txt:
        """从文件批量刷新下载链接"""
        sw_list = []
        with open(txt) as file:
            for index in file.readlines():
                if index is not None:
                    sw_list.append(index.strip('\n'))
        for sw_info in sw_list:
            result = refresh_task.get_refresh_software_download_link_by_sw_info(sw_info)
            if not result:
                print(sw_info + "软件未找到或被锁定，请确认!")
            else:
                for sw_download in result:
                    print("刷新软件：" + sw_info)
                    print("软件包名：" + sw_download.name)
                    print("下载链接：" + sw_download.download_link + " 有效截止时间：" + sw_download.deadline + "\n")
    elif sw:
        """只刷新一个软件版本"""
        result = refresh_task.get_refresh_software_download_link_by_sw_info(sw)
        if not result:
            print("软件未找到或被锁定，请确认!")
        else:
            for sw_download in result:
                print("软件包名：" + sw_download.name)
                print("下载链接：" + sw_download.download_link + " 有效截止时间：" + sw_download.deadline)


@click.command()
@click.option('--ocs', help='需要做bin的订单')
@click.option('--sw', help='需要做bin的软件名')
def autobin(ocs, sw):
    """ --ocs 传入订单号，对此订单上的启用的软件发起做bin
    或  --sw 传入软件名，对此软件发起做bin
    """
    if ocs:
        sw_module = pyocs_software.PyocsSoftware()
        sw_list = sw_module.get_enable_software_list(ocs)
        if sw_list:
            for sw in sw_list:
                while 1:
                    ret = input("请确认做bin软件名：" + sw.name + "是否正确（Y/N）：")
                    if ret is 'Y' or ret is 'y':
                        sw_module.set_master_sw(sw.fw_id)
                        ret = sw_module.auto_make_bin(ocs, sw.attachment_id)
                        if ret:
                            print("成功发起做bin")
                        else:
                            print("做bin失败，请重新尝试")
                        break
                    elif ret is 'N' or ret is 'n':
                        break
                    else:
                        print('输入错误，请重新输入！！！')
                        continue
    elif sw:
        sw_module = pyocs_software.PyocsSoftware()
        ret = sw_module.auto_make_bin_by_sw_name(sw)
        if ret:
            print("success")
        else:
            print("failed")


@click.command()
@click.option('--content', help='需要获取的资源,常给jenkins用')
def resource(content):
    """获取一些资源"""
    if content == 'signature':
        ret = pyocs_jenkins.PyocsJenkins.get_jenkins_mail_signature()
        click.echo(ret)


@click.command()
@click.option('--ocs', help='ocs订单号')
@click.option('--type', default='order', help='备注类型，order:订单备注；fac:工厂测试备注')
@click.argument("message")
def comment(ocs, type, message):
    """给订单增加备注信息，eg: pyocs comment --ocs=434390 message"""
    sw = pyocs_software.PyocsSoftware()
    if ocs is None:
        click.echo("参照 --ocs=434390 传入需要增加备注信息的ocs订单号")
    elif type == 'fac':
        sw.comment_factory_test_info(ocs_num=ocs, message=message)
    elif type == 'order':
        sw.add_comment_to_ocs(ocs_number=ocs, message=message)
    else:
        click.echo("还未添加此种类型的备注功能")

@click.command()
@click.option('--ocs', help='订单OCS号')
@click.argument("ocs")
def setpreupload(ocs):
    """修改OCS订单为待上传软件状态"""
    sw = pyocs_software.PyocsSoftware()
    ret = sw.set_ocs_status(ocs_number=ocs, status_type=20)

def get_burn_info_with_upload(ocs):
    sw = pyocs_software.PyocsSoftware()
    ddr_info_str = PyocsDemand(ocs).get_ddr_info()
    if not ddr_info_str:
        raise RuntimeError("无法获取DDR信息，请确认订单状态")

    ddr_info_dict = eval(ddr_info_str)
    print(ddr_info_dict)
    burn_place_hold_nums = ddr_info_str.count('refDec')
    burn_place_hold_itemNo = ddr_info_dict['categoryDescp']
    flash_list1 = ['EMMC FLASH', 'NAND FLASH']
    flash_list2 = ['NOR FLASH']
    if 1 == burn_place_hold_nums:
        if ddr_info_dict['refDec'] is None:
            click.echo("烧录位号为null，不存在，默认不设置；烧录方式默认离线烧录")
            burn_place_hold_type = ''
            burn_type = sw.sw_burn_type["离线烧录"]
        else:
            click.echo("订单录入的烧录位号只有一种，默认匹配设置，详情如下：")
            burn_place_hold = '【' + ddr_info_dict['refDec'] + '】,' + ddr_info_dict['supplierNo'] + ',' + \
                            ddr_info_dict['itemNo'] + ',' + ddr_info_dict['categoryDescp'] + ',' + ddr_info_dict['capacity']
            click.echo("烧录位号: " + burn_place_hold)
            burn_place_hold_type = ddr_info_dict['refDec']
            if burn_place_hold_itemNo in flash_list1:
                burn_type = sw.sw_burn_type["在线烧录"]
                click.echo("烧录类型：" + "在线烧录")
            elif burn_place_hold_itemNo in flash_list2:
                burn_type = sw.sw_burn_type["离线烧录"]
                click.echo("烧录类型：" + "离线烧录")
    elif 2 == burn_place_hold_nums:
        if ddr_info_dict['refDec'] is None or ddr_info_dict['refDec1'] is None:
            click.echo("烧录位号为null，不存在，默认不设置；烧录方式默认离线烧录")
            burn_place_hold_type = ''
            burn_type = sw.sw_burn_type["离线烧录"]
        else:
            categoryDescp = [ddr_info_dict['categoryDescp'], ddr_info_dict['categoryDescp1']]

            if categoryDescp.count('DDR') == 1:#刚好有一个是DDR，那就用非DDR的那个
                click.echo("烧录位号只有一个非DDR类型的，默认设置烧录位号为非DDR类型的")
                if categoryDescp[0] == 'DDR':
                    burn_place_hold_type = ddr_info_dict['refDec1']
                    burn_place_hold_itemNo = ddr_info_dict['categoryDescp1']
                else:
                    burn_place_hold_type = ddr_info_dict['refDec']
                    burn_place_hold_itemNo = ddr_info_dict['categoryDescp']
                if burn_place_hold_itemNo in flash_list1:
                    burn_type = sw.sw_burn_type["在线烧录"]
                    click.echo("烧录类型：" + "在线烧录")
                elif burn_place_hold_itemNo in flash_list2:
                    burn_type = sw.sw_burn_type["离线烧录"]
                    click.echo("烧录类型：" + "离线烧录")
                click.echo("烧录位号：" + burn_place_hold_type)
            else:
                click.echo("订单录入的烧录位号有两种，请手动设置，详情如下：")
                burn_place_hold = '【' + ddr_info_dict['refDec'] + '】,' + ddr_info_dict['supplierNo'] + ',' + \
                                ddr_info_dict['itemNo'] + ',' + ddr_info_dict['categoryDescp'] + ',' + ddr_info_dict['capacity']
                burn_place_hold_option = ddr_info_dict['refDec']
                burn_place_hold1 = '【' + ddr_info_dict['refDec1'] + '】,' + ddr_info_dict['supplierNo1'] + ',' + \
                                ddr_info_dict['itemNo1'] + ',' + ddr_info_dict['categoryDescp1'] + ',' + ddr_info_dict['capacity1']
                burn_place_hold_option1 = ddr_info_dict['refDec1']
                click.echo("烧录位号: \n"
                        "1: " + burn_place_hold + "\n"
                        "2: " + burn_place_hold1)
                burn_place_hold_str = '请输入烧录位号选项' + '(' + burn_place_hold_option + ', ' + burn_place_hold_option1 + '): '
                burn_place_hold_type = input(burn_place_hold_str)
                burn_place_hold_type = burn_place_hold_type.upper()
                click.echo("烧录类型：\n"
                        "1 : 在线烧录\n"
                        "2 : 离线烧录")
                burn_type = input("请输入烧录类型选项(1,2)：")
    elif 3 == burn_place_hold_nums:
        if ddr_info_dict['refDec'] is None or ddr_info_dict['refDec1'] is None or ddr_info_dict['refDec2'] is None:
            click.echo("烧录位号为null，不存在，默认不设置；烧录方式默认离线烧录")
            burn_place_hold_type = ''
            burn_type = sw.sw_burn_type["离线烧录"]
        else:
            categoryDescp = [ddr_info_dict['categoryDescp'], ddr_info_dict['categoryDescp1'], ddr_info_dict['categoryDescp2']]

            if categoryDescp.count('DDR') == 2:#刚好有两个是DDR，那就用非DDR的那个
                click.echo("烧录位号只有一个非DDR类型的，默认设置烧录位号为非DDR类型的")
                if categoryDescp[0] != 'DDR':
                    burn_place_hold_type=ddr_info_dict['refDec']
                    burn_place_hold_itemNo = ddr_info_dict['categoryDescp']
                elif categoryDescp[1] != 'DDR':
                    burn_place_hold_type = ddr_info_dict['refDec1']
                    burn_place_hold_itemNo = ddr_info_dict['categoryDescp1']
                else:
                    burn_place_hold_type = ddr_info_dict['refDec2']
                    burn_place_hold_itemNo = ddr_info_dict['categoryDescp2']
                if burn_place_hold_itemNo in flash_list1:
                    burn_type = sw.sw_burn_type["在线烧录"]
                    click.echo("烧录类型：" + "在线烧录")
                elif burn_place_hold_itemNo in flash_list2:
                    burn_type = sw.sw_burn_type["离线烧录"]
                    click.echo("烧录类型：" + "离线烧录")
                click.echo("烧录位号：" + burn_place_hold_type)
            else:
                click.echo("订单录入的烧录位号有两种，请手动设置，详情如下：")
                burn_place_hold = '【' + ddr_info_dict['refDec'] + '】,' + ddr_info_dict['supplierNo'] + ',' + \
                                ddr_info_dict['itemNo'] + ',' + ddr_info_dict['categoryDescp'] + ',' + ddr_info_dict['capacity']
                burn_place_hold_option = ddr_info_dict['refDec']
                burn_place_hold1 = '【' + ddr_info_dict['refDec1'] + '】,' + ddr_info_dict['supplierNo1'] + ',' + \
                                ddr_info_dict['itemNo1'] + ',' + ddr_info_dict['categoryDescp1'] + ',' + ddr_info_dict['capacity1']
                burn_place_hold_option1 = ddr_info_dict['refDec1']
                burn_place_hold2 = '【' + ddr_info_dict['refDec2'] + '】,' + ddr_info_dict['supplierNo2'] + ',' + \
                                ddr_info_dict['itemNo2'] + ',' + ddr_info_dict['categoryDescp2'] + ',' + ddr_info_dict['capacity2']
                burn_place_hold_option2 = ddr_info_dict['refDec2']
                click.echo("烧录位号: \n"
                        "1: " + burn_place_hold + "\n"
                        "2: " + burn_place_hold1 + "\n"
                        "3: " + burn_place_hold2)
                burn_place_hold_str = '请输入烧录位号选项' + '(' + burn_place_hold_option + ', ' + burn_place_hold_option1 + burn_place_hold_option2 + '): '
                burn_place_hold_type = input(burn_place_hold_str)
                burn_place_hold_type = burn_place_hold_type.upper()
                click.echo("烧录类型：\n"
                        "1 : 在线烧录\n"
                        "2 : 离线烧录")
                burn_type = input("请输入烧录类型选项(1,2)：")
    else:
        click.echo("存储器信息异常")
    return burn_place_hold_type, burn_type

@click.command()
@click.option('--software', help='软件所在的路径（相对路径或者绝对路径）')
@click.option('--old', help='库存软件名（软件名或版本号）')
@click.option('--direct', help='是否直接上传查询到的第一个软件，使用old参数时有效')
@click.option('--cps', help='CPS软件名（软件名或版本号）')
@click.option('--test_type', help='测试类型（上传CPS的软件）')
@click.option('--bin', help='是否做bin(True/False)')
@click.argument("ocs")
def upload(ocs, software, old, direct, cps, test_type, bin):
    """给订单上传软件，库存软件支持批量上传"""
    if old:  # 如果传参old则上传库存软件
        ocs_list = ocs.split(",")
        sw = pyocs_software.PyocsSoftware()
        old_sw_dict = sw.find_old_sw_id_by_name(old_sw_name=old)
        if old_sw_dict:
            for old_sw_id, old_sw_name in old_sw_dict.items():
                while 1:
                    if direct:
                        ret = 'Y'
                    else:
                        ret = input("请确认库存软件名：" + old_sw_name + "是否正确（Y/N）：")
                    if ret not in {'Y', 'y', 'N', 'n'}:
                        continue
                    else:
                        break
                if ret is 'Y' or ret is 'y':
                    for ocs_number in ocs_list:
                        burn_place_hold_type, burn_type = get_burn_info_with_upload(ocs_number)
                        is_success = sw.upload_old_sw_by_id(ocs_num=ocs_number, old_sw_id=old_sw_id, burn_place_hold=burn_place_hold_type, burn_type=burn_type)
                        sta = ocs_number
                        sta += "上传成功" if is_success else "上传失败"
                        click.echo(sta)
                        if is_success:
                            sta += "上传成功"
                            if bin:
                                click.echo("--------------------发起做bin申请----------------------")
                                sw_list = sw.get_enable_software_list(ocs)
                                for sw_nm in sw_list:
                                    sw.set_master_sw(sw_nm.fw_id)
                                    ret = sw.auto_make_bin(ocs, sw_nm.attachment_id)
                                    if ret:
                                        click.echo("做bin申请成功")
                                    else:
                                        click.echo("做bin申请失败")
                        else:
                            sta += "上传失败"
                    break
                elif ret is 'N' or ret is 'n':
                    continue
        else:
            click.echo("无法搜索到库存软件，请自行检查原因")
            os.sys.exit(0)
        os.sys.exit(1)

    if cps:
        ocs_list = ocs.split(",")
        sw = pyocs_software.PyocsSoftware()
        cps_sw_msg_list = sw.find_cps_id_by_name(cps)
        if test_type is None:#默认不用测试
            test_type = 'N'
        if test_type not in {'N', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'BC'}:
            return False
        if cps_sw_msg_list:
            for ocs_number in ocs_list:
                        click.echo("正在上传到订单：" + ocs_number)
                        first_sign = True
                        burn_place_hold_type, burn_type = get_burn_info_with_upload(ocs_number)
                        for i in reversed(range(len(cps_sw_msg_list[0]))):
                            sw_name = cps_sw_msg_list[0][i]
                            click.echo(sw_name + " 上传中...")
                            ##EMMCBIN固定是要离线烧录的
                            if re.match("EMMCBIN",sw_name):
                                click.echo("此软件包为EMMCBIN，固定设置烧录方式为离线烧录")
                                is_success = sw.upload_cps_sw_by_id(ocs_num=ocs_number , cps_sw_name=cps_sw_msg_list[0][i],cps_sw_id=cps_sw_msg_list[1][i],
                                                                    cps_xml_name=cps_sw_msg_list[2][i],cps_xml_id=cps_sw_msg_list[3][i],build_id=cps_sw_msg_list[4][i],
                                                                    burn_place_hold=burn_place_hold_type, burn_type=sw.sw_burn_type["离线烧录"], disable_origin_sw=first_sign,
                                                                    Test_type=test_type)
                            else:
                                is_success = sw.upload_cps_sw_by_id(ocs_num=ocs_number,
                                                                    cps_sw_name=cps_sw_msg_list[0][i],
                                                                    cps_sw_id=cps_sw_msg_list[1][i],
                                                                    cps_xml_name=cps_sw_msg_list[2][i],
                                                                    cps_xml_id=cps_sw_msg_list[3][i],
                                                                    build_id=cps_sw_msg_list[4][i],
                                                                    burn_place_hold=burn_place_hold_type,
                                                                    burn_type=burn_type, disable_origin_sw=first_sign,Test_type=test_type)
                            first_sign=False
                            sta = sw_name
                            sta += "上传成功" if is_success else "上传失败"
                            click.echo(sta)
        else:
            click.echo("无法搜索到库存CPS软件，请自行检查原因")
            os.sys.exit(1)
        os.sys.exit(0)

    if software is None:
        code_root_path = PyocsFileSystem.get_current_code_root_dir()
        if code_root_path:
            ab_code_root_path = os.path.abspath(code_root_path)
            bin_sw_path = ab_code_root_path + '/bin'
            images_sw_path = ab_code_root_path + '/images'
            if os.path.exists(bin_sw_path):
                software = bin_sw_path
            elif os.path.exists(images_sw_path):
                software = images_sw_path
            for files in os.listdir(software):
                if os.path.splitext(files)[1] == '.zip' or os.path.splitext(files)[1] == '.tar' or os.path.splitext(files)[1] == '.7z':
                    software = software + '/' + files
        else:
            return False

    tail = software.split('.')[-1]
    xml_path = software.split('.' + tail)[0] + '.xml'
    if not os.path.exists(xml_path) and "EMMCBIN" in xml_path:
        xml_path = re.sub(r'EMMCBIN_', '', xml_path)
    # xml_path = sw_path.split('/')[-1].split('.')[0] + '.xml'
    if os.path.exists(software) and os.path.exists(xml_path):
        sw = pyocs_software.PyocsSoftware()
        current_test_type = sw.get_test_type_from_ocs(ocs)
        if current_test_type is None:
            current_test_type = "当前OCS为样机or无软件"
        while 1:
            click.echo("测试类型如下：\n"
                       "A : A类 - 全面测试\n"
                       "B : B类 - 针对遥控器的测试\n"
                       "C : C类 - 局部修改针对性测试\n"
                       "D : D类 - 测配屏\n"
                       "E : E类 - 首测，无任何功能及BUG的修改\n"
                       "F : F类 - 过硬件首测，只要求匹配硬件\n"
                       "G : G类 - 仅测试BOOT\n"
                       "BC : B+C - 新遥控器测试，局部功能修改/添加\n"
                       "N : 不用测试\n"
                       "OCS最新软件测试类型：" + current_test_type + " \n ")
            test_type = input("请输入测试类型(N,A,B,C,D,E,F,G,BC)：")
            test_type = test_type.upper()
            if test_type not in {'N', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'BC'}:
                click.echo("测试类型输入错误，请重新输入")
                continue

            click.echo("------------------烧录位号和烧录方式-------------------")

            burn_place_hold_type, burn_type = get_burn_info_with_upload(ocs)
            if ('EMMCBIN' in software or 'NANDBIN' in software) and burn_type == sw.sw_burn_type["在线烧录"]:
                burn_type = sw.sw_burn_type["离线烧录"]
                click.echo("上传的是bin软件，强制修改烧录类型为：" + "离线烧录")

            click.echo("-----------------------------------------------------")

            message = input("请输入软件备注：")
            ret = sw.upload_software_to_ocs(ocs_num=ocs, zip_path=software,
                                            xml_path=xml_path, test_type=sw.sw_test_type[test_type],
                                            burn_place_hold=burn_place_hold_type, burn_type=burn_type, message=message)
            sw_name = software.split('/')[-1]
            if ret:
                while sw_name\
                        not in sw.get_enable_software_list_from_html(PyocsDemand(ocs_number=ocs).get_ocs_html()):
                    continue
                else:
                    if 'EMMCBIN' in software or 'NANDBIN' in software:
                        sw_dlink = sw.get_software_download_link(ocs_number=ocs, sw_name=sw_name, exclude_bin=False, use_cache=False)
                    else:
                        sw_dlink = sw.get_software_download_link(ocs_number=ocs, sw_name=sw_name, use_cache=False)
                    click.echo("--------------------XML不匹配项----------------------")
                    xml_echo_flg = True
                    audit_link = sw.get_enable_sw_audit_link(ocs_number=ocs)
                    if audit_link is None:
                        xml_echo_flg = False
                    else:
                        audit_msg = sw.get_self_audit_msg(audit_link_str=audit_link)
                        if audit_msg is None:
                            xml_echo_flg = False
                    if xml_echo_flg:
                        for msg in audit_msg:
                            click.echo(msg)
                    click.echo("-----------------------------------------------------")
                    click.echo(use_style("软件包名：" + sw_dlink.name, mode="bold"))
                    click.echo(use_style("下载链接：" + sw_dlink.download_link +
                                         " 有效截止时间：" + sw_dlink.deadline, mode="bold"))
                    click.echo("-----------------------------------------------------")
                    click.echo("上传完成")
            else:
                click.echo("上传失败")
            break
    else:
        click.echo("本地未找到上传软件")
        click.echo("确认软件包路径是否正确：" + software)
        click.echo("确认xml路径是否正确：" + xml_path)


@click.command()
@click.option('--src', help='源订单号')
@click.option('--dst', help='目标订单号')
@click.option('--workspace', help='工作区（jenkins参数）')
def copy(src, dst, workspace):
    """从源订单上拷贝所有启用状态下的库存软件到目标订单上"""
    try:
        dst_ocs_list = dst.split(";")
        if not workspace:
            workspace = os.getcwd()
        for dst_ocs in dst_ocs_list:
            sw = pyocs_software.PyocsSoftware()
            sw.reuse_old_sw_from_src_to_dst(src_ocs=src, dst_ocs=dst_ocs, workspace=workspace)
    except NoSoftwareError:
        click.echo("Fail:源订单上无软件")
    except ReviewExcelError:
        click.echo("Fail:客户批号信息不匹配，请检查并重新上传Excel")


@click.command()
@click.option('--ocs', help='订单号')
@click.argument("color")
def mark(ocs, color):
    """标记订单颜色"""
    de = pyocs_software.PyocsDemand(ocs_number=ocs)
    de.set_flag_color(color)

@click.command()
@click.option('--ocs', help='订单号')
@click.argument("sw_name")
def mid_audit(ocs, sw_name):
    """获取软件审核状态     --ocs传入ocs订单号"""
    sf = pyocs_software.PyocsSoftware()
    link = sf.get_audit_failed_link(ocs, sw_name)
    if link:
        audit_link = sf.get_enable_sw_audit_link(ocs)
        audit_msg = sf.get_self_audit_msg(audit_link)
        click.echo('软件自动审核不通过，请检查\n%s' % link)
        click.echo('审核不匹配项如下：')
        for msg in audit_msg:
            click.echo(msg)


@click.command()
@click.option('--ocs', help='订单号')
@click.argument("sw_name")
def mid_ocs_audit(ocs, sw_name):
    """获取软件审核状态     --ocs传入ocs订单号"""
    CHECK_STATUS_FLAG = 1  # 用于定义是否执行检测
    if CHECK_STATUS_FLAG:
        click.echo('由于OCS系统更新，脚本无法获取审核差异项，暂停显示审核差异详情')
    else:
        sf = pyocs_software.PyocsSoftware()
        demand = pyocs_software.PyocsDemand(ocs)
        link = sf.get_audit_failed_link(ocs, sw_name)
        task_type = demand.get_task_type()
        task_type_list = ["虚拟软件任务", "生产软件任务"]
        if link and (task_type in task_type_list):
            audit_link = sf.get_enable_sw_audit_link(ocs)
            audit_msg = sf.get_self_audit_msg(audit_link)
            click.echo('软件自动审核不通过，请检查\n%s' % link)
            click.echo('审核不匹配项如下：')
            for msg in audit_msg:
                click.echo(msg)

@click.command()
@click.option('--ocs', help='订单号')
def mid_ocs_state(ocs):
    """根据订单状态和任务阶段来设置不同状态，用于jenkins pipeline返回参数"""
    CHECK_STATUS_FLAG = 1 #用于定义是否执行检测
    if CHECK_STATUS_FLAG:
        ret = False
    else:
        demand = pyocs_software.PyocsDemand(ocs)
        software = pyocs_software.PyocsSoftware()
        task_stage = demand.get_task_stage()
        release_state = software.get_enable_sw_release_state(ocs)
        task_stage_list = ["未下计划", "已下计划未发放", "已最终发放"]
        customer = demand.get_ocs_customer()
        task_type = demand.get_task_type()
        # 朝野订单不做拦截：https://kb.cvte.com/pages/viewpage.action?pageId=181674703
        if task_type == "生产软件任务" and release_state is True and task_stage in task_stage_list and customer != "朝野":
            ret = True
        else:
            ret = False
    click.echo(ret)

@click.command()
@click.option('--id', help='key仓库ID')
@click.argument("key_folder_path")
@click.argument("account")
def keyupload(id, key_folder_path, account):
    """ 上传key至指定key仓库：    --id —— 传入key仓库ID；    key_folder_path —— key仓库目录路径名称；     account —— CPS账户 """

    instance = cps_upload_key.CpsUploadKey(account)
    upload_status = instance.upload_key_to_cps_multiple(id, key_folder_path)
    if upload_status:
        click.echo('key上传成功')
    else:
        alert_msg = instance.get_alert_msg()
        email_receiver = instance.get_email_receiver()
        click.echo("{\"error\": \"" + alert_msg + "\", " + "\"email_receiver\": \"" + email_receiver + "\"}")

@click.command()
@click.option('--customer', type=str, help='客户')
@click.option('--engineer', type=str, help='软件工程师')
def tclq(customer: str, engineer: str):
    """ 批量查询tcl软件释放状态 """
    t = tcl_order.TclOrder()
    t.query(customer, engineer)

@click.command()
def myjira():
    """获取状态不等于‘无效’的jira号及其标题 """
    my_jira = pyocs_jira.JiraCVTE()
    my_jira.print_jiras()

@click.command()
@click.argument("customer")
@click.argument("file_name")
@click.option('--workspace', help='工作区（jenkins参数）')
def dg_reuse(customer, file_name, workspace):
    '''代工翻单用 --传入客户名 和 冻结书名（包含路径）'''
    dg_reuse_sw.DGReuseSw.make_res_dir()
    dg_reuse_sw.DGReuseSw.dg_reuse_software(customer, file_name, workspace)

@click.command()
@click.option('--row',help='朝野订单需求表指定行')
def cyocs(row):
    """ 通过ocs号将customer needs 特殊需求备注在ocs评论区"""
    deal_status = CyNeedsToOcs.cli_customer_excel_row_date_to_ocs(row_index=row)
    if deal_status:
        click.echo('客户需求备注成功')
    else:
        click.echo('客户需求备注失败')

@click.command()
@click.option('--id', help='指定需要分配列表的Id')
def mid_ocs_assign(id: str):
    """分配订单软件工程师或者软件审核人员"""
    click.echo("正在分配订单工程师...")
    # if workspace is None:
    #     workspace = '/'
    order_assign = osm_order_assign.OsmOrderAssign()
    ocs_attr_fail_list, ocs_rule_fail_list, ocs_dist_fail_list, ocs_dist_success_list = order_assign.set_ocs_assigner(id)
    if ocs_attr_fail_list == [] and ocs_rule_fail_list  == [] and ocs_dist_fail_list  == []:
        click.echo("全部订单分配完成，没有异常！")
    else:
        if ocs_attr_fail_list != []:
            click.echo("这些订单没有分配属性：" + " ".join(ocs_attr_fail_list))
        if ocs_rule_fail_list != []:
            click.echo("这些订单分配规则异常：" + " ".join(ocs_rule_fail_list))
        if ocs_dist_fail_list != []:
            click.echo("这些订单分配操作失败：" + " ".join(ocs_dist_fail_list))
        if ocs_dist_success_list != []:
            click.echo("这些订单已经分配成功：" + " ".join(ocs_dist_success_list))

@click.command()
@click.option('--searchid', help='指定需要分配的订单列表')
@click.option('--status', help='设置待发放订单状态流')
def mid_ocs_status(searchid: str, status):
    """维护待发放订单状态流"""
    click.echo("正在关闭订单...")
    ocs_sum = 0
    ocs_list = list()
    order_status = opm_order_status.OpmOrderStatus()

    if searchid == '2675115':
        ret_status_dict = order_status.set_ocs_status_by_search_id(searchid, status=80)
        if ret_status_dict['type'] != "无":
            click.echo("已成功关闭的特殊备注的订单: " + ','.join(ret_status_dict['type']))
        else:
            click.echo("没有符合关闭条件的订单关闭")
    elif searchid == '3370029':
        ret_status_dict = order_status.set_ocs_tasks_status_by_searchid(searchid, status=80)
        click.echo("如下TV功能小板订单已直接关闭: " + ','.join(ret_status_dict['type']))
    else:
        si = pyocs_searchid.PyocsSearchid(searchid)
        ext_list = si.get_ocs_id_list_info()
        ext_sum = si.get_searchid_ocs_number()
        ocs_sum += ext_sum
        ocs_list.extend(ext_list)
        if ocs_sum == 0:
            click.echo("没有需要处理的订单")
        else:
            ret_status_dict = order_status.set_ocs_status_by_ocs_list(ocs_list, status=80)
            click.echo("此次处理的待发放订单数量为: " + str(ocs_sum))
            if ret_status_dict['type0'] != "无":
                click.echo("订单已完成状态: " + ','.join(ret_status_dict['type0']))
            if ret_status_dict['type1'] != "无":
                click.echo("软件命名不规范: " + ','.join(ret_status_dict['type1']))
            if ret_status_dict['type2'] != "无":
                click.echo("启用软件超两个: " + ','.join(ret_status_dict['type2']))
            if ret_status_dict['type3'] != "无":
                click.echo("软件可能被锁定: " + ','.join(ret_status_dict['type3']))
            if ret_status_dict['type4'] != "无":
                click.echo("软件没经过测试: " + ','.join(ret_status_dict['type4']))
            if ret_status_dict['type5'] != "无":
                click.echo("软件测试不通过: " + ','.join(ret_status_dict['type5']))
            if ret_status_dict['type6'] != "无":
                click.echo("订单状态不正确: " + ','.join(ret_status_dict['type6']))
            if ret_status_dict['type7'] != "无":
                click.echo("订单转为待测试: " + ','.join(ret_status_dict['type7']))
            if ret_status_dict['type8'] != "无":
                click.echo("视睿订单需提醒: " + ','.join(ret_status_dict['type8']))
            if ret_status_dict['type9'] != "无":
                click.echo("朝野特殊单提醒: " + ','.join(ret_status_dict['type9']))
            if ret_status_dict['type10'] != "无":
                click.echo("此订单未做终测: " + ','.join(ret_status_dict['type10']))
            if ret_status_dict['type11'] != "无":
                click.echo("研发专用单跳过: " + ','.join(ret_status_dict['type11']))
            if ret_status_dict['typex'] != "无":
                click.echo("已成功关闭订单: " + ','.join(ret_status_dict['typex']))

@click.command()
@click.option('--searchid', help='通过searchid指定搜索范围')
@click.option('--addr', help='指定mac地址')
def mid_ocs_find(searchid, addr):
    """通过指定的mac地址查找特定searchid下与之匹配的订单，返回ocs"""
    click.echo("正在查找订单...")
    ocs_request = pyocs_software_report.PyocsSoftwareReport()
    ocs = ocs_request.find_ocs_match_mac_addr(searchid, addr)
    click.echo("查找结果：" + ocs)

@click.command()
@click.argument('abstract', nargs=-1)
# @click.option('--abstract2', help='订单摘要信息')
def find_mac_by_abstract(abstract):
    """通过指定的摘要查找对应订单的MAC区间"""
    click.echo("正在查找订单...")
    for item in abstract:
        click.echo("=========== 摘要：" + item + " ===========")
        ocs_request = pyocs_software_report.PyocsSoftwareReport()
        ocs_list = pyocs_software.PyocsSoftware().get_ocs_number_from_abstract(item)
        if ocs_list:
            for ocs in ocs_list:
                if "[虚拟]" not in PyocsDemand(ocs).get_ocs_title():
                    click.echo("匹配到的OCS：" + ocs)
                    click.echo("此OCS的MAC区间" + str(ocs_request.get_mac_addr_info(str(ocs))))


@click.command()
@click.option('--searchid', help='通过searchid指定搜索范围')
@click.option('--start', help='统计开始日期：例如2020-07-01')
@click.option('--end', help='统计结束日期：例如2020-07-20')
def mid_ocs_data(searchid, start, end):
    """统计OSM订单绩效数据"""
    click.echo("正在计算OSM订单绩效...")
    order_data = osm_order_data.OsmOrderData()
    release_data_dict = order_data.get_release_order_data(searchid, start, end)
    click.echo(release_data_dict)

@click.command()
@click.option('--searchid', help='通过searchid指定订单范围')
@click.option('--ocs', help='指定存放OCS')
def mid_ocs_package(searchid, ocs):
    """通过指定的searchid, 将该searchid包含的ocs订单的启用软件全部下载下来, 然后打包上传到指定ocs, 获取下载链接"""
    click.echo("正在获取下载链接...")
    order = opm_order_status.OpmOrderStatus()
    download_link = order.get_sw_download_link_with_searchid_ocs(searchid, ocs)
    click.echo("下载链接：", download_link)

@click.command()
@click.option('--input', help='过滤器条件之项目组，多个项目组以空格隔开，如："V35X MS6886 T960"')
def mid_ocs_edit(input: str):
    """校正OSM订单烧录方式"""
    click.echo("校正订单烧录方式...")
    order_edit = osm_order_edit.OsmOrderEdit()
    order_edit.update_order_burn_type(input)

@click.command()
@click.option('--ocs', help='ocs 号')
@click.option('--sw_name', help='软件名')
def mid_ocs_set(ocs, sw_name):
    """设置ocs订单软件名sw_name为主程序"""
    pyocs_software.PyocsSoftware().set_master_sw_by_ocs_and_sw_name(ocs, sw_name)

@click.command()
@click.option('--ocs', help='ocs 号')
@click.option('--test', default='N', help='测试类型，默认为不用测试')
def mid_ocs_test(ocs, test):
    """设置ocs所有已启用软件的测试类型，默认类型是不用测试"""
    edit_task = pyocs_edit.PyocsEdit()
    ret = edit_task.set_ocs_test_type_for_all(ocs, test)
    click.echo(ret)

@click.command()
@click.option('--searchid', help='通过searchid指定搜索范围')
@click.option('--type', default='mulVer', help='备注类型，mulVer:多版本软件；swLock:被锁定的软件；mulUploader:多人协同订单')
def mid_ocs_notice(searchid, type):
    """OCS订单异常设置提醒"""
    click.echo("正在查询...")
    order_notice = osm_order_notice.OsmOrderNotice()
    if type == 'mulVer':
        order_notice.send_mail_for_ocs_with_mul_ver(searchid)
    elif type == 'swLock':
        order_notice.send_mail_for_ocs_with_sw_lock(searchid)
    elif type == 'mulUploader':
        order_notice.send_mail_for_ocs_with_mul_uploader(searchid)

@click.command()
@click.option('--info',help='获取指定app_config.json配置的信息。参数:app_cofnig.json路径')
@click.option('--file',help='获取指定app_config.json的Apk文件。参数:app_cofnig.json路径')
@click.option('--xls',help='获取指定app_config.json的翻译表格。参数:app_cofnig.json路径')
@click.option('--allxls',help='在common_app目录下,将所有能RRO的APK文件翻译表格导出到指定文件夹。参数:指定文件夹名称')
@click.option('--res',help='获取指定app_config.json的反编译res资源文件')
@click.option('--allres',help='在common_app目录下,将所有能RRO的APK反编译res资源文件导出到指定文件夹。参数:指定文件夹名称')
def tv_appjson(info,file,xls,allxls,res,allres):
    api_id = "0846725"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)

    """ 通过app_config.json文件获取到此apk的一些信息和文件"""
    if info:
        appjson = pyocs_appjson.PyocsAppJson(info)
        appjson.GetAppInfo(info)
    elif file:
        appjson = pyocs_appjson.PyocsAppJson(file)
        appjson.GetAppFile(".")
    elif xls:
        appjson = pyocs_appjson.PyocsAppJson(xls)
        appjson.GetAppXls(".")
    elif allxls:
        pyocs_appjson.Deal_AppJsonTranslation().GetALLAppTranslationXls(allxls)
    elif res:
        appjson = pyocs_appjson.PyocsAppJson(res)
        appjson.GetAppRes(".")
        appjson.RemoveApktool(".")
    elif allres:
        pyocs_appjson.Deal_AppJsonTranslation().GetALLAppResFile(allres)

@click.command()
@click.option('--name',help='需要获取对应邮件地址的工程师名称')
def mid_emailaddr(name):
    """ 通过指定工程师名称获取对应的邮件地址 """
    email_addr = pyocs_software.PyocsSoftware().get_email_addr_from_ocs(name)
    click.echo(email_addr)

@click.command()
@click.option('--ocs',help='需要获取对应工程师名称的OCS号')
def mid_softengineername(ocs):
    """ 通过指定OCS编号获取对应的软件工程师名字 """
    engineer_name = PyocsDemand(ocs_number=ocs).get_ocs_software_engineer()
    click.echo(engineer_name)

@click.command()
@click.option('--ocs',help='需要获取CKD信息对应的OCS号')
def ckd_info(ocs):
    """ 通过指定OCS编号获取对应订单的CKD信息 """
    engineer_name = PyocsDemand(ocs_number=ocs).get_ocs_ckd_info()
    click.echo(engineer_name)

@click.command()
@click.argument("file_name")
def rsa_decrypt(file_name):
    """ RSA解密 """
    api_id = "3742615"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)

    if os.path.exists(file_name) == False:
        click.echo("文件不存，请检测文件名是否正确！")
        return
    PyocsRsa.rsa_decrypt(file_name)

@click.command()
@click.argument("file_name")
def rsa_encrypt(file_name):
    """ RSA加密 """
    api_id = "3742615"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)

    if os.path.exists(file_name) == False:
        click.echo("文件不存，请检测文件名是否正确！")
        return
    PyocsRsa.rsa_encrypt(file_name)

@click.command()
def rsa_gen_key():
    """ 生成RSA密钥 """
    api_id = "3742615"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)

    PyocsRsa.rsa_gen_key()

@click.command()
def ocs_search_comment():
    """ocs订单场景与对应评论信息查询"""
    click.echo("OCS评论信息...")
    order_edit = opm_order_status.OpmOrderStatus()
    order_edit.get_ocs_comment()

@click.command()
def mid_gerrit_assignee():
    api_id = "8126534"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)
    """从代码审核人列表[https://kb.cvte.com/pages/viewpage.action?pageId=184943467]获取当天审核人邮件地址"""
    assignee = pyocs_gerrit.PyocsGerrit().get_assignee_from_conflunce()
    click.echo(assignee)

@click.command()
def gerrit_gtpush():
    """推送非直推代码时自动填充审核人"""
    ret = pyocs_gerrit.PyocsGerrit().gerrit_gtpush()
    click.echo(ret)

@click.command()
@click.option('--team',help='需要获取信息的战队名称')
@click.option('--fc',help='使用命令操作JIRA的功能，目前支持overdue查询超期数据功能')
def jira(team, fc):
    """ 通过app_config.json文件获取到此apk的一些信息和文件"""
    if (fc == "overdue"):
        if (team == None):
            click.echo("请通过该命令参数--team输入战队的名称! 例如 --team BT5")
        else:
            jira_func = pyocs_jira_func.PyocsJiraFunc()
            jira_func.calculate_the_overdue_rate(team)
            click.echo("------------------------------------命令执行完毕  感谢您的使用--------------------------------------")
    else:
        click.echo("您输入命令参数有误，请重新输入，如对命令有疑问可通过--help获取帮助信息!")

@click.command()
@click.argument("file_name")
def ocs_sw_msg(file_name):
    """ 代工软件任务信息获取 """
    if os.path.exists(file_name) == False:
        click.echo("文件不存，请检测文件名是否正确！")
        return
    if not file_name.endswith(r".csv"):
        click.echo("文件格式不对，请输入csv文件！")
        return
    dg_sw_task_msg.DgSwTaskMsg.dg_get_sw_task_msg(file_name)

@click.command()
@click.option('--boardcode', type=str, help='板卡条形码')
def ocs_get_link(boardcode):
    """从板卡条形码中获取对应的ocs"""

    """BI 计数"""
    api_id = "5632170"
    statistics_url = statistics_url_prefix + api_id +"?user=" + user
    requests.post(statistics_url)

    board_code_len = 12
    if len(boardcode) < board_code_len:
        print("\n输入格式为：pyocs ocs-get-link --boardcode=XXXXXXXXXX-XX \n")
        return

    no_Found_Url = "http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/1"
    get_Link_Task = pyocs_software.PyocsSoftware()
    board_code_List = PyocsConfluence().get_key_value_list_from_kb_table(boardcode[0], "208862276")

    if len(board_code_List) == 0:
        print("找不到对应的工厂代码，请确认条码输入是否有误!!")
        return
    else:
        split_str = board_code_List[0].split(',')
        for code in split_str:
            if boardcode[10]=='0':
                if boardcode[11]=='H' or boardcode[11]=='B':
                    product_code = code + boardcode[1:9]+boardcode[11]
                else:
                    product_code = code + boardcode[1:9]
            else:
                if boardcode[11]=='H' or boardcode[11]=='B':
                    product_code = code + boardcode[1:9]+'_' + boardcode[10:11]
                else:
                    product_code = code + boardcode[1:9] + '_' + boardcode[10]

            url = get_Link_Task.get_ocs_from_board_code(product_code)
            url = url.strip()
            no_Found_Url = no_Found_Url.strip()
            if url == no_Found_Url:
                continue

            print("\n对应的ocs订单为：\n"+ url.replace('range:my/','')+"\n")
            return
        print("\n没有找到对应的ocs订单!!\n")

@click.command()
@click.option('--tag', type=int, help='GAIA类型[1：GAIA; 3：GAIA AI; 5：maxhub share]')
@click.option('--mac', type=str, help='GAIA or GAIA AI:单个mac地址，不需要带间隔符，如：b4ada328d99a\nmaxhubShare:多个mac可以逗号分隔开，或者用-报备mac范围，如b4ada328d99a,b4ada328d99b 或者 b4ada328d99a-b4ada328d99b')
def mac_report(tag, mac):
    if tag == 5:

        """maxhub share报备"""
        mac = mac.upper()
        if ',' in mac:
            ret = ImportArray(mac.split(','))
        elif '-' in mac:
            ret = (mac.split('-')[0], mac.split('-')[1])
        else:
            ret = ImportArray([mac])
        if ret[0] == 200:
            click.echo("报备成功，详细信息：" + ret[1])
        else:
            click.echo("操作失败")

    else:
        """客户样机或者调试机的GAIA软件mac地址报备"""
        api_id = '1568723'
        statistics_url = statistics_url_prefix + api_id + "?user=" + user
        requests.post(statistics_url)
        ret_dict = pyocs_software.PyocsSoftware().report_mac_address_for_gaia(tag, mac)
        if ret_dict['error_code'] == 0:
            click.echo("报备MAC成功")
        else:
            click.echo(ret_dict['message'])

@click.command()
@click.option('--ocs', help='需要上传软件的OCS订单号')
def boe_reuse(ocs):
    "BOE出海信的订单根据订单信息与客户确认软件表上传软件"
    try:
        sw = pyocs_software.PyocsSoftware()
        workspace = os.getcwd()
        sw.reuse_old_sw_for_boe(ocs, workspace)
    except NoConfirmSoftwareError:
        click.echo("确认表中没有找到客户确认的软件！")

@click.command()
@click.option('--ocs', help='上传的订单OCS号')
@click.option('--test_type', help='OCS测试类型')
@click.option('--message', help='OCS备注信息')
def mid_ocs_upload(ocs, test_type, message):
    """给订单上传软件，库存软件支持批量上传"""
    code_root_path = PyocsFileSystem.get_current_code_root_dir()
    if code_root_path:
        ab_code_root_path = os.path.abspath(code_root_path)
        bin_sw_path = ab_code_root_path + '/code/bin'
        if os.path.exists(bin_sw_path):
            software = bin_sw_path
        for files in os.listdir(software):
            if os.path.splitext(files)[1] == '.zip' or os.path.splitext(files)[1] == '.tar' or \
                    os.path.splitext(files)[1] == '.7z':
                software = software + '/' + files
    else:
        return False

    xml_path = re.sub(r'zip|tar|7z', 'xml', software)

    if os.path.exists(software) and os.path.exists(xml_path):
        sw = pyocs_software.PyocsSoftware()
        burn_place_hold_type, burn_type = get_burn_info_with_upload(ocs)
        ret = sw.upload_software_to_ocs(ocs_num=ocs, zip_path=software,
                                        xml_path=xml_path, test_type=sw.sw_test_type[test_type],
                                        burn_place_hold=burn_place_hold_type, burn_type=burn_type, message=message)
        sw_name = software.split('/')[-1]
        if ret:
            while sw_name\
                    not in sw.get_enable_software_list_from_html(PyocsDemand(ocs_number=ocs).get_ocs_html()):
                continue
            else:
                sw_dlink = sw.get_software_download_link(ocs_number=ocs, sw_name=sw_name)
                click.echo("--------------------XML不匹配项----------------------")
                xml_echo_flg = True
                audit_link = sw.get_enable_sw_audit_link(ocs_number=ocs)
                if audit_link is None:
                    xml_echo_flg = False
                else:
                    audit_msg = sw.get_self_audit_msg(audit_link_str=audit_link)
                    if audit_msg is None:
                        xml_echo_flg = False
                if xml_echo_flg:
                    for msg in audit_msg:
                        click.echo(msg)
                click.echo("-----------------------------------------------------")
                click.echo(use_style("软件包名：" + sw_dlink.name, mode="bold"))
                click.echo(use_style("下载链接：" + sw_dlink.download_link +
                                     " 有效截止时间：" + sw_dlink.deadline, mode="bold"))
                click.echo("-----------------------------------------------------")
                click.echo("上传完成")
        else:
            click.echo("上传失败")
    else:
        click.echo("本地未找到上传软件")
        click.echo("确认软件包路径是否正确：" + software)
        click.echo("确认xml路径是否正确：" + xml_path)

@click.command()
@click.option('--sw', type=str, help='需要获取下载链接的软件全名')
def mid_ocs_swlink(sw):
    """获取软件外网下载链接"""
    _search_task = pyocs_software.PyocsSoftware()
    result = _search_task.get_download_link_by_software_name(sw)
    print(result.download_link + " <Deadline Time:" + result.deadline + ">")

@click.command()
@click.option('--project', help='方案名')
@click.option('--branch', help='OCS测试类型')
@click.option('--customerid', help='客户ID')
@click.option('--modelid_name', help='model id名')
@click.option('--modelid', help='model配置内容')
@click.option('--test', help='OCS测试类型')
@click.option('--message', help='OCS备注信息')
@click.option('--bin', help='是否做bin')
def mid_jenkins_jdy(project, branch, customerid, modelid_name, modelid, test, message, bin):
    """获取软件外网下载链接"""
    try:
        obj = PyocsAutoConfig()
        para = obj.jdy_auto_config(project_name=project, branch_name=branch, customerid=customerid, modelid_name=modelid_name,
                              modelid=modelid, test=test, message=message, is_make_bin=bin)
        click.echo(para)
    except ProjectNoSupportError:
        click.echo("Fail:暂不支持此方案，请勿重复提交")
    except CustomerNoSupportError:
        click.echo("Fail:暂不支持此客户，请勿重复提交")
    except NoRegionError:
        click.echo("Fail:订单无区域信息，请确认推动解决区域问题")
    except OcsRegionError:
        click.echo("Fail:订单区域错误，请推动解决区域问题")
    except ReadPwmError:
        click.echo("Fail:占空比错误，请检查订单占空比格式是否正确")
    except No358GaiaAI:
        click.echo("Fail:358 没有导入GAIA AI，请确认")
    except OcsSystemError:
        click.echo("Fail:无法访问OCS系统，请确认")
    except GitError:
        click.echo("Fail:代码服务器存在问题，请确认")
    except RuntimeError:
        raise

cli.add_command(require)
cli.add_command(mid_ocs_list)
cli.add_command(edit)
cli.add_command(jenkins)
cli.add_command(download)
cli.add_command(refresh)
cli.add_command(autobin)
cli.add_command(resource)
cli.add_command(autoconf)
cli.add_command(update)
cli.add_command(comment)
cli.add_command(upload)
cli.add_command(autodt)
cli.add_command(copy)
cli.add_command(mark)
cli.add_command(keyupload)
cli.add_command(tclq)
cli.add_command(dg_reuse)
cli.add_command(status)
cli.add_command(myjira)
cli.add_command(cyocs)
cli.add_command(setpreupload)
cli.add_command(mid_ocs_assign)
cli.add_command(mid_ocs_status)
cli.add_command(mid_ocs_find)
cli.add_command(mid_ocs_data)
cli.add_command(mid_ocs_package)
cli.add_command(mid_ocs_edit)
cli.add_command(mid_ocs_set)
cli.add_command(mid_ocs_test)
cli.add_command(mid_ocs_notice)
cli.add_command(mid_ocs_upload)
cli.add_command(mid_ocs_swlink)
cli.add_command(mid_jenkins_jdy)
cli.add_command(tv_appjson)
cli.add_command(mid_emailaddr)
cli.add_command(mid_softengineername)
cli.add_command(mid_audit)
cli.add_command(mid_ocs_audit)
cli.add_command(mid_ocs_state)
cli.add_command(ocs_search_comment)
cli.add_command(mid_gerrit_assignee)
cli.add_command(gerrit_gtpush)
cli.add_command(jira)
cli.add_command(ocs_sw_msg)
cli.add_command(checkocs)
cli.add_command(find_mac_by_abstract)
cli.add_command(ocs_get_link)
cli.add_command(mac_report)
cli.add_command(boe_reuse)
cli.add_command(updatesw)
cli.add_command(ckd_info)
cli.add_command(rsa_decrypt)
cli.add_command(rsa_encrypt)
cli.add_command(rsa_gen_key)


if __name__ == '__main__':
    cli()
