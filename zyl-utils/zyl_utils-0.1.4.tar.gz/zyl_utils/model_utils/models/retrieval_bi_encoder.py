# encoding: utf-8
"""
@author: zyl
@file: retrieval_bi_encoder.py
@time: 2021/12/16 9:45
@desc:
"""

import math
from dataclasses import dataclass
from typing import Dict

import pandas as pd
from sentence_transformers import datasets
from sentence_transformers import losses
from sentence_transformers import models
from simpletransformers.config.model_args import ModelArgs
from tqdm import tqdm

from zyl_utils import get_best_cuda_device

MODEL_TYPE = [
    'sts',  # 两个文本相似性，
    'nli',  # 句子关系，多对多，只有蕴含和矛盾
    'paraphrase',  # 释义，（从一组数据中找出其中相似含义的句子）
    'duplicate_text'  # 相同文本集，多对一
    'information retrieval'  # 信息检索
]

# from sklearn.metrics.pairwise import paired_cosine_distances, paired_euclidean_distances, paired_manhattan_distances
# from scipy.stats import pearsonr, spearmanr

# from sentence_transformers.readers import InputExample
from sentence_transformers import SentenceTransformer, util, InputExample

from sentence_transformers.evaluation import BinaryClassificationEvaluator


@dataclass
class ReTrievalBiEncoderArgs(ModelArgs):
    """
        Model args for a ReTrievalBiEncoderArgs
        num_labels:Number of labels of the classifier. If 1, the CrossEncoder is a regression model that outputs a
        continous score 0...1. If > 1, it output several scores that can be soft-maxed to get probability
        scores for the different classes.
    """
    cuda_device: str = get_best_cuda_device(gpu_num=1)
    train_batch_size: int = 16
    max_seq_length: int = 128

    use_sbert_model: bool = True
    tokenizer_args: Dict = dict
    default_activation_function = None
    num_labels: int = 1

    output_path: str = './'
    model_version: str = 'test'

    loss_func: str = 'MultipleNegativesRankingLossHard'
    evaluator_func: str = 'BinaryClassificationEvaluator'

    show_encode_progress_bar: bool = True

    learning_rate = 1e-4
    query_chunk_size: int = 100
    retrieval_top_k: int = 10  # corpus中最大搜索多少个实体
    retrieval_score: float = -1  # corpus大于多少得分的被搜索出来
    at_least_top_k: int = -1  # corpus最少搜索出多少个词条



# class RecallEvaluator(SentenceEvaluator):
#     """
#     Evaluate a model based on the similarity of the embeddings by calculating the Spearman and Pearson rank correlation
#     in comparison to the gold standard labels.
#     The metrics are the cosine similarity as well as euclidean and Manhattan distance
#     The returned score is the Spearman correlation with a specified metric.
#
#     The results are written in a CSV. If a CSV already exists, then values are appended.
#     """
#
#     def __init__(self, to_predict_texts: List[str], labels: List[str], corpus, batch_size: int = 16,
#                  main_similarity: SimilarityFunction = None, name: str = '', show_progress_bar: bool = False,
#                  write_csv: bool = True, top_k=100, encode_batch_size=128):
#         """
#         Constructs an evaluator based for the dataset
#
#         The labels need to indicate the similarity between the sentences.
#
#         :param to_predict_texts:  List with the first sentence in a pair
#         :param labels: List with the second sentence in a pair
#         :param scores: Similarity score between to_predict_texts[i] and labels[i]
#         :param write_csv: Write results to a CSV file
#         """
#         self.corpus = corpus
#         self.to_predict_texts = to_predict_texts
#         self.labels = labels
#         self.write_csv = write_csv
#         self.top_k = top_k
#         self.encode_batch_size = encode_batch_size
#         assert len(self.to_predict_texts) == len(self.labels)
#
#         self.main_similarity = main_similarity
#         self.name = name
#
#         self.batch_size = batch_size
#         if show_progress_bar is None:
#             show_progress_bar = (
#                     logger.getEffectiveLevel() == logging.INFO or logger.getEffectiveLevel() == logging.DEBUG)
#         self.show_progress_bar = show_progress_bar
#
#         self.csv_file = "similarity_evaluation" + ("_" + name if name else '') + "_results.csv"
#         self.csv_headers = ["epoch", "steps", "score"]
#
#     @classmethod
#     def from_input_examples(cls, examples: List[InputExample], **kwargs):
#         to_predict_texts = []
#         labels = []
#
#         for example in examples:
#             to_predict_texts.append(example.texts[0])
#             labels.append(example.texts[1])
#         return cls(to_predict_texts, labels, **kwargs)
#
#     @staticmethod
#     def caculate_recall(y_true, y_pred):
#         recall = 0
#         for t, p in zip(y_true, y_pred):
#             if len(t) == 0:
#                 recall += 1
#             else:
#                 recall += (len(set(t) & set(p)) / len(t))
#         return recall / len(y_true)
#
#     def __call__(self, model, output_path: str = None, epoch: int = -1, steps: int = -1):
#         res = RetrievalEvaluator.query_result(model, queries=self.to_predict_texts, corpus=self.corpus,
#                                               corpus_embeddings=None, top_k=self.top_k, return_format='result')
#         y_true = [set(i) for i in self.labels]
#
#         res_1 = [r[0:1] for r in res]
#
#         res_10 = [r[0:10] for r in res]
#         res_50 = [r[0:50] for r in res]
#         res_100 = [r[0:100] for r in res]
#
#         recall_1 = RecallEvaluator.caculate_recall(y_true, res_1)
#         recall_10 = RecallEvaluator.caculate_recall(y_true, res_10)
#         recall_50 = RecallEvaluator.caculate_recall(y_true, res_50)
#         recall_100 = RecallEvaluator.caculate_recall(y_true, res_100)
#         print(f'\nrecall@1      {recall_1}\n'
#               f'recall@10     {recall_10}\n'
#               f'recall@50     {recall_50}\n'
#               f'recall@100    {recall_100}\n')
#         return recall_10
import random


