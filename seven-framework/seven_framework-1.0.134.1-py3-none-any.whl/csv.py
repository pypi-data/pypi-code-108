
# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-11-04 10:37:38
:LastEditTime: 2021-09-16 12:12:56
:LastEditors: ChenXiaolei
:Description: csv helper
"""
import csv
import os

class CSVHelper:
    def __init__(self):
        self.__file_name = ''
        self.__max_row = 0
        self.__max_col = 0
        self.__data_list = []
        
    def input(self,file_name):
        """
        :Description: 导入csv文件
        :param file_name: 文件名（包含地址）
        :return 二维数组
        :last_editors: ChenXiaolei
        """
        if self.__file_name=="":
            self.open(file_name)
        return self.__data_list
    
    def export(self, dict_list, file_name=""):
        """
        :Description: 数据导出到csv
        :param data: 字典数组 
        :param file_name: 文件名（包含地址）,默认在当前文件夹下创建一个"新建export.csv" 
        :return: 导出成功True 失败False
        :last_editors: ChenXiaolei
        """
        if not file_name:
            file_name = self.__get_file_name_by_csv()
        self.create(file_name)

        if not dict_list or len(dict_list)==0:
            return
        
        # 创建标题
        key_index=0
        for key in dict_list[0].keys():
            self.set_cell(0,key_index,key)
            key_index+=1
            
        for row_index in range(len(dict_list)):
            for col_index in range(len(dict_list[0].keys())):
                self.set_cell(row_index+1,col_index,dict_list[row_index][list(dict_list[0].keys())[col_index]])
        return self.save()
        
    def __get_file_name_by_csv(self):
        """
        :Description: 获取文件名
        :return 获取文件名,默认(文件目录/export.csv)
        :last_editors: ChenXiaolei
        """
        if self.__file_name=='':
            return os.path.abspath('.') + r'/export.csv'
        return self.__file_name
        
    def __insert_blank_row(self):
        """
        :Description: 插入空行
        :return 无
        :last_editors: ChenXiaolei
        """
        if self.__max_row != 0 and self.__max_col != 0:
            row_data = ['']*self.__max_col
            self.__data_list.append(row_data)
            self.__max_row += 1
        else:
            print('表中数据为空,请先创建一个空单元格')

    def __insert_blank_column(self):
        """
        :Description: 插入空列
        :return 无
        :last_editors: ChenXiaolei
        """
        if self.__max_row != 0 and self.__max_col != 0:
            col_data = [''] * self.__max_row
            for index in range(self.__max_row):
                self.__data_list[index].append(col_data[index])
            self.__max_col += 1
        else:
            print('表中数据为空,请先创建一个空单元格')

    def __create_blank_cell(self):
        """
        :Description: 创建一个单元格
        :return 无
        :last_editors: ChenXiaolei
        """
        if self.__max_row == 0 and self.__max_col == 0:
            col_data = ['']
            self.__data_list.append(col_data)
            self.__max_row += 1
            self.__max_col += 1

    def create(self, file_name=''):
        """
        :Description: 创建csv文件
        :param file_name: 文件名(带路径)
        :return: 创建成功True 创建失败False
        :last_editors: ChenXiaolei
        """
        if file_name == '':
            self.__file_name = '新建文件.csv'
        else:
            self.__file_name = file_name
        try:
            with open(self.__file_name, 'x') as outfile:
                print(self.__file_name, '文件创建成功')
            return True
        except FileExistsError:
            print(self.__file_name, '文件已存在,尝试删除')
            os.remove(self.__file_name)
            with open(self.__file_name, 'x') as outfile:
                print(self.__file_name, '文件创建成功')
            return True
        except OSError:
            print(self.__file_name, '文件创建失败')
            return False

    def open(self, file_name):
        """
        :Description: 打开csv文件
        :param file_name: 文件名(带路径)
        :return 打开文件成功True 打开文件失败False
        :last_editors: ChenXiaolei
        """
        try:
            with open(file_name, 'r', newline='') as file:
                self.__file_name = file_name
                data = csv.reader(file)
                for row in data:
                    self.__max_row += 1
                    self.__max_col = len(row)
                    self.__data_list.append(row)
                if len(self.__data_list) == 1 and len(self.__data_list[0]) == 0:
                    self.__data_list.clear()
                    self.__max_col = 0
                    self.__max_row = 0
                print(file_name, '文件打开成功')
                return True
        except OSError:
            print(file_name, '文件打开失败')
            return False

    def get_row(self, row_index):
        """
        :Description: 提取CSV中的行,返回列表
        :param row_index: 行索引下标(从0开始)
        :return 行数据(数组)
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return []
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return []
        elif self.__max_row <= row_index:
            print('读取行号超出范围')
            return []
        else:
            return self.__data_list[row_index]

    def get_column(self, col_index):
        """
        :Description: 提取CSV中的列,返回列表
        :param col_index: 列索引下标(从0开始)
        :return 列数据(数组)
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return []
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return []
        elif self.__max_col <= col_index:
            print('读取列号超出范围')
            return []
        else:
            return [self.__data_list[index][col_index] for index in range(len(self.__data_list))]

    def get_cell(self, row_index, col_index):
        """
        :Description: 提取CSV单元格
        :param row_index: 行索引下标
        :param col_index: 列索引下标
        :return 单元格数据
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return ''
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return ''
        elif self.__max_row <= row_index:
            print('读取行号超出范围')
            return ''
        elif self.__max_col <= col_index:
            print('读取列号超出范围')
            return ''
        else:
            return self.__data_list[row_index][col_index]

    def insert_row(self, row_index, row_data=[]):
        """
        :Description: 插入行数据
        :param row_index: 行索引下标(从0开始)
        :param row_data: 行数据(数组)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__max_col == 0 and self.__max_row == 0:
            return self.set_row(row_index, row_data)
        temp_data = [temp for temp in row_data]
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif len(temp_data) == 0:
            print('插入数据为空')
            return False
        elif len(temp_data) == self.__max_col:
            self.__data_list.insert(row_index, temp_data)
            self.__max_row += 1
            return True
        elif len(temp_data) < self.__max_col:
            for index in range(len(temp_data), self.__max_col):
                temp_data.append('')
            self.__data_list.insert(row_index, temp_data)
            self.__max_row += 1
            return True
        else:
            for index in range(self.__max_col, len(temp_data)):
                self.__insert_blank_column()
            self.__data_list.insert(row_index, temp_data)
            self.__max_row += 1
            return True

    def insert_column(self, col_index, col_data=[]):
        """
        :Description: 插入列数据
        :param col_index: 列索引下标(从0开始)
        :param col_data: 列数据(数组)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__max_col == 0 and self.__max_row == 0:
            return self.set_column(col_index, col_data)
        temp_data = [temp for temp in col_data]
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif len(temp_data) == 0:
            print('插入数据为空')
            return False
        elif len(temp_data) == self.__max_row:
            for index in range(self.__max_row):
                self.__data_list[index].insert(col_index, temp_data[index])
            self.__max_col += 1
            return True
        elif len(temp_data) < self.__max_row:
            for index in range(len(temp_data), self.__max_row):
                temp_data.append('')
            for index in range(self.__max_row):
                self.__data_list[index].insert(col_index, temp_data[index])
            self.__max_col += 1
            return True
        else:
            for index in range(self.__max_row, len(temp_data)):
                self.__insert_blank_row()
            for index in range(self.__max_row):
                self.__data_list[index].insert(col_index, temp_data[index])
            self.__max_col += 1
            return True

    def delete_row(self, row_index):
        """
        :Description: 删除行
        :param row_index: 行索引下标(从0开始)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return False
        elif self.__max_row <= row_index:
            print('删除行号超出范围')
            return False
        else:
            self.__data_list.pop(row_index)
            self.__max_row -= 1
            return True

    def delete_column(self, col_index):
        """
        :Description: 删除列
        :param col_index: 列索引下标(从0开始)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return False
        elif self.__max_col <= col_index:
            print('删除列号超出范围')
            return False
        else:
            for index in range(self.__max_row):
                self.__data_list[index].pop(col_index)
            self.__max_col -= 1
            return True

    def delete_row_by_key(self, col_index, key):
        """
        :Description: 以col_index列为查找源，删除=key的行
        :param col_index: 列索引下标(从0开始)
        :param key: 满足条件的key值
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return False
        elif self.__max_col <= col_index:
            print('删除列号超出范围')
            return False
        index = self.get_row_index(col_index, key)
        if index == -1:
            print('在', col_index, '列找不到', key)
            return False
        else:
            return self.delete_row(index)

    def delete_column_by_key(self, row_index, key):
        """
        :Description: 以row_index列为查找源，删除=key的列
        :param row_index: 行索引下标(从0开始)
        :param key: 满足条件的key值
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif self.__max_row == 0 or self.__max_col == 0:
            print('表格无数据')
            return False
        elif self.__max_row <= row_index:
            print('删除行号超出范围')
        index = self.get_column_index(row_index, key)
        if index == -1:
            print('在', row_index, '行找不到', key)
        else:
            return self.delete_column(index)

    def set_row(self, row_index, row_data):
        """
        :Description: 写行数据，覆盖原来的数据
        :param row_index: 行索引下标(从0开始)
        :param row_data: 行数据(数组)
        :return 写入成功True
        :last_editors: ChenXiaolei
        """
        temp_data = [temp for temp in row_data]
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif len(temp_data) == 0:
            print('写入数据为空')
            return False
        #表格为空
        if self.__max_row == 0 and self.__max_col == 0:
            self.__create_blank_cell()
        if row_index >= self.__max_row:
            for index in range(self.__max_row, row_index+1):
                self.__insert_blank_row()
        if len(temp_data) == self.__max_col:
            self.__data_list[row_index] = [temp for temp in temp_data]
            return True
        elif len(temp_data) < self.__max_col:
            for index in range(len(temp_data), self.__max_col):
                temp_data.append('')
            self.__data_list[row_index] = [temp for temp in temp_data]
            return True
        else:
            for index in range(self.__max_col, len(temp_data)):
                self.__insert_blank_column()
            self.__data_list[row_index] = [temp for temp in temp_data]
            return True

    def set_column(self, col_index, col_data):
        """
        :Description: 写列数据，覆盖原来的数据
        :param col_index: 列索引下标(从0开始)
        :param col_data: 列数据(数组)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        temp_data = [temp for temp in col_data]
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        elif len(temp_data) == 0:
            print('写入数据为空')
            return False
        #表格为空
        if self.__max_row == 0 and self.__max_col == 0:
            self.__create_blank_cell()
        if col_index >= self.__max_col:
            for index in range(self.__max_col, col_index+1):
                self.__insert_blank_column()
        if len(temp_data) == self.__max_row:
            for index in range(self.__max_row):
                self.__data_list[index][col_index] = temp_data[index]
            return True
        elif len(temp_data) < self.__max_row:
            for index in range(len(temp_data), self.__max_row):
                temp_data.append('')
            for index in range(self.__max_row):
                self.__data_list[index][col_index] = temp_data[index]
            return True
        else:
            for index in range(self.__max_row, len(temp_data)):
                self.__insert_blank_row()
            for index in range(self.__max_row):
                self.__data_list[index][col_index] = temp_data[index]
            return True

    def set_cell(self, row_index, col_index, data):
        """
        :Description: 写列数据，覆盖原来的数据
        :param row_index: 行索引下标(从0开始)
        :param col_index: 列索引下标(从0开始)
        :param data: 单元格数据
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if self.__file_name == '':
            print('请先打开csv文件')
            return False
        #表格为空
        if self.__max_row == 0 and self.__max_col == 0:
            self.__create_blank_cell()
        if row_index >= self.__max_row:
            for index in range(self.__max_row, row_index + 1):
                self.__insert_blank_row()
        if col_index >= self.__max_col:
            for index in range(self.__max_col, col_index + 1):
                self.__insert_blank_column()
        self.__data_list[row_index][col_index] = data
        return True

    def get_column_index(self, row_index, key):
        """
        :Description: 以row_index行为查找源，返回=key的列索引号
        :param row_index: 行索引下标(从0开始)
        :param key: 需满足条件的key
        :return 列索引
        :last_editors: ChenXiaolei
        """
        row_data = self.get_row(row_index)
        if key not in row_data:
            return -1
        else:
            return row_data.index(key)

    def get_row_index(self, col_index, key):
        """
        :Description: 以col_index列为查找源，返回=key的行索引号
        :param col_index: 列索引下标(从0开始)
        :param key: 需满足条件的key
        :return 行索引
        :last_editors: ChenXiaolei
        """
        col_data = self.get_column(col_index)
        if key not in col_data:
            return -1
        else:
            return col_data.index(key)

    def get_max_row(self):
        """
        :Description: 获取最大行数
        :return 最大行数
        :last_editors: ChenXiaolei
        """
        return self.__max_row

    def get_max_column(self):
        """
        :Description: 获取最大列数
        :return 最大列数
        :last_editors: ChenXiaolei
        """
        return self.__max_col

    def save(self, file_name=''):
        """
        :Description: 保存csv文件
        :param file_name: 文件名(带路径)
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if file_name != '':
            self.__file_name = file_name
        try:
            with open(self.__file_name, 'w') as outfile:
                for row in self.__data_list:
                    str_write = ''
                    for data in row:
                        str_write += str(data)
                        str_write += ','
                    str_write = str_write[0:len(str_write) - 1]
                    str_write += '\n'
                    outfile.write(str_write)
            return True
        except OSError:
            print(self.__file_name, '文件打开失败')
            return False