import collections
import math
import jieba.posseg as pseg
# https://github.com/liuhuanyong/WordCollocation
class MI_Train:
    def __init__(self, window_size, filepath, mipath):
        self.window_size = window_size
        self.filepath = filepath
        self.mipath = mipath

    #对语料进行处理
    def build_corpus(self):
        def cut_words(sent):
            return [word.word for word in pseg.cut(sent) if word.flag[0] not in ['x', 'w', 'p', 'u', 'c']]
       # sentences = [sent.split(' ') for sent in open(self.filepath).read().split('\n')]，若处理英文语料则使用这种方法
        sentences = [cut_words(sent) for sent in open(self.filepath).read().split('\n')]
        return sentences

    #统计词频
    def count_words(self, sentences):
        words_all = list()
        for sent in sentences:
            words_all.extend(sent)
        word_dict = {item[0]:item[1] for item in collections.Counter(words_all).most_common()}
        return word_dict, len(words_all)

    #读取训练语料
    def build_cowords(self, sentences):
        train_data = list()
        for sent in sentences:
            for index, word in enumerate(sent):
                if index < self.window_size:
                    left = sent[:index]
                else:
                    left = sent[index - self.window_size: index]
                if index + self.window_size > len(sent):
                    right = sent[index+1 :]
                else:
                    right = sent[index+1: index + self.window_size + 1]
                data = left + right + [sent[index]]
                if '' in data:
                    data.remove('')
                train_data.append(data)
        return train_data

    #统计共现次数
    def count_cowords(self, train_data):
        co_dict = dict()
        print(len(train_data))
        for index, data in enumerate(train_data):
            for index_pre in range(len(data)):
                for index_post in range(len(data)):
                    if data[index_pre] not in co_dict:
                        co_dict[data[index_pre]] = data[index_post]
                    else:
                        co_dict[data[index_pre]] += '@' + data[index_post]
        return co_dict

    # 计算互信息
    def compute_mi(self, word_dict, co_dict, sum_tf):
        def compute_mi(p1, p2, p12):
            return math.log2(p12) - math.log2(p1) - math.log2(p2)

        def build_dict(words):
            return {item[0]:item[1] for item in collections.Counter(words).most_common()}

        mis_dict = dict()
        for word, co_words in co_dict.items():
            co_word_dict = build_dict(co_words.split('@'))
            mi_dict = {}
            for co_word, co_tf in co_word_dict.items():
                if co_word == word:
                    continue
                p1 = word_dict[word]/sum_tf
                p2 = word_dict[co_word]/sum_tf
                p12 = co_tf/sum_tf
                mi = compute_mi(p1, p2, p12)
                mi_dict[co_word] = mi
            mi_dict = sorted(mi_dict.items(), key = lambda asd:asd[1], reverse= True)
            mis_dict[word] = mi_dict

        return mis_dict

    # 保存互信息文件
    def save_mi(self, mis_dict):
        f = open(self.mipath, 'w+')
        for word, co_words in mis_dict.items():
            co_infos = [item[0] + '@' + str(item[1]) for item in co_words]
            f.write(word + '\t' + ','.join(co_infos) + '\n')
        f.close()

    # 运行主函数
    def mi_main(self):
        print('step 1/6: build corpus ..........')
        sentences = self.build_corpus()
        print('step 2/6: compute worddict..........')
        word_dict, sum_tf = self.count_words(sentences)
        print('step 3/6: build cowords..........')
        train_data = self.build_cowords(sentences)
        print('step 4/6: compute coinfos..........')
        co_dict = self.count_cowords(train_data)
        print('step 5/6: compute words mi..........')
        mi_data = self.compute_mi(word_dict, co_dict, sum_tf)
        print('step 6/6: save words mi..........')
        self.save_mi(mi_data)
        print('done!.......')

#测试
def test():
    filepath = './data/data.txt'
    mipath = './data/result.txt'
    window_size = 5
    mier = MI_Train(window_size, filepath, mipath)
    mier.mi_main()

if __name__=='__main__':
    test()
# WordCollocation
# Self complemented Word Collocation(词语搭配) using MI method which is tested to be effective..
#
# 原理
# 互信息体现了两个变量之间的相互依赖程度。二元互信息是指两个事件相关性的量，互信息值越高, 表明X和Y相关性越高, 则X和Y 组成短语的可能性越大; 反之, 互信息值越低,X 和Y之间相关性越低, 则X 和Y之间存在短语边界的可能性越大。
#
# 用途
# 利用两个词语之间的相互依赖程度，能够求得一个词的常用搭配，可以有以下用途：
# 1、为词语搭配知识库建设，可用于输入短语推荐
# 2、词语语义刻画与表示提供帮助，若以搭配强度作为词-词矩阵的weight度量，可以用来计算两个词之间的相似度
# 3、若给定历史语料库，可以通过历时搭配来监测词汇语义的变迁
#
# 提取步骤
# step 1/6: build corpus ..........
# step 2/6: compute worddict..........
# step 3/6: build cowords..........
# step 4/6: compute coinfos..........
# step 5/6: compute words mi..........
# step 6/6: save words mi..........
#
# 输入与输出
# 1）输入：
# 1、1W个文档，每个文档为一行，保存在'./data/data.txt'中
# 2）输出：
# 1、格式：(词语 制表符 搭配词1_搭配强度1,搭配词2_搭配强度2)
# 2、结果保存，保存在'./data/resut.txt'中
# 3）参数： 1、window_size: 默认为5， 左右窗口为5， 作为词共现窗口
#
# 效果
# 以1W个文档/句子作为训练语料，进行训练，得到结果举例如下：
# word:陷入
# word collocations Top 10:
# 不由得@18.05618124455273
# 两难@17.83378882321628
# 林林总总@17.57075441738249
# 不怎么@17.248826322495123
# 误区@17.248826322495123
# 市面上@17.248826322495123
# 失落@16.386329846245058
# 困境@15.83378882321628
# 母亲@15.511860728328918
# 常@15.471218743831571
#
# word:乐于
# word collocations Top 10:
# 吃苦耐劳@19.57075441738249
# 奉献@18.57075441738249
# 事业心@18.57075441738249
# 作风@18.248826322495123
# 务实@17.418751323937435
# 责任感@17.248826322495123
# Kevin@17.248826322495123
# 政治素质@16.248826322495123
# 热爱@15.959319705300139
# 客户@15.734253149665365