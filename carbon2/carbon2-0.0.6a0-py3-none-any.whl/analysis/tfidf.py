import pickle, json, requests
import numpy as np
import jieba
import os
from tqdm import tqdm
import pickle
from quick_crawler.page import *
import jieba.posseg as peg
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def load_all_data(source_csv_file,raw_data_folder,keywords_path="",keyword_file_list="",keyword_file_list_folder="",save_corpus_path=""):
    # load all data
    corpus = []
    list_model = quick_read_csv_model(source_csv_file)

    if keywords_path!="" and keyword_file_list!="":
        carbon2_dictionary = load_high_quality_dictionary(keyword_file_list)
        pickle.dump(carbon2_dictionary, open(keywords_path, "wb"))
        print(carbon2_dictionary)
        jieba.load_userdict(carbon2_dictionary)

    for model in tqdm(list_model):
        file_id = model["FileId"]
        file_path = f"{raw_data_folder}/{file_id}.txt"
        if os.path.exists(file_path):
            html_obj = BeautifulSoup(open(file_path, 'r', encoding='utf-8').read(), features='lxml')
            remove_tags = ['style', 'script', 'svg', 'path', 'noscript']
            for tag in remove_tags:
                for item in html_obj.findAll(tag):
                    item.decompose()
            full_text = ""
            ps = html_obj.findAll("p")
            for p in ps:
                p_text = p.text
                p_text = p_text.strip()
                if len(p_text) > 10:
                    full_text += p_text + "\n"
            full_text = full_text.strip()
            full_text = ' '.join(jieba.cut(full_text))
            # print(full_text)
            tokens = process_text_into_tokens(full_text)
            print(file_path, tokens)
            corpus.append(tokens)

    pickle.dump(corpus, open(save_corpus_path, "wb"))
    return corpus

def load_high_quality_dictionary(file_list="cnki_data.txt;cnki_data1.txt;cnki_data2.txt",folder="datasets"):
    files=file_list.split(";")
    list_words = []
    for f in files:
        lines=open(f"{folder}/{f}","r",encoding='utf-8')
        for l in lines:
            l=l.strip()
            if l.startswith("K1"):
                ks=l.split(" ")
                if len(ks)==2:
                    ws=ks[1].split(";")
                    print(ws)
                    for k in ws:
                        if k not in list_words:
                            list_words.append(k)
    return list_words



def load_stopwords(stopwords_folder="datasets/stopwords"):
    list_stopwords_all=[]
    for file in os.listdir(stopwords_folder):
        path=os.path.join(stopwords_folder,file)
        lines=open(path,'r',encoding='utf-8').readlines()
        for w in lines:
            w=w.strip()
            if w!="":
                if w not in list_stopwords_all:
                    list_stopwords_all.append(w)
    return list_stopwords_all

list_stopwords=load_stopwords()

def seg_cut(in_str):
    words = peg.cut(in_str)
    result1 = ""
    list_word=[]
    for word, flag in words:
        # temp = "%s_%s " % (word, flag)
        # result1 = result1 + temp
        list_word.append([word,flag])
    return list_word

def process_text_into_tokens(text):
    text=text.strip()
    lines=text.split("\n")
    tokens=[]
    for line in lines:
        line=line.strip()
        sentences=line.split("。")
        for sentence in sentences:
            sentence=sentence.strip()
            # words=jieba.cut(sentence,cut_all=False)
            words=seg_cut(sentence)
            new_words=[]
            for item in words:
                w=item[0]
                pos=item[1]
                w=w.strip()
                w = w.lower()
                if w=="":
                    continue
                if len(w)!=4 and w.isnumeric():
                    continue
                if len(w)==4 and w.isnumeric() and not w.startswith("20") and not w.startswith("19"):
                    continue
                if pos not in ['n']: # 词性过滤
                    continue
                if not w in list_stopwords:
                    new_words.append(w)

            for w in new_words:
                tokens.append(w)
    return tokens



class KeyWordsBasesOnTermFreq():

    def get_freq(self, words):  # 统计一个词语列表中的term freq
        word_freq_map = {}
        for word in words:
            word_freq_map[word] = word_freq_map.get(word, 0) + 1
        return word_freq_map

    # 基于词语频数/term freq抽取关键词
    def get_keywords_based_on_freq(self, content, topN=10):
        words = process_text_into_tokens(content)  # 分词
        word_freq_map = self.get_freq(words)  # 获取词频
        keywords = sorted(word_freq_map.items(), key=lambda x: x[1], reverse=True)  # 按照词频倒序排列
        keywords = keywords[:topN]  # 挑选关键词
        keywords = list(map(lambda x: x[0], keywords))
        return keywords


class KeyWOrdsBasedOnTFIDF(KeyWordsBasesOnTermFreq):

    def __init__(self, corpus=None, idf_path=None):
        self.init_idf(corpus, idf_path)

    def init_idf(self, corpus, idf_path):
        # 初始化idf.如果制定了文件路径就直接加载；如果没有指定就训练一个
        if idf_path == None:

            words_list = corpus
            doc_num = len(words_list)
            doc_freq_map = {}
            for words in words_list:
                for word in set(words):
                    doc_freq_map[word] = doc_freq_map.get(word, 0) + 1
            self.idf_map = {}
            for word in doc_freq_map:
                self.idf_map[word] = np.log(doc_num / (doc_freq_map[word] + 1) ** 0.6)
            print(self.idf_map)
            # pickle.dump(self.idf_map, open('idf.pkl', 'wb'))
        else:
            self.idf_map = pickle.load(open(idf_path, 'rb'))

    def get_tfidf(self, content):
        words = process_text_into_tokens(content)
        tf_map = self.get_freq(words)
        tfidf_map = {}
        for word in tf_map:
            if word in self.idf_map:  # 训练语料中没有出现的词语就干掉了
                tfidf_map[word] = tf_map[word] * self.idf_map[word]
        return tfidf_map

    def get_keywords_based_on_tfidf(self, content, topN=10):
        tfidf_map = self.get_tfidf(content)  # 获取tfidf值
        keywords = sorted(tfidf_map.items(), key=lambda x: x[1], reverse=True)
        keywords = keywords[:topN]
        keywords = list(map(lambda x: x[0], keywords))
        return keywords

