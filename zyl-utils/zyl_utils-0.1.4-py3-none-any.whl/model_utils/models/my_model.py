# encoding: utf-8
'''
@author: zyl
@file: my_model.py
@time: 2021/11/11 10:56
@desc:
'''

import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.classification import ClassificationModel, ClassificationArgs, DDPClassificationModel
from simpletransformers.t5 import T5Args

from zyl_utils.model_utils.models.my_T5model import MyT5, MyDDPT5


class MyModel:
    """
    my model for train and eval
    """

    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'

        self.wandb_proj = 'test'
        self.model_version = 'test'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，比如mt5和分类，
        # c进行模型的数据批次，比如同一输入，输出是文本还是序号，d：迭代调参批次

        self.use_model = 'classification'  # mt5 /classification
        self.model_type = 'bert'
        self.pretrained_model = './best/v1.1.1.1/'  # 预训练模型位置

        self.use_cuda = True
        self.cuda_device = 0
        self.num_labels = 2

        self.args = MyModel.set_model_parameter(model_version=self.model_version,
                                                args=self._set_args(), save_dir='../')

    def _set_args(self):
        if self.use_model == 't5' or self.use_model == 'mt5':
            return T5Args()
        else:
            return ClassificationArgs()

    @staticmethod
    def set_model_parameter(model_version='test', args=ClassificationArgs(), save_dir='./'):
        # multiprocess
        args.use_multiprocessing = False
        args.use_multiprocessing_for_evaluation = False

        # base config
        args.reprocess_input_data = True
        args.use_cached_eval_features = False
        args.fp16 = False
        args.manual_seed = 234
        args.gradient_accumulation_steps = 2  # ==increase batch size,Use time for memory,

        # save
        args.no_save = False
        args.save_eval_checkpoints = False
        args.save_model_every_epoch = False
        args.save_optimizer_and_scheduler = True
        args.save_steps = -1

        # eval
        args.evaluate_during_training = True
        args.evaluate_during_training_verbose = True

        args.no_cache = False
        args.use_early_stopping = False
        args.encoding = None
        args.do_lower_case = False
        args.dynamic_quantize = False
        args.quantized_model = False
        args.silent = False

        args.overwrite_output_dir = True
        args.output_dir = save_dir + 'outputs/' + model_version + '/'
        args.cache_dir = save_dir + 'cache/' + model_version + '/'
        args.best_model_dir = save_dir + 'best_model/' + model_version + '/'
        args.tensorboard_dir = save_dir + 'runs/' + model_version + '/' + time.strftime("%Y%m%d_%H%M%S",
                                                                                        time.localtime()) + '/'
        return args

    def get_train_model(self):
        if self.args.n_gpu <= 1:
            if self.use_model == 't5' or self.use_model == 'mt5':
                self.args.use_multiprocessed_decoding = False
                return MyT5(model_type=self.model_type, model_name=self.pretrained_model,
                            use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args)
            else:
                return ClassificationModel(model_type=self.model_type, model_name=self.pretrained_model,
                                           use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args,
                                           num_labels=self.num_labels)
        else:
            if self.use_model == 't5' or self.use_model == 'mt5':
                self.args.use_multiprocessed_decoding = False
                return MyDDPT5(model_type=self.model_type, model_name=self.pretrained_model, use_cuda=True,
                               cuda_device=-1, args=self.args)
            elif self.use_model == 'classification':
                return ClassificationModel(model_type=self.model_type, model_name=self.pretrained_model,
                                           use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args,
                                           num_labels=self.num_labels)
            else:
                return DDPClassificationModel(model_type=self.model_type, model_name=self.pretrained_model,
                                              use_cuda=True, args=self.args, num_labels=self.num_labels)

    @staticmethod
    def deal_with_df(df, use_model='cls'):
        if use_model == 't5' or use_model == 'mt5':
            df = df[['prefix', 'input_text', 'target_text']]
            df = df.astype('str')
        elif use_model == 'sentence_pair':
            df = df[['text_a', 'text_b', 'labels']]
            df = df.astype({'text_a': 'str', 'text_b': 'str', 'labels': 'int'})
        else:
            df = df.astype({'text': 'str', 'labels': 'int'})
            df = df[['text', 'labels']]
        return df

    def train(self, train_df: pd.DataFrame, eval_df: pd.DataFrame, if_send_message=False):
        # deal with dt
        train_df = MyModel.deal_with_df(train_df, use_model=self.use_model)
        eval_df = MyModel.deal_with_df(eval_df, use_model=self.use_model)

        # config some parameters
        train_size = train_df.shape[0]
        self.args.update_from_dict({'train_length': train_size})
        all_steps = train_size / self.args.train_batch_size
        self.args.logging_steps = int(max(all_steps / 10 / self.args.gradient_accumulation_steps, 1))
        self.args.evaluate_during_training_steps = int(
            max(all_steps / 10 / self.args.gradient_accumulation_steps, 1))

        self.args.wandb_project = self.wandb_proj
        self.args.wandb_kwargs = {
            'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
            'tags': [self.model_version, 'train']}

        # get model
        model = self.get_train_model()

        # train
        try:
            start_time = time.time()
            logger.info(f'start training: model_version---{self.model_version},train length---{train_size}')
            if self.use_model == 't5' or self.use_model == 'mt5':
                model.train_model(train_data=train_df, eval_data=eval_df)
            else:
                model.train_model(train_df=train_df, eval_df=eval_df)
            logger.info('training finished!!!')
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
            if if_send_message:
                print(f'train failed!!! ERROR:{error}')
                # ModelUtils.send_to_me(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)

    def get_predict_model(self):
        if self.args.n_gpu <= 1:
            if self.use_model == 't5' or self.use_model == 'mt5':
                self.args.use_multiprocessed_decoding = False
                return MyT5(model_type=self.model_type, model_name=self.args.best_model_dir,
                            use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args)
            else:
                return ClassificationModel(model_type=self.model_type, model_name=self.args.best_model_dir,
                                           use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args,
                                           num_labels=self.num_labels)
        else:
            if self.use_model == 't5' or self.use_model == 'mt5':
                self.args.use_multiprocessed_decoding = False
                return MyDDPT5(model_type=self.model_type, model_name=self.args.best_model_dir, use_cuda=True,
                               cuda_device=-1, args=self.args)
            elif self.use_model == 'sentence_pair':
                return ClassificationModel(model_type=self.model_type, model_name=self.args.best_model_dir,
                                           use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.args,
                                           num_labels=self.num_labels)
            else:
                return DDPClassificationModel(model_type=self.model_type, model_name=self.args.best_model_dir,
                                              use_cuda=True, args=self.args, num_labels=self.num_labels)

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
            eval_length = eval_df.shape[0]

            # wand_b
            wandb.init(project=self.wandb_proj, config=self.args,
                       name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                       tags=[self.model_version, 'eval'])
            try:
                start_time = time.time()
                logger.info(f'start eval: model_version---{self.model_version},eval length---{eval_length}')
                eval_res = eval_func(self, eval_df, *args, **kwargs)  # type:dict
                logger.info('eval finished!!!')
                end_time = time.time()
                need_time = round((end_time - start_time) / eval_length, 5)
                eval_time = round(need_time * eval_length, 4)
                print(f'eval results: {eval_res}')
                logger.info(f'eval time: {need_time} s * {eval_length} = {eval_time} s')
                assert isinstance(eval_res, dict) == True
                eval_res.update({"eval_length": eval_length})
                wandb.log(eval_res)
            except Exception as error:
                logger.error(f'eval failed!!! ERROR:{error}')
                eval_res = dict()
            finally:
                wandb.finish()
            return eval_res

        return eval_method
