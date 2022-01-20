# encoding: utf-8
"""
@author: zyl
@file: my_utils.py
@time: ~~
@desc: zyl utils
"""

import re

import langid
import pandas as pd


class MyTokenizer:
    def __init__(self):
        # 把连号‘-’分开
        self.sentences_tokenizer_zh = self._cut_paragraph_to_sentences_zh
        self.sentences_tokenizer_en = self._cut_paragraph_to_sentences_en().tokenize

        self.words_tokenizer_zh = self._cut_sentence_to_words_zh
        self.words_tokenizer_en = self._cut_sentence_to_words_en().tokenize

    def _cut_paragraph_to_sentences_zh(self, para: str, drop_empty_line=True, strip=True, deduplicate=False):
        """
        Args:
           para: 输入文本
           drop_empty_line: 是否丢弃空行
           strip:  是否对每一句话做一次strip
           deduplicate: 是否对连续标点去重，帮助对连续标点结尾的句子分句

        Returns:
           sentences: list of str
        """
        if deduplicate:
            para = re.sub(r"([。！？\!\?])\1+", r"\1", para)

        para = re.sub('([。！？\?!])([^”’])', r"\1\n\2", para)  # 单字符断句符
        para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
        para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
        para = re.sub('([。！？\?!][”’])([^，。！？\?])', r'\1\n\2', para)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        para = para.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        sentences = para.split("\n")
        if strip:
            sentences = [sent.strip() for sent in sentences]
        if drop_empty_line:
            sentences = [sent for sent in sentences if len(sent.strip()) > 0]
        return sentences

    def _cut_paragraph_to_sentences_en(self):
        from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
        punkt_param = PunktParameters()
        abbreviation = ['et al.', 'i.e.', 'e.g.', 'etc.', 'i.e', 'e.g', 'etc', ' et al']
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param)
        return tokenizer

    def _cut_sentence_to_words_zh(self, sentence: str):
        english = 'abcdefghijklmnopqrstuvwxyz0123456789αγβδεζηθικλμνξοπρστυφχψω'
        output = []
        buffer = ''
        for s in sentence:
            if s in english or s in english.upper():  # 英文或数字
                buffer += s
            else:  # 中文
                if buffer:
                    output.append(buffer)
                buffer = ''
                output.append(s)
        if buffer:
            output.append(buffer)
        return output

    def _cut_sentence_to_words_en(self):
        from nltk import WordPunctTokenizer
        # from transformers import BasicTokenizer
        # BasicTokenizer(do_lower_case=False).tokenize()
        return WordPunctTokenizer()

    def cut_sentence_to_words(self, sentence: str):
        if langid.classify(sentence)[0] == 'zh':
            return self.words_tokenizer_zh(sentence)
        else:
            return self.words_tokenizer_en(sentence)

    def cut_paragraph_to_sentences(self, paragraph: str):
        if langid.classify(paragraph)[0] == 'zh':
            return self.sentences_tokenizer_zh(paragraph)
        else:
            return self.sentences_tokenizer_en(paragraph)


