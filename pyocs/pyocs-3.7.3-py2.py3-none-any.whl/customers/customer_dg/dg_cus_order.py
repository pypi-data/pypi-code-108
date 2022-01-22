from pyocs import pyocs_demand
import pprint
from pyocs import pyocs_list
import csv
import xlwt
from pyocs.pyocs_filesystem import PyocsFileSystem
import datetime


class DaiGongOrderInfoExport:
    def __init__(self,cus_name, searchid):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y%m%d_%H%M%S")
        self.filename = cus_name+'_'+time_str+'.xlsx'
        self.ocs_list = pyocs_list.PyocsList().get_ocs_id_list(searchid)
        print('【%s】一共有%s个订单需要处理'% (cus_name,self.ocs_list[0]))

        self.f = xlwt.Workbook()
        self.sheet1 = self.f.add_sheet(u'sheet1',cell_overwrite_ok=True)
        #设置表格宽度
        self.head = ['工程师', '客户', '需求数量', 'OCS号', '摘要', '客批次', '机型', '计划完成日期', '软件信息', '下载链接']
        for i in range(len(self.head)):
            self.sheet1.col((i)).width = 350*20

    @staticmethod
    def get_ocsinfo_list(ocsnum, info_row):
        pyocs_demand.PyocsDemand(ocsnum).set_flag_color('red')   #处理后，将OCS旗子颜色标记为蓝色
        pyocs_demond = pyocs_demand.PyocsDemand(ocsnum)

        info_row.append(pyocs_demond.get_ocs_software_engineer())#软件工程师
        info_row.append(pyocs_demond.get_ocs_customer())         #客户
        info_row.append(pyocs_demond.get_requirement_nums())     #需求数量
        info_row.append(ocsnum)                                  #OCS号
        info_row.append(pyocs_demond.get_ocs_title())            #摘要
        info_row.append(pyocs_demond.get_customer_batch_code())  #批次号  
        info_row.append(pyocs_demond.get_customer_machine())     #机型 
        info_row.append(pyocs_demond.get_plan_end_date())        #计划完成日期

    @staticmethod    
    def set_head_style():  
        font = xlwt.Font() # 为样式创建字体  
        font.name = 'name Times New Roman'
        font.bold = 1   #加粗
        font.color_index = 4  
        font.height = 15*20  

        #设置背景色
        style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow; font: bold on')
        style.font = font  

        #设置对齐方式
        al = xlwt.Alignment()
        al.horz = 0x02      # 设置水平居中
        al.vert = 0x01      # 设置垂直居中
        al.wrap = 1         # 设置自动换行
        style.alignment = al

        #设置边框
        borders = xlwt.Borders()  # Create borders
        borders.left = xlwt.Borders.MEDIUM  # 添加边框-虚线边框
        borders.right = xlwt.Borders.MEDIUM  # 添加边框-虚线边框
        borders.top = xlwt.Borders.MEDIUM  # 添加边框-虚线边框
        borders.bottom = xlwt.Borders.MEDIUM  # 添加边框-虚线边框
        borders.left_colour = 0x90 # 边框上色
        borders.right_colour = 0x90
        borders.top_colour = 0x90
        borders.bottom_colour = 0x90
        style.borders= borders
        return style  

    @staticmethod    
    def set_content_style():  
        font = xlwt.Font() # 为样式创建字体  
        font.name = 'name Times New Roman'
        font.bold = 0   #加粗 
        font.color_index = 4  
        font.height = 12*20  

        #设置背景色
        style = xlwt.XFStyle()
        style.font = font

        al = xlwt.Alignment()
        al.horz = 0x02      # 设置水平居中
        al.vert = 0x01      # 设置垂直居中
        al.wrap = 1         # 设置自动换行
        style.alignment = al
        return style  

    def write_csv_head(self):
        for i in range(len(self.head)):
            self.sheet1.write(0,i,self.head[i],self.set_head_style())

    def write_csv_info(self,info_row):
        with open('333.csv','a',newline='',encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(info_row)

    def write_to_csv(self):
        #1、写表格头
        self.write_csv_head()
        row = 1
        for ocsnum in self.ocs_list[1]:
            info_row = [] #存储每个ocs的关键信息列表
            #只处理非蓝色旗子
            if pyocs_demand.PyocsDemand(ocsnum).get_flag_color() == "red":
                print('OCS: %s 旗子颜色为蓝色，已经处理过，跳过不处理'%(ocsnum))
                pass
            else:
                self.get_ocsinfo_list(ocsnum, info_row)
                print('正在处理OCS : %s ...' % ocsnum)
                for i in range(len(info_row)):
                    self.sheet1.write(row, i, info_row[i], self.set_content_style())
                row = row + 1
                self.f.save(self.filename)

if __name__ == '__main__':
    tmp = []
    search_id = []
    cus_name = []
    cus_info_link = 'https://drive.cvte.com/p/DedM58QQsIgCGL-WBg'

    #从坚果云下载客户和search id对应的txt文件保存在当前目录
    getfile = PyocsFileSystem()
    getfile.get_file_from_nut_driver(cus_info_link,'.')

    file1 = open('dg_cus_search_id.txt', 'r', encoding='utf-8')
    filecontent = file1.readlines()

    # 从Begin的下一行开始取数据，并去掉可能存在的空格
    a = 'none'
    for value in filecontent:
        if 'Begin' in value:
            a = 'start'
            continue
        if a == 'start':
            tmp.append(value.replace(' ', ''))

    # 截取':'之后的字符串，并将换行符去掉
    for i in range(len(tmp) - 1):
        index1 = tmp[i].index(':')
        str2 = tmp[i][index1 + 1:]
        str3 = tmp[i][:index1]
        search_id.append(str2.strip('\n'))
        cus_name.append(str3)

    tmpdic = zip(cus_name, search_id)
    dic_cus_search = dict((cus_name, search_id) for cus_name, search_id in tmpdic)
    #print(dic_cus_search)

    for cus, search_id in dic_cus_search.items():
        print('正在处理【%s】...'%cus)
        info = DaiGongOrderInfoExport(cus,search_id)
        if info.ocs_list[0] != 0:
            info.write_to_csv()


        
