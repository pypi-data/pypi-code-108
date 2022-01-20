# encoding: utf-8
'''
@author: zyl
@file: entry_match.py
@time: 2021/11/11 9:58
@desc:
'''

pass
# ##################################################################
# @staticmethod
# def eval_entry_match(model, eval_df: pd.DataFrame, my_dict, delimiter='|', use_dict_match=True,
#                      pos_neg_ratio=None, keep_entry_in_dict=True, use_multi_gpus=None):
#     prefixes = eval_df['prefix'].tolist()
#     input_texts = eval_df['input_text'].tolist()
#     target_texts = eval_df['target_text'].tolist()
#
#     revised_target_texts = NERUtils.em_revise_target_texts(prefixes=prefixes, target_texts=target_texts,
#                                                            prefix_dict=my_dict.prefix_dict,
#                                                            delimiter=delimiter,
#                                                            keep_entry_in_dict=keep_entry_in_dict)
#
#     pred_target_texts = NERUtils.predict_entry_match(em_model=model, prefix_match_dict=my_dict.prefix_match_dict,
#                                                      prefixes=prefixes, input_texts=input_texts,
#                                                      use_multi_gpus=use_multi_gpus,
#                                                      use_dict_match=use_dict_match)
#
#     revised_pred_target_texts = NERUtils.em_revise_target_texts(prefixes=prefixes, target_texts=pred_target_texts,
#                                                                 prefix_dict=my_dict.prefix_dict,
#                                                                 delimiter=delimiter,
#                                                                 keep_entry_in_dict=keep_entry_in_dict)
#
#     eval_df['true_target_text'] = revised_target_texts
#     eval_df['pred_target_text'] = revised_pred_target_texts
#
#     eval_res = {}
#     for prefix in set(prefixes):
#         prefix_df = eval_df[eval_df['prefix'] == prefix]
#         y_true = prefix_df['true_target_text'].tolist()
#         y_pred = prefix_df['pred_target_text'].tolist()
#         print(f'{prefix} report:')
#         res_df = NERUtils.entity_recognition_v2(y_true, y_pred, pos_neg_ratio=pos_neg_ratio)
#         eval_res[prefix] = res_df
#
#     print(f'sum report:')
#     res_df = NERUtils.entity_recognition_v2(revised_target_texts, revised_pred_target_texts,
#                                             pos_neg_ratio=pos_neg_ratio)
#     eval_res['sum'] = res_df
#     return eval_res
#
#
# @staticmethod
# def predict_entry_match(em_model, prefix_match_dict, prefixes: list, input_texts: list, use_dict_match=True,
#                         use_multi_gpus=None):
#     if len(input_texts) == 1:
#         use_multi_gpus = None
#     if use_dict_match:
#         pred_by_dict = []
#         for p, i in zip(prefixes, input_texts):
#             pred_by_dict.append(
#                 NERUtils.predict_entry_match_by_dict_match(str(i).strip(), dictionary=prefix_match_dict.get(p),
#                                                            use_edit_distance=False))
#
#             # i = i.lower()  # modify
#
#             # if p == 'disease_em':
#             #     pred_by_dict.append(
#             #         NERUtils.predict_entry_match_by_dict_match(i, dictionary=di_dict, use_edit_distance=False))
#             # else:
#             #     pred_by_dict.append(
#             #         NERUtils.predict_entry_match_by_dict_match(i, dictionary=tar_dict, use_edit_distance=False))
#     else:
#         pred_by_dict = [None] * len(input_texts)
#
#     to_predict_texts = [i + ': ' + j for i, j in zip(prefixes, input_texts)]
#     if not use_multi_gpus:
#         pred_by_model = em_model.predict(to_predict_texts)
#     else:
#         pred_by_model = em_model.predict_gpu(to_predict_texts, gpus=use_multi_gpus)
#     # pred_by_model = em_model.predict(to_predict_texts)
#     assert len(pred_by_model) == len(pred_by_dict)
#     pred_target_texts = [d if d else m for d, m in zip(pred_by_dict, pred_by_model)]
#     return pred_target_texts
#
#
# @staticmethod
# def predict_entry_match_by_dict_match(input_text: str, dictionary: dict, use_edit_distance: bool = False):
#     """predict the entry of a string by using dictionary match
#
#     Args:
#         input_text: a string
#         dictionary: the dict, {entity:entry}
#         use_edit_distance: True or False
#
#     Returns:
#         None or entry(str)
#     """
#     entry = dictionary.get(input_text)
#     if not entry:
#         if use_edit_distance:
#             import Levenshtein
#             max_score = 0
#             for every_entity in dictionary.keys():
#                 score = Levenshtein.ratio(every_entity, input_text)
#                 if score >= max_score and score > 0.80:  # 42-->43-->52
#                     max_score = score
#                 entry = dictionary.get(every_entity)
#     return entry  # None or entry
#
#
# @staticmethod
# def em_revise_target_texts(prefixes, target_texts, prefix_dict, delimiter='|', keep_entry_in_dict=False):
#     revised_target_texts = [NERUtils.revise_target_text(t_t, return_format='set', delimiter=delimiter) for
#                             t_t in target_texts]  # type:list[set,...]
#
#     if keep_entry_in_dict:
#         result = []
#         for p, r_t_t in zip(prefixes, revised_target_texts):
#             res = set()
#             if r_t_t:
#                 for j in list(r_t_t):
#                     if j in prefix_dict.get(p):
#                         res.add(j)
#             result.append(res)
#         return result
#     return revised_target_texts  # type:list[set]


    # @staticmethod
    # def eval_by_auto_batch_size(job, eval_df, initial_eval_batch_size=600):
    #     """
    #
    #     Args:
    #         job: you function. if run error, return None.
    #         eval_df: eval dataframe
    #         initial_eval_batch_size:
    #
    #     Returns:
    #
    #     """
    #     eval_batch_size = initial_eval_batch_size
    #     q = mp.Queue()
    #     pl = {'eval_batch_size': eval_batch_size}
    #     res = None
    #     while not res:
    #         eval_batch_size = int(eval_batch_size * 0.8)
    #         print(f'try eval_batch_size: {eval_batch_size}')
    #         pl['eval_batch_size'] = eval_batch_size
    #         eval_process = mp.Process(target=job, args=(pl, q, eval_df,))
    #         eval_process.start()
    #         eval_process.join()
    #         res = q.get()
    #         print(res)
    #
    # @staticmethod
    # def eval_by_different_parameters(job, parameter_cfg: dict, eval_df):
    #     q = mp.Queue()
    #     parameters_list = NERUtils.get_parameters_list(parameter_cfg)
    #     for pl in parameters_list:
    #         eval_process = mp.Process(target=job, args=(pl, q, eval_df,))
    #         eval_process.start()
    #         eval_process.join()
    #         print(q.get())
    #
    # @staticmethod
    # def get_parameters_list(parameter_cfg: dict):
    #     """
    #
    #     Args:
    #         parameter_cfg: like:{'truncating_size': [100,10], 'overlapping_size': [10],'max_seq_length':[100,30]}
    #
    #     Returns:[{'truncating_size': 100, 'overlapping_size': 10, 'max_seq_length': 100}, {'truncating_size': 100,
    #               'overlapping_size': 10, 'max_seq_length': 30}, {'truncating_size': 10, 'overlapping_size': 10,
    #               'max_seq_length': 100}, {'truncating_size': 10, 'overlapping_size': 10, 'max_seq_length': 30}]
    #
    #     """
    #     parameters_list = []
    #     keys = []
    #     values = []
    #     for i, j in parameter_cfg.items():
    #         keys.append(i)
    #         values.append(j)
    #     for para in product(*values):  # 求多个可迭代对象的笛卡尔积
    #         cfg = dict(zip(keys, para))
    #         parameters_list.append(cfg)
    #     return parameters_list  # type:list

    # @staticmethod
    # def cut_entities(input_entities: list, prefixes: list):
    #     assert len(input_entities) == len(prefixes)  # a input_text corresponds a prefix
    #     input_texts_ids = range(len(input_entities))
    #
    #     cut_ids = []
    #     cut_input_entities = []
    #     cut_prefixes = []

    #     for id, i_e, p in zip(input_texts_ids, input_entities, prefixes):
    #         if not isinstance(i_e, set):
    #             cut_i_e = NERUtils.revise_target_text(target_text=i_e, return_format='set', delimiter='|')
    #         else:
    #             cut_i_e = i_e
    #         if cut_i_e != set():
    #             for c_i_t in cut_i_e:
    #                 cut_ids.append(id)
    #                 cut_input_entities.append(c_i_t)
    #                 cut_prefixes.append(p)
    #     return cut_ids, cut_input_entities, cut_prefixes  # type:list
    #
    # @staticmethod
    # def combine_cut_entities(input_entities: list, cut_entities: list, cut_ids: list):
    #     dic = dict()
    #     for i, j in zip(cut_ids, cut_entities):
    #         if i not in dic.keys():
    #             dic[i] = j
    #         else:
    #             if isinstance(j, str):
    #                 dic[i] = dic[i] + '|' + j
    #             else:
    #                 dic[i].update(j)
    #
    #     res = []
    #     all_keys = list(dic.keys())
    #     for i in range(len(input_entities)):
    #         if i in all_keys:
    #             res.append(dic[i])
    #         else:
    #             res.append(set())
    #     return res
###################################
# eval_entry_match
#       em_revise_target_texts
#       predict_entry_match
#               predict_entry_match_by_dict_match
#               model.predict_gpu
#