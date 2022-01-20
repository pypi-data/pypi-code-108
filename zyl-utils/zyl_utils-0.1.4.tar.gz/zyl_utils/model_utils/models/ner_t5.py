import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.t5 import T5Model

from ..metrics.ner_metric import entity_recognition_metrics


class NerT5:
    """
    ner model for train and eval---t5--simple-trainsformers
    """

    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'
        self.describe = " use simple-transformers--t5-model"

        self.wandb_proj = 'mt5'
        self.save_dir = './'  # save output_file
        self.model_version = 'v0.0.0.0'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，c进行模型的处理的数据批次，d：迭代调参批次

        self.model_type = 't5'
        self.pretrained_model = 't5-base'  # 预训练模型位置 model_name

        self.use_cuda = True
        self.cuda_device = 0

        self.model_args = self.my_config()

    def my_config(self):
        return {
            'train_batch_size': 8,
            'max_seq_length': 256,

            # multiprocess
            'use_multiprocessing': False,
            'use_multiprocessing_for_evaluation': False,

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

            # normal
            'no_cache': False,
            'use_early_stopping': False,
            'encoding': None,
            'do_lower_case': False,
            'dynamic_quantize': False,
            'quantized_model': False,
            'silent': False,

            # save
            'overwrite_output_dir': True,
            'output_dir': self.save_dir + 'outputs/' + self.model_version + '/',
            'cache_dir': self.save_dir + 'cache/' + self.model_version + '/',
            'best_model_dir': self.save_dir + 'best_model/' + self.model_version + '/',
            'tensorboard_dir': self.save_dir + 'runs/' + self.model_version + '/' + time.strftime("%Y%m%d_%H%M%S",
                                                                                                  time.localtime()) + '/',

            # t5 args
            'use_multiprocessed_decoding': False,
            'num_beams': 1,
            'length_penalty': 2.0,
            'max_length': 20,
            'num_return_sequences': 1,
            'preprocess_inputs': True,
            'repetition_penalty': 1.0,
            'special_tokens_list': [],
            'top_k': None,
            'top_p': None,
        }

    def _deal_with_df(self, data, sliding_window=False, delimiter='|', up_sampling=False):
        data = data[['prefix', 'input_text', 'target_text']]
        data = data.astype('str')

        if sliding_window:
            from transformers import T5Tokenizer
            tokenizer = T5Tokenizer.from_pretrained(self.pretrained_model)
            data['input_text'] = data['input_text'].apply(NerT5._split_text_with_sliding_window,
                                                          args=(self.model_args.get('max_seq_length'),
                                                                tokenizer, 0.8))
            data = data.explode('input_text')

            res = []
            for i, t in zip(data['input_text'].tolist(), data['target_text'].tolist()):
                if t != delimiter:
                    all_entities = list(set(t.split(delimiter)))
                    if '' in all_entities:
                        all_entities.remove('')
                    r = delimiter
                    if all_entities:
                        for e in all_entities:
                            if str(e) in str(i):
                                r = r + str(e) + delimiter
                    res.append(r)
                else:
                    res.append(t)

            data['target_text'] = res

        if up_sampling:
            pos_data = data[data['target_text'] != '|']
            from sklearn.utils import resample
            up_sampling_data = resample(pos_data, replace=True, n_samples=(len(data) - len(pos_data) - len(pos_data)))
            data = pd.concat([data, up_sampling_data], ignore_index=True)
            data = resample(data, replace=False)
        data.dropna(inplace=True)
        return data

    def train(self, train_data: pd.DataFrame, eval_data: pd.DataFrame, sliding_window=False, up_sampling=False,
              wandb_log=None):
        # deal with dt
        train_raw_size = train_data.shape[0]
        eval_raw_size = eval_data.shape[0]
        logger.info('processing data...')
        train_data = self._deal_with_df(train_data, sliding_window=sliding_window, delimiter='|',
                                        up_sampling=up_sampling)
        eval_data = self._deal_with_df(eval_data, sliding_window=sliding_window, delimiter='|')

        train_size = train_data.shape[0]
        all_steps = train_size / self.model_args.get('train_batch_size')
        self.model_args.update(
            {
                'logging_steps': int(max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'evaluate_during_training_steps': int(
                    max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'wandb_project': self.wandb_proj,
                'wandb_kwargs': {
                    'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                    'tags': [self.model_version, 'train'],
                }
            }
        )

        model = T5Model(model_type=self.model_type, model_name=self.pretrained_model,
                        use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.model_args)

        # train
        try:
            start_time = time.time()
            logger.info(f'start training: model_version---{self.model_version},train_size---{train_raw_size}')
            model.train_model(train_data=train_data, eval_data=eval_data)
            logger.info('training finished!!!')
            wandb.log({"eval_size": eval_raw_size, 'train_size': train_raw_size})
            if wandb_log:
                wandb.log(wandb_log)
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)

    def eval(self, eval_data: pd.DataFrame, check_in_input_text: bool = False, delimiter='|',
             tokenizer=None, use_sliding_window=False, sliding_window=None, stride=0.8,
             pos_neg_ratio=None, use_multi_gpus=None, self_metric=False, wandb_log=None):
        # deal_with_dt
        eval_data = self._deal_with_df(eval_data, sliding_window=False)
        eval_size = eval_data.shape[0]

        # wand_b
        wandb.init(project=self.wandb_proj, config=self.model_args,
                   name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                   tags=[self.model_version, 'eval'])

        try:
            start_time = time.time()
            logger.info(f'start eval: model_version---{self.model_version},eval size---{eval_size}')

            model = T5Model(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                            use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.model_args)

            eval_res = NerT5._eval_entity_recognition(model, eval_data=eval_data, delimiter=delimiter,
                                                      check_in_input_text=check_in_input_text,
                                                      tokenizer=tokenizer, use_sliding_window=use_sliding_window,
                                                      sliding_window=sliding_window, stride=stride,
                                                      pos_neg_ratio=pos_neg_ratio, use_multi_gpus=use_multi_gpus,
                                                      self_metric=self_metric)

            if wandb_log:
                wandb.log(wandb_log)
            wandb_log = {"eval_size": eval_size}
            for k, v in eval_res.items():
                wandb_log.update({k: v.iloc[2, -1]})
            wandb.log(wandb_log)
            logger.info('eval finished!!!')
            end_time = time.time()
            need_time = round((end_time - start_time) / eval_size, 5)
            eval_time = round(need_time * eval_size, 4)
            print(f'eval results: {eval_res}')
            logger.info(f'eval time: {need_time} s * {eval_size} = {eval_time} s')
        except Exception as error:
            logger.error(f'eval failed!!! ERROR:{error}')
        finally:
            wandb.finish()

    @staticmethod
    def _eval_entity_recognition(model, eval_data: pd.DataFrame, check_in_input_text: bool, delimiter='|',
                                 tokenizer=None, use_sliding_window=False, sliding_window=512, stride=0.8,
                                 pos_neg_ratio=None, use_multi_gpus=None, self_metric=False):
        """eval entity recognition in mt5 model, version-v2 , reference: https://docs.qq.com/doc/DYXRYQU1YbkVvT3V2

        Args:
            model: a mt5 model
            eval_data: a pd.Dataframe , must have columns ['prefix','input_text','target_text']
            check_in_input_text: if the entities are in input_texts
            delimiter: the delimiter in target_text to split different entities
            use_sliding_window: if truncate the input text when predict
            sliding_window: truncating_size
            stride: overlapping_size
            use_multi_gpus:use_multi_gpus
            pos_neg_ratio : the ratio of positive and negative sample importance
            self_metric:self_metric
            tokenizer: tokenizer to split sentence

        Returns:
            show report and res, {prefix:res_df},type:dict
        """
        eval_data = eval_data[['prefix', 'input_text', 'target_text']]
        eval_data = eval_data.astype('str')

        prefixes = eval_data['prefix'].to_list()
        input_texts = eval_data['input_text'].tolist()
        target_texts = eval_data['target_text'].tolist()
        revised_target_texts = NerT5._revise_target_texts(target_texts=target_texts,
                                                          input_texts=input_texts, delimiter=delimiter,
                                                          check_in_input_text=check_in_input_text)

        pred_target_texts = NerT5.predict_entity_recognition(model, prefixes, input_texts, tokenizer=tokenizer,
                                                             use_sliding_window=use_sliding_window,
                                                             sliding_window=sliding_window, stride=stride,
                                                             delimiter=delimiter, use_multi_gpus=use_multi_gpus)

        revised_pred_target_texts = NerT5._revise_target_texts(target_texts=pred_target_texts,
                                                               input_texts=input_texts, delimiter=delimiter,
                                                               check_in_input_text=check_in_input_text)

        eval_data['true_target_text'] = revised_target_texts
        eval_data['pred_target_text'] = revised_pred_target_texts

        eval_res = {}
        for prefix in set(prefixes):
            prefix_df = eval_data[eval_data['prefix'] == prefix]
            y_true = prefix_df['true_target_text'].tolist()
            y_pred = prefix_df['pred_target_text'].tolist()
            print(f'{prefix} report:')
            res_df = entity_recognition_metrics(y_true, y_pred, pos_neg_ratio=pos_neg_ratio,
                                           self_metric=self_metric)
            eval_res[prefix] = res_df

        print(f'sum report:')
        res_df = entity_recognition_metrics(revised_target_texts, revised_pred_target_texts,
                                       pos_neg_ratio=pos_neg_ratio, self_metric=self_metric)
        eval_res['ner_t5_metric'] = res_df

        return eval_res  # {prefix:res_df},type:dict

    @staticmethod
    def predict_entity_recognition(model, prefixes: list, input_texts: list, use_sliding_window=False,
                                   sliding_window=None, stride=0.8, tokenizer=None,
                                   delimiter='|', use_multi_gpus=None) -> list:
        """predict entity recognition in mt5 model,
        Args:
            model: a mt5 model
            prefixes: prefixes
            input_texts: input_texts
            use_sliding_window: if use_sliding_window
            sliding_window: sliding_window,the max token length for the model input(max_sequence_length)
            tokenizer: tokenizer
            stride: stride,(1-stride)*sliding_window for overlapping

            delimiter: the delimiter in target_text to split different entities,default: '|'
            use_multi_gpus: use_multi_gpus

        Returns:
            pred_target_texts:list,every element in pred_target_texts corresponds a prefix and an input_text
        """
        if not sliding_window:
            sliding_window = model.args.max_seq_length

        if len(input_texts) == 1:
            use_multi_gpus = None
        assert len(prefixes) == len(input_texts)

        if use_sliding_window:
            t_ids, t_prefixes, t_input_texts = NerT5._split_texts_with_sliding_window(input_texts, prefixes,
                                                                                      tokenizer=tokenizer,
                                                                                      sliding_window=sliding_window,
                                                                                      stride=stride)

            to_predict_texts = [i + ': ' + j for i, j in zip(t_prefixes, t_input_texts)]

            if not use_multi_gpus:
                pred_target_texts = model.predict(to_predict_texts)
            else:
                pred_target_texts = model.predict_gpu(to_predict_texts, gpus=use_multi_gpus)

            pred_target_texts = NerT5._combine_pred_target_texts_by_ids(pred_target_texts, t_ids, delimiter)
        else:
            to_predict_texts = [i + ': ' + j for i, j in zip(prefixes, input_texts)]
            if not use_multi_gpus:
                pred_target_texts = model.predict(to_predict_texts)
            else:
                pred_target_texts = model.predict_gpu(to_predict_texts, gpus=use_multi_gpus)
        assert len(pred_target_texts) == len(input_texts)
        return pred_target_texts  # type:list[str]

    @staticmethod
    def _split_text_with_sliding_window(text: str, sliding_window=128, tokenizer=None, stride=0.8) -> list:
        """ any sequence exceeding the max_seq_length will be split into several windows (sub-sequences),
        each of length max_seq_length. The windows will typically overlap each other to a certain degree to
        minimize any information loss that may be caused by hard cutoffs.


        Args:
            text: a str text
            sliding_window: truncating_size:sliding window, max_seq_length
            tokenizer: tokenizer
            stride: The amount of overlap between the windows,The stride can be specified in terms of either a fraction
             of the max_seq_length, or as an absolute number of tokens.

        Returns:
            truncated_input_text: the list of truncated_input_text
        """
        sliding_window = sliding_window - 8  # 防止一些词： <\s> <sep>等

        if not isinstance(text, str):
            text = str(text)

        if not tokenizer:
            try:
                from simpletransformers.t5 import T5Model
                tokenizer = T5Model('mt5', 'google/mt5-base').tokenizer
            except Exception:
                print('no tokenizer....')

        tokens = tokenizer.tokenize(text)

        if len(tokens) <= sliding_window:
            return [text]
        else:
            split_text = []
            if stride < 1:
                step_size = int(sliding_window * stride)
            else:
                step_size = int(stride)
            steps = int(len(tokens) / step_size)
            for i in range(0, steps + 1):
                text_i_tokens = tokens[i * step_size:i * step_size + sliding_window]
                if text_i_tokens:
                    text_i = ''.join(text_i_tokens).replace('▁', ' ').strip()
                    split_text.append(text_i)

            if (len(split_text) > 1) and (
                    len(tokenizer.tokenize(split_text[-1])) < (sliding_window - step_size)):
                split_text = split_text[0:-1]
            return split_text

    @staticmethod
    def _split_texts_with_sliding_window(input_texts: list, prefixes: list, tokenizer=None,
                                         sliding_window=512, stride=0.8):
        """ for every input_text in input_texts, split it and record the split_ids for combining

        Args:
            input_texts: the list of many input_text
            prefixes: the prefix list of the input_texts list
            sliding_window: sliding_window,the max token length for the model input(max_sequence_length)
            tokenizer: tokenizer
            stride: stride,(1-stride)*sliding_window for overlapping

        Returns:
            split_ids, split_prefixes, split_input_texts
        """
        assert len(input_texts) == len(prefixes)  # every input_text corresponds a prefix
        input_texts_ids = range(len(input_texts))

        split_ids = []
        split_prefixes = []
        split_input_texts = []

        if not tokenizer:
            try:
                from transformers.models.t5 import T5Tokenizer
                tokenizer = T5Tokenizer.from_pretrained("google/mt5-base")
            except Exception:
                print('no tokenizer....')

        for i_t_d, p, i_t in zip(input_texts_ids, prefixes, input_texts):
            split_input_text = NerT5._split_text_with_sliding_window(i_t, sliding_window, tokenizer, stride)
            for t_i_t in split_input_text:
                split_ids.append(i_t_d)
                split_input_texts.append(t_i_t)
                split_prefixes.append(p)
        return split_ids, split_prefixes, split_input_texts  # type:tuple[list[int],list[str],list[str]]

    @staticmethod
    def _combine_pred_target_texts_by_ids(pred_target_texts, split_ids, delimiter: str = '|') -> list:
        """combine truncated_predicted_target_texts split_ids

        Args:
            pred_target_texts: the result of predicting the truncated input_texts
            split_ids: get the truncated_ids when truncating input_texts
            delimiter: the delimiter in target_text to split different entities

        Returns:
            pred_target_texts: predicted target_texts
        """
        ids_target_text_dict = dict()
        for i, j in zip(split_ids, pred_target_texts):
            if not ids_target_text_dict.get(i):
                ids_target_text_dict[i] = delimiter + j + delimiter
            else:
                ids_target_text_dict[i] = ids_target_text_dict[i] + j + delimiter

        pred_target_texts = [ids_target_text_dict[k] for k in sorted(ids_target_text_dict.keys())]
        return pred_target_texts  # type:list

    @staticmethod
    def _revise_target_texts(target_texts: list, input_texts: list, check_in_input_text: bool = False, delimiter='|'):
        """revise the target texts,

        Args:
            target_texts: the list of the target_texts
            input_texts:  the list of the input_texts
            check_in_input_text: if check the entities in input_text
            delimiter: the delimiter in target_text to split different entities

        Returns:
            revised_target_texts = list[set]
        """
        revised_target_texts = [NerT5._revise_target_text(t_t, return_format='set', delimiter=delimiter) for
                                t_t in target_texts]  # type:list[set,...]
        if check_in_input_text:
            revised_target_texts = NerT5._keep_entities_in_input_text(input_texts, revised_target_texts)
        return revised_target_texts  # type:list[set]

    @staticmethod
    def _revise_target_text(target_text: str, delimiter: str = '|', return_format='set'):
        """ revise the target text

        Args:
            target_text: str, target_text
            return_format: 'set' means:'every entity is an element in a set', 'str' means: different entities are split
                            by the delimiter
            delimiter: the delimiter in target_text to split different entities

        Returns:
            revised_target_text : set or list
        """
        assert isinstance(target_text, str)
        target_text = target_text.split(delimiter)
        target_text = set([' '.join(e.strip().split()) for e in target_text])
        if '' in target_text:
            target_text.remove('')
        if return_format == 'set':
            revised_target_text = target_text
        elif return_format == 'list':
            revised_target_text = list(target_text)
        else:  # return_format == 'str'
            revised_target_text = '|'
            if target_text != set():
                for entity in list(target_text):
                    revised_target_text += (str(entity) + '|')
        return revised_target_text

    @staticmethod
    def _keep_entities_in_input_text(input_texts: list, target_texts: list):
        """for each sample, for every entity ,keep the entities that are in the input text,and remove other entities

        Args:
            input_texts: the list of many input_text,and every input text is a string
            target_texts: the list of many target_text,and evert target text is a set

        Returns:
            revise_target_texts: list[str]
        """
        revised_target_texts = []
        for input_text, target_text in zip(input_texts, target_texts):
            if target_text != set():
                elements = list(target_text)
                for e in elements:
                    if str(e) not in input_text:
                        target_text.remove(e)  # type:set
            revised_target_texts.append(target_text)
        return revised_target_texts  # type:list[set]


if __name__ == '__main__':
    from zyl_utils import get_best_cuda_device


    class M(NerT5):
        def __init__(self):
            super(M, self).__init__()
            self.wandb_proj = 'test'
            self.save_dir = './'
            self.model_type = 'mt5'  # t5
            self.use_cuda = True
            self.cuda_device = get_best_cuda_device()

        def train_sample(self):
            train_file = './test.xlsx'
            eval_file = './test.xlsx'
            train_df = pd.read_excel(train_file)  # type:pd.DataFrame
            eval_df = pd.read_excel(eval_file)  # type:pd.DataFrame

            self.model_version = 'v0.0.0.0'
            self.pretrained_model = 'google/mt5-base'  # 预训练模型位置 model_name

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
            self.train(train_df, eval_df, sliding_window=True,
                       wandb_log={'train_file': train_file, 'eval_file': eval_file})

        def eval_sample(self):
            eval_file = './test.xlsx'
            eval_data = pd.read_excel(eval_file)

            self.model_version = 'erv0.0.0.0'
            self.model_args = self.my_config()
            self.model_args.update(
                {
                    'eval_batch_size': 16,
                    # 'best_model_dir':'./'
                }
            )
            self.eval(eval_data, check_in_input_text=False, delimiter='|',
                      tokenizer=None, use_sliding_window=False)
