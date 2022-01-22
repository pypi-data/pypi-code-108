import os
import pandas as pd
import xlrd
import xlwt
from xlutils.copy import copy
from collections import Counter
from itertools import chain  
import numpy as np
import sys


#将3列表格数据转为字典存储{code:[commont+loc]}
def handle_original_data(code, loc, commont):
    n = 0
    list_com_loc = []

    for i in range(len(commont)):
        list_com_loc.append(str(commont[i]) + ','+ str(loc[i])) 
    for i in list_com_loc:
        list_com_loc[n] = (i).split(',')
        n = n + 1

    for value in list_com_loc:
        if value[0] == '厚膜电阻' or value[0] == '陶瓷电容':
            #除了最后一个位置元素不处理外，其余元素全部转为小写
            for i in (range(len(value)-1)):
                value[i] = value[i].lower() #转为小写
                if value[i] == 'smd':
                    if '-' in value[i-1]:
                        value[i-1] = value[i-1].split('-')[0]
                    break

    tmp = zip(code,list_com_loc)
    dic_bom = dict((code,list_com_loc) for code,list_com_loc in tmp)
    return dic_bom

def handle_target_bom_commont(list_commont):
    list_bom_comment_final = []
    list_bom_comment_key = []
    #print(list_commont)
    for bom_commont in list_commont:
        list_bom_comment_final.append(str(bom_commont).split(','))

    for i in range(len(list_bom_comment_final)):
        tmp = []
        #寻找厚膜电阻和陶瓷电容最后一个关键字,存在last_key_data
        if list_bom_comment_final[i][0] == '厚膜电阻' or list_bom_comment_final[i][0] == '陶瓷电容':
            for j in range(len(list_bom_comment_final[i])):
                if list_bom_comment_final[i][j] == 'SMD':
                    last_key_data = list_bom_comment_final[i][j-1]
                    if '-' in last_key_data:
                        last_key_data = last_key_data.split('-')[0]
                    break

        #寻找厚膜电阻的阻值关键字,存在second_key_data
        if list_bom_comment_final[i][0] == '厚膜电阻':
            for j in range(len(list_bom_comment_final[i])):
                if 'ohm' in list_bom_comment_final[i][j]:
                    second_key_data = list_bom_comment_final[i][j].lower()
                    break

        if list_bom_comment_final[i][0] == '厚膜电阻':
            tmp.append(list_bom_comment_final[i][0])
            tmp.append(second_key_data)
            tmp.append(last_key_data)
            list_bom_comment_key.append(tmp)
        elif list_bom_comment_final[i][0] == '陶瓷电容':
            tmp.append(list_bom_comment_final[i][0])
            tmp.append(list_bom_comment_final[i][2].lower())
            tmp.append(list_bom_comment_final[i][3].lower())
            tmp.append(last_key_data)
            list_bom_comment_key.append(tmp)
        else:
            list_bom_comment_key.append(list_bom_comment_final[i])

    return list_bom_comment_key
    
def handle_taget_data(bom_code, bom_commont):
    bom_commont_new = []
    tup = zip(bom_code, bom_commont)
    list_new = []
    for list_ in list(tup):
        list_new.append(list(list_))

    dirc_ = {}
    for i in range(len(list_new)):
        dirc_[i] = list_new[i]

    #预处理后的字典格式：
    # dirc_ = {
    #     0: [nan, 'SYEQ3213-T004A变压器'],
    #     1: ['004.002.0000039', '厚膜电阻,RES,1/4W,20ohm,±1%,1206,SMD'],
    # }    
    list_tmp = []
    for value in dirc_.values():
        list_tmp.append(value[1])
    
    #print(list_tmp)
    bom_commont_new = handle_target_bom_commont(list_tmp)

    for i in range(len(bom_commont_new)):
        dirc_[i][1] = bom_commont_new[i]

    #返回的字典格式：
    # dirc_ = {
    #     0: [nan, ['SYEQ3213-T004A变压器']], 
    #     1: ['004.002.0001096', ['厚膜电阻', '510ohm', '0603']],
    # }
    #print(dirc_) 
    return dirc_