def get_all_tokens(corpus):
    all_text=[]
    for tokens in corpus:
        all_text+=tokens
    return all_text

def get_all_text(corpus):
    all_text=""
    for tokens in corpus:
        all_text+=''.join(tokens)
    return all_text

def run_tfidf_model(source_csv_file,raw_data_folder,keywords_path="",keyword_file_list="",keyword_file_list_folder="",save_corpus_path="",save_freq_filepath="",save_tfidf_path=""):

    corpus=load_all_data(source_csv_file,raw_data_folder,keywords_path,keyword_file_list,keyword_file_list_folder, save_corpus_path)

    kw_extractor_tf = KeyWordsBasesOnTermFreq()
    print("Term Frequency: ")
    kw_extractor_tf.get_freq(get_all_tokens(corpus))
    keywords=kw_extractor_tf.get_keywords_based_on_freq(get_all_text(corpus), topN=100)
    pickle.dump(keywords,open(save_freq_filepath,"wb"))
    for w in keywords:
        print(w)
    print()
    print("TF-IDF ：")
    kw_extractor_tfidf = KeyWOrdsBasedOnTFIDF(corpus=corpus)
    dict_words={}
    for c in corpus:
        list_words=kw_extractor_tfidf.get_keywords_based_on_tfidf(''.join(c),topN=20)
        for w in list_words:
            if w in dict_words:
                dict_words[w]+=1
            else:
                dict_words[w]=1
    sorted_dict_words=sorted(dict_words.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
    pickle.dump(sorted_dict_words,open(save_tfidf_path,"wb"))
    print("Term\tFrequency")
    count=0
    for word, freq in sorted_dict_words[:100]:
        if count >= 100:
            break
        print(f"{word}\t{freq}")
        count += 1


def export_keywords(freq_file, tfidf_file, save_tfidf_keywords, save_tf_keywords):
    keywords_freq = pickle.load(open(freq_file, 'rb'))
    for k in keywords_freq:
        print(k)

    print()

    keywords_tfidf = pickle.load(open(tfidf_file, "rb"))
    print(keywords_tfidf)
    count = 0
    for word, freq in keywords_tfidf[:100]:
        if count >= 100:
            break
        print(f"{word}\t{freq}")
        count += 1

    f_out = open(save_tfidf_keywords, "w", encoding='gbk')
    f_out.write("Keyword(TF),Keywords(TF-IDF)\n")
    for idx, k in enumerate(keywords_freq):
        f_out.write(f"{k},{keywords_tfidf[idx][0]}\n")
    f_out.close()

def load_cnki_dictionary(file_list="cnki_data.txt;cnki_data1.txt;cnki_data2.txt",folder="datasets"):
    files=file_list.split(";")
    dict_words={}
    for f in files:
        lines=open(f"{folder}/{f}","r",encoding='utf-8')
        for l in lines:
            l=l.strip()
            if l.startswith("K1"):
                ks=l.split(" ")
                if len(ks)==2:
                    ws=ks[1].split(";")
                    print(ws)
                    for k in ws:
                        if k.strip()=="":
                            continue
                        if k not in dict_words:
                            dict_words[k]=1
                        else:
                            dict_words[k]+=1
    return dict_words

def export_keywords_dictionary(file_list="cnki_data.txt;cnki_data1.txt;cnki_data2.txt",folder="datasets",save_csv_path=""):
    dict_words_cnki = load_cnki_dictionary(file_list,folder)
    sorted_dict_words_cnki = sorted(dict_words_cnki.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    f_out = open(save_csv_path, "w", encoding='gbk')
    f_out.write("Keyword,Frequency\n")
    for t, f in sorted_dict_words_cnki:
        f_out.write(f"{t},{f}\n")
    f_out.close()


def load_corpus(corpus_path,remove_words=""):

    corpus=pickle.load(open(corpus_path,"rb"))

    all_text=[]
    for tokens in corpus:
        new_tokens=[]
        for w in tokens:
            if remove_words!="":
                wl=remove_words.split(";")
                if w not in wl:
                    new_tokens.append(w)
            else:
                new_tokens.append(w)

        all_text=all_text + new_tokens

    return all_text

def run_wordcloud(corpus_path,save_fig_path, font_path):
    # list_word=load_cnki_dictionary()
    list_word = load_corpus(corpus_path)

    print(len(list_word))
    mytext = ' '.join(list_word)
    current_path = os.path.dirname(os.path.realpath(__file__))
    wordcloud = WordCloud(
        max_words=150,
        # font_path=f"{current_path}/utils/fonts/SimHei.ttf",
        font_path=font_path,
        width=2000, height=2000, background_color="white",
    ).generate(mytext)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(save_fig_path, dpi=600)
    plt.show()