class NlpUtils:
    def __init__(self):
        pass

    @staticmethod
    def show_all():
        import pandas as pd
        # 设置value的显示长度为200，默认为50
        pd.set_option('max_colwidth', 250)
        # 显示所有列，把行显示设置成最大
        pd.set_option('display.max_columns', None)
        # 显示所有行，把列显示设置成最大
        pd.set_option('display.max_rows', None)

    @staticmethod
    def df_clean_language(df, column_name, language_list=('en', 'zh')):
        # dataframe过滤出某一列文本的语言
        import langid
        df['language'] = df[column_name].apply(lambda x: langid.classify(str(x))[0])
        df = df[df['language'].isin(language_list)]
        df = df.drop(['language'], axis=1)
        return df

    @staticmethod
    def split_data_evenly(dt, num):
        dt_length = len(dt)
        step = int(dt_length / num)
        other_dt = dt_length % num

        if dt_length <= num:
            print('dt_length <= dt_num')
            return dt
        if other_dt == 0:
            return [dt[i:i + step] for i in range(0, dt_length, step)]
        else:
            first_dt = [dt[i:i + step + 1] for i in range(0, int((step + 1) * other_dt), step + 1)]
            second_list = [dt[i:i + step] for i in range(int((step + 1) * other_dt), dt_length, step)]
            first_dt.extend(second_list)
            return first_dt

    @staticmethod
    def clean_text(text):
        import re
        text = re.sub('<[^<]+?>', '', text).replace('\n', '').strip()  # 去html中的<>标签
        text = ' '.join(text.split()).strip()
        return text

    @staticmethod
    def cut_train_eval(all_df):
        from sklearn.utils import resample
        raw_df = resample(all_df, replace=False)
        cut_point = min(5000, int(0.2 * len(raw_df)))
        eval_df = raw_df[0:cut_point]
        train_df = raw_df[cut_point:]
        return train_df, eval_df

    @staticmethod
    def two_classification_sampling(train_df, column='labels', pos_label=1, mode='up_sampling'):
        import pandas as pd
        from sklearn.utils import resample
        negative_df = train_df[train_df[column] != pos_label]
        neg_len = negative_df.shape[0]
        positive_df = train_df[train_df[column] == pos_label]
        pos_len = positive_df.shape[0]
        if neg_len > pos_len:
            if mode == 'down_sampling':
                down_sampling_df = resample(negative_df, replace=False, n_samples=pos_len, random_state=242)
                return pd.concat([positive_df, down_sampling_df], ignore_index=True)
            else:

                up_sampling_df = resample(positive_df, replace=True, n_samples=(neg_len - pos_len), random_state=242)
                return pd.concat([train_df, up_sampling_df], ignore_index=True)
        elif neg_len < pos_len:
            if mode == 'down_sampling':
                down_sampling_df = resample(positive_df, replace=False, n_samples=neg_len, random_state=242)
                return pd.concat([down_sampling_df, negative_df], ignore_index=True)
            else:
                up_sampling_df = resample(negative_df, replace=True, n_samples=(pos_len - neg_len), random_state=242)
                return pd.concat([train_df, up_sampling_df], ignore_index=True)
        else:
            return train_df

    @staticmethod
    def find_index(raw_text, find_text, label='label'):
        # special_character = set(re.findall('\W', str(raw_text)))
        # for i in special_character:
        #     raw_text = raw_text.replace(i, '\\' + i)
        re_result = re.finditer(find_text, raw_text)
        starts = []
        for i in re_result:
            starts.append(i.span()[0])
        return [{'label': label, 'start': s, 'offset': len(find_text)} for s in starts]

    @staticmethod
    def ner_find(text: str, entities: dict, ignore_nested=True):
        """
        find the loaction of entities in a text
        Args:
            text: a text, like '我爱吃苹果、大苹果，小苹果，苹果【II】，梨子，中等梨子，雪梨，梨树。'
            entities: {'entity_type1':{entity_str1,entity_str2...},
                       'entity_type2':{entity_str1,entity_str2...},
                       ...}
                       like : {'apple': ['苹果', '苹果【II】'], 'pear': ['梨', '梨子'],}
            ignore_nested: if nested
        #>>>IndexedRuleNER().ner(text, entities, False)
        Returns:
            indexed_entities:{'entity_type1':[[start_index,end_index,entity_str],
                                              [start_index,end_index,entity_str]...]
                              'entity_type2':[[start_index,end_index,entity_str],
                                              [start_index,end_index,entity_str]...]
                                              ...}
        #>>>{'apple': [[3, 5, '苹果'], [7, 9, '苹果'], [11, 13, '苹果'], [14, 16, '苹果'], [14, 20, '苹果【II】']],
        'pear': [[21, 22, '梨'], [26, 27, '梨'], [30, 31, '梨'], [32, 33, '梨'], [21, 23, '梨子'], [26, 28, '梨子']]}
        """

        indexed_entities = dict()
        for every_type, every_value in entities.items():
            every_type_value = []
            for every_entity in list(every_value):
                special_character = set(re.findall('\W', str(every_entity)))
                for i in special_character:
                    every_entity = every_entity.replace(i, '\\' + i)
                re_result = re.finditer(every_entity, text)
                for i in re_result:
                    res = [i.span()[0], i.span()[1], i.group()]
                    if res != []:
                        every_type_value.append([i.span()[0], i.span()[1], i.group()])
            indexed_entities[every_type] = every_type_value
        if ignore_nested:
            for key, value in indexed_entities.items():
                all_indexs = [set(range(i[0], i[1])) for i in value]
                for i in range(len(all_indexs)):
                    for j in range(i, len(all_indexs)):
                        if i != j and all_indexs[j].issubset(all_indexs[i]):
                            value.remove(value[j])
                            indexed_entities[key] = value
                        elif i != j and all_indexs[i].issubset(all_indexs[j]):
                            value.remove(value[i])
                            indexed_entities[key] = value
        return indexed_entities

    @staticmethod
    def remove_some_model_files(args):
        import os
        if os.path.isdir(args.output_dir):
            cmd = 'rm -rf ' + args.output_dir.split('outputs')[0] + 'outputs/'
            os.system(cmd)
        if os.path.isdir(args.output_dir.split('outputs')[0] + '__pycache__/'):
            cmd = 'rm -rf ' + args.output_dir.split('outputs')[0] + '__pycache__/'
            os.system(cmd)
        if os.path.isdir(args.output_dir.split('outputs')[0] + 'cache/'):
            cmd = 'rm -rf ' + args.output_dir.split('outputs')[0] + 'cache/'
            os.system(cmd)

    # @staticmethod
    # def sunday_match(target, pattern):
    #     """
    #
    #     Args:
    #         target:
    #         pattern:
    #
    #     Returns:
    #
    #     """
    #     len_target = len(target)
    #     len_pattern = len(pattern)
    #
    #     if len_pattern > len_target:
    #         return list()
    #
    #     index = 0
    #     starts = []
    #     while index < len_target:
    #         if pattern == target[index:index + len_pattern]:
    #             starts.append(index)
    #             index += 1
    #         else:
    #             if (index + len(pattern)) >= len_target:
    #                 return starts
    #             else:
    #                 if target[index + len(pattern)] not in pattern:
    #                     index += (len_pattern + 1)
    #                 else:
    #                     index += 1
    #     return starts

    # @staticmethod
    # def transfomer_data_format_from_t5_to_ner(df: pd.DataFrame, delimiter='|',
    #                                           keep_addition_info=('id', 'text_type')):
    #     """
    #
    #     Args:
    #         df: dataframe,must have the columns-['prefix','input_text','target_text']
    #
    #     Returns:
    #
    #     """
    #     all_cls = df.value_counts('prefix').index.to_list()
    #     custom_labels = ['O']
    #     for c in all_cls:
    #         custom_labels.append('B-' + c.upper())
    #         custom_labels.append('I-' + c.upper())
    #     sentence_id = 0
    #     res_li = []
    #     my_tokenizer = MyTokenizer()
    #
    #     df = df.drop_duplicates(subset=['input_text'])
    #     for input_text, sub_df in tqdm(df.groupby('input_text', sort=False)):
    #         words = my_tokenizer.cut_sentence_to_word_piece(input_text)
    #         labels = ['O'] * len(words)
    #
    #         for _, d in sub_df.iterrows():
    #             if keep_addition_info:
    #                 for k in range(len(keep_addition_info)):
    #                     exec(f'info_{k} = d[keep_addition_info[{k}]]')
    #
    #             cls = d['prefix']
    #             sub_label = set(d['target_text'].split(delimiter))
    #             while '' in sub_label:
    #                 sub_label.remove('')
    #             if sub_label:
    #                 for every_entity in sub_label:
    #                     entity = my_tokenizer.cut_sentence_to_word_piece(every_entity)
    #                     res_starts = sunday_match(target=words, pattern=entity)
    #                     if res_starts:
    #                         for r in res_starts:
    #                             labels[r] = 'B-' + cls.upper()
    #                             if len(entity) > 1:
    #                                 labels[r + 1: r + len(entity)] = ['I-' + cls.upper()] * (len(entity) - 1)
    #
    #         sentence_ner = []
    #         for w, l in zip(words, labels):
    #             r = {'sentence_id': sentence_id, 'words': w, 'labels': l}
    #             if keep_addition_info:
    #                 for k in range(len(keep_addition_info)):
    #                     r.update({keep_addition_info[k]: eval(f'info_{k}')})
    #             sentence_ner.append(r)
    #
    #         res_li.extend(sentence_ner)
    #         sentence_id += 1
    #
    #     df = pd.DataFrame(res_li)
    #     return df


