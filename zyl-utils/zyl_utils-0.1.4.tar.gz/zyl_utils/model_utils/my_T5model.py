# encoding: utf-8
'''
@author: zyl
@file: T5_model.py
@time: 2021/11/11 10:54
@desc:
'''
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed

import torch
from simpletransformers.t5 import T5Model, DDPT5Model

from zyl_utils.data_utils.nlp_utils import DTUtils


class MyT5(T5Model):
    """
    add function: use-multi-gpu
    """

    def __init__(self, model_type, model_name, args=None, tokenizer=None, use_cuda=True, cuda_device=-1, **kwargs):
        super(MyT5, self).__init__(model_type=model_type, model_name=model_name, args=args,
                                   tokenizer=tokenizer, use_cuda=use_cuda, cuda_device=cuda_device, **kwargs)

    def get_funcs(self, gpus):
        self.funcs = []
        for i in gpus:
            if i != self.device.index:
                other_m = copy.deepcopy(self)
                other_m.device = torch.device(f"cuda:{i}")
                self.funcs.append(other_m.predict)
            else:
                self.funcs.append(self.predict)

    def predict_gpu(self, to_predict, gpus: list = None):
        # gpus can be like： ["1","2"]
        if len(to_predict) <= len(gpus):
            gpus = None
        if gpus and (len(gpus) == 1):
            gpus = None
        if not gpus:
            outputs = self.predict(to_predict=to_predict)
        else:
            if not self.funcs:
                self.get_funcs(gpus)
            print('Start processing data...')
            max_workers = len(gpus)
            sub_data_sets = DTUtils.split_data_evenly(to_predict, len(gpus))
            res = dict()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                assert len(self.funcs) == len(sub_data_sets)
                futures = {executor.submit(self.funcs[n], dt): n for dt, n in
                           zip(sub_data_sets, list(range(len(sub_data_sets))))}

                for f in as_completed(futures):  # not block,iterator
                    f.dt_id = futures[f]
                    res.update({f.dt_id: f.result()})
            outputs = []
            for i in sorted(res.keys()):
                for j in res[i]:
                    outputs.append(j)
        return outputs


class MyDDPT5(DDPT5Model):
    """
    add function: use-multi-gpu
    """

    def __init__(self, model_type, model_name, args=None, tokenizer=None, use_cuda=True, cuda_device=-1, **kwargs):
        super(MyDDPT5, self).__init__(model_type=model_type, model_name=model_name, args=args,
                                      tokenizer=tokenizer, use_cuda=use_cuda, cuda_device=cuda_device, **kwargs)

    def get_funcs(self, gpus):
        self.funcs = []
        for i in gpus:
            if i != self.device.index:
                other_m = copy.deepcopy(self)
                other_m.device = torch.device(f"cuda:{i}")
                self.funcs.append(other_m.predict)
            else:
                self.funcs.append(self.predict)

    def predict_gpu(self, to_predict, gpus: list = None):
        # gpus can be like： ["1","2"]
        if len(to_predict) <= len(gpus):
            gpus = None
        if gpus and (len(gpus) == 1):
            gpus = None
        if not gpus:
            outputs = self.predict(to_predict=to_predict)
        else:
            if not self.funcs:
                self.get_funcs(gpus)
            print('Start processing data...')
            max_workers = len(gpus)
            sub_data_sets = DTUtils.split_data_evenly(to_predict, len(gpus))
            res = dict()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                assert len(self.funcs) == len(sub_data_sets)
                futures = {executor.submit(self.funcs[n], dt): n for dt, n in
                           zip(sub_data_sets, list(range(len(sub_data_sets))))}

                for f in as_completed(futures):  # not block,iterator
                    f.dt_id = futures[f]
                    res.update({f.dt_id: f.result()})
            outputs = []
            for i in sorted(res.keys()):
                for j in res[i]:
                    outputs.append(j)
        return outputs
