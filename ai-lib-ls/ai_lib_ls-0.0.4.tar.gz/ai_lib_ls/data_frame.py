"""
*@File    : data_frame.py
*@Time    :9/10/21 5:45 下午
*author:QauFue ,技术改变未来
*doc ：Dataframe 数据常见的操作
参考：https://www.delftstack.com/zh/howto/python-pandas/pandas-replace-values-in-column/#%E5%9C%A8-pandas-dataframe-%E4%B8%AD%E7%94%A8%E5%87%BD%E6%95%B0%E6%9B%BF%E6%8D%A2%E5%88%97%E5%80%BC
"""

class DataframeUtil():

    def __init__(self, df):
        df = df

    def df_head(self):
        '''查询面几行的数据'''
        self.df.head()

    def get_h_data(self, array_h):
        '''查询一列的数据'''
        self.df.reindex(columns=[array_h])   # 添加在数组中 ['Sex', 'Age', 'Parch', 'Fare']

    def drop_data(self ,array_w_h ,item_type=0):
        ''' 去除某行的内容
        array_w_h :有关 去除数据中的行名称或者列名称
        item_type：0去除列，1去除行
        array_w_h：传入的参数需要 【】 数组
        '''
        self.df.drop(columns=array_w_h,axis=item_type)


    def updata_data(self, key_str, map_values):
        '''将列中的数据修改替换
        key_str ：列的名称
        map_values=  {'male'(列表的参数值): 1.0（修改变为的值）, 'female': 0.0}
        '''
        self .df[ key_str] =self.df[ key_str].map(map_values)
        '''数值的方法查询替换的方法 ：  X_multi.loc[X_multi.Age > 20, 'Age'(列的名称)] = 'success' '''

class ndarray:

    #numpy.ndarray
    '''
    将数据修改为
    y_predict[y_predict > 0.5] = 1
    '''


    ''' 一维数组变成2维 数组
    np.reshape(y_predict, (-1, 1))
    '''



if __name__ == '__main__':

    d=DataframeUtil()
    d.updata_data()