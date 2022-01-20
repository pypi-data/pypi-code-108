# encoding: utf-8
"""
@author: zyl
@file: ner_model.py
@time: 2021/11/25 13:59
@desc:
"""
import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.ner import NERModel


class NerModel:
    """
    ner model for train and eval
    """

    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'
        self.describe = " use simple-transformers--ner-model"
        self.show_running_loss = False

        self.wandb_proj = 'ner'
        self.save_dir = '../'
        self.model_version = 'v0.0.0.0'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，比如mt5和分类，
        # c进行模型的处理的数据批次，比如同一输入，输出是文本还是序号，d：迭代调参批次

        self.model_type = 'roberta'
        self.pretrained_model = 'roberta-base'  # 预训练模型位置 model_name

        self.use_cuda = True
        self.cuda_device = 0
        self.labels = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]

        self.model_args = self.my_config()

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
    def deal_with_df(df):
        df = df[["sentence_id", "words", "labels"]]
        df = df.astype({'sentence_id': 'int', 'words': 'str', 'labels': 'str'})
        return df

    def train(self, train_data: pd.DataFrame, eval_data: pd.DataFrame):
        # deal with dt
        train_data = NerModel.deal_with_df(train_data)
        eval_data = NerModel.deal_with_df(eval_data)
        train_size = len(set(train_data['sentence_id'].tolist()))
        eval_size = len(set(eval_data['sentence_id'].tolist()))

        all_steps = train_size / self.model_args.get('train_batch_size')
        self.model_args.update(
            {
                'train_size': train_size,
                'eval_size': eval_size,
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
            logger.info(f'start training: model_version---{self.model_version}')
            model.train_model(train_data=train_data, eval_data=eval_data)
            logger.info('training finished!!!')
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)

    def train_example(self):
        train_file = './test.xlsx'
        eval_file = './test.xlsx'
        train_data = pd.read_excel(train_file)
        eval_data = pd.read_excel(eval_file)

        self.save_dir = '../'
        self.model_version = 'erv4.2.0.2'
        self.model_type = 'bert'
        self.pretrained_model = 'bert-base-multilingual-cased'  # 预训练模型位置 model_name
        self.use_cuda = True
        self.cuda_device = 0
        self.labels = ["O", "B-DISEASE", "I-DISEASE"]

        self.model_args = self.my_config()
        self.model_args.update(
            {
                'train_file': train_file,
                'eval_file': eval_file,
                'num_train_epochs': 3,
                'learning_rate': 1e-3,
                'train_batch_size': 24,  # 28
                'gradient_accumulation_steps': 16,
                'eval_batch_size': 16,
                'max_seq_length': 512,
            }
        )
        self.train(train_data, eval_data)

    @staticmethod
    def eval_decoration(eval_func):
        # #############################################################
        # examples: should set : self.wandb_proj , self.ver , self.args.hyper_args
        # >>> @eval_decoration
        # >>> def eval(eval_df,a,b):
        # >>>     eval_res = func... a,b
        # >>>     return eval_res
        # ############################################################
        def eval_method(self, eval_df, *args, **kwargs):
            evel_size = self.model_args.get('eval_size')
            # wand_b
            wandb.init(project=self.wandb_proj, config=self.model_args,
                       name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                       tags=[self.model_version, 'eval'])
            try:
                start_time = time.time()
                logger.info(f'start eval: model_version---{self.model_version},eval size---{evel_size}')
                eval_res = eval_func(self, eval_df, *args, **kwargs)  # type:dict
                logger.info('eval finished!!!')
                end_time = time.time()
                need_time = round((end_time - start_time) / evel_size, 5)
                eval_time = round(need_time * evel_size, 4)
                print(f'eval results: {eval_res}')
                logger.info(f'eval time: {need_time} s * {evel_size} = {eval_time} s')
                assert isinstance(eval_res, dict) == True
                eval_res.update({"eval_length": evel_size})
                wandb.log(eval_res)
            except Exception as error:
                logger.error(f'eval failed!!! ERROR:{error}')
                eval_res = dict()
            finally:
                wandb.finish()
            return eval_res

        return eval_method

    @staticmethod
    def get_entity(pred_list, label='DISEASE'):
        if not label:
            label = ''
        entities = []
        e = ''
        is_entity = 0
        for index, p in enumerate(pred_list):
            if p == '0':
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
        return entities

    def eval(self, eval_df: pd.DataFrame,use_t5_matric=False):
        eval_data = NerModel.deal_with_df(eval_df)
        eval_size = len(set(eval_df['sentence_id'].tolist()))

        self.model_args.update(
            {
                'eval_size': eval_size,
                'wandb_project': self.wandb_proj,
                'wandb_kwargs': {
                    'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                    'tags': [self.model_version, 'eval']
                }
            }
        )

        model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device)

        result, model_outputs, preds_list = model.eval_model(eval_data)

        if use_t5_matric:
            labels = eval_data.groupby(by=['sentence_id'],sort =False)
            labels = labels.apply(lambda x: x['labels'].tolist())

            preds_list = [set(NerModel.get_entity(p)) for p in preds_list]
            labels = [set(NerModel.get_entity(l)) for l in labels]
            from zyl_utils.model_utils.ner_utils import NERUtils
            NERUtils.entity_recognition_v2(labels,preds_list)


        print('1')
        # # wandb updata
        # wandb.init(
        #     project=self.wandb_proj,
        #     config = self.model_args,
        #     name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
        #     tags=[self.model_version, 'eval']
        # )
        # wandb.log({"f1_score": result.get('f1_score')})

    def eval_sample(self):
        eval_file = './test.xlsx'
        eval_data = pd.read_excel(eval_file)

        self.save_dir = '../'
        self.model_version = 'erv4.2.0.2'
        self.model_type = 'bert'
        self.use_cuda = True
        self.cuda_device = 1

        self.model_args = self.my_config()
        self.model_args.update(
            {
                'eval_file': eval_file,
                'eval_batch_size': 16,
                'max_seq_length': 512,
            }
        )
        self.eval(eval_data)


if __name__ == '__main__':
    s = ['O', 'O', 'O', 'B-DISEASE', 'I-DISEASE', 'O', 'B-DISEASE', 'B-DISEASE', 'B-DISEASE', 'I-DISEASE',
         'I-DISEASE', 'O', 'B-DISEASE', 'O', 'I-DISEASE', 'I-DISEASE', 'B-DISEASE', 'I-DISEASE']

    print(NerModel.get_entity(s))
