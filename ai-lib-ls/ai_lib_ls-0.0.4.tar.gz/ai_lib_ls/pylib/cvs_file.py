import pandas as pd

class FileCSV():

    def get_csv(self,filecsv_url):
        """获取csv的数据，filecsv_url：传入 <CSV>格式的数据类型表格"""
        return pd.read_csv(filecsv_url)
    
    def save_csv(self,save_file,data_list):
        """
        将数据保存为CSV 格式的表格
        save_file： 保存数据的路径及名称：/Users/apple/Desktop/save_name.csv'
        data_list: 保存的数据，需要是集合形式 ([['','']] / [''])
        """
        pd.DataFrame(data_list).to_csv(save_file)

    def get_excel(self, fileexcel_url):
        """获取csv的数据，filecsv_url：传入 <excel>格式的数据类型表格"""
        return pd.read_excel(fileexcel_url)

    def save_excel(self, save_file, data_list):
        """
        将数据保存为excel 格式的表格
        save_file： 保存数据的路径及名称：/Users/apple/Desktop/save_name.excel'
        data_list: 保存的数据，需要是集合形式 ([['','']] / [''])
        """
        pd.DataFrame(data_list).to_excel(save_file)




        #  y_eval = eval_df.pop('survived')  将数据中的数据 去除'survived' 后在返回y_eval


# train_df.describe()  ，查看 数据的参数信息
# train_df.age.hist(bins = 20)  这个参数的画图分布