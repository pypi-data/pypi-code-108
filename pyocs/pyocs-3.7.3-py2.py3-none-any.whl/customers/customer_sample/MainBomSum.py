import os
import pandas as pd
import xlrd
import xlwt
from xlutils.copy import copy
from collections import Counter
from itertools import chain  

path = './Power_TV'
dirs = os.listdir(path)
bomsumlist=[]
bomdesclist=[]
bomnum_bomcount = {}
bomnum_bomdesc = {}
bomcount = []

for file in dirs:
#files = ['002.001.0005885.xls','002.001.0005913.xls']
#for file in files:
    #过滤掉非xls文件
    if os.path.splitext(file)[1] != '.xls':
        continue
    df = pd.DataFrame(pd.read_excel(file))
    #获取表格第8列数据，并将其转化为列表存储
    list1_bom_id = df.iloc[:,8].tolist() #Bom号
    list1_bom_dec = df.iloc[:,9].tolist() #Bom描述
    #将列表进行切割，取其中第21行-倒数第二行数据
    list1_bom_id = list1_bom_id[21:(len(list1_bom_id)-2)]
    list1_bom_dec = list1_bom_dec[21:(len(list1_bom_dec)-2)]
    bomsumlist.append(list1_bom_id)
    bomdesclist.append(list1_bom_dec)

#将两个嵌套列表转为为普通列表
bomsumlist = list(chain(*bomsumlist))
bomdesclist = list(chain(*bomdesclist))

#字典bomnum_bomdesc：{BOM号：BOM描述}
temp = zip(bomsumlist,bomdesclist)
bomnum_bomdesc = dict((bomsumlist,bomdesclist) for bomsumlist,bomdesclist in temp)

#字典bomnum_bomcount：{BOM号：BOM重复次数}
for i in set(bomsumlist):
    bomnum_bomcount[i] = bomsumlist.count(i)

#遍历两个字典，将Bom号、Bom描述、Bom重复次数进行对应匹配，将重复次数存在列表bomcount中
for key1, value1 in bomnum_bomdesc.items():
    for key2, value2 in bomnum_bomcount.items():
        if key1 == key2:
            bomcount.append(value2)

#上面已经完成了需要的数据，下面我们只需要将 bomnum_bomdesc、bomcount写到excel即可
#先写字典bomnum_bomdesc，再将重复次数插到第3列
file_path = 'WG_RESULT.xls'
test = pd.DataFrame.from_dict(bomnum_bomdesc,orient='index')
test.to_excel(file_path,encoding='utf-8',index=1,header=0)

rb = xlrd.open_workbook(file_path)
wb = copy(rb)
sheet = wb.get_sheet(0)
for i in range(0,len(bomcount)):
    sheet.write(i,2,bomcount[i])
os.remove(file_path)
wb.save(file_path)