class ReTrievalBiEncoderModel:
    def __init__(self,model_name="sentence-transformers/distiluse-base-multilingual-cased-v1",args=None):
        """

        Args:
            model_type: 'two_classification',  # 输出0或1. 'sts',  # 语义相似性，输出0-1连续值，无序
                        'nli'  # 自然语言推理，输出前后两句话的关系，有序，输出：0，1，2
            model_name: "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
            args: dict
        """
        self.score_function = util.dot_score
        self.args = self._load_model_args(model_name)
        self.args.model_name = model_name
        self.corpus_embeddings = None
        self.mention_corpus = self.get_mention_corpus()
        self.entries_corpus = self.get_entries_corpus()
        self.corpus_dict = self.get_corpus_dict()

        if isinstance(args, dict):
            self.args.update_from_dict(args)
        elif isinstance(args, ReTrievalBiEncoderArgs):
            self.args = args

        self.model = None

    def _load_model_args(self, input_dir):
        args = ReTrievalBiEncoderArgs()
        args.load(input_dir)
        return args

    def train(self, train_dt, eval_dt):
        """
        Args:
            train_dt: df,['mention','entries'],'mention' is string text,'entries' is a list of entries.
            eval_dt:

        Returns:

        """
        self.model = self.get_model()
        self.args.best_model_dir = self.args.output_dir + 'best_model/' + self.args.model_version + '/'
        train_objectives = self.get_train_objects(train_dt)  # type:list

        evaluator = self.get_evaluator(eval_dt)

        warmup_steps = math.ceil(
            len(train_objectives[0]) * self.args.num_train_epochs * 0.1)  # 10% of train data for warm-up
        evaluation_steps = math.ceil(len(train_objectives[0]) * 0.1)

        self.model.fit(train_objectives=train_objectives, evaluator=evaluator, epochs=self.args.num_train_epochs,
                       warmup_steps=warmup_steps, evaluation_steps=evaluation_steps, save_best_model=True,
                       output_path=self.args.best_model_dir, use_amp=False, callback=self.call_back,
                       show_progress_bar=True, optimizer_params={'lr': self.args.learning_rate})

    def get_model(self):
        if self.args.use_sbert_model:
            # 预测和训练sentence-transformers_model时用到
            model = SentenceTransformer(self.args.model_name, device=f'cuda:{str(self.args.cuda_device)}')
        else:
            # 训练时，修改模型结构，比如输出，用到，得到的是一个sentencetransformer_model模型
            # max_seq_length,model_args,cache_dir,tokenizer_args, do_lower_case,tokenizer_name_or_path
            word_embedding_model = models.Transformer(self.args.model_name, max_seq_length=self.args.max_seq_length, )
            pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
                                           pooling_mode='mean')
            model = SentenceTransformer(modules=[word_embedding_model, pooling_model],
                                        device=f'cuda:{str(self.args.cuda_device)}')
            # dense_layer = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(),
            #                            out_features=self.output_dimension, activation_function=nn.Tanh())
            # normalize_layer = models.Normalize()
            # model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_layer, normalize_layer],
            #                             device=f'cuda:{str(self.cuda_device)}')

            # from sentence_transformers.models.T5 import T5
            # word_embedding_model = T5(self.model_path,max_seq_length=self.max_seqence_length)
            # dense_model = models.Dense(in_features=word_embedding_model.get_word_embedding_dimension(),
            #                            out_features=word_embedding_model.get_word_embedding_dimension(),
            #                            activation_function=nn.Tanh())
        return model

    def get_train_objects(self, df):
        """

        Args:
            df: 输入： ['mention','entries'],'mention' is string text,'entries' is a list of entries.
        Returns:

        """
        if self.args.loss_func == 'MultipleNegativesRankingLossHard':
            df = df[df['entries'].apply(len).gt(0)] # 去除空列表
            train_samples = []
            for _, sub_df in tqdm(df.iterrows()):
                contradiction_entries = self.get_candidate_entries(sub_df['mention'])
                contradiction_entries = [c for c in contradiction_entries if c not in sub_df['entries']]

                for e in sub_df['entries']:
                    train_samples.append(
                        InputExample(texts=[sub_df['mention'], e, random.choice(contradiction_entries)]))
                    train_samples.append(
                        InputExample(texts=[e, sub_df['mention'], random.choice(contradiction_entries)]))

            train_dataloader = datasets.NoDuplicatesDataLoader(train_samples, batch_size=self.args.train_batch_size)
            train_loss = losses.MultipleNegativesRankingLoss(model=self.model, scale=20.0,
                                                             similarity_fct=util.dot_score)
            train_obj = [(train_dataloader, train_loss)]
        elif self.args.loss_func == 'MultipleNegativesRankingLoss':
            df = df[df['entry'] != []]
            df = df.explode('entry')
            train_samples = []
            for _, sub_df in tqdm(df.iterrows()):
                train_samples.append(InputExample(texts=[sub_df['entry'], sub_df['entity']]))

            print(len(train_samples))
            # Special data loader that avoid duplicates within a batch
            train_dataloader = datasets.NoDuplicatesDataLoader(train_samples, batch_size=self.args.train_batch_size)
            train_loss = losses.MultipleNegativesRankingLoss(model=self.model, scale=20.0,
                                                             similarity_fct=util.dot_score)
            train_obj = [(train_dataloader, train_loss)]
        else:
            df = df[df['entry'] != []]
            df = df.explode('entry')
            train_samples = []
            for _, sub_df in tqdm(df.iterrows()):
                train_samples.append(InputExample(texts=[sub_df['entry'], sub_df['entity']]))

            print(len(train_samples))
            # Special data loader that avoid duplicates within a batch
            train_dataloader = datasets.NoDuplicatesDataLoader(train_samples, batch_size=self.args.train_batch_size)
            train_loss = losses.MultipleNegativesRankingLoss(model=self.model, scale=20.0,
                                                             similarity_fct=util.dot_score)
            train_obj = [(train_dataloader, train_loss)]
        return train_obj

    def get_mention_corpus(self):
        # 评估时的实体语料库（非词条）,所有提及，
        mention_corpus = []
        return mention_corpus

    def get_entries_corpus(self):
        # 所有词条的语料库
        entries_corpus = []
        return entries_corpus

    def get_corpus_dict(self):
        # 评估时每个语料库中的实体 映射为词条的字典
        # 评估时使用训练集的字典，接口使用所有数据的字典
        corpus_dict = {'entity': 'entry'}
        return corpus_dict

    def get_candidate_entries(self, text):
        # 对于一个文本，从所有字典词条中获取最相似的若干个词条
        candidate_entries = []
        return candidate_entries

    def call_back(self, score, epoch, steps):
        print(f'epoch:{epoch}: score:{score}, steps:{steps} ')

    def query(self, queries, return_format='result'):
        if not self.model:
            self.model = self.get_model()
        # 从预料库中搜索最相似的
        if not self.mention_corpus:
            self.mention_corpus = self.get_mention_corpus()

        if not self.corpus_embeddings:
            self.corpus_embeddings = self.model.encode(self.mention_corpus, self.args.eval_batch_size,
                                                       self.args.show_encode_progress_bar,
                                                       'sentence_embedding',
                                                       True, True, f'cuda:{self.args.cuda_device}', False)
            self.corpus_embeddings = util.normalize_embeddings(self.corpus_embeddings)

        queries_embeddings = self.model.encode(queries, self.args.eval_batch_size,
                                               self.args.show_encode_progress_bar,
                                               'sentence_embedding',
                                               True, True, f'cuda:{self.args.cuda_device}', False)
        queries_embeddings = util.normalize_embeddings(queries_embeddings)

        hits = util.semantic_search(queries_embeddings, self.corpus_embeddings,
                                    top_k=self.args.retrieval_top_k,
                                    corpus_chunk_size=len(self.mention_corpus),
                                    query_chunk_size=self.args.query_chunk_size,
                                    score_function=self.score_function)  # 排过序，得分从大到小

        if return_format == 'result':
            res = []
            for h in hits:
                r = []
                for i in h:
                    if i['score'] > self.args.retrieval_score:
                        r.append(self.mention_corpus[i['corpus_id']])
                if len(r) < self.args.at_least_top_k:
                    for i in range(len(r), self.args.at_least_top_k):
                        r.append(self.mention_corpus[i['corpus_id']])
                res.append(r)
            return res
        else:
            return hits

    @staticmethod
    def caculate_recall(y_true, y_pred):
        recall = 0
        for t, p in zip(y_true, y_pred):
            if len(t) == 0:
                recall += 1
            else:
                recall += (len(set(t) & set(p)) / len(t))
        return recall / len(y_true)

    def eval(self, to_predicts, labels, batch_size=16, retrieval_top_k=100, at_least_top_k=10,
             retrieval_score=0.1):
        pred = self.query(to_predicts, batch_size=batch_size, show_progress_bar=True,
                          retrieval_top_k=retrieval_top_k,
                          at_least_top_k=at_least_top_k, retrieval_score=retrieval_score,
                          return_format='result')
        res_1 = [r[0:1] for r in pred]

        res_10 = [r[0:10] for r in pred]
        res_50 = [r[0:50] for r in pred]
        res_100 = [r[0:100] for r in pred]

        recall_1 = ReTrievalBiEncoderModel.caculate_recall(labels, res_1)
        recall_10 = ReTrievalBiEncoderModel.caculate_recall(labels, res_10)
        recall_50 = ReTrievalBiEncoderModel.caculate_recall(labels, res_50)
        recall_100 = ReTrievalBiEncoderModel.caculate_recall(labels, res_100)
        print(f'\nrecall@1      {recall_1}\n'
              f'recall@10     {recall_10}\n'
              f'recall@50     {recall_50}\n'
              f'recall@100    {recall_100}\n')
        return recall_10

    def get_evaluator(self, dev_df):
        if self.args.evaluator_func == 'BinaryClassificationEvaluator':
            eval_samples = []
            for _, sub_df in tqdm(dev_df.iterrows()):
                for e in sub_df['entries']:
                    eval_samples.append(InputExample(texts=[sub_df['mention'], e], label=1))
                    contradiction_entries = self.get_candidate_entries(sub_df['mention'])
                    contradiction_entries = [c for c in contradiction_entries if c not in sub_df['entries']]
                    for e in contradiction_entries:
                        eval_samples.append(InputExample(texts=[sub_df['mention'], e], label=0))
            evaluator = BinaryClassificationEvaluator.from_input_examples(examples=eval_samples,
                                                                          name='eval',
                                                                          batch_size=self.args.eval_batch_size,
                                                                          show_progress_bar=True)

        else:
            eval_samples = []
            for _, sub_df in tqdm(dev_df.iterrows()):
                for e in sub_df['entries']:
                    eval_samples.append(InputExample(texts=[sub_df['mention'], e], label=1))
                    contradiction_entries = self.get_candidate_entries(sub_df['mention'])
                    contradiction_entries = [c for c in contradiction_entries if c not in sub_df['entries']]
                    for e in contradiction_entries:
                        eval_samples.append(InputExample(texts=[sub_df['mention'], e], label=0))

            evaluator = BinaryClassificationEvaluator.from_input_examples(examples=eval_samples,
                                                                          name='eval',
                                                                          batch_size=self.args.eval_batch_size,
                                                                          show_progress_bar=True,
                                                                          )
        return evaluator


if __name__ == '__main__':


    class Test(ReTrievalBiEncoderModel):
        def __init__(self):
            super(Test, self).__init__()

        def get_mention_corpus(self):
            # disease_dict = pd.read_excel("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_v2_1221.xlsx")
            disease_dict = pd.read_hdf(
                "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
                'train')
            corpus = disease_dict['entity'].tolist()
            return [str(c) for c in set(corpus)]

        def get_entries_corpus(self):
            disease_dict = pd.read_hdf(
                "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
                'train')
            corpus = disease_dict['entity'].tolist()
            return [str(c) for c in set(corpus)]
            pass

        def get_corpus_dict(self):
            disease_dict = pd.read_hdf(
                "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
                'train')
            disease_dict = dict(zip(disease_dict['entity'].tolist(), disease_dict['entry'].tolist()))
            return disease_dict

        def get_candidate_entries(self, one_text):
            # 对于一个文本，从所有字典词条中获取最相似的若干个词条

            candidate_entries = self.query(one_text, return_format='result')[0]
            return candidate_entries

        def test_train(self):
            self.args.update_from_dict(
                {
                    'model_name':"sentence-transformers/distiluse-base-multilingual-cased-v1",
                    'cuda_device': '1',
                    'train_batch_size': 16,
                    'max_seq_length': 128,

                    'loss_func': 'MultipleNegativesRankingLossHard',
                    'evaluator_func': 'BinaryClassificationEvaluator',
                    'learning_rate': 1e-4,

                    'output_path':'/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/',
                    'model_version': 'test',
                }
            )
            train_dt = pd.read_hdf('/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5',
                                   'train')
            train_dt.rename(columns={'entity':'mention','entry':'entries'},inplace=True)
            eval_dt = pd.read_hdf('/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5',
                                  'eval')
            eval_dt.rename(columns={'entity': 'mention', 'entry': 'entries'}, inplace=True)
            self.train(train_dt, eval_dt)

        def test_predict(self, to_predict):
            self.args.model_name = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/di_retrieval_v2.1/"
            self.args.update_from_dict(
                {}
            )
            self.model = self.get_model()
            res = self.query(to_predict, return_format='result')
            print(res)

        def test_eval(self):
            self.args.model_name = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/di_retrieval_v2.1/"
            self.model = self.get_model()

            dev_df = pd.read_hdf(
                "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
                'eval')
            to_predict = dev_df['entity'].tolist()
            labels = dev_df['entry'].tolist()
            self.eval(to_predict, labels, batch_size=16, retrieval_top_k=100, at_least_top_k=10,
                      retrieval_score=-1)


    # Test().test_predict(['肿瘤', 'cancer'])
    Test().test_train()


    # def get_samples(self, df):
    #     samples = []
    #     if self.args.loss=='MultipleNegativesRankingLoss':
    #
    #         # entry , entity ,other_entry
    #
    #
    #     elif self.args.loss=='MultipleNegativesRankingLossHard':
    #
    #     elif self.args.loss=='OnlineContrastiveLoss':
    #
    #     elif self.args.loss ==

    #
    #     if self.args.model_type == 'nli':
    #         for _, sub_df in df.iterrows():
    #             candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #             if sub_df['entries']:
    #                 entries_length = len(sub_df['entries'])
    #                 if entries_length > 1:
    #                     label_id = 1  # 蕴含关系
    #                 else:
    #                     label_id = 2  # 等价关系
    #                 for e in sub_df['entries']:
    #                     samples.append(InputExample(texts=[sub_df['mention'], e], label=label_id))
    #                     if e in candidate_entries:
    #                         candidate_entries.remove(e)
    #             for c_e in candidate_entries:
    #                 samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #     elif self.args.model_type == 'sts':
    #         for _, sub_df in df.iterrows():
    #             candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #             if sub_df['entries']:
    #                 entries_length = len(sub_df['entries'])
    #                 if 'label' in sub_df.index:
    #                     score = sub_df['label']
    #                 else:
    #                     score = round(1 / entries_length, 4)
    #                 for e in sub_df['entries']:
    #                     samples.append(InputExample(texts=[sub_df['mention'], e], label=score))
    #                     samples.append(InputExample(texts=[e, sub_df['mention']], label=score))
    #                     if e in candidate_entries:
    #                         candidate_entries.remove(e)
    #             for c_e in candidate_entries:
    #                 samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #                 samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
    #     else:
    #         for _, sub_df in df.iterrows():
    #             candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #             if sub_df['entries']:
    #                 for e in sub_df['entries']:
    #                     samples.append(InputExample(texts=[sub_df['mention'], e], label=1))
    #                     samples.append(InputExample(texts=[e, sub_df['mention']], label=1))
    #             for c_e in candidate_entries:
    #                 samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #                 samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
    #     return samples
    #
    # def get_candidade_entries(self, query):
    #     candidate_entries = query
    #     return candidate_entries  # type:list
    #
    # def get_evaluator(self, eval_samples):
    #     if self.args.model_type == 'nli':
    #         return CECorrelationEvaluator.from_input_examples(eval_samples, name='eval')
    #     elif self.args.model_type == 'two_classification':
    #         return CEBinaryClassificationEvaluator.from_input_examples(eval_samples, name='eval')
    #     else:
    #         return CESoftmaxAccuracyEvaluator.from_input_examples(eval_samples, name='eval')
    #
    #     # class RerankerTrainer:
    #     #     def __init__(self):
    #     #         self.model_path = "distiluse-base-multilingual-cased-v1"
    #     #         self.dimensions = 512
    #     #         self.cuda_device = get_best_cuda_device(gpu_num=1)
    #     #         self.max_seqence_length = 128
    #     #         self.use_st_model = True
    #     #         self.train_batch_size = 16
    #     #         self.epoch = 5
    #     #         self.learning_rate = 1e-5
    #     #         self.all_scores = []
    #     #         self.best_score = 0
    #     #         self.label2int = {"contradiction": 0, "entailment": 1, "neutral": 1}
    #     #         self.train_num_labels = len(set(self.label2int.values()))
    #     #         pass
    #     #
    #     #     def train(self, train_df, dev_df, save_model="./best_model/test/", loss_func='SoftmaxLoss',
    #     #               evaluator_func='MyEvaluator2', top_k=30):
    #     #
    #     #         self.save_model = save_model
    #     #         model = self.get_model()
    #     #
    #     #         train_dataloader, train_loss = self.get_train_objectives(train_df, model, loss_func=loss_func,
    #     #                                                                  top_k=top_k)
    #     #
    #     #         evaluator = self.get_evaluator(dev_df, evaluator_func=evaluator_func)
    #     #
    #     #         warmup_steps = math.ceil(len(train_dataloader) * self.epoch * 0.1)  # 10% of train data for warm-up
    #     #         evaluation_steps = math.ceil(len(train_dataloader) * 0.1)
    #     #
    #     #         print('start train...')
    #     #         # Which loss function to use for training. If None, will use nn.BCEWithLogitsLoss() if self.config.num_labels == 1 else nn.CrossEntropyLoss()
    #     #         model.fit(train_dataloader=train_dataloader, epochs=self.epoch, warmup_steps=warmup_steps,
    #     #                   evaluator=evaluator, save_best_model=True,
    #     #                   output_path=save_model,
    #     #                   evaluation_steps=evaluation_steps,
    #     #                   callback=self.call_back,
    #     #                   loss_fct=train_loss,
    #     #                   optimizer_params={'lr': self.learning_rate})
    #     #
    #     #         df = pd.DataFrame(self.all_scores)
    #     #         df.to_excel(save_model + 'my_score.xlsx')
    #     #         RerankerTrainer.save_parameters(self, save_model=f'{save_model}parameters.json')
    #     #
    #     #     def get_retrieval_model(self):
    #     #         from sentence_transformers import SentenceTransformer
    #     #         model = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/v2/"
    #     #         model = SentenceTransformer(self.model_path, device=f'cuda:{self.cuda_device}')
    #     #         return model
    #     #
    #     #     def get_evaluator(self, dev_df, evaluator_func='MyEvaluator2', collection='t1'):
    #     #         from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
    #     #         from sklearn.utils import resample
    #     #
    #     #         self.evaluator_func = evaluator_func
    #     #         dev_df = resample(dev_df, replace=False)
    #     #
    #     #         if evaluator_func == 'MyEvaluator':
    #     #             from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator
    #     #             from sentence_transformers import InputExample
    #     #             dev_df = dev_df[dev_df['label'] != 0.0]  # type:pd.DataFrame
    #     #             dev_df = dev_df.groupby('entity').apply(lambda x: x['entry'].tolist())
    #     #             scores = dev_df.index.tolist()
    #     #             eval_examples = []
    #     #             dev_samples = []
    #     #             for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
    #     #                 eval_examples.append(InputExample(texts=[t, r]))
    #     #             evaluator = MyEvaluator.from_input_examples(eval_examples, name='sts-eval', collection=collection)
    #     #
    #     #         elif evaluator_func == 'EmbeddingSimilarityEvaluator':
    #     #             sentences_1 = []
    #     #             sentences_2 = []
    #     #             scores = []
    #     #             dev_samples = []
    #     #             for _, sub_df in dev_df.iterrows():
    #     #                 if sub_df['label'] != 0.0:
    #     #                     sentences_1.append(sub_df['entity'])
    #     #                     sentences_2.append(sub_df['entry'])
    #     #                     scores.append(sub_df['label'])
    #     #
    #     #             evaluator = EmbeddingSimilarityEvaluator(sentences_1, sentences_2, scores)
    #     #         else:
    #     #             from sentence_transformers import InputExample
    #     #             from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator2
    #     #             dev_samples = []
    #     #             for _, sub_df in dev_df.iterrows():
    #     #                 if sub_df['label'] == 1:
    #     #                     dev_samples.append(
    #     #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=1))
    #     #                 elif sub_df['label'] > 0:
    #     #                     dev_samples.append(
    #     #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=1))
    #     #                 else:
    #     #                     dev_samples.append(
    #     #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=0))
    #     #             evaluator = MyEvaluator2.from_input_examples(dev_samples, name='AllNLI-dev')
    #     #
    #     #         print(f'dev_length:{len(dev_samples)}')
    #     #         self.dev_length = len(dev_samples)
    #     #         return evaluator
    #     #
    #     #     @staticmethod
    #     #     def save_parameters(para_obj, save_model='./test.json'):
    #     #         """
    #     #         存储一个对象的参数，对象参数可以是模型参数或超参数
    #     #         Args:
    #     #             para_obj: 要存储的参数的对象
    #     #             save_model: 保存路径
    #     #
    #     #         Returns:
    #     #
    #     #         """
    #     #         para_list = para_obj.__dir__()
    #     #         # save_para_list = ['best_score','device','max_seq_length','tokenizer']
    #     #         para = {}
    #     #         for p in para_list:
    #     #             if not p.startswith('_'):
    #     #                 # if p in save_para_list:
    #     #                 r = getattr(para_obj, p)
    #     #                 if isinstance(r, int) or isinstance(r, str) or isinstance(r, float) or isinstance(r, list) \
    #     #                         or isinstance(r, bool):
    #     #                     para[p] = r
    #     #
    #     #         with open(save_model, "w", encoding='utf-8') as f:
    #     #             # indent 超级好用，格式化保存字典，默认为None，小于0为零个空格
    #     #             # f.write(json.dumps(para,indent=4))
    #     #             json.dump(para, f, indent=4)  # 传入文件描述符，和dumps一样的结果
    #     #
    #     #         para.pop("all_scores")
    #     #         with open(log_file, "a", encoding='utf-8') as f:
    #     #             json.dump(para, f, indent=4)
    #     #             f.write('\n')
    #     #
    #     #     def call_back(self, score, epoch, steps):
    #     #         self.all_scores.append({str(epoch) + '-' + str(steps): score})
    #     #         if score > self.best_score:
    #     #             self.best_score = score
    #     #         print(f'epoch:{epoch}: score:{score} ')
    #     #
    #     # class TrainerV1(RerankerTrainer):
    #     #     def __init__(self):
    #     #         super(TrainerV1, self).__init__()
    #     #
    #     #     def run(self):
    #     #         self.train_1011()
    #     #
    #     #     def train_1011(self):
    #     #         def deal_with_df(df, corpus):
    #     #             df['entry'] = df['entry'].astype('str')
    #     #             df['entity'] = df['entity'].astype('str')
    #     #             m = self.get_retrieval_model()
    #     #             qs = df['entity'].tolist()
    #     #             res = RetrievalEvaluator.query_result(model=m, corpus=corpus, queries=qs, top_k=10)
    #     #             li = []
    #     #             for i, r in zip(qs, res):
    #     #                 for _ in r:
    #     #                     li.append({'entity': i, 'entry': _, 'label': 0})
    #     #             df_ = pd.DataFrame(li)
    #     #             print(len(df))
    #     #             df = pd.concat([df, df_], ignore_index=True)
    #     #             print(len(df))
    #     #             df.drop_duplicates(subset=['entity', 'entry'], keep='first', inplace=True)
    #     #             print(len(df))
    #     #             return df
    #     #
    #     #         self.train_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5"
    #     #         train_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
    #     #                                'train')
    #     #         corpus = list(set(train_df['entry'].tolist()))
    #     #         corpus = [str(c) for c in corpus]
    #     #         train_df = deal_with_df(train_df, corpus=corpus)
    #     #
    #     #         self.dev_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5"
    #     #         dev_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
    #     #                              'eval')
    #     #         dev_df = deal_with_df(dev_df, corpus=corpus)
    #     #
    #     #         self.model_path = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    #     #         # self.model_path = "./best_model/di_reranker_v2.0/"
    #     #
    #     #         # self.model_path = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/em9/"
    #     #         # self.model_path = '/large_files/pretrained_pytorch/mt5_zh_en/'
    #     #
    #     #         # self.model_path = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    #     #         # self.model_path = "./best_model/v2/v2.2.1/"
    #     #
    #     #         # self.model_path = "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
    #     #
    #     #         self.cuda_device = get_best_cuda_device(gpu_num=1)
    #     #         self.dimensions = 768
    #     #         self.max_seqence_length = 64
    #     #         self.use_st_model = True
    #     #         self.train_batch_size = 32
    #     #         self.epoch = 3
    #     #         self.learning_rate = 1e-5
    #     #         self.train(train_df, dev_df, save_model="./best_model/di_reranker_2/",
    #     #                    loss_func='CrossEntropyLoss',  # CrossEntropyLoss，BCEWithLogitsLoss，nli
    #     #                    evaluator_func="MyEvaluator2",
    #     #                    top_k=10)
    #     #
    #     #     # def train_cross_model(self):
    #     #     #     self.train_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
    #     #     #     train_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
    #     #     #                            'train')
    #     #     #     m = self.get_retrieval_model()
    #     #     #     RetrievalEvaluator.query_result(model=model, corpus=corpus, queries=queries, top_k=1)
    #     #     #
    #     #     #     self.dev_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
    #     #     #     dev_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
    #     #     #                          'eval')
    #     #     #
    #     #     #     # self.train_file = "./data/v2/train_2.csv.gz"
    #     #     #     # train_df = pd.read_csv(self.train_file, compression='gzip', sep='|')
    #     #     #     # self.dev_file = "./data/v2/eval.csv.gz"
    #     #     #     # dev_df = pd.read_csv(self.dev_file, compression='gzip', sep='|')
    #     #     #
    #     #     #
    #     #     #     # self.model_path = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    #     #     #     self.model_path = "./best_model/di_reranker_v2.0/"
    #     #     #
    #     #     #     # self.model_path = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/em9/"
    #     #     #     # self.model_path = '/large_files/pretrained_pytorch/mt5_zh_en/'
    #     #     #
    #     #     #     # self.model_path = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    #     #     #     # self.model_path = "./best_model/v2/v2.2.1/"
    #     #     #
    #     #     #     # self.model_path = "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
    #     #     #
    #     #     #
    #     #     #
    #     #     #     self.dimensions = 768
    #     #     #     self.max_seqence_length = 128
    #     #     #     self.use_st_model = True
    #     #     #     self.train_batch_size = 32
    #     #     #     self.epoch = 3
    #     #     #     self.learning_rate = 2e-5
    #     #     #     self.train(train_df, dev_df, save_model="./best_model/v2/v2.2.2/",
    #     #     #                loss_func='CrossEntropyLoss',  # CrossEntropyLoss，BCEWithLogitsLoss，nli
    #     #     #                evaluator_func="MyEvaluator2",
    #     #     #                top_k=10)
    #
    # def call_back(self, score, epoch, steps):
    #     print(f'epoch:{epoch}----step:{steps}----score:{score} ')

    # class RetrievalDT:
    #     def __init__(self):
    #         pass
    #
    #     @staticmethod
    #     def convert_dt_for_MultipleNegativesRankingLoss(train_data: pd.DataFrame, neg_data=2, corpus=None,
    #                                                     mode='sentence_pair'):
    #         train_data = v
    #         train_data.dropna(inplace=True)
    #         if mode == 'sentence_pair':
    #             return train_data
    #         else:
    #             new_train_data = []
    #             for _, sub_df in tqdm(train_data.iterrows()):
    #                 count = 1
    #                 while count <= neg_data / 2:
    #                     neg_entity = random.choice(corpus)
    #                     if train_data[
    #                         (train_data['entry'] == neg_entity) & (train_data['entity'] == sub_df['entity'])].empty:
    #                         new_train_data.append({
    #                             'entry': sub_df['entry'],
    #                             'pos_entity': sub_df['entity'],
    #                             'neg_entity': neg_entity,
    #                         })
    #                         new_train_data.append({
    #                             'entry': sub_df['entity'],
    #                             'pos_entity': sub_df['entry'],
    #                             'neg_entity': neg_entity,
    #                         })
    #                         count += 1
    #             return pd.DataFrame(new_train_data)

    # class RetrievalBiEncoder:
    #     def __init__(self):
    #         self.pretrained_model = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    #         self.output_dimension = 768  # 输出向量维度
    #         self.cuda_device = get_best_cuda_device(gpu_num=1)
    #         self.max_seqence_length = 128  # 输入长度
    #         self.use_sbert_model = True  # 是否改变模型结构
    #         self.train_batch_size = 16
    #         self.epoch = 5
    #         self.data_top_k = 3  # 负样本数
    #         self.learning_rate = 1e-5
    #
    #         self.save_model = "./best_model/"  # 模型保存路径
    #         self.model_version = 'test'  # 版本号，最好模型路径
    #
    #         self.logging_scores = []
    #         self.logging_best_score = 0
    #         self.log_file = './best_model/retrieval_logging.json'
    #
    #     def train_model(self, train_df, dev_df, loss_func='CosineSimilarityLoss',
    #                     evaluator_func='EmbeddingSimilarityEvaluator',
    #                     eval_batch_size=128):
    #
    #         model = self.get_model()
    #         train_samples = self.get_samples(train_dt)
    #
    #         corpus = self.get_corpus()
    #         corpus = [str(c) for c in corpus]
    #         train_obj = self.get_train_objectives(train_df, model, loss_func=loss_func, corpus=corpus)
    #
    #         self.train_size = 9999999999
    #         for t in train_obj:
    #             self.train_size = min(len(t[0]), self.train_size)
    #
    #         print(f'train_size:{self.train_size}')
    #         evaluator = self.get_evaluator(dev_df, evaluator_func=evaluator_func, corpus=corpus,
    #                                        encode_batch_size=encode_batch_size)
    #
    #         warmup_steps = math.ceil(self.train_size * 1 * 0.1)  # 10% of train data for warm-up
    #         evaluation_steps = math.ceil(self.train_size * 0.1)
    #
    #         print('start train...')
    #         print(f"save to :{self.save_model + self.model_version + '/'}")
    #         model.fit(train_objectives=train_obj, epochs=self.epoch, warmup_steps=warmup_steps,
    #                   evaluator=evaluator,
    #                   save_best_model=True,
    #                   output_path=self.save_model + self.model_version + '/',
    #                   evaluation_steps=evaluation_steps,
    #                   callback=self.call_back,
    #                   optimizer_params={'lr': self.learning_rate})
    #
    #         df = pd.DataFrame(self.all_scores)
    #         df.to_excel(self.save_model + self.model_version + '/my_score.xlsx')
    #         TrainRetrieval.save_parameters(self,
    #                                          save_model=f"{self.save_model + self.model_version + '/'}parameters.json")
    #
    #     def get_model(self):
    #         print(f'use_pretrained_model: {self.pretrained_model}')
    #         if self.use_sbert_model:
    #             model = SentenceTransformer(self.pretrained_model, device=f'cuda:{str(self.cuda_device)}')
    #         else:
    #             word_embedding_model = models.Transformer(self.pretrained_model, max_seq_length=self.max_seqence_length)
    #             # from sentence_transformers.models.T5 import T5
    #             # word_embedding_model = T5(self.model_path,max_seq_length=self.max_seqence_length)
    #             # dense_model = models.Dense(in_features=word_embedding_model.get_word_embedding_dimension(),
    #             #                            out_features=word_embedding_model.get_word_embedding_dimension(),
    #             #                            activation_function=nn.Tanh())
    #             pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),
    #                                            pooling_mode_cls_token=False, pooling_mode_max_tokens=False,
    #                                            pooling_mode_mean_tokens=True, pooling_mode_mean_sqrt_len_tokens=False, )
    #             dense_layer = models.Dense(in_features=pooling_model.get_sentence_embedding_dimension(),
    #                                        out_features=self.output_dimension, activation_function=nn.Tanh())
    #             normalize_layer = models.Normalize()
    #             model = SentenceTransformer(modules=[word_embedding_model, pooling_model, dense_layer, normalize_layer],
    #                                         device=f'cuda:{str(self.cuda_device)}')
    #         self.output_dimension = model.get_sentence_embedding_dimension()
    #         return model
    #
    #     def get_samples(self, df):
    #         samples = []
    #         if self.args.model_type == 'nli':
    #             for _, sub_df in df.iterrows():
    #                 candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #                 if sub_df['entries']:
    #                     entries_length = len(sub_df['entries'])
    #                     if entries_length > 1:
    #                         label_id = 1  # 蕴含关系
    #                     else:
    #                         label_id = 2  # 等价关系
    #                     for e in sub_df['entries']:
    #                         samples.append(InputExample(texts=[sub_df['mention'], e], label=label_id))
    #                         if e in candidate_entries:
    #                             candidate_entries.remove(e)
    #                 for c_e in candidate_entries:
    #                     samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #         elif self.args.model_type == 'sts':
    #             for _, sub_df in df.iterrows():
    #                 candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #                 if sub_df['entries']:
    #                     entries_length = len(sub_df['entries'])
    #                     if 'label' in sub_df.index:
    #                         score = sub_df['label']
    #                     else:
    #                         score = round(1 / entries_length, 4)
    #                     for e in sub_df['entries']:
    #                         samples.append(InputExample(texts=[sub_df['mention'], e], label=score))
    #                         samples.append(InputExample(texts=[e, sub_df['mention']], label=score))
    #                         if e in candidate_entries:
    #                             candidate_entries.remove(e)
    #                 for c_e in candidate_entries:
    #                     samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #                     samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
    #         else:
    #             for _, sub_df in df.iterrows():
    #                 candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
    #                 if sub_df['entries']:
    #                     for e in sub_df['entries']:
    #                         samples.append(InputExample(texts=[sub_df['mention'], e], label=1))
    #                         samples.append(InputExample(texts=[e, sub_df['mention']], label=1))
    #                 for c_e in candidate_entries:
    #                     samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
    #                     samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
    #         return samples
    #
    #
    #     def get_train_objectives(self, train_data, model, loss_func='MultipleNegativesRankingLoss', corpus=None):
    #         """
    #
    #         Args:
    #             train_data: ['entity','entry'],entity:要查询的文本，entry：匹配到的词条列表，可以多条
    #             model:
    #             loss_func:
    #             corpus: 输入的语料库用以构建负样本
    #
    #         Returns:
    #             train_obj = [(train_dataloader, train_loss)]
    #         """
    #         train_samples = []
    #         self.loss_func = loss_func
    #         if loss_func == 'MultipleNegativesRankingLoss':
    #             train_data = RetrievalDT.convert_dt_for_MultipleNegativesRankingLoss(train_data, neg_data=2, corpus=corpus)
    #             # Special data loader that avoid duplicates within a batch
    #
    #             train_dataloader = datasets.NoDuplicatesDataLoader(train_samples, batch_size=self.train_batch_size)
    #             train_loss = losses.MultipleNegativesRankingLoss(model=model)
    #             train_obj = [(train_dataloader, train_loss)]
    #             return train_obj
    #         elif loss_func == 'MultipleNegativesRankingLoss2':
    #             for _, sub_df in tqdm(train_data.iterrows()):
    #                 if sub_df['label'] != 0:
    #                     train_samples.append(InputExample(texts=[sub_df['entity'], sub_df['entry']]))
    #
    #             print(len(train_samples))
    #             # Special data loader that avoid duplicates within a batch
    #             train_dataloader = datasets.NoDuplicatesDataLoader(train_samples, batch_size=self.train_batch_size)
    #             train_loss = losses.MultipleNegativesRankingLoss(model=model)
    #             train_obj = [(train_dataloader, train_loss)]
    #             return train_obj
    #         elif loss_func == 'OnlineContrastiveLoss':
    #             train_data = train_data[train_data['label'] != 0.0]  # type:pd.DataFrame
    #
    #             dev_df = train_data.groupby('entity').apply(lambda x: x['entry'].tolist())
    #
    #             scores = dev_df.index.tolist()
    #             eval_examples = []
    #             for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
    #                 eval_examples.append(InputExample(texts=[t, r]))
    #
    #             for _, sub_df in train_data.iterrows():
    #                 if sub_df['label'] > 0:
    #                     label = 1
    #                     train_samples.append(InputExample(texts=[sub_df['entity'], sub_df['entry']], label=label))
    #                     train_samples.append(InputExample(texts=[sub_df['entry'], sub_df['entity']], label=label))
    #                 else:
    #                     label = 0
    #                     train_samples.append(InputExample(texts=[sub_df['entity'], sub_df['entry']], label=label))
    #
    #             train_loss = losses.OnlineContrastiveLoss(model=model)
    #         elif loss_func == 'multi-task':
    #             train_samples_MultipleNegativesRankingLoss = []
    #             train_samples_ConstrativeLoss = []
    #
    #             for _, sub_df in train_data.iterrows():
    #                 if sub_df['label'] > 0:
    #                     label = 1
    #                 else:
    #                     label = 0
    #                 train_samples_ConstrativeLoss.append(
    #                     InputExample(texts=[sub_df['entity'], sub_df['entry']], label=label))
    #                 if str(label) == '1':
    #                     for _ in range(int(self.data_top_k / 2)):
    #                         train_samples_MultipleNegativesRankingLoss.append(
    #                             InputExample(texts=[sub_df['entity'], sub_df['entry']], label=1))
    #                         train_samples_MultipleNegativesRankingLoss.append(
    #                             InputExample(texts=[sub_df['entry'], sub_df['entity']], label=1))
    #
    #             # Create data loader and loss for MultipleNegativesRankingLoss
    #             train_dataset_MultipleNegativesRankingLoss = SentencesDataset(
    #                 train_samples_MultipleNegativesRankingLoss,
    #                 model=model)
    #             train_dataloader_MultipleNegativesRankingLoss = DataLoader(train_dataset_MultipleNegativesRankingLoss,
    #                                                                        shuffle=True,
    #                                                                        batch_size=self.train_batch_size)
    #             train_loss_MultipleNegativesRankingLoss = losses.MultipleNegativesRankingLoss(model)
    #
    #             # Create data loader and loss for OnlineContrastiveLoss
    #             train_dataset_ConstrativeLoss = SentencesDataset(train_samples_ConstrativeLoss, model=model)
    #             train_dataloader_ConstrativeLoss = DataLoader(train_dataset_ConstrativeLoss, shuffle=True,
    #                                                           batch_size=self.train_batch_size)
    #
    #             # As distance metric, we use cosine distance (cosine_distance = 1-cosine_similarity)
    #             distance_metric = losses.SiameseDistanceMetric.COSINE_DISTANCE
    #             # Negative pairs should have a distance of at least 0.5
    #             margin = 0.5
    #             train_loss_ConstrativeLoss = losses.OnlineContrastiveLoss(model=model, distance_metric=distance_metric,
    #                                                                       margin=margin)
    #             train_object = [
    #                 (train_dataloader_MultipleNegativesRankingLoss, train_loss_MultipleNegativesRankingLoss),
    #                 (train_dataloader_ConstrativeLoss, train_loss_ConstrativeLoss)]
    #
    #             return train_object
    #         elif loss_func == 'BatchHardSoftMarginTripletLoss':
    #             ### There are 4 triplet loss variants:
    #             ### - BatchHardTripletLoss
    #             ### - BatchHardSoftMarginTripletLoss
    #             ### - BatchSemiHardTripletLoss
    #             ### - BatchAllTripletLoss
    #
    #             from sentence_transformers.datasets.SentenceLabelDataset import SentenceLabelDataset
    #
    #             guid = 1
    #             self.label_map_file = "./data/v2/label_dict.xlsx"
    #             label_map = pd.read_excel(self.label_map_file)
    #             label_map = dict(zip(label_map['entry'].tolist(), label_map['label_num'].tolist()))
    #             train_samples = []
    #             for _, sub_df in train_data.iterrows():
    #                 if sub_df['label'] != 0:
    #                     train_samples.append(InputExample(guid=str(guid), texts=[sub_df['entity']],
    #                                                       label=label_map.get(sub_df['entry'])))
    #                     guid += 1
    #
    #             print(f'train_length:{len(train_samples)}')
    #             self.train_length = len(train_samples)
    #
    #             train_dataset = SentenceLabelDataset(train_samples)
    #             train_dataloader = DataLoader(train_dataset, batch_size=self.train_batch_size, drop_last=True)
    #             train_loss = losses.BatchHardSoftMarginTripletLoss(model=model)
    #             return train_dataloader, train_loss
    #         else:
    #             for _, sub_df in train_data.iterrows():
    #                 train_samples.append(InputExample(texts=[sub_df['entity'], sub_df['entry']], label=sub_df['label']))
    #             train_loss = losses.CosineSimilarityLoss(model=model)
    #
    #         train_dataset = SentencesDataset(train_samples, model)
    #         train_dataloader = DataLoader(dataset=train_dataset, shuffle=True, batch_size=self.train_batch_size)
    #         train_obj = [(train_dataloader, train_loss)]
    #         return train_obj
    #
    #         #
    #         #
    #         # def get_evaluator(self, dev_df, evaluator_func='EmbeddingSimilarityEvaluator', collection='t1', corpus=None,
    #         #                   top_k=100, encode_batch_size=128):
    #         #     self.evaluator_func = evaluator_func
    #         #     dev_df = resample(dev_df, replace=False)
    #         #
    #         #     if evaluator_func == 'MyEvaluator':
    #         #         from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator
    #         #         from sentence_transformers import InputExample
    #         #         dev_df = dev_df[dev_df['label'] != 0.0]  # type:pd.DataFrame
    #         #         dev_df = dev_df.groupby('entity').apply(lambda x: x['entry'].tolist())
    #         #         scores = dev_df.index.tolist()
    #         #         eval_examples = []
    #         #         for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
    #         #             eval_examples.append(InputExample(texts=[t, r]))
    #         #         evaluator = MyEvaluator.from_input_examples(eval_examples, name='sts-eval', collection=collection,
    #         #                                                     top_k=top_k, encode_batch_size=encode_batch_size)
    #         #
    #         #     # elif evaluator_func == 'InformationRetrievalEvaluator':
    #         #     # ir_evaluator = InformationRetrievalEvaluator(dev_queries, corpus, dev_rel_docs,
    #         #     #                                                         show_progress_bar=True,
    #         #     #                                                         corpus_chunk_size=100000,
    #         #     #                                                         precision_recall_at_k=[10, 100],
    #         #     #                                                         name="msmarco dev")
    #         #     elif evaluator_func == 'recall_evaluator':
    #         #         from pharm_ai.panel.entry_match.retrieval_eval import RecallEvaluator
    #         #         # dev_df = dev_df[dev_df['label'] != 0.0]  # type:pd.DataFrame
    #         #         from sentence_transformers import InputExample
    #         #         dev_df = dev_df.groupby('entity').apply(lambda x: x['entry'].tolist())
    #         #
    #         #         scores = dev_df.index.tolist()
    #         #         eval_examples = []
    #         #         for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
    #         #             eval_examples.append(InputExample(texts=[t, r]))
    #         #
    #         #         evaluator = RecallEvaluator.from_input_examples(examples=eval_examples, corpus=corpus, name='sts-eval',
    #         #                                                         top_k=top_k, encode_batch_size=encode_batch_size)
    #         #         return evaluator
    #         #
    #         #     elif evaluator_func == 'seq_evaluator':
    #         #         from sentence_transformers import evaluation
    #         #         from sentence_transformers import InputExample
    #         #         from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator
    #         #         evaluators = []
    #         #
    #         #         sentences_1 = []
    #         #         sentences_2 = []
    #         #         scores_ = []
    #         #         for _, sub_df in dev_df.iterrows():
    #         #
    #         #             sentences_1.append(sub_df['entity'])
    #         #             sentences_2.append(sub_df['entry'])
    #         #             if sub_df['label'] > 0:
    #         #                 scores_.append(1)
    #         #             else:
    #         #                 scores_.append(0)
    #         #
    #         #         binary_acc_evaluator = evaluation.BinaryClassificationEvaluator(sentences_1, sentences_2, scores_)
    #         #         evaluators.append(binary_acc_evaluator)
    #         #
    #         #         dev_df = dev_df[dev_df['label'] != 0.0]  # type:pd.DataFrame
    #         #         dev_df = dev_df.groupby('entity').apply(lambda x: x['entry'].tolist())
    #         #         # scores = dev_df.index.tolist()
    #         #         eval_examples = []
    #         #         for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
    #         #             eval_examples.append(InputExample(texts=[t, r]))
    #         #         my_evaluator = MyEvaluator.from_input_examples(eval_examples, name='sts-eval', collection=collection,
    #         #                                                        top_k=top_k, encode_batch_size=encode_batch_size)
    #         #
    #         #         evaluators.append(my_evaluator)
    #         #         seq_evaluator = evaluation.SequentialEvaluator(evaluators,
    #         #                                                        main_score_function=lambda scores: scores[-1])
    #         #         return seq_evaluator
    #         #
    #         #     elif evaluator_func == 'EmbeddingSimilarityEvaluator':
    #         #         sentences_1 = []
    #         #         sentences_2 = []
    #         #         scores = []
    #         #         for _, sub_df in dev_df.iterrows():
    #         #             # if sub_df['label'] != 0.0:
    #         #             sentences_1.append(sub_df['entity'])
    #         #             sentences_2.append(sub_df['entry'])
    #         #             scores.append(sub_df['label'])
    #         #
    #         #         evaluator = EmbeddingSimilarityEvaluator(sentences_1, sentences_2, scores)
    #         #     else:
    #         #         sentences_1 = []
    #         #         sentences_2 = []
    #         #         scores = []
    #         #         for _, sub_df in dev_df.iterrows():
    #         #             if sub_df['label'] != 0.0:
    #         #                 sentences_1.append(sub_df['entity'])
    #         #                 sentences_2.append(sub_df['entry'])
    #         #                 scores.append(sub_df['label'])
    #         #         evaluator = EmbeddingSimilarityEvaluator(sentences_1, sentences_2, scores)
    #         #     print(f'dev_length:{len(scores)}')
    #         #     self.dev_length = len(scores)
    #         #     return evaluator
    #         #
    #         # @staticmethod
    #         # def save_parameters(para_obj, save_model='./test.json'):
    #         #     """
    #         #     存储一个对象的参数，对象参数可以是模型参数或超参数
    #         #     Args:
    #         #         para_obj: 要存储的参数的对象
    #         #         save_model: 保存路径
    #         #
    #         #     Returns:
    #         #
    #         #     """
    #         #     para_list = para_obj.__dir__()
    #         #     # save_para_list = ['best_score','device','max_seq_length','tokenizer']
    #         #     para = {}
    #         #     for p in para_list:
    #         #         if not p.startswith('_'):
    #         #             # if p in save_para_list:
    #         #             r = getattr(para_obj, p)
    #         #             if isinstance(r, int) or isinstance(r, str) or isinstance(r, float) or isinstance(r, list) \
    #         #                     or isinstance(r, bool):
    #         #                 para[p] = r
    #         #
    #         #     with open(save_model, "w", encoding='utf-8') as f:
    #         #         # indent 超级好用，格式化保存字典，默认为None，小于0为零个空格
    #         #         # f.write(json.dumps(para,indent=4))
    #         #         json.dump(para, f, indent=4)  # 传入文件描述符，和dumps一样的结果
    #         #
    #         #     para.pop("all_scores")
    #         #     with open(log_file, "a", encoding='utf-8') as f:
    #         #         json.dump(para, f, indent=4)
    #         #         f.write('\n')
    #         #
    #         # def call_back(self, score, epoch, steps):
    #         #     self.all_scores.append({str(epoch) + '-' + str(steps): score})
    #         #     if score > self.best_score:
    #         #         self.best_score = score
    #         #     print(f'epoch:{epoch}: score:{score} ')
    #         #
    #         # def get_corpus(self):
    #         #     self.corpus_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_v2_1217.xlsx"
    #         #     corpus = pd.read_excel(self.corpus_file)
    #         #     corpus = list(set(corpus['entry'].tolist()))
    #         #     return corpus
    #         #
    #         # def run(self):
    #         #     self.train_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
    #         #     train_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
    #         #                            'train')
    #         #     self.dev_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
    #         #     dev_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
    #         #                          'eval')
    #         #
    #         #     # self.model_path = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    #         #     # self.model_path = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    #         #     self.model_path = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/disease_v2.0/"
    #         #
    #         #     self.use_st_model = True
    #         #     self.model_version = 'di_retrieval_v2.1'
    #         #
    #         #     from zyl_utils import get_best_cuda_device
    #         #     self.cuda_device = get_best_cuda_device(gpu_num=1)
    #         #     self.max_seqence_length = 128
    #         #     self.output_dimension = 1024
    #         #     self.train_batch_size = 256
    #         #     self.data_top_k = 3
    #         #     self.epoch = 5
    #         #     self.learning_rate = 1e-5
    #         #
    #         #     self.train_model(train_df, dev_df,
    #         #                      loss_func='MultipleNegativesRankingLoss2',  # multi-task
    #         #                      evaluator_func="recall_evaluator",
    #         #                      encode_batch_size=32)
    #
    #     if __name__ == '__main__':
    #         # get_auto_device()
    #         # FineTurn().run()
    #         # Trainer().run()
    #
    #         TrainRetrieval().run()
    #
    #         pass

    # if __name__ == '__main__':
    #     class Re
