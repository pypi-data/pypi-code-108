# -*- coding: utf-8 -*-
__author__ = 'heroli'
'''
将所有的词进行词频统计,并且将生成词频图 ,
清晰看清词的核心程度
'''

# wordcloud生成中文词云
from wordcloud import WordCloud
import jieba
# 词频计算
import jieba.analyse as analyse
# from scipy.misc import imread
import os
from os import path
import matplotlib.pyplot as plt


class WC(object):
    # 绘制词云
    def draw_wordcloud(self, text):
        # 读入一个txt文件
        comment_text = text
        # 结巴分词，生成字符串，如果不通过分词，无法直接生成正确的中文词云
        cut_text = " ".join(jieba.cut(comment_text))
        result = jieba.analyse.textrank(cut_text, topK=1000, withWeight=True)
        # 生成关键词比重字典
        keywords = dict()

        for i in result:
            keywords[i[0]] = i[1]

        d = path.dirname(__file__)  # 当前文件文件夹所在目录
        # color_mask = imread("static/images/alice.png") # 读取背景图片
        cloud = WordCloud(
            # 设置字体，不指定就会出现乱码
            font_path="./simfang.ttf",
            # font_path=path.join(d,'simsun.ttc'),
            width=500,
            height=500,
            # 设置背景色
            background_color='white',
            # 词云形状
            # mask=color_mask,
            # 允许最大词汇
            max_words=2000,
            # 最大号字体
            max_font_size=60
        )
        word_cloud = cloud.generate(cut_text)  # 产生词云
        # word_cloud.to_file("/Users/apple/Desktop/归档/user_img.jpg") #保存图片的位置
        # 或者 显示词云图片
        plt.imshow(word_cloud)
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    wc = WC()
    wc.draw_wordcloud(
        '爱是什么？一个精灵坐在碧绿的枝叶间沉思。风儿若有若无。一只鸟儿飞过来，停在枝上，望着远处将要成熟的稻田。精灵取出一束黄澄澄的稻谷问道：“你爱这稻谷吗？”“爱。”“为什么？”“它驱赶我的饥饿。”鸟儿啄完稻谷，轻轻梳理着光润的羽毛。“现在你爱这稻谷吗？”精灵又取出一束黄澄澄的稻谷。鸟儿抬头望着远处的一湾泉水回答：“现在我爱那一湾泉水，我有点渴了。”精灵摘下一片树叶，里面盛了一汪泉水。鸟儿喝完泉水，准备振翅飞去。“请再回答我一个问题，”精灵伸出指尖，鸟儿停在上面。“你要去做什么更重要的事吗？我这里又稻谷也有泉水。”“我要去那片开着风信子的山谷，去看那朵风信子。”“为什么？它能驱赶你的饥饿？”“不能。”“它能滋润你的干渴？”“不能。”“那你为什么要去看它呢？”“我需要它啊。”“为什么需要？”“我爱它啊。”“为什么爱它？”“我日日夜夜都在思念它。”“为什么思念它？”“我爱它。”精灵沉默了片刻，又提出一个问题：“你为什么只爱那一朵风信子呢？山谷里有无数朵风信子。”“因为它是唯一的一朵啊。”“为什么？它和其他所有的风信子有什么不同的地方吗？”“有的。”“哪里不同呢？”“只有它才是我爱的那一朵啊。”精灵忽然轻轻笑了起来，鸟儿振翅而去')
