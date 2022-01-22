from pyocs import pyocs_demand_xml
from pyocs import pyocs_demand
import xlrd
import os
from pathlib import Path


class Customer_DG:

    sw_type = ["NANDBIN", "EMMC软件", "加密EMMC", "非加密EMMC", "USB软件", "加密USB", "非加密USB"]

    def __init__(self, ocs_number, path_xls_xml, path_xls_name, path_package):
        self.ocs_number = ocs_number
        self.path_package = path_package
        self.demand_xml = pyocs_demand_xml.PyocsDemand(self.ocs_number)
        self.Chipset = pyocs_demand.PyocsDemand(self.ocs_number).get_chipset_name()   # 板卡型号
        self.Customer = pyocs_demand.PyocsDemand(self.ocs_number).get_ocs_customer()  # 客户

        file_name_xls = xlrd.open_workbook(path_xls_name)     # 打开软件命名规则xls文件
        file_xls_xml = xlrd.open_workbook(path_xls_xml)       # 打开生成xml文件的xls

        self.sheet_name = file_name_xls.sheets()[0]
        self.sheet_xml = file_xls_xml.sheets()[0]

        self.output_path, self.origin_sw_name = os.path.split(path_package)
        self.output_pathlib = Path(self.output_path)

    def Generate_XML(self, sw_name):        # 根据两个表格生成XML
        path_xml = self.output_pathlib / (sw_name + ".xml")   
        file = open(str(path_xml), mode='w', encoding='utf-8')
        xml_content = ''
        xml_content += '<?xml version="1.0" encoding="utf-8"?>\n<Root>\n\t<Contract>\n\t\t<Summary></Summary>\n'
        xml_content += "\t\t<Account></Account>\n\t\t<MidAccount></MidAccount>\n\t\t<Quantity></Quantity>\n\t\t<ContractNo></ContractNo>\n"
        xml_content += "\t\t<OrderTime></OrderTime>\n\t</Contract>\n\t<ProdLine>\n\t\t<LineName></LineName>\n"
        xml_content += "\t\t<PcbNum></PcbNum>\n\t\t<ShortPcbNum></ShortPcbNum>\n\t\t<Solution></Solution>\n\t\t<Region></Region>\n"
        xml_content += "\t\t<OwnedBy></OwnedBy>\n\t\t<PhaseState></PhaseState>\n\t\t<Standard></Standard>\n\t\t<Structure></Structure>\n"
        xml_content += "\t\t<OwnedUnit></OwnedUnit>\n\t\t<UseState></UseState>\n\t</ProdLine>\n\t<Confirmation>\n\t\t<SW_Items>\n"

        xml_content += "\n\t\t\t<!-- 1 通用属性 -->\n"
        xml_content += '\t\t\t<Attr Name="SW_ChipSeries" Alias="SW_ChipSeries" Ids="0" Atoms="{}'.format(self.demand_xml.xml_chipseries()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_Chipset" Alias="SW_Chipset" Ids="0" Atoms="{}'.format(self.Chipset) + '"/>\n'  # 板卡型号
        xml_content += '\t\t\t<Attr Name="SW_Tuner" Alias="SW_Tuner" Ids="0" Atoms="{}'.format(self.demand_xml.xml_tuner()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_FlashSize" Alias="SW_FlashSize" Ids="0" Atoms="{}'.format(self.demand_xml.xml_flashsize()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_InputSource" Alias="SW_InputSource" Ids="0" Atoms="{}'.format(self.demand_xml.xml_inputsource()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_SVNPath" Alias="SW_SVNPath" Ids="0" Atoms="OEM_projects_do_not_have_to_check_the_code_path"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_Panel" Alias="SW_Panel" Ids="0" Atoms="{}'.format(self.demand_xml.xml_panel()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_OptFunc_CI" Alias="SW_OptFunc_CI" Ids="0" Atoms="{}'.format(self.demand_xml.xml_CI()) + '"/>\n'
        xml_content += '\t\t\t<Attr Name="SW_KeyboardType" Alias="SW_KeyboardType" Ids="0" Atoms="{}'.format(self.demand_xml.xml_key()) + '"/>\n'
        xml_content += "\n\t\t\t<!-- 2 客户特殊属性 -->\n"
        if self.search_row(self.sheet_xml) == -1:
            file.close()
            return "xml表格无匹配项"
        else:
            for j in range(0, self.sheet_xml.ncols):
                if "index" not in self.sheet_xml.cell_value(0, j):
                    xml_content += '\t\t\t<Attr Name="{}'.format(self.Judging(self.sheet_xml, 0, j))
                    xml_content += '" Alias="{}'.format(self.Judging(self.sheet_xml, 0, j)) + '" Ids="0" '
                    xml_content += 'Atoms="{}'.format(self.Judging(self.sheet_xml, self.search_row(self.sheet_xml), j))+'"/>\n'

        if self.search_row(self.sheet_name) == -1:
            return "软件命名表格无匹配项"
        else:
            xml_content += "\n\t\t\t<!-- 3 软件版本：SW_CheckSum -->\n"
            xml_content += '\t\t\t<Attr Name="SW_CheckSum" Alias="SW_CheckSum" Ids="0" Atoms="{}'.format(self.Judging(self.sheet_name, self.search_row(self.sheet_name), 2)) + '"/>\n'
            xml_content += "\t\t</SW_Items>\n\t\t<HW_Items>\n\t\t</HW_Items>\n\t</Confirmation>\n</Root>\n"
            file.write(xml_content)
            file.close()
            return str(path_xml)

    def Software_Prefix(self, soft):       # 生成新单软件包文件名
        if self.search_row(self.sheet_name) == -1:
            return "软件命名表格无匹配项"
        else:
            str1 = self.ocs_number + "_" + self.Chipset  # ocs号、板卡型号
            SoftwarePrefix = {
                self.sw_type[0]: "NANDBIN_CP" + str1,
                self.sw_type[1]: "EMMCBIN_CP" + str1,
                self.sw_type[2]: "EMMCBIN_SECURED_CP" + str1,
                self.sw_type[3]: "EMMCBIN_UNSECURED_CP" + str1,
                self.sw_type[4]: "CP" + str1 + "_USB",
                self.sw_type[5]: "CP" + str1 + "_SECURED_USB",
                self.sw_type[6]: "CP" + str1 + "_UNSECURED_USB",
            }
            newname = SoftwarePrefix[str(soft)]
            for j in range(1, self.sheet_name.ncols):
                if "index" not in self.sheet_xml.cell_value(0, j):
                    if len(str(self.sheet_name.cell_value(self.search_row(self.sheet_name), j))) != 0:
                        newname += "_" + str(self.Judging(self.sheet_name, self.search_row(self.sheet_name), j))
            return newname

    def Judging(self, sheet, i, j):         # 输入行和列. 判断是否是单个数字,若是,则去除.和0两个字符
        if sheet.cell(i, j).ctype == 2:     # 浮点型
            str1 = str(sheet.cell(i, j).value).split(".")  # 强制类型转换
            return str1[0]
        else:
            return str(sheet.cell(i, j).value).replace("\n", "")

    def ocs_model_handle(self, str1):        # 机型：①售后单 ②非售后单   str1:传入的需要处理的机型字符串
        if "售后" not in str1 and len(str1.split("-")) == 3:
            str1 = str1.split("-")[0] + "-" + str1.split("-")[1]  # 去掉第二个-后面的内容
        elif "售后" in str1:
            str1 = "售后-" + str1.split("-")[-1]  # 售后加上-后面的内容
        return str1

    def search_row(self, sheet):   # 匹配机型/客料号，返回xml表格对应的行号
        flag = {}
        type1 = self.ocs_model_handle(pyocs_demand.PyocsDemand(self.ocs_number).get_customer_machine())
        passengernum = pyocs_demand.PyocsDemand(self.ocs_number).get_passenger_number()
        for i in range(0, 3):
            if "index" in sheet.cell_value(0, i):
                flag[sheet.cell_value(0, i).split("-")[-1]] = i
        if len(flag) == 2:
            for i in range(1, sheet.nrows):
                if "机型" in flag and "客料号" in flag:
                    if self.ocs_model_handle(self.Judging(sheet, i, flag["机型"])) == type1\
                            and self.Judging(sheet, i, flag["客料号"]) == passengernum:
                        return i         # 返回特定行
                elif "客户" in flag and "板卡型号" in flag:
                    if self.Judging(sheet, i, flag["客户"]) == self.Customer\
                         and self.Judging(sheet, i, flag["板卡型号"]) in self.Chipset:
                        return i         # 返回特定行
        elif len(flag) == 1:
            for dict_key in flag.keys():
                if dict_key == "机型":
                    for j in range(1, sheet.nrows):
                        if type1 == self.ocs_model_handle(self.Judging(sheet, j, flag["机型"])):
                            return j
                elif dict_key == "客料号":
                    for k in range(1, sheet.nrows):
                        if passengernum == self.Judging(sheet, k, flag["客料号"]):
                            return k
                elif dict_key == "客户":
                    for k in range(1, sheet.nrows):
                        if self.Customer == self.Judging(sheet, k, flag["客户"]):
                            return k
                elif dict_key == "板卡型号":
                    for k in range(1, sheet.nrows):
                        if self.Judging(sheet, k, flag["板卡型号"]) in self.Chipset:   # 去掉硬件版本号匹配
                            return k
        return -1

    def mkdir(self, path):
        path = path.strip()                    # 去除首位空格
        path1 = path.rstrip("\\")              # 去除尾部 \ 符号
        isExists = os.path.exists(path1)       # 判断路径是否存在   存在:True 不存在:False
        if not isExists:
            os.makedirs(path)                  # 创建目录操作函数
            return True
        else:
            return False
