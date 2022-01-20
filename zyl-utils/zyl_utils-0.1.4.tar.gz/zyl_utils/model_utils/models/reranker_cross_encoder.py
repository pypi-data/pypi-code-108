# encoding: utf-8
"""
@author: zyl
@file: re_ranker_cross_encoder.py
@time: 2021/12/16 9:46
@desc:
选取候选集的方法
数据；【'mention'：str,'entries'；list】
"""

import math
from dataclasses import dataclass
from typing import Dict

from sentence_transformers import InputExample
from sentence_transformers.cross_encoder import CrossEncoder
from sentence_transformers.cross_encoder.evaluation import \
    CESoftmaxAccuracyEvaluator, CECorrelationEvaluator, CEBinaryClassificationEvaluator
from simpletransformers.config.model_args import ModelArgs
from torch.utils.data import DataLoader

from zyl_utils import get_best_cuda_device

MODEL_TYPE = [
    'two_classification',  # 输出0或1
    'sts',  # 语义相似性，输出0-1连续值，无序
    'nli'  # 自然语言推理，输出前后两句话的关系，有序，输出：0，1，2
]


@dataclass
class ReRankerCrossEncoderArgs(ModelArgs):
    """
        Model args for a ReRankerCrossEncoder
        num_labels:Number of labels of the classifier. If 1, the CrossEncoder is a regression model that outputs a
        continous score 0...1. If > 1, it output several scores that can be soft-maxed to get probability
        scores for the different classes.
    """
    cuda_device: str = get_best_cuda_device(gpu_num=1)
    train_batch_size: int = 16
    max_seq_length: int = 128


    tokenizer_args: Dict = dict
    default_activation_function = None
    num_labels:int =1


