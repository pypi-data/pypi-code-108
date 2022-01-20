# encoding: utf-8
"""
@author: zyl
@file: utils.py
@time: 2021/11/29 15:18
@desc:
"""
import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.ner import NERModel

class Utils:
    def __init__(self):
        pass

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



