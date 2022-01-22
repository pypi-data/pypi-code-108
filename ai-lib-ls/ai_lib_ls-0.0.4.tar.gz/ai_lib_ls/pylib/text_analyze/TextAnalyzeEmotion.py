# -*- coding: utf-8 -*-
from aliyunsdkcore.client import AcsClient
from snownlp import SnowNLP  # 情感分析取值
from aip import AipNlp  # 百度的情感分析


# SnowNLP的情感分析取值，表达的是“这句话代表正面情感的概率”。
# 也就是说，对“我今天很愤怒”一句，SnowNLP认为，它表达正面情感的概率很低很低
class SnowNLPText:

    def good_probability(self, text):
        ''' 好消息的概率 '''
        s = SnowNLP(text)
        s1 = SnowNLP(s.sentences[0])
        return s1.sentiments

    def text_words(self, text):
        ''' 信息的分词 '''
        s = SnowNLP(text)
        s1 = SnowNLP(s.sentences[0])
        return s1.words

class BaiNLP:
    def __init__(self):
        """ 你的 APPID AK SK """
        APP_ID = '23985926'
        API_KEY = 'Ieo3GfdpCGWN6iQn8tPQLsGa'
        SECRET_KEY = '1TByQj5Me8OsxoqntT7z5fvyWylnvrww'
        self.client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

    def cheak(self, text):  # 2次/秒 ,50w使用量
        """ 调用情感倾向分析 """
        # return :
        # sentiment :表示情感极性分类结果, 0:负向，1:中性，2:正向
        # confidence:表示分类的置信度
        # positive_prob: 表示属于积极类别的概率
        # negative_prob : 表示属于消极类别的概率
        return self.client.sentimentClassify(text)


# 阿里云 NLP 情感模型分析 要 150/年
class ALiNLP:

    def __init__(self):
        # 创建AcsClient实例
        self.client = AcsClient(
            'LTAI5tQ9uYTsficdW4pqeEov',
            '1B4BbL2V9CpMBP09HQ7fOTeL29i3zX',
            "cn-hangzhou"
        )

    def go(self):
        pass


if __name__ == '__main__':
    # ali = ALiNLP()
    # ali.go()

    '''
    baiduNlptext = BaiNLP()
    item = baiduNlptext.cheak("听到这句话,我很不安!")
    print(item)
    '''
    # 处理的是评论,建议使用规则是一句话
    '''
    s = SnowNLP(u'听到这句话,我很不安!')
    s1 = SnowNLP(s.sentences[0])
    print(s1.sentiments)  # positive正面的概率
    print(s1.words)
    

    # for sentence in s.sentences:
    #     s1 = SnowNLP(s.sentences[0])
    #     s1.sentiments
    #     print(sentence)

    '''

    # for sentence in s.sentences:
    #     s1 = SnowNLP(s.sentences[0])
    #     s1.sentiments
    #     print(sentence)
