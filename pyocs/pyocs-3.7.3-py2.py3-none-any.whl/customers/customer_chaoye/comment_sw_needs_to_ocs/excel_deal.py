import xlrd
import os
from pyocs.pyocs_login import PyocsLogin

#--------------------------------------------------------
#  EXCEL 解析
#--------------------------------------------------------
def getRowsClosNum():
    return Dear_excel().request_rows


class Dear_excel:

    excel_sheet = "订单需求"
    request_sheet = None
    request_rows = 0
    request_columns = 0

    # 获取绝对路径下带"软件需求表"的excel文件。可以自己修改为自己的表格路径


    ColumnsStr=["0","1","2","3","4","5","6","7","8","9","10","11"]

    ReuestInfo={"KEY0":"",    #序号
                "KEY1":"",    #订单号
                "KEY2":"",    #销往地
                "KEY3":"",    #开机LOGO
                "KEY4":"",    #机型
                "KEY5":"",    #板卡
                "KEY6":"",    #屏型号
                "KEY7":"",    #软件时间
                "KEY8":"",    #OSD语言
                "KEY9":"",    #遥控器
                "KEY10":"",   #出货方式
                "KEY11":"",   #要求完成时间
                "KEY12":"",   #OCS号
                "KEY20":"",   # KEY12 是对应B列中的EXCEL批注
                "KEY21":""}   # KEY13 是对应F列中的板卡料号，不需要修改表格，只是做数据暂存

    def __init__(self):
        pyocs_login=PyocsLogin()
        account_info = pyocs_login.get_account_from_json_file()
        chaoye_request_excel_path = account_info["chaoye_request_excel_path"]
        workbook = xlrd.open_workbook(chaoye_request_excel_path, formatting_info=1)
        self.request_sheet = workbook.sheet_by_index(1)
        self.request_rows = self.request_sheet.nrows
        self.request_columns = self.request_sheet.ncols
        self.request_notmap = self.request_sheet.cell_note_map

    def get_order_request(self,num):
        row = int(num)
        if (row == None):
            return

        index=0
        for column in self.ColumnsStr:
            self.ReuestInfo["KEY"+str(index)] = self.request_sheet.cell_value(int(row), int(column))
            index = index+1
            #客户需求批注
            if int(column)==1:
                if (int(row), int(column)) in self.request_notmap:
                    self.ReuestInfo["KEY20"] = self.request_notmap[(int(row), int(column))].text
                else:
                    self.ReuestInfo["KEY20"] = "无"
            #客户料号
            if int(column)==5:
                if (int(row), int(column)) in self.request_notmap:
                    self.ReuestInfo["KEY21"] = self.request_notmap[(int(row), int(column))].text
                else:
                    self.ReuestInfo["KEY21"] = "无"
            #OCS号         
            try:
                if self.request_sheet.cell_type(int(row), 12) == 0:
                    self.ReuestInfo["KEY12"] = "None"
                else:
                    self.ReuestInfo["KEY12"] = int(self.request_sheet.cell_value(int(row), 12))
            except IndexError:
                self.ReuestInfo["KEY12"] = "None"

        return self.ReuestInfo


class SoftwareRequest(object):
    """customer software request"""
    def __init__(self, num):
        super(SoftwareRequest, self).__init__()
        self.num = num
        self.software_request = Dear_excel().get_order_request(self.num)

    def get_order_number(self):
        if(self.software_request['KEY1'] == None):
            print("Get_num_none")
            return "Get_num_none"
        else:
            return (self.software_request['KEY1'])

    def get_logo_text(self):
        return (self.software_request['KEY3'])

    def get_machine_type(self):
        return (self.software_request['KEY4'])

    def get_board_type(self):
        return (self.software_request['KEY5'])

    def get_language_group(self):
        return (self.software_request['KEY8'])

    def get_remoter_type(self):
        return (self.software_request['KEY9'])

    def get_ocsnum(self):
        return (self.software_request['KEY12'])

    def get_order_needs(self):
        return (self.software_request['KEY20'])

    def get_bom_number(self):
        return (self.software_request['KEY21'])