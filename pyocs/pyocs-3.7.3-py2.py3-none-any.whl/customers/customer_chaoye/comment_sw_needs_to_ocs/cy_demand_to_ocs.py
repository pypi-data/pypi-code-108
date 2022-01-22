from pyocs import pyocs_software
from pyocs.pyocs_login import PyocsLogin
from customers.customer_chaoye.comment_sw_needs_to_ocs.excel_deal import SoftwareRequest

class CyNeedsToOcs:
    def cli_customer_excel_row_date_to_ocs(row_index):
        sw_req = SoftwareRequest(int(row_index)-1)
        ordernum = str(sw_req.get_order_number())  # 订单号
        logo = str(sw_req.get_logo_text())  # logo
        language = str(sw_req.get_language_group())  # 语言
        needs = str(sw_req.get_order_needs())  # 客户需求
        ocsnum = str(sw_req.get_ocsnum())  # OCS
        if ocsnum == "None":
            print("OCS号获取失败。请查询该行M列是否有添加ocs号")
            return False


        # 订单号处理 从后往前数第五个插入-  解决X2-190 or X2200等 特殊业务员编号
        ordernum_list = list(ordernum)
        ordernum_list.insert(-5, '-')
        chaoye_order_info = ''.join(ordernum_list)

        if "酒店模式" in needs:
            needs = needs+"\n注：此处只是提示大部分订单方式(如有特殊无法进入，需找工程师确认方式)：智能机进入酒店模式方式为menu+4711，普通机酒店模式通过菜单条目进入，8503方案密码0000，56方案密码4711，3663密码0000"

        html_table = '<table border="1">'
        header = '<tr>'
        message = '<tr>'

        header += '<td colspan="6" height=30 bgcolor="#F5DEB3" align="center">' + '朝野客户' + chaoye_order_info + '订单特殊需求' + '</td>'
        message += '<td>' + "语言："+language + '</td>'
        message += '</tr>'
        message += '<tr>'
        message += '<td>' + "LOGO："+logo + '</td>'
        message += '</tr>'
        message += '<tr>'
        message += '<td>' + "特殊需求:\n"+needs + '</td>'
        message += '</tr>'
        message += '</tr>'
        header += '</tr>'
        html_table += header + message + '</table>'
        confirm_task = pyocs_software.PyocsSoftware()
        ret = confirm_task.add_comment_to_ocs(ocs_number=ocsnum, message=html_table)
        return ret

    def deal_customer_excel_date_to_ocs(row_index):
        pyocs_login=PyocsLogin()
        account_info = pyocs_login.get_account_from_json_file()
        AutoDailylogpath = account_info["chaoye_request_autodeal_dailylog_path"]

        # 创建对象
        sw_req = SoftwareRequest(row_index)
        confirm_task = pyocs_software.PyocsSoftware()
        ordernum = str(sw_req.get_order_number())  # 订单号
        if (ordernum == "Get_num_none"):
            return "Get_num_none"

        logo = str(sw_req.get_logo_text())  # logo
        board = str(sw_req.get_board_type())  # 板型
        language = str(sw_req.get_language_group())  # 语言
        bomnum = str(sw_req.get_bom_number())  # 料号
        needs = str(sw_req.get_order_needs())  # 客户需求

        if "酒店模式" in needs:
            needs = needs+"\n注：此处只是提示大部分订单方式(如有特殊无法进入，需找工程师确认方式)：智能机进入酒店模式方式为menu+4711，普通机酒店模式通过菜单条目进入，8503方案密码0000，56方案密码4711，3663密码0000\n"
        
        if bomnum == "无":
            infotext = "error  :" + ordernum + "   " + board + "   客户料号为空，无法搜索请确认！\n"
        else:  
            board = board.split('.')
            chaoye_board_str = board[1]
            #订单号处理 从后往前数第五个插入-  解决X2-190 or X2200等 特殊业务员编号
            ordernum_list = list(ordernum)
            ordernum_list.insert(-5, '-')
            chaoye_order_info = ''.join(ordernum_list)

            customer_needs = "语言: " + language + "@" + "LOGO: " + logo + "@" + "特殊需求: \n" + needs
            infotext = confirm_task.set_software_customer_chaoye_needs_to_ocs(customer_name="朝野", order_info=chaoye_order_info,
                                                                   customer_bom=bomnum, board_type=chaoye_board_str,
                                                                   customer_needs=customer_needs)
        fd = open(AutoDailylogpath, 'a+',encoding='utf-8',errors='ignore')
        fd.write(infotext)
        fd.close()        