import xlrd
import os
from pyocs import pyocs_software
import datetime

# 创建对象
confirm_task = pyocs_software.PyocsSoftware()


now_time = datetime.datetime.now()
dailylog = "/disk2/zhaoxinan/tools/py/Confirmdailylog.txt"
os.remove(dailylog)

fp=open(dailylog,"a")
fp.write(str(now_time)+"客户邮件确认信息汇总(无信息 代表全部确认ok)\r\n\r\n\r\n")


# 获取当前路径下带"确认"or"汇总"的excel文件
dirPath = "/disk2/zhaoxinan/Toolszxn/pyocs/customers/customer_chaoye/confirm_software/"
file_str = str()
for file in os.listdir(dirPath):
    if ("汇总" in file) or ("确认" in file):
        file_str = file


# 只打开第一个sheet
if file_str.strip() == '':
    print("未找到确认表，请确认！")
else:
    filepath = dirPath+file_str
    print(filepath)
    workbook = xlrd.open_workbook(filepath, formatting_info=1)
    sheet = workbook.sheet_by_index(0)
    max_rows = sheet.nrows
    row_index = max_rows - 1
    sheet_cell = sheet.cell

    soft_version = str()
    order_info = str()
    order_soft_list = list()

    while row_index > 0:
        # 把确认表的订单号，板卡名，软件版本拿出
        order_info = sheet_cell(row_index, 1)
        board_type = sheet_cell(row_index, 5)
        soft_version = sheet_cell(row_index, 7)
        # 把需要的信息放入列表
        if str(soft_version.value).rstrip(" "):
            str_soft_version = str(soft_version.value).replace("-", "_").split("\n")[0]
            str_order_info = str(order_info.value).replace("-", "")
            tmp_list = [str_order_info, str_soft_version, board_type.value]
            order_soft_list.append(tmp_list)
        # 行索引从最大值自减，判断背景色
        row_index = row_index - 1
        xfx = sheet.cell_xf_index(row_index, 7)
        xf = workbook.xf_list[xfx]
        bgx = xf.background.pattern_colour_index
        if bgx == 64:  # 无任何颜色的背景色为64
            break

    print("本次确认软件个数：", len(order_soft_list))
    fp.write("本次确认软件个数："+str(len(order_soft_list))+"\r\n\r\n")
    #os.remove(filepath)  # 删除已经确认OK的表格
    for key in order_soft_list:
        ret = confirm_task.set_software_confirm(key[1], key[0])
        if not ret:  # 确认失败的将信息显示出来
            #print(key[0] + " -- " + key[1] + "--" + key[2] + " confirm failed"+"\n")
            fp.write(key[0] + " -- " + key[1] + "--" + key[2] + " confirm failed"+"\r\n")
    fp.close()
    os.remove(filepath)  # 删除已经确认OK的表格