if __name__ == '__main__':
    test_df = pd.read_excel("/home/zyl/disk/PharmAI/pharm_ai/panel/data/v2.4.c/processed_0820.xlsx", 'eval')[0:100]

    print('1')
    # DTUtils.transfomer_data_format_from_t5_to_ner(test_df)
    pass
    # class Project(MyModel):
    #     def __init__(self):
    #         super(Project, self).__init__()
    #         self.start_time = '...'
    #         self.end_time = '...'
    #
    #         self.wandb_proj = 'test'
    #         self.use_model = 'classification'  # mt5 /classification
    #         self.model_type = 'bert'
    #         self.pretrained_model = ConfigFilePaths.bert_dir_remote
    #
    #     def run(self):
    #         self.train_test()
    #
    #     def train_test(self):
    #         self.model_version = 'vtest'
    #         self.pretrained_model = '/home/zyl/disk/PharmAI/pharm_ai/po/best_model/v4.2.0.4/'
    #         self.args = MyModel.set_model_parameter(model_version=self.model_version,
    #                                                 args=ClassificationArgs(),
    #                                                 save_dir='po')
    #         os.environ["CUDA_VISIBLE_DEVICES"] = "1,2,3"
    #         self.cuda_device = 0
    #         self.args.n_gpu = 3
    #
    #         self.args.num_train_epochs = 1
    #         self.args.learning_rate = 5e-5
    #         self.args.train_batch_size = 64  # 512
    #         self.args.eval_batch_size = 32  # 256
    #         self.args.max_seq_length = 512
    #         self.args.gradient_accumulation_steps = 8  # 256
    #
    #         train_df = pd.read_excel('./data/processed_0825.xlsx', 'train')
    #         eval_df = pd.read_excel('./data/processed_0825.xlsx', 'test')
    #         self.train(train_df=train_df, eval_df=eval_df)
    #
    #
    # pass
    # # d = range(0, 10)
    # # num = 5
    # # print(DTUtils.split_data_evenly(d, 5))
    # # print('1')
    # r = ['a',' ','','df','x',]
    # f = ['','df']
    # g = DTUtils.find_index(r, f)
    # print(g)
    # for i in g:
    #     print(r[i['start']:i['start']+i['offset']])
    # print(r[22:25])