class ReRankerCrossEncoderModel:
    def __init__(self, model_type='two_classification',
                 model_name="sentence-transformers/distiluse-base-multilingual-cased-v1", args=None):
        """

        Args:
            model_type: 'two_classification',  # 输出0或1. 'sts',  # 语义相似性，输出0-1连续值，无序
                        'nli'  # 自然语言推理，输出前后两句话的关系，有序，输出：0，1，2
            model_name: "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
            args: dict
        """

        self.args = self._load_model_args(model_name)
        self.args.model_type = model_type
        self.args.model_name = model_name

        if isinstance(args, dict):
            self.args.update_from_dict(args)
        elif isinstance(args, ReRankerCrossEncoderArgs):
            self.args = args

        if self.args.model_type == 'sts':
            self.args.num_labels = 1
        elif self.args.model_type == 'two_classification':
            self.args.num_labels = 1
        else:
            self.args.num_labels = 3
        # loss_fct = nn.BCEWithLogitsLoss() if self.config.num_labels == 1 else nn.CrossEntropyLoss()
        # num_labels: int = 1  # softmaxed类的数量，默认1:continous score,

        self.model = self.get_model()

    def get_model(self):
        return CrossEncoder(model_name=self.args.model_name, num_labels=self.args.num_labels,
                            max_length=self.args.max_seq_length, device=f'cuda:{self.args.cuda_device}',
                            tokenizer_args=self.args.tokenizer_args,
                            default_activation_function=self.args.default_activation_function)

    def _load_model_args(self, input_dir):
        args = ReRankerCrossEncoderArgs()
        args.load(input_dir)
        return args

    def train(self, train_dt, eval_dt):
        """
        loss_fct = nn.BCEWithLogitsLoss() if self.config.num_labels == 1 else nn.CrossEntropyLoss()
        Args:
            train_dt: df,['mention','entries'],'mention' is string text,'entries' is a list of entries.
            eval_dt:

        Returns:

        """
        self.model = self.get_model()
        train_samples = self.get_samples(train_dt)
        print(f'train_sample_length:{len(train_samples)}')
        train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=self.args.train_batch_size)

        eval_samples = self.get_samples(eval_dt)

        evaluator = self.get_evaluator(eval_samples)

        warmup_steps = math.ceil(
            len(train_dataloader) * self.args.num_train_epochs * 0.1)  # 10% of train data for warm-up
        evaluation_steps = math.ceil(len(train_dataloader) * 0.1)

        self.model.fit(train_dataloader=train_dataloader, evaluator=evaluator, epochs=self.args.num_train_epochs,
                       warmup_steps=warmup_steps, evaluation_steps=evaluation_steps, save_best_model=True,
                       output_path=self.args.best_model_dir, use_amp=False, callback=self.call_back,
                       show_progress_bar=True, optimizer_params={'lr': self.args.learning_rate})

    def get_samples(self, df):
        samples = []
        if self.args.model_type == 'nli':
            for _, sub_df in df.iterrows():
                candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
                if sub_df['entries']:
                    entries_length = len(sub_df['entries'])
                    if entries_length > 1:
                        label_id = 1  # 蕴含关系
                    else:
                        label_id = 2  # 等价关系
                    for e in sub_df['entries']:
                        samples.append(InputExample(texts=[sub_df['mention'], e], label=label_id))
                        if e in candidate_entries:
                            candidate_entries.remove(e)
                for c_e in candidate_entries:
                    samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
        elif self.args.model_type == 'sts':
            for _, sub_df in df.iterrows():
                candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
                if sub_df['entries']:
                    entries_length = len(sub_df['entries'])
                    if 'label' in sub_df.index:
                        score = sub_df['label']
                    else:
                        score = round(1 / entries_length, 4)
                    for e in sub_df['entries']:
                        samples.append(InputExample(texts=[sub_df['mention'], e], label=score))
                        samples.append(InputExample(texts=[e, sub_df['mention']], label=score))
                        if e in candidate_entries:
                            candidate_entries.remove(e)
                for c_e in candidate_entries:
                    samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
                    samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
        else:
            for _, sub_df in df.iterrows():
                candidate_entries = self.get_candidade_entries(query=sub_df['mention'])
                if sub_df['entries']:
                    for e in sub_df['entries']:
                        samples.append(InputExample(texts=[sub_df['mention'], e], label=1))
                        samples.append(InputExample(texts=[e, sub_df['mention']], label=1))
                for c_e in candidate_entries:
                    samples.append(InputExample(texts=[sub_df['mention'], c_e], label=0))
                    samples.append(InputExample(texts=[c_e, sub_df['mention']], label=0))
        return samples

    def get_candidade_entries(self, query):
        candidate_entries = query
        return candidate_entries  # type:list

    def get_evaluator(self, eval_samples):
        if self.args.model_type == 'nli':
            return CECorrelationEvaluator.from_input_examples(eval_samples, name='eval')
        elif self.args.model_type == 'two_classification':
            return CEBinaryClassificationEvaluator.from_input_examples(eval_samples, name='eval')
        else:
            return CESoftmaxAccuracyEvaluator.from_input_examples(eval_samples, name='eval')

        # class RerankerTrainer:
        #     def __init__(self):
        #         self.model_path = "distiluse-base-multilingual-cased-v1"
        #         self.dimensions = 512
        #         self.cuda_device = get_best_cuda_device(gpu_num=1)
        #         self.max_seqence_length = 128
        #         self.use_st_model = True
        #         self.train_batch_size = 16
        #         self.epoch = 5
        #         self.learning_rate = 1e-5
        #         self.all_scores = []
        #         self.best_score = 0
        #         self.label2int = {"contradiction": 0, "entailment": 1, "neutral": 1}
        #         self.train_num_labels = len(set(self.label2int.values()))
        #         pass
        #
        #     def train(self, train_df, dev_df, save_model="./best_model/test/", loss_func='SoftmaxLoss',
        #               evaluator_func='MyEvaluator2', top_k=30):
        #
        #         self.save_model = save_model
        #         model = self.get_model()
        #
        #         train_dataloader, train_loss = self.get_train_objectives(train_df, model, loss_func=loss_func,
        #                                                                  top_k=top_k)
        #
        #         evaluator = self.get_evaluator(dev_df, evaluator_func=evaluator_func)
        #
        #         warmup_steps = math.ceil(len(train_dataloader) * self.epoch * 0.1)  # 10% of train data for warm-up
        #         evaluation_steps = math.ceil(len(train_dataloader) * 0.1)
        #
        #         print('start train...')
        #         # Which loss function to use for training. If None, will use nn.BCEWithLogitsLoss() if self.config.num_labels == 1 else nn.CrossEntropyLoss()
        #         model.fit(train_dataloader=train_dataloader, epochs=self.epoch, warmup_steps=warmup_steps,
        #                   evaluator=evaluator, save_best_model=True,
        #                   output_path=save_model,
        #                   evaluation_steps=evaluation_steps,
        #                   callback=self.call_back,
        #                   loss_fct=train_loss,
        #                   optimizer_params={'lr': self.learning_rate})
        #
        #         df = pd.DataFrame(self.all_scores)
        #         df.to_excel(save_model + 'my_score.xlsx')
        #         RerankerTrainer.save_parameters(self, save_model=f'{save_model}parameters.json')
        #
        #     def get_retrieval_model(self):
        #         from sentence_transformers import SentenceTransformer
        #         model = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/v2/"
        #         model = SentenceTransformer(self.model_path, device=f'cuda:{self.cuda_device}')
        #         return model
        #
        #     def get_evaluator(self, dev_df, evaluator_func='MyEvaluator2', collection='t1'):
        #         from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator
        #         from sklearn.utils import resample
        #
        #         self.evaluator_func = evaluator_func
        #         dev_df = resample(dev_df, replace=False)
        #
        #         if evaluator_func == 'MyEvaluator':
        #             from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator
        #             from sentence_transformers import InputExample
        #             dev_df = dev_df[dev_df['label'] != 0.0]  # type:pd.DataFrame
        #             dev_df = dev_df.groupby('entity').apply(lambda x: x['entry'].tolist())
        #             scores = dev_df.index.tolist()
        #             eval_examples = []
        #             dev_samples = []
        #             for t, r in zip(dev_df.index.tolist(), dev_df.tolist()):
        #                 eval_examples.append(InputExample(texts=[t, r]))
        #             evaluator = MyEvaluator.from_input_examples(eval_examples, name='sts-eval', collection=collection)
        #
        #         elif evaluator_func == 'EmbeddingSimilarityEvaluator':
        #             sentences_1 = []
        #             sentences_2 = []
        #             scores = []
        #             dev_samples = []
        #             for _, sub_df in dev_df.iterrows():
        #                 if sub_df['label'] != 0.0:
        #                     sentences_1.append(sub_df['entity'])
        #                     sentences_2.append(sub_df['entry'])
        #                     scores.append(sub_df['label'])
        #
        #             evaluator = EmbeddingSimilarityEvaluator(sentences_1, sentences_2, scores)
        #         else:
        #             from sentence_transformers import InputExample
        #             from pharm_ai.panel.entry_match.revise_evaluator import MyEvaluator2
        #             dev_samples = []
        #             for _, sub_df in dev_df.iterrows():
        #                 if sub_df['label'] == 1:
        #                     dev_samples.append(
        #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=1))
        #                 elif sub_df['label'] > 0:
        #                     dev_samples.append(
        #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=1))
        #                 else:
        #                     dev_samples.append(
        #                         InputExample(texts=[sub_df['entity'], sub_df['entry']], label=0))
        #             evaluator = MyEvaluator2.from_input_examples(dev_samples, name='AllNLI-dev')
        #
        #         print(f'dev_length:{len(dev_samples)}')
        #         self.dev_length = len(dev_samples)
        #         return evaluator
        #
        #     @staticmethod
        #     def save_parameters(para_obj, save_model='./test.json'):
        #         """
        #         存储一个对象的参数，对象参数可以是模型参数或超参数
        #         Args:
        #             para_obj: 要存储的参数的对象
        #             save_model: 保存路径
        #
        #         Returns:
        #
        #         """
        #         para_list = para_obj.__dir__()
        #         # save_para_list = ['best_score','device','max_seq_length','tokenizer']
        #         para = {}
        #         for p in para_list:
        #             if not p.startswith('_'):
        #                 # if p in save_para_list:
        #                 r = getattr(para_obj, p)
        #                 if isinstance(r, int) or isinstance(r, str) or isinstance(r, float) or isinstance(r, list) \
        #                         or isinstance(r, bool):
        #                     para[p] = r
        #
        #         with open(save_model, "w", encoding='utf-8') as f:
        #             # indent 超级好用，格式化保存字典，默认为None，小于0为零个空格
        #             # f.write(json.dumps(para,indent=4))
        #             json.dump(para, f, indent=4)  # 传入文件描述符，和dumps一样的结果
        #
        #         para.pop("all_scores")
        #         with open(log_file, "a", encoding='utf-8') as f:
        #             json.dump(para, f, indent=4)
        #             f.write('\n')
        #
        #     def call_back(self, score, epoch, steps):
        #         self.all_scores.append({str(epoch) + '-' + str(steps): score})
        #         if score > self.best_score:
        #             self.best_score = score
        #         print(f'epoch:{epoch}: score:{score} ')
        #
        # class TrainerV1(RerankerTrainer):
        #     def __init__(self):
        #         super(TrainerV1, self).__init__()
        #
        #     def run(self):
        #         self.train_1011()
        #
        #     def train_1011(self):
        #         def deal_with_df(df, corpus):
        #             df['entry'] = df['entry'].astype('str')
        #             df['entity'] = df['entity'].astype('str')
        #             m = self.get_retrieval_model()
        #             qs = df['entity'].tolist()
        #             res = RetrievalEvaluator.query_result(model=m, corpus=corpus, queries=qs, top_k=10)
        #             li = []
        #             for i, r in zip(qs, res):
        #                 for _ in r:
        #                     li.append({'entity': i, 'entry': _, 'label': 0})
        #             df_ = pd.DataFrame(li)
        #             print(len(df))
        #             df = pd.concat([df, df_], ignore_index=True)
        #             print(len(df))
        #             df.drop_duplicates(subset=['entity', 'entry'], keep='first', inplace=True)
        #             print(len(df))
        #             return df
        #
        #         self.train_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5"
        #         train_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
        #                                'train')
        #         corpus = list(set(train_df['entry'].tolist()))
        #         corpus = [str(c) for c in corpus]
        #         train_df = deal_with_df(train_df, corpus=corpus)
        #
        #         self.dev_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5"
        #         dev_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval.h5",
        #                              'eval')
        #         dev_df = deal_with_df(dev_df, corpus=corpus)
        #
        #         self.model_path = "sentence-transformers/distiluse-base-multilingual-cased-v1"
        #         # self.model_path = "./best_model/di_reranker_v2.0/"
        #
        #         # self.model_path = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/em9/"
        #         # self.model_path = '/large_files/pretrained_pytorch/mt5_zh_en/'
        #
        #         # self.model_path = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        #         # self.model_path = "./best_model/v2/v2.2.1/"
        #
        #         # self.model_path = "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
        #
        #         self.cuda_device = get_best_cuda_device(gpu_num=1)
        #         self.dimensions = 768
        #         self.max_seqence_length = 64
        #         self.use_st_model = True
        #         self.train_batch_size = 32
        #         self.epoch = 3
        #         self.learning_rate = 1e-5
        #         self.train(train_df, dev_df, save_model="./best_model/di_reranker_2/",
        #                    loss_func='CrossEntropyLoss',  # CrossEntropyLoss，BCEWithLogitsLoss，nli
        #                    evaluator_func="MyEvaluator2",
        #                    top_k=10)
        #
        #     # def train_cross_model(self):
        #     #     self.train_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
        #     #     train_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
        #     #                            'train')
        #     #     m = self.get_retrieval_model()
        #     #     RetrievalEvaluator.query_result(model=model, corpus=corpus, queries=queries, top_k=1)
        #     #
        #     #     self.dev_file = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5"
        #     #     dev_df = pd.read_hdf("/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/data/v2/disease_retrieval_v2.h5",
        #     #                          'eval')
        #     #
        #     #     # self.train_file = "./data/v2/train_2.csv.gz"
        #     #     # train_df = pd.read_csv(self.train_file, compression='gzip', sep='|')
        #     #     # self.dev_file = "./data/v2/eval.csv.gz"
        #     #     # dev_df = pd.read_csv(self.dev_file, compression='gzip', sep='|')
        #     #
        #     #
        #     #     # self.model_path = "sentence-transformers/distiluse-base-multilingual-cased-v1"
        #     #     self.model_path = "./best_model/di_reranker_v2.0/"
        #     #
        #     #     # self.model_path = "/home/zyl/disk/PharmAI/pharm_ai/panel/entry_match/best_model/em9/"
        #     #     # self.model_path = '/large_files/pretrained_pytorch/mt5_zh_en/'
        #     #
        #     #     # self.model_path = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        #     #     # self.model_path = "./best_model/v2/v2.2.1/"
        #     #
        #     #     # self.model_path = "sentence-transformers/distilbert-multilingual-nli-stsb-quora-ranking"
        #     #
        #     #
        #     #
        #     #     self.dimensions = 768
        #     #     self.max_seqence_length = 128
        #     #     self.use_st_model = True
        #     #     self.train_batch_size = 32
        #     #     self.epoch = 3
        #     #     self.learning_rate = 2e-5
        #     #     self.train(train_df, dev_df, save_model="./best_model/v2/v2.2.2/",
        #     #                loss_func='CrossEntropyLoss',  # CrossEntropyLoss，BCEWithLogitsLoss，nli
        #     #                evaluator_func="MyEvaluator2",
        #     #                top_k=10)

    def call_back(self, score, epoch, steps):
        print(f'epoch:{epoch}----step:{steps}----score:{score} ')


if __name__ == '__main__':
    import pandas as pd
    class Test(ReRankerCrossEncoderModel):
        def __init__(self):
            super(Test, self).__init__()

        def get_candidade_entries(self, query):
            candidate_entries = []
            # 模糊搜索

            # 语义搜索

            return candidate_entries

        def test_train(self):
            train_file = './test.xlsx'
            eval_file = './test.xlsx'
            train_df = pd.read_excel(train_file)  # type:pd.DataFrame
            eval_df = pd.read_excel(eval_file)  # type:pd.DataFrame

            self.model_version = 'v0.0.0.0'

            self.args.update_from_dict(
                {
                    'model_type' : 'two_classification',
                    'model_name' : "sentence-transformers/distiluse-base-multilingual-cased-v1",

                    'num_train_epochs': 3,
                    'learning_rate': 3e-4,
                    'train_batch_size': 24,  # 28
                    'eval_batch_size': 16,
                    'max_seq_length': 512,
                }
            )
            self.train(train_df, eval_df)
