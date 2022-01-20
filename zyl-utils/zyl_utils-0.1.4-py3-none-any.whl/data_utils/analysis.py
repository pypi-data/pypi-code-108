import langid
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Analyzer:
    def __init__(self):
        pass

    @staticmethod
    def get_text_language(text: str):
        """
        注意：短语尽量不要输入判断，越短越不准，# ’癌症‘判断为‘ja'
        Args:
            text:

        Returns:

        """
        return langid.classify(text)[0]

    @staticmethod
    def get_text_string_length(text: str):
        return len(text)

    @staticmethod
    def get_text_token_length(text: str, model_tokenizer=None):
        if not model_tokenizer:
            from transformers import BertTokenizer
            model_tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        return len(model_tokenizer.tokenize(text))

    @staticmethod
    def show_dataframe_base_info(df: pd.DataFrame, column=None):
        if column:
            df = df[column]
        print(df.describe())
        print(df.info())

    @staticmethod
    def show_dataframe_completely():
        """
            完全显示pandas的dataframe的所有值
        Returns:

        """
        import pandas as pd
        pd.set_option('max_colwidth', 500)  # 设置value的显示长度为200，默认为50
        pd.set_option('display.max_columns', None)  # 显示所有列，把行显示设置成最大
        pd.set_option('display.max_rows', None)  # 显示所有行，把列显示设置成最大

    @staticmethod
    def show_plt_completely():
        """
            plt显示问题
        Returns:

        """
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    @staticmethod
    def analyze_numerical_array(data):
        """
        分析数值数组
        Args:
            data:

        Returns:

        """
        Analyzer.show_plt_completely()
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        q1 = np.percentile(data, 25)  # 第一四分位数，从小到大25%,下四分位数
        q2 = np.percentile(data, 50)  # 第二四分位数，从小到大50%，中位数
        q3 = np.percentile(data, 75)  # 第三四分位数，从小到大75%，上四分位数
        iqr = q3 - q1  # 四分位数差（IQR，interquartile range），上四分位数-下四分位数
        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr
        print(f"""
        计数：      {len(data)}
        均值：      {data.mean()}
        标准差：     {data.std()}
        方差：      {data.var()}
        最大值：    {np.max(data)}
        最小值：    {np.min(data)}
        下四分位数： {q1}
        中位数：     {q2}
        上四分位数:  {q3}
        下异常值界限：{lower_limit}   ,异常值数:{len(np.where(data < lower_limit)[0])}
        上异常值界限：{upper_limit}   ,异常值数:{len(np.where(data > upper_limit)[0])}
            """
              )
        plt.subplot(211)
        plt.hist(data)
        plt.subplot(212)
        plt.boxplot(data, vert=False)
        plt.show()

    @staticmethod
    def analyze_category_array(data: pd.Series):
        """
        分析类型数据
        Args:
            data:

        Returns:

        """
        Analyzer.show_plt_completely()
        if not isinstance(data, pd.Series):
            data = pd.Series(data)
        data_value_counts = data.value_counts()
        data_pie = data_value_counts / len(data)
        print(f"""
        data: 
        {data_value_counts}
        data_percent:
        {data_pie.sort_values}
        """
              )
        plt.subplot()
        data_value_counts.plot.bar()
        plt.show()
        plt.subplot()
        data_pie.plot.pie(autopct='%.1f%%', title='pie', )
        plt.show()

    @staticmethod
    def show_bio_data_info(bio_dt: pd.DataFrame, label='DISEASE'):
        """
        show bio format data info
        Args:
            bio_dt: ["sentence_id", "words", "labels"]
            label: entity cls

        Returns:
            info
        """

        labels = bio_dt.groupby(by=['sentence_id'], sort=False)
        from zyl_utils.model_utils.models.ner_bio import NerBIO
        labels = labels.apply(lambda x: x['labels'].tolist())
        y_true = [set(NerBIO.get_id_entity(l, label=label)) for l in labels]
        pos = [y for y in y_true if y != set()]
        neg = [y for y in y_true if y == set()]
        print(f'数据集大小(句): {len(labels)}句')
        print(f'其中有实体的样本数: {len(pos)}句')
        print(f'其中没有实体的样本数: {len(neg)}句')
        print(f'数据集大小(词): {len(bio_dt)}词')
        print(f"其中‘O’标签大小(词): {len(bio_dt[bio_dt['labels'] == 'O'])}词")
        print(f"其中‘B’标签大小(词): {len(bio_dt[bio_dt['labels'].str.startswith('B')])}词")
        print(f"其中‘I’标签大小(词): {len(bio_dt[bio_dt['labels'].str.startswith('I')])}词")


if __name__ == '__main__':
    df = pd.read_hdf('/home/zyl/disk/PharmAI/pharm_ai/panel/data/v4/processing_v4_4.h5',
                     'disease_eval_bio')

    Analyzer.show_bio_data_info(df, label='DISEASE')
