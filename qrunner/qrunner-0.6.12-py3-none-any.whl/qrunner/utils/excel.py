import pandas as pd


# 读写excel
class Excel(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def read_all(self, sheet_name=0):
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df.values.tolist()
        print(res)
        return res

    def read_row_index(self, row_index: int, sheet_name=0):
        """
        index：从1开始
        """
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df.values[row_index-1].tolist()
        print(res)
        return res

    def read_col_index(self, col_index: int, sheet_name=0):
        """
        index：从1开始
        """
        df = pd.read_excel(self.file_name, usecols=[col_index-1], sheet_name=sheet_name)
        res = [r[0] for r in df.values.tolist()]
        print(res)
        return res

    def read_col_name(self, col_name: str, sheet_name=0):
        df = pd.read_excel(self.file_name, sheet_name=sheet_name)
        res = df[col_name].values.tolist()
        print(res)
        return res

    def write(self, data: dict, sheet_name='sheet1', column_width=20):
        """
        数据格式：{
            '标题列1': ['张三', '李四'],
            '标题列2': [80, 90]
        }
        """

        df = pd.DataFrame(data)
        writer = pd.ExcelWriter(self.file_name)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        sheet = writer.sheets.get(sheet_name)
        for index in range(len(df)):
            # print(index, value)
            for i in range(len(df.columns)):
                sheet.set_column(index+1, i, column_width)
        writer.save()

    def write_sheets(self, sheet_dict: dict, column_width=20):
        """
        sheet_dict: {
            'sheet1_name': {'标题列1': ['张三', '李四'], '标题列2': [80, 90]},
            'sheet2_name': {'标题列3': ['王五', '郑六'], '标题列4': [100, 110]}
        }
        """
        writer = pd.ExcelWriter(self.file_name)
        for sheet_name, sheet_data in sheet_dict.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            sheet = writer.sheets.get(sheet_name)
            for index in range(len(df)):
                for i in range(len(df.columns)):
                    sheet.set_column(index + 1, i, column_width)
        writer.save()
	
    def get_sheet_names(self):
        return list(pd.read_excel(self.file_name, sheet_name=None))


# 读写csv
class CSV(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def read_all(self):
        df = pd.read_csv(self.file_name)
        res = df.values.tolist()
        print(res)
        return res

    def read_row_index(self, row_index: int):
        """
        index: 从1开始
        """
        df = pd.read_csv(self.file_name)
        res = df.values[row_index-1].tolist()
        print(res)
        return res

    def read_col_index(self, col_index: int):
        """
        index：从1开始
        """
        df = pd.read_csv(self.file_name, usecols=[col_index-1])
        res = [r[0] for r in df.values.tolist()]
        print(res)
        return res

    def read_col_name(self, col_name: str):
        df = pd.read_csv(self.file_name, usecols=[col_name])
        res = [r[0] for r in df.values.tolist()]
        print(res)
        return res

    def write(self, data: dict, sheet_name='sheet1', column_width=20):
        """
        数据格式：{
            '标题列1': ['张三', '李四'],
            '标题列2': [80, 90]
        }
        """
        df = pd.DataFrame(data)
        df.to_csv(self.file_name, index=False)


if __name__ == '__main__':
    data = {
        '标题列1': ['张三', '李四'],
        '标题列2': [80, 90]
    }
    data_dict = {
        'sheet1_name': {'标题列1': ['张三', '李四'], '标题列2': [80, 90]},
        'sheet2_name': {'标题列3': ['王五', '郑六'], '标题列4': [100, 110]}
    }

    # excel = Excel('test.xlsx')
    # excel.write_sheets(data_dict)

    # test = Excel('test.xlsx')
    # test.write(data)
    # test.read_all()
    # test.read_row_index(1)
    # test.read_col_name('标题列2')
    # test.read_col_index(1)

    # test_csv = CSV('test1.csv')
    # # test_csv.write(data)
    # test_csv.read_all()
    # test_csv.read_row_index(1)
    # test_csv.read_col_index(2)
    # test_csv.read_col_name('标题列2')
