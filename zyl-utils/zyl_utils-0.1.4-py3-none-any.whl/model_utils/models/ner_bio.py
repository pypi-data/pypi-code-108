import copy
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import torch
import wandb
from loguru import logger
from simpletransformers.ner import NERModel

from zyl_utils.data_utils.processing import Processor
from ..metrics.ner_metric import entity_recognition_metrics


from tqdm import tqdm
class NerBIO:
    """
    ner model for train and eval---bio--simple-trainsformers
    """

    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'
        self.describe = " use simple-transformers--ner-model"

        self.wandb_proj = 'ner'
        self.save_dir = './'
        self.model_version = 'v0.0.0.0'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，c进行模型的处理的数据批次，d：迭代调参批次

        self.model_type = 'roberta'
        self.pretrained_model = 'roberta-base'  # 预训练模型位置 model_name
        self.labels = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]

        self.use_cuda = True
        self.cuda_device = 0

        self.model_args = self.my_config()
        self.funcs = None
        self.model = None
        self.my_tokenizer =None

    def my_config(self):
        return {
            'train_batch_size': 8,

            'use_multiprocessing': False,
            'use_multiprocessing_for_evaluation': False,
            # multiprocess

            # base config
            'reprocess_input_data': True,
            'use_cached_eval_features': False,
            'fp16': False,
            'manual_seed': 234,
            'gradient_accumulation_steps': 1,  # ::increase batch size,Use time for memory,

            # save
            'no_save': False,
            'save_eval_checkpoints': False,
            'save_model_every_epoch': False,
            'save_optimizer_and_scheduler': True,
            'save_steps': -1,

            # eval
            'evaluate_during_training': True,
            'evaluate_during_training_verbose': True,

            'no_cache': False,
            'use_early_stopping': False,
            'encoding': None,
            'do_lower_case': False,
            'dynamic_quantize': False,
            'quantized_model': False,
            'silent': False,

            'overwrite_output_dir': True,
            'output_dir': self.save_dir + 'outputs/' + self.model_version + '/',
            'cache_dir': self.save_dir + 'cache/' + self.model_version + '/',
            'best_model_dir': self.save_dir + 'best_model/' + self.model_version + '/',
            'tensorboard_dir': self.save_dir + 'runs/' + self.model_version + '/' + time.strftime("%Y%m%d_%H%M%S",
                                                                                                  time.localtime()) + '/',
        }

    @staticmethod
    def deal_with_df(df: pd.DataFrame):
        df = df[["sentence_id", "words", "labels"]]
        df = df.astype({'sentence_id': 'int', 'words': 'str', 'labels': 'str'})
        return df

    def train(self, train_data: pd.DataFrame, eval_data: pd.DataFrame, wandb_log=None):
        # deal with dt
        train_data = NerBIO.deal_with_df(train_data)
        eval_data = NerBIO.deal_with_df(eval_data)
        train_size = len(set(train_data['sentence_id'].tolist()))
        eval_size = len(set(eval_data['sentence_id'].tolist()))

        # update args
        all_steps = train_size / self.model_args.get('train_batch_size')

        self.model_args.update(
            {
                'logging_steps': int(max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'evaluate_during_training_steps': int(
                    max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'wandb_project': self.wandb_proj,
                'wandb_kwargs': {
                    'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                    'tags': [self.model_version, 'train']
                }
            }
        )

        # get model
        model = NERModel(model_type=self.model_type, model_name=self.pretrained_model, labels=self.labels,
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device)
        # train
        try:
            start_time = time.time()
            logger.info(f'start training: model_version---{self.model_version},train_size---{train_size}')
            model.train_model(train_data=train_data, eval_data=eval_data)
            logger.info('training finished!!!')
            wandb.log({'train_size': train_size, 'eval_size': eval_size})
            if wandb_log:
                wandb.log(wandb_log)
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)

    @staticmethod
    def get_id_entity(pred_list, label='DISEASE'):
        """
        从一个bio格式的序列中获得id实体，比如：['O', 'O', 'O', 'B-DISEASE', 'I-DISEASE', 'O', ]---->['-3-4']
        Args:
            pred_list: ['O', 'O', 'O', 'B-DISEASE', 'I-DISEASE', 'O', ]
            label: DISEASE

        Returns:
                ['-3-4']
        """
        if not label:
            label = ''
        entities = []
        e = ''
        is_entity = 0
        for index, p in enumerate(pred_list):
            if p == 'O':
                if is_entity == 1:
                    entities.append(e)
                is_entity = 0
            elif p.startswith('B-' + label):
                if is_entity == 1:
                    if e:
                        entities.append(e)
                e = '-' + str(index)
                is_entity = 1
            elif p.startswith('I-' + label):
                e = e + ('-' + str(index))
        if is_entity == 1:
            entities.append(e)
        return entities  # list or []

    def eval(self, eval_df: pd.DataFrame, ner_t5_metric=False, wandb_log=None):
        eval_data = NerBIO.deal_with_df(eval_df)
        eval_size = len(set(eval_df['sentence_id'].tolist()))

        # wand_b
        wandb.init(project=self.wandb_proj, config=self.model_args,
                   name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                   tags=[self.model_version, 'eval'])

        model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device,
                         labels=self.labels)
        result, model_outputs, preds_list = model.eval_model(eval_data)
        if wandb_log:
            wandb.log(wandb_log)
        wandb.log({"f1_score": result.get('f1_score'), 'eval_size': eval_size})

        if ner_t5_metric:
            all_entities_cls = set()
            for c in self.labels:
                if c.startswith('B'):
                    all_entities_cls.add(c.split('-')[-1])

            labels = eval_data.groupby(by=['sentence_id'], sort=False)
            labels = labels.apply(lambda x: x['labels'].tolist())

            for c in all_entities_cls:
                y_pred = [set(NerBIO.get_id_entity(p, label=c)) for p in preds_list]
                y_true = [set(NerBIO.get_id_entity(l, label=c)) for l in labels]
                print(c + ": \n")
                res_df = entity_recognition_metrics(y_true, y_pred)
                wandb.log({c + "_" + "ner_t5_metric": res_df.iloc[2, -1]})

    def predict_with_multi_gpus(self, to_predict, gpus: list = None, **kwargs):
        """
        多gpu预测,大数据量评估时用，必须在init中加入”self.funcs=None“
        Args:
            self: cls 某个模型类
            to_predict: 要预测的东西，list
            gpus: 若干gpu，list, gpus can be like： ["1","2"],多gpu预测时，若gpu列表中无本身的cuda-device，则不用，
            只用gpus里面的gpu进行预测

        Returns:
            预测的结果
        """
        if not self.model:
            self.model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device,
                         labels=self.labels)
        if len(to_predict) <= len(gpus):
            gpus = None
        if gpus and (len(gpus) == 1):
            gpus = None
        if not gpus:
            preds, model_outputs = self.model.predict(to_predict=to_predict, **kwargs)
        else:
            if not self.funcs:
                self.funcs = []
                for i in gpus:
                    if i != self.model.device.index:
                        other_m = copy.deepcopy(self.model)
                        other_m.device = torch.device(f"cuda:{i}")
                        self.funcs.append(other_m.predict)
                    else:
                        self.funcs.append(self.model.predict)
            max_workers = len(gpus)
            sub_data_sets = Processor.split_data_evenly(to_predict, len(gpus))
            res = dict()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                assert len(self.funcs) == len(sub_data_sets)
                futures = {executor.submit(self.funcs[n], dt, **kwargs): n for dt, n in
                           zip(sub_data_sets, list(range(len(sub_data_sets))))}

                for f in as_completed(futures):  # not block,iterator
                    f.dt_id = futures[f]
                    res.update({f.dt_id: f.result()})

            preds = []
            model_outputs = []
            for i in sorted(res.keys()):
                preds.extend(res[i][0])
                model_outputs.extend(res[i][1])
        return preds, model_outputs


    def predict_texts(self, to_predict,split_on_space=False,if_cut_sentences=False):
        if not self.model:
            self.model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                                  args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device,
                                  labels=self.labels)
        if not self.my_tokenizer:
            from zyl_utils.data_utils.text_processing import MyTokenizer
            self.my_tokenizer = MyTokenizer()

        predict_ids = list(range(len(to_predict))) # 样本id
        sentence_ids = []  # 句子id
        sentences = []
        if if_cut_sentences:
            for t,i in zip(to_predict,predict_ids):
                tmp_sentences = self.my_tokenizer.cut_paragraph_to_sentences(t) # [str]
                for s in tmp_sentences:
                    words = self.my_tokenizer.cut_sentence_to_words(s, return_starts=False)
                    sentences.append(words)
                    sentence_ids.append(i)
        else:
            for t,i in zip(to_predict,predict_ids):
                words = self.my_tokenizer.cut_sentence_to_words(t, return_starts=False)
                sentences.append(words)
                sentence_ids.append(i)

        pred_res, _ = self.model.predict(sentences, split_on_space=split_on_space)
        labels = set()
        for l in self.labels:
            if l!='O':
                labels.add(l.split('-')[-1])

        if split_on_space:
            split_symbol = ' '
        else:
            split_symbol = ''

        results = []
        for p_i in predict_ids:
            res = {l:set() for l in labels}
            for p_r,s_i in zip(pred_res,sentence_ids):
                if p_i == s_i:
                    words = [list(_.keys())[0] for _ in p_r]
                    pred = [list(_.values())[0] for _ in p_r]  # ['B-DISEASE','I'....]
                    for l in labels:
                        entities_ids = NerBIO.get_id_entity(pred, label=l)  # ['-0-1-2','-3-4'...]
                        for entity_id in entities_ids:
                            starts_id = int(entity_id.split('-')[1])
                            end_id = int(entity_id.split('-')[-1])
                            res[l].add(split_symbol.join(words[starts_id:end_id+1]))
            results.append(res)
        return results  # [{'TENDEREE': {'临沂市人民医院'}}]




        # pred = NerBIO.get_id_entity(pred, label=label)

        # pred = [list(p.values())[0] for p in pred[0]]




        # preds = []
        # for text in tqdm(to_predict):
        #     if if_cut_sentences:
        #
        #     else:
        #         sentences = [text]
        #     entities_in_one_text = []
        #     for sentence in sentences:
        #         words, starts = self.my_tokenizer.cut_sentence_to_words(sentence, return_starts=True)
        #
        #         pred, _ = self.predict_with_multi_gpus([words], split_on_space=split_on_space)  # [{'entity':'B-DISEASE'...}]
        #         pred = [list(p.values())[0] for p in pred[0]]  # ['B-DISEASE','I'....]
        #         pred = NerBIO.get_id_entity(pred, label=label)  # ['-0-1-2','-3-5'...]
        #
        #         entities_in_one_sentence = []
        #         if pred:
        #             for entity in pred:
        #                 starts_id = int(entity.split('-')[1])
        #                 end_id = int(entity.split('-')[-1])
        #                 entities_in_one_sentence.append(sentence[starts[starts_id]:
        #                                                          starts[end_id] + len(words[end_id])])  # ['癌症'...]
        #         entities_in_one_text.extend(entities_in_one_sentence)
        #     preds.append(entities_in_one_text)
        # return preds



class NerBIOModel(NERModel):
    def __init__(self, model_type, model_name, labels=None, weight=None, args=None, use_cuda=True, cuda_device=-1,
                 onnx_execution_provider=None, **kwargs, ):
        super(NerBIOModel, self).__init__(model_type, model_name, labels=labels, weight=weight, args=args,
                                          use_cuda=use_cuda,
                                          cuda_device=cuda_device, onnx_execution_provider=onnx_execution_provider,
                                          **kwargs)
        self.funcs = None
        from zyl_utils.data_utils.text_processing import MyTokenizer
        self.my_tokenizer = MyTokenizer()

    def predict_with_multi_gpus(self, to_predict, gpus: list = None, **kwargs):
        """
        多gpu预测，必须在init中加入”self.funcs=None“
        Args:
            self: cls 某个模型类
            to_predict: 要预测的东西，list
            gpus: 若干gpu，list, gpus can be like： ["1","2"]

        Returns:
            预测的结果
        """
        if len(to_predict) <= len(gpus):
            gpus = None
        if gpus and (len(gpus) == 1):
            gpus = None
        if not gpus:
            preds, model_outputs = self.predict(to_predict=to_predict, **kwargs)
        else:
            if not self.funcs:
                self.funcs = []
                for i in gpus:
                    if i != self.device.index:
                        other_m = copy.deepcopy(self)
                        other_m.device = torch.device(f"cuda:{i}")
                        self.funcs.append(other_m.predict)
                    else:
                        self.funcs.append(self.predict)
            max_workers = len(gpus)
            sub_data_sets = Processor.split_data_evenly(to_predict, len(gpus))
            res = dict()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                assert len(self.funcs) == len(sub_data_sets)
                futures = {executor.submit(self.funcs[n], dt, **kwargs): n for dt, n in
                           zip(sub_data_sets, list(range(len(sub_data_sets))))}

                for f in as_completed(futures):  # not block,iterator
                    f.dt_id = futures[f]
                    res.update({f.dt_id: f.result()})

            preds = []
            model_outputs = []
            for i in sorted(res.keys()):
                preds.extend(res[i][0])
                model_outputs.extend(res[i][1])
        return preds, model_outputs

    def predict_texts(self, to_predict, split_on_space=False, label='DISEASE'):
        from tqdm import tqdm
        preds = []
        for text in tqdm(to_predict):
            sentences = self.my_tokenizer.cut_paragraph_to_sentences(text)
            entities_in_one_text = []
            for sentence in sentences:
                words, starts = self.my_tokenizer.cut_sentence_to_words(sentence, return_starts=True)

                pred, _ = self.predict([words], split_on_space=split_on_space)  # [{'entity':'B-DISEASE'...}]
                pred = [list(p.values())[0] for p in pred[0]]  # ['B-DISEASE','I'....]
                pred = NerBIO.get_id_entity(pred, label=label)  # ['-0-1-2','-3-5'...]

                entities_in_one_sentence = []
                if pred:
                    for entity in pred:
                        starts_id = int(entity.split('-')[1])
                        end_id = int(entity.split('-')[-1])
                        entities_in_one_sentence.append(sentence[starts[starts_id]:
                                                                 starts[end_id] + len(words[end_id])])  # ['癌症'...]
                entities_in_one_text.extend(entities_in_one_sentence)
            preds.append(entities_in_one_text)
        return preds


if __name__ == '__main__':
    from zyl_utils import get_best_cuda_device


    class M(NerBIO):
        def __init__(self):
            super(M, self).__init__()
            self.wandb_proj = 'test'
            self.use_cuda = True
            self.cuda_device = get_best_cuda_device()
            self.save_dir = './'

        def train_sample(self):
            train_file = './test.xlsx'
            eval_file = './test.xlsx'
            train_df = pd.read_excel(train_file)  # type:pd.DataFrame
            eval_df = pd.read_excel(eval_file)  # type:pd.DataFrame

            self.model_version = 'v0.0.0.0'
            self.model_type = 'bert'
            self.pretrained_model = 'bert-base-multilingual-cased'  # 预训练模型位置 model_name

            self.model_args = self.my_config()
            self.model_args.update(
                {
                    'num_train_epochs': 3,
                    'learning_rate': 3e-4,
                    'train_batch_size': 24,  # 28
                    'gradient_accumulation_steps': 16,
                    'eval_batch_size': 16,
                    'max_seq_length': 512,
                }
            )
            self.labels = ["O", "B-DISEASE", "I-DISEASE"]
            self.train(train_df, eval_df, wandb_log=None)

        def eval_sample(self):
            eval_file = './test.xlsx'
            eval_data = pd.read_excel(eval_file)

            self.model_version = 'erv4.2.0.2'
            self.model_type = 'bert'

            self.model_args = self.my_config()
            self.model_args.update(
                {
                    # 'best_model_dir':'./',
                    'eval_batch_size': 16,
                }
            )
            self.eval(eval_data, ner_t5_metric=True, wandb_log={'eval_file': eval_file})
