# encoding: utf-8
'''
@author: zyl
@file: Analyzer.py
@time: 2021/11/11 9:34
@desc:
'''
import langid
import matplotlib.pyplot as plt

class BaseAnalyzer:
    def __init__(self):
        pass

    def run(self):
        pass

    @staticmethod
    def get_text_string_length(text:str):
        return len(text)

    @staticmethod
    def get_text_word_length(text: str):
        if langid.classify(text)[0]=='zh':
            return len(text)  # zh -word-piece
        else:
            return len(text.split())  # en - split by space

    @staticmethod
    def get_text_token_length(text: str, tokenizer=None):
        if not tokenizer:
            from transformers import BertTokenizer
            tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        return len(tokenizer.tokenize(text))

    @staticmethod
    def show_df_base_info(df):
        desc = df.describe(percentiles=[0.10,0.25,0.5,0.75,0.85,0.95,0.99])
        print(desc)
        info = df.info()
        print(info)

    @staticmethod
    def draw_box(df,column):
        plt.subplots()
        plt.boxplot(df[column])
        plt.show()

    @staticmethod
    def draw_hist(df,column):
        # df['input_text_length'].plot.hist(bins=2000)  # 列的直方图
        plt.subplots()
        plt.hist(df[column])
        plt.show()

if __name__ == '__main__':

    pass
