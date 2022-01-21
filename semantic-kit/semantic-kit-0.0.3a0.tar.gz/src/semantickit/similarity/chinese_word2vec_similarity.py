import jieba
import os
from gensim.models import word2vec
import multiprocessing

class ChineseWord2Vec:
    def __init__(self,data_path,user_dict_path,output_segment_path,stop_words_path, word2vec_model_path):
        self.data_path=data_path
        self.user_dict_path=user_dict_path
        self.output_segment_path=output_segment_path
        self.word2vec_model_path=word2vec_model_path
        self.stop_words_path=stop_words_path

    def getStopwords(self,path):
        stopwords = []
        with open(path, "r", encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                stopwords.append(line.strip())
        return stopwords

    def segment_lines(self,file_list, segment_out_dir, stopwords=None):
        for i, file in enumerate(file_list):
            segment_out_name = os.path.join(segment_out_dir, 'segment_{}.txt'.format(i))
            segment_file = open(segment_out_name, 'a', encoding='utf8')
            with open(file, encoding='utf8') as f:
                text = f.readlines()
                for sentence in text:
                    # jieba.cut():参数sentence必须是str(unicode)类型
                    sentence = list(jieba.cut(sentence))
                    sentence_segment = []
                    for word in sentence:
                        if word not in stopwords:
                            sentence_segment.append(word)
                    segment_file.write(" ".join(sentence_segment))
                del text
                f.close()
            segment_file.close()

    def getFilePathList(self,file_dir):
        filePath_list = []
        for walk in os.walk(file_dir):
            part_filePath_list = [os.path.join(walk[0], file) for file in walk[2]]
            filePath_list.extend(part_filePath_list)
        return filePath_list

    def get_files_list(self,file_dir, postfix='ALL'):
        postfix = postfix.split('.')[-1]
        file_list = []
        filePath_list = self.getFilePathList(file_dir)
        if postfix == 'ALL':
            file_list = filePath_list
        else:
            for file in filePath_list:
                basename = os.path.basename(file)  # 获得路径下的文件名
                postfix_name = basename.split('.')[-1]
                if postfix_name == postfix:
                    file_list.append(file)
        file_list.sort()
        return file_list

    def train_wordVectors(self,sentences, embedding_size=128, window=5, min_count=5):
        w2vModel = word2vec.Word2Vec(sentences, size=embedding_size, window=window, min_count=min_count,
                                     workers=multiprocessing.cpu_count())
        return w2vModel

    def save_wordVectors(self,w2vModel, word2vec_path):
        w2vModel.save(word2vec_path)

    def load_wordVectors(self,word2vec_path):
        w2vModel = word2vec.Word2Vec.load(word2vec_path)
        return w2vModel

    def cut(self,enable_parallel=False):
        # 多线程分词
        if enable_parallel:
            jieba.enable_parallel()
        # 加载自定义词典
        jieba.load_userdict(self.user_dict_path)

        stopwords = self.getStopwords(self.stop_words_path)

        file_list = self.get_files_list(self.data_path, postfix='*.txt')
        self.segment_lines(file_list, self.output_segment_path, stopwords)

    def train(self,embedding_size=128,window=5,min_count=5):
        sentences = word2vec.PathLineSentences(self.output_segment_path)

        # 简单的训练
        # model = word2vec.Word2Vec(sentences, hs=1, min_count=1, window=3, size=100)
        # print(model.wv.similarity('沙瑞金', '高育良'))
        # print(model.wv.similarity('李达康'.encode('utf-8'), '王大路'.encode('utf-8')))

        # 一般训练，设置以下几个参数即可：
        # word2vec_path = './models/word2Vec.model'
        model2 = self.train_wordVectors(sentences, embedding_size=embedding_size, window=window, min_count=min_count)
        self.save_wordVectors(model2, self.word2vec_model_path)

    def similarity(self,word1,word2):
        model2 = self.load_wordVectors(self.word2vec_model_path)
        result=model2.wv.similarity(word1, word2)
        return result