# value[0] = '004.002.0001096'
# value[1] = ['厚膜电阻', '510ohm', '0603']
# value[1][0] = '厚膜电阻'
def search(dic_bom_taget, dic_bom):
    bom_location_output = []

    for value in dic_bom_taget.values():  #遍历需要查找的数据
        if value[0] == 'nan':
            bom_location_output.append('无')
        elif value[1][0] == '厚膜电阻' or value[1][0] == '陶瓷电容':
            for bom_code, bom_commont in dic_bom.items():   #遍历数据库
                #1、在物料编号查找
                if value[0] == bom_code:
                    bom_location_output.append(dic_bom[bom_code][len((bom_commont))-1])
                    print('%s 在物料编号里面找到了: %s'% (value[0],dic_bom[bom_code][len((bom_commont))-1]))
                    break
                #2、如果物料编号没有，就去物料描述查找关键字
                if set(value[1]) < set(bom_commont):
                    bom_location_output.append(dic_bom[bom_code][len((bom_commont))-1])
                    print('%s 在物料描述里面找到了: %s'% (value[0],dic_bom[bom_code][len((bom_commont))-1]))
                    break
            #3、如果都没有就返回"无"
            else:
                bom_location_output.append('无')
        else:
            for bom_code, bom_commont in dic_bom.items():
                if value[0] == bom_code:
                    print('%s 普通物料找到了: %s'% (value[0],dic_bom[bom_code][len((bom_commont))-1]))
                    bom_location_output.append(dic_bom[bom_code][len((bom_commont))-1])
                    break
            else:
                bom_location_output.append('无')

    return bom_location_output

def add_title_to_list(list_, title):
    tmp = [];
    tmp.append(title)
    for i in range(len(list_)):
        tmp.append(list_[i])
    return tmp    

def write_to_excel(file_name, list_, n):
    rb = xlrd.open_workbook(file_name)
    wb = copy(rb)
    sheet = wb.get_sheet(0)
    for i in range(0,len(list_)):
        sheet.write(i,n-1,list_[i])
    os.remove(file_name)
    wb.save(file_name)


def get_excel_one_colume_to_list(df, m, n):
    return df.iloc[m-2:,n-1].tolist()

def get_taget_data():
    #获取目标数据2列：物料编码、物料描述
    df = pd.DataFrame(pd.read_excel(target_file))
    #list_bom_code_t = get_excel_one_colume_to_list(df,2,1)
    list_bom_code_t = df.iloc[0:,1].tolist()
    list_bom_commont_t = get_excel_one_colume_to_list(df,2,3)
    dic_t = handle_taget_data(list_bom_code_t, list_bom_commont_t)
    return dic_t

def get_taget_position_data():
    #获取坐标和仓位的对应关系
    df = pd.DataFrame(pd.read_excel(target_file))
    list_bom_changwei_t = df.iloc[0:,0].tolist()   #仓位
    list_bom_position_t = df.iloc[0:,5].tolist()   #坐标
    list_new = []
    for i in range(len(list_bom_changwei_t)):
        list_new.append(str(list_bom_changwei_t[i]) + ','+ str(list_bom_position_t[i]))
    dirc_ = {}
    for i in range(len(list_new)):
        dirc_[i] = list_new[i].replace('\t','').split(',')
    #dirc_ = {0:[仓位+坐标]}
    #print(dirc_)
    return  dirc_

def check_pick_file():
    df = pd.DataFrame(pd.read_excel(pick_file))
    list_position = df.iloc[0:,0].tolist()     #坐标
    dir_t = {}
    exit = 0
    for value in set(list_position):
        dir_t[value] = list_position.count(value)
    for loc, counts in dir_t.items():
        if counts > 1:
            print('%s在pick第一列重复了%s次'%(loc,counts))
            exit = exit +1
    if exit != 0:
        print('请去掉重复元素所在行再操作！')
        sys.exit(1)
    else:
        print('pick文件校验成功!')

def get_pick_data():
    #获取坐标和默认封装的数据
    df = pd.DataFrame(pd.read_excel(pick_file))
    list_position = df.iloc[0:,0].tolist()     #坐标
    list_fengzhuang = df.iloc[0:,1].tolist()   #封装
    tmp = zip(list_position,list_fengzhuang)
    dic_pick = dict((list_position,list_fengzhuang) for list_position,list_fengzhuang in tmp)
    #{坐标,封装}
    return dic_pick


def get_changwei_fengzuang():
    #获取仓位和默认封装的数据
    df = pd.DataFrame(pd.read_excel(original_file))
    list_changwei = df.iloc[0:,0].tolist()     #仓位
    list_fengzhuang = df.iloc[0:,4].tolist()   #封装
    tmp = zip(list_changwei,list_fengzhuang)
    dic_cf = dict((list_changwei,list_fengzhuang) for list_changwei,list_fengzhuang in tmp)
    #{仓位,封装}
    return dic_cf

def search_pick_in_target():
    dir_pick = get_pick_data()
    dir_target = get_taget_position_data()
    dir_cf = get_changwei_fengzuang()
    list_t = []
    for key in dir_pick.keys():
        # 1、判断坐标是否在给定target的参考指示项里面
        for value in dir_target.values():
            if key in value:
                #如果找到，那么进一步判断所在仓位是否为无
                if value[0] == '无':
                    print('Pick的%s 在target中成功匹配到坐标,但是对应仓位为空' %(str(key)))
                    break
                else:
                    print('Pick的%s 在target中成功匹配到坐标,并且仓位有效: %s' %(str(key),value[0]))
                    #如果封装有效，就获取覆盖默认封装
                    if value[0] in dir_cf.keys():
                        print('有效仓位对应的封装为%s'%dir_cf[value[0]])
                        if str(dir_cf[value[0]]) != 'nan':
                            dir_pick[key] = dir_cf[value[0]]
                    else:
                        print('仓位不在仓位表中!!')
                    break
        else:
            print('Pick给定的该坐标:%s 根本不在给定target的参考指示项!!!'%(str(key)))
    for value in dir_pick.values():
        list_t.append(str(value))
    # print('需要写入的数据位')
    # print(list_t)
    loc_fengzuang = add_title_to_list(list_t, 'Footprint')
    write_to_excel(pick_file, loc_fengzuang, 2)

def get_changwei_data():
    #获取仓位数据源文件3列：物料编码、仓位号、物料描述
    df = pd.DataFrame(pd.read_excel(original_file,original_file_sheet))
    list_bom_code_o = df.iloc[:,1].tolist()
    list_bom_location_o = df.iloc[:,0].tolist()
    list_bom_location_f = []
    for value in list_bom_location_o:
        list_bom_location_f.append(value.replace('\t','').replace(',',''))
    list_bom_comment_o = df.iloc[:,2].tolist()
    dic_c = handle_original_data(list_bom_code_o, list_bom_location_f, list_bom_comment_o)
    return dic_c

def get_feida_data():
    #获取飞达位置的源文件：物料编码、飞达号、物料描述
    df = pd.DataFrame(pd.read_excel(feida_file,feida_file_sheet,header=None))
    list_bom_code_f = df.iloc[:,0].tolist()
    list_bom_location_f = df.iloc[:,2].tolist()
    list_bom_comment_f = df.iloc[:,1].tolist()
    dic_f = handle_original_data(list_bom_code_f, list_bom_location_f, list_bom_comment_f)
    return dic_f

def check_target_file():
    df = pd.DataFrame(pd.read_excel(target_file,header=None))
    list_header = df.iloc()[0,:].tolist()
    if list_header[1] == '物料编码' and list_header[2] == '物料描述':
        print('target文件格式检测正常!\n')
        pass
    else:
        print('''target.xlsx的表头格式有误！请按照以下格式输入：
                仓位   物料编码    物料描述   ...
                        xxx         xxx
                        ...         ...    ''')
        sys.exit(1)


def get_bom_from_feida(k):
    df = pd.DataFrame(pd.read_excel(feida_file,feida_file_sheet, header=None))
    list_bom_code_o = df.iloc[:, 0].tolist()
    list_bom_location_o = df.iloc[:, 2].tolist()
    num = 0
    for i in list_bom_location_o:
        if i == k:
            return list_bom_code_o[num]
        num = num + 1

def get_bom_from_changwei(k):
    df = pd.DataFrame(pd.read_excel(original_file, original_file_sheet))
    list_bom_location_o = df.iloc[:, 0].tolist()
    list_bom_code_o = df.iloc[:, 1].tolist()
    num = 0
    for i in list_bom_location_o:
        if i == k:
            return list_bom_code_o[num]
        num = num + 1

def update_bomcode_target(loc_changwei,list_target_bom,loc_feida):
    num = 0;
    for x in loc_changwei:
        if ('M' in x) or ('L' in x) or ('J' in x) or ('K' in x):
            if '替代料' in x:
                x = x.replace('替代料','')
            print("%s的仓位为:%s,包含了MLJK,物料需要更新..."%(list_target_bom[num],x))
            if(loc_feida[num] != '无'):
                print('飞达有效:%s，将从飞达更新物料!!!!!!!!!!!!!!'%(loc_feida[num]))
                list_target_bom[num] = get_bom_from_feida(loc_feida[num])
                print('更新后物料为:%s\n'%list_target_bom[num])
            else:
                print('飞达无效，将从仓位:%s更新'%x)
                list_target_bom[num] = get_bom_from_changwei(x)
                print('更新后物料为:%s\n' %list_target_bom[num])
        else:
            print('%s的仓位為:%s,不包含JKML, 将维持不变\n'%(list_target_bom[num],x))
        num = num+1
    print('更新后的物料列表为')
    print(list_target_bom)
    return list_target_bom


original_file = 'data_changwei.xlsx'
original_file_sheet = 'current_new'
feida_file =    'data_feida.xlsx'
feida_file_sheet = 'feida'
target_file =  'target.xlsx'
pick_file =  'pick.xlsx'

#对target文件校验
print('【开始校验target...】')
check_target_file()

#如果存在pick文件，对pick文件校验
if os.path.exists(pick_file):
    print('【开始校验pick...】')
    check_pick_file()

#获取数据
dir_t = get_taget_data()
dir_c = get_changwei_data()
dir_f = get_feida_data()

#开始查找
print('\n--------------------开始查找仓位号-----------------------')
changwei = search(dir_t,dir_c)
print('--------------------仓位号查找完成-----------------------\n\n')

print('--------------------开始查找飞达位置-----------------------')
feida = search(dir_t,dir_f)
print('--------------------飞达位置查找完成-----------------------\n\n')

#添加标题
loc_changwei = add_title_to_list(changwei,'仓位')
loc_feida = add_title_to_list(feida,'位置')
#写入文件
write_to_excel(target_file, loc_changwei, 1)
write_to_excel(target_file, loc_feida, 7)


print('--------------------开始根据仓位和位置更新target物料--------------------')
#获取更新后的target物料
list_target_bom =[]
for value in dir_t.values():
    list_target_bom.append(value[0])
update_bom = update_bomcode_target(changwei,list_target_bom,feida)
#添加标题
update_bom_list = add_title_to_list(update_bom,'物料编码')
#写入文件
write_to_excel(target_file, update_bom_list, 2)
print('--------------------target物料更新完毕-----------------------\n\n')


print('--------------------开始处理pick文件-----------------------')
#如果存在pick文件，又需要统计封装信息到第二列
if os.path.exists(pick_file):
    print('存在Pick文件需要处理\n')
    search_pick_in_target()
else:
    print('没有pick文件')
print('--------------------pick文件处理完毕-----------------------\n\n')












