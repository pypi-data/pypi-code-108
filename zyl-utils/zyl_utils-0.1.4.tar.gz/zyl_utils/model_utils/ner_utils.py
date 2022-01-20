# encoding: utf-8
"""
@author: zyl
@file: ner_utils.py
@time: 2021/9/14 14:03
@desc: ner utils for simple-transformer mt5 model, eval and predict
"""
import pandas as pd


class NERUtils:
    # ner utils for mt5 model
    def __init__(self):
        # eval_entity_recognition  ------评估
        #       revise_target_texts。
        #               revise_target_text
        #               keep_entities_in_input_text
        #       predict_entity_recognition-------预测
        #               split_texts_with_sliding_window
        #               model.predict_gpu
        #               combine_pred_target_texts_by_ids
        #       revise_target_texts
        #               revise_target_text
        #               keep_entities_in_input_text
        #       entity_recognition_v2-----标准
        pass

    @staticmethod
    def eval_entity_recognition(model, eval_df: pd.DataFrame, check_in_input_text: bool, delimiter='|', tokenizer=None,
                                use_sliding_window=False, sliding_window=512, stride=0.8, pos_neg_ratio=None,
                                use_multi_gpus=None, self_metric=False):
        """eval entity recognition in mt5 model, version-v2 , reference: https://docs.qq.com/doc/DYXRYQU1YbkVvT3V2

        Args:
            model: a mt5 model
            eval_df: a pd.Dataframe , must have columns ['prefix','input_text','target_text']
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

        prefixes = eval_df['prefix'].to_list()
        input_texts = eval_df['input_text'].tolist()
        target_texts = eval_df['target_text'].tolist()
        revised_target_texts = NERUtils.revise_target_texts(target_texts=target_texts,
                                                            input_texts=input_texts, delimiter=delimiter,
                                                            check_in_input_text=check_in_input_text)

        pred_target_texts = NERUtils.predict_entity_recognition(model, prefixes, input_texts, tokenizer=tokenizer,
                                                                use_sliding_window=use_sliding_window,
                                                                sliding_window=sliding_window, stride=stride,
                                                                delimiter=delimiter, use_multi_gpus=use_multi_gpus)

        revised_pred_target_texts = NERUtils.revise_target_texts(target_texts=pred_target_texts,
                                                                 input_texts=input_texts, delimiter=delimiter,
                                                                 check_in_input_text=check_in_input_text)

        eval_df['true_target_text'] = revised_target_texts
        eval_df['pred_target_text'] = revised_pred_target_texts

        eval_res = {}
        for prefix in set(prefixes):
            prefix_df = eval_df[eval_df['prefix'] == prefix]
            y_true = prefix_df['true_target_text'].tolist()
            y_pred = prefix_df['pred_target_text'].tolist()
            print(f'{prefix} report:')
            res_df = NERUtils.entity_recognition_v2(y_true, y_pred, pos_neg_ratio=pos_neg_ratio,
                                                    self_metric=self_metric)
            eval_res[prefix] = res_df

        print(f'sum report:')
        res_df = NERUtils.entity_recognition_v2(revised_target_texts, revised_pred_target_texts,
                                                pos_neg_ratio=pos_neg_ratio, self_metric=self_metric)
        eval_res['sum'] = res_df

        return eval_res  # {prefix:res_df},type:dict

    @staticmethod
    def predict_entity_recognition(model, prefixes: list, input_texts: list, use_sliding_window=False,
                                   sliding_window=512, stride=0.8, tokenizer=None,
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
        if len(input_texts) == 1:
            use_multi_gpus = None
        assert len(prefixes) == len(input_texts)

        if use_sliding_window:
            t_ids, t_prefixes, t_input_texts = NERUtils.split_texts_with_sliding_window(input_texts, prefixes,
                                                                                        tokenizer=tokenizer,
                                                                                        sliding_window=sliding_window,
                                                                                        stride=stride)

            to_predict_texts = [i + ': ' + j for i, j in zip(t_prefixes, t_input_texts)]

            if not use_multi_gpus:
                pred_target_texts = model.predict(to_predict_texts)
            else:
                pred_target_texts = model.predict_gpu(to_predict_texts, gpus=use_multi_gpus)

            pred_target_texts = NERUtils.combine_pred_target_texts_by_ids(pred_target_texts, t_ids, delimiter)
        else:
            to_predict_texts = [i + ': ' + j for i, j in zip(prefixes, input_texts)]
            if not use_multi_gpus:
                pred_target_texts = model.predict(to_predict_texts)
            else:
                pred_target_texts = model.predict_gpu(to_predict_texts, gpus=use_multi_gpus)
        assert len(pred_target_texts) == len(input_texts)
        return pred_target_texts  # type:list[str]

    @staticmethod
    def split_text_with_sliding_window(text: str, sliding_window=128, tokenizer=None, stride=0.8) -> list:
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

        if not isinstance(text, str):
            text = str(text)

        if not tokenizer:
            try:
                from transformers.models.t5 import T5Tokenizer
                tokenizer = T5Tokenizer.from_pretrained("mt5-base")
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
    def split_texts_with_sliding_window(input_texts: list, prefixes: list, tokenizer=None,
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
                tokenizer = T5Tokenizer.from_pretrained("mt5-base")
            except Exception:
                print('no tokenizer....')

        for i_t_d, p, i_t in zip(input_texts_ids, prefixes, input_texts):
            split_input_text = NERUtils.split_text_with_sliding_window(i_t, sliding_window, tokenizer, stride)
            for t_i_t in split_input_text:
                split_ids.append(i_t_d)
                split_input_texts.append(t_i_t)
                split_prefixes.append(p)
        return split_ids, split_prefixes, split_input_texts  # type:tuple[list[int],list[str],list[str]]

    @staticmethod
    def combine_pred_target_texts_by_ids(pred_target_texts, split_ids, delimiter: str = '|') -> list:
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
    def revise_target_texts(target_texts: list, input_texts: list, check_in_input_text: bool = False, delimiter='|'):
        """revise the target texts,

        Args:
            target_texts: the list of the target_texts
            input_texts:  the list of the input_texts
            check_in_input_text: if check the entities in input_text
            delimiter: the delimiter in target_text to split different entities

        Returns:
            revised_target_texts = list[set]
        """
        revised_target_texts = [NERUtils.revise_target_text(t_t, return_format='set', delimiter=delimiter) for
                                t_t in target_texts]  # type:list[set,...]
        if check_in_input_text:
            revised_target_texts = NERUtils.keep_entities_in_input_text(input_texts, revised_target_texts)
        return revised_target_texts  # type:list[set]

    @staticmethod
    def revise_target_text(target_text: str, delimiter: str = '|', return_format='set'):
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
    def keep_entities_in_input_text(input_texts: list, target_texts: list):
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

    @staticmethod
    def entity_recognition_v2(y_true: list, y_pred: list, pos_neg_ratio: str = None, self_metric=False):
        """the metric of entity_recognition, version-v2, reference: https://docs.qq.com/doc/DYXRYQU1YbkVvT3V2

        Args:
            y_true: list[set],the list of true target texts,each element is a set
            y_pred: list[set],the list of pred target texts,each element is a set
            pos_neg_ratio: the ratio of positive and negative sample importance, default: the ratio of positive and
                           negative sample sizes, you can set it,like"7:3"
            self_metric: self_metric

        Returns:
            show report and res
        """

        neg_data = 0
        neg_correct_dt = 0
        neg_wrong_dt = 0
        neg_redundant_entities = 0

        pos_data = 0
        pos_correct_dt = 0
        pos_wrong_dt = 0
        pos_correct_entities = 0
        pos_wrong_entities = 0
        pos_omitted_entities = 0
        pos_redundant_entities = 0

        for i, j in zip(y_true, y_pred):
            if i == set():
                neg_data += 1
                if j == set():
                    neg_correct_dt += 1
                else:
                    neg_wrong_dt += 1
                    neg_redundant_entities += len(j)
            else:
                pos_data += 1
                true_pred = len(i & j)
                pos_correct_entities += true_pred

                if i == j:
                    pos_correct_dt += 1
                elif len(i) >= len(j):
                    pos_wrong_dt += 1
                    pos_wrong_entities += (len(j) - true_pred)
                    pos_omitted_entities += (len(i) - len(j))
                else:
                    pos_wrong_dt += 1
                    pos_redundant_entities += (len(j) - len(i))
                    pos_wrong_entities += (len(i) - true_pred)

        all_pos_entities = pos_correct_entities + pos_wrong_entities + pos_omitted_entities + pos_redundant_entities
        if neg_data == 0:
            neg_metric = 0
        else:
            neg_metric = neg_correct_dt / (neg_correct_dt + neg_redundant_entities)
        if pos_data == 0:
            pos_metric = 0
        else:
            pos_metric = pos_correct_entities / all_pos_entities

        sum_metric_micro = (pos_correct_entities + neg_correct_dt) / (
                neg_correct_dt + neg_redundant_entities + all_pos_entities)
        # sum_metric_macro = neg_metric * 0.5 + pos_metric * 0.5

        if pos_neg_ratio:
            pos_all = float(pos_neg_ratio.split(':')[0])
            neg_all = float(pos_neg_ratio.split(':')[1])
            pos_ratio = pos_all / (pos_all + neg_all)
            neg_ratio = neg_all / (pos_all + neg_all)
        else:
            pos_ratio = pos_data / (pos_data + neg_data)
            neg_ratio = neg_data / (pos_data + neg_data)

        sum_metric_weighted = pos_ratio * pos_metric + neg_ratio * neg_metric

        # pos_precision = pos_correct_dt / (neg_correct_dt + pos_correct_dt)
        # recall = pos_correct_dt / pos_data
        tp = pos_correct_dt
        fn = pos_wrong_dt
        fp = neg_wrong_dt
        tn = neg_correct_dt

        accuracy = (tp + tn) / (tp + fn + fp + tn)
        # precision = tp / (tp + fp)
        # recall = tp / (tp + fn)
        # f1 = 2 / (1 / precision + 1 / recall)
        r = {
            'positive data': [str(pos_data), pos_correct_dt, pos_wrong_dt, pos_correct_entities,
                              pos_wrong_entities, pos_omitted_entities, pos_redundant_entities, pos_metric],
            'negative data': [neg_data, neg_correct_dt, neg_wrong_dt, '-', '-', '-', neg_redundant_entities,
                              neg_metric],

            'all data ': [str(pos_data + neg_data), neg_correct_dt + pos_correct_dt, neg_wrong_dt + pos_wrong_dt,
                          pos_correct_entities, pos_wrong_entities, pos_omitted_entities,
                          pos_redundant_entities + neg_redundant_entities,
                          sum_metric_micro],
            # 'precision': ['', '', '', '', '', '', '', precision],
            # 'recall': ['', '', '', '', '', '', '', recall],
            # 'f1 score': ['', '', '', '', '', '', '', (2 * precision * recall) / (precision + recall)],
            # 'accuracy score': ['', '', '', '', '', '', '', (neg_correct_dt + pos_correct_dt) / (pos_data + neg_data)],
            # 'micro score': ['', '', '', '', '', '', '', sum_metric_micro],
            # 'macro score': ['', '', '', '', '', '', '', sum_metric_macro],
            'weighted score': ['', '', '', '', '', '', '', sum_metric_weighted],
        }

        index = ['| data_num', '| correct_data', '| wrong_data', '| correct_entities', '| wrong_entities',
                 '| omitted_entities', '| redundant_entities', '| score']

        res_df = pd.DataFrame(r, index=index).T
        pd.set_option('precision', 4)
        pd.set_option('display.width', None)
        pd.set_option('display.max_columns', None)
        pd.set_option("colheader_justify", "center")
        print(res_df)

        print(
            f"正样本集得分为：{pos_correct_entities} / "
            f"({pos_correct_entities}+{pos_wrong_entities}+{pos_omitted_entities}+"
            f"{pos_redundant_entities}) = {round(pos_metric, 4)}，负样本集得分为：{neg_correct_dt} / ({neg_correct_dt} + "
            f"{neg_redundant_entities})={round(neg_metric, 4)}，",
            f"总体得分为： ({pos_correct_entities} + {neg_correct_dt}) / "
            f"({all_pos_entities}+{neg_correct_dt + neg_redundant_entities})={round(sum_metric_micro, 4)}",
            f"准确率：{accuracy}",
        )
        print('\n')
        if self_metric:
            more_not_error_pos = (pos_correct_entities + pos_redundant_entities) / (
                    pos_correct_entities + pos_wrong_entities + pos_omitted_entities + pos_redundant_entities)
            f"自定义-正样本集得分为：{pos_correct_entities + pos_redundant_entities} /" \
            f" ({pos_correct_entities}+{pos_wrong_entities}+{pos_omitted_entities}+"
            f"{pos_redundant_entities}) = {round(more_not_error_pos, 4)}，负样本集得分为：{round(1, 4)}，"
            print('\n')
        return res_df  # type:pd.DataFrame


if __name__ == '__main__':
    pass
