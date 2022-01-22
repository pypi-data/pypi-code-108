# -*- coding: utf-8 -*-
# file: augment_lib.py
# time: 2021/12/20
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import random

import tqdm

from findfile import find_cwd_files, find_cwd_dirs

from pyabsa import APCCheckpointManager

import os

from findfile import find_files, find_dir
from termcolor import colored

from pyabsa.functional.dataset import DatasetItem
from pyabsa.functional.dataset.dataset_manager import download_datasets_from_github, ABSADatasetList


def nlpaug_augment(dataset: DatasetItem):
    for f in find_cwd_files('.augment'):
        os.remove(f)
    import nlpaug.augmenter.word as naw

    checkpoint = max(find_cwd_dirs('fast_lcf_bert_{}'.format(dataset.dataset_name)))
    sent_classifier = APCCheckpointManager.get_sentiment_classifier(checkpoint=checkpoint,
                                                                    auto_device=True,  # Use CUDA if available
                                                                    )

    augmenter = naw.ContextualWordEmbsAug(
        # model_path='microsoft/deberta-v3-base', action="insert")
        model_path='roberta-base', action="substitute", device='cuda')
    dataset_files = detect_dataset(dataset, 'apc')
    valid_sets = dataset_files['valid']

    for valid_set in valid_sets:
        if '.augment' in valid_set:
            continue
        print('processing {}'.format(valid_set))
        augmentations = []
        fin = open(valid_set, encoding='utf8', mode='r', newline='\r\n')
        lines = fin.readlines()
        fin.close()
        for i in tqdm.tqdm(range(0, len(lines), 3), postfix='Augmenting...'):
            try:
                lines[i] = lines[i].strip()
                lines[i + 1] = lines[i + 1].strip()
                lines[i + 2] = lines[i + 2].strip()

                augs = augmenter.augment(lines[i].replace('$T$', '%%'), n=10, num_thread=os.cpu_count())

                for text in augs:
                    if '$ * $' in text:
                        _text = text.replace('$ * $', '[ASP]{}[ASP] '.format(lines[i + 1]), 1) + ' !sent! {}'.format(lines[i + 2])
                    elif '$*$' in text:
                        _text = text.replace('$*$', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    elif '$-$' in text:
                        _text = text.replace('$-$', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    elif '%%' in text:
                        _text = text.replace('%%', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    else:
                        continue
                    results = sent_classifier.infer(_text, print_result=False)
                    # if results[0]['ref_check'][0] != 'Correct':
                    if results[0]['ref_check'][0] != 'Correct' and results[0]['confidence'][0] > 0.9:
                        augmentations.extend(
                            [text.replace('%%', '$T$').replace('$*$', '$T$').replace('$-$', '$T$').replace('$ * $', '$T$'), lines[i + 1], lines[i + 2]]
                        )
                augmentations.extend(
                    [lines[i].replace('%%', '$T$').replace('$*$', '$T$').replace('$-$', '$T$').replace('$ * $', '$T$'), lines[i + 1], lines[i + 2]]
                )
            except Exception as e:
                print('Exception:{}, {}'.format(e, lines[i]))

        fout = open(valid_set.replace('Valid', 'train').replace('valid', 'train') + '.augment', encoding='utf8', mode='w')

        for line in augmentations:
            fout.write(line + '\n')
        fout.close()
    del sent_classifier
    del augmenter


def text_attack_augment(dataset: DatasetItem):
    for f in find_cwd_files('.augment'):
        os.remove(f)
    from textattack.augmentation import EasyDataAugmenter as Aug
    # Alter default values if desired
    augmenter = Aug(pct_words_to_swap=0.3, transformations_per_example=10)

    checkpoint = max(find_cwd_dirs('fast_lcf_bert_{}'.format(dataset.dataset_name)))
    sent_classifier = APCCheckpointManager.get_sentiment_classifier(checkpoint=checkpoint,
                                                                    auto_device=True,  # Use CUDA if available
                                                                    )

    dataset_files = detect_dataset(dataset, 'apc')
    valid_sets = dataset_files['valid']

    for valid_set in valid_sets:
        if '.augment' in valid_set:
            continue
        print('processing {}'.format(valid_set))
        augmentations = []
        fin = open(valid_set, encoding='utf8', mode='r', newline='\r\n')
        lines = fin.readlines()
        fin.close()
        for i in tqdm.tqdm(range(0, len(lines), 3), postfix='Augmenting...'):
            try:
                lines[i] = lines[i].strip()
                lines[i + 1] = lines[i + 1].strip()
                lines[i + 2] = lines[i + 2].strip()

                augs = augmenter.augment(lines[i].replace('$T$', '%%'))

                for text in augs:
                    if '$ * $' in text:
                        _text = text.replace('$ * $', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    elif '$*$' in text:
                        _text = text.replace('$*$', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    elif '$-$' in text:
                        _text = text.replace('$-$', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    elif '%%' in text:
                        _text = text.replace('%%', '[ASP]{}[ASP] '.format(lines[i + 1])) + ' !sent! {}'.format(lines[i + 2])
                    else:
                        continue
                    results = sent_classifier.infer(_text, print_result=False)
                    # if results[0]['ref_check'][0] != 'Correct':
                    if results[0]['ref_check'][0] != 'Correct' and results[0]['confidence'][0] > 0.9:
                        augmentations.extend(
                            [text.replace('%%', '$T$').replace('$*$', '$T$').replace('$-$', '$T$').replace('$ * $', '$T$'), lines[i + 1], lines[i + 2]]
                        )
                augmentations.extend(
                    [lines[i].replace('%%', '$T$').replace('$*$', '$T$').replace('$-$', '$T$').replace('$ * $', '$T$'), lines[i + 1], lines[i + 2]]
                )
            except Exception as e:
                print('Exception:{}, {}'.format(e, lines[i]))

        fout = open(valid_set.replace('Valid', 'train').replace('valid', 'train') + '.augment', encoding='utf8', mode='w')

        for line in augmentations:
            fout.write(line + '\n')
        fout.close()
    del sent_classifier
    del augmenter


def detect_dataset(dataset_path, task='apc'):
    filter_key_words = ['.py', '.ignore', '.md', 'readme', 'log', 'result', 'zip', '.state_dict', '.model', '.png']

    if not isinstance(dataset_path, DatasetItem):
        dataset_path = DatasetItem(dataset_path)
    dataset_file = {'train': [], 'test': [], 'valid': []}
    for d in dataset_path:
        if not os.path.exists(d) or hasattr(ABSADatasetList, d):
            print('{} dataset is loading from: {}'.format(d, 'https://github.com/yangheng95/ABSADatasets'))
            download_datasets_from_github(os.getcwd())
            search_path = find_dir(os.getcwd(), [d, task], exclude_key=['infer', 'test.'] + filter_key_words, disable_alert=False)
            dataset_file['train'] += find_files(search_path, [d, 'train', task], exclude_key=['.inference', 'test.'] + filter_key_words)
            dataset_file['test'] += find_files(search_path, [d, 'test', task], exclude_key=['inference', 'train.'] + filter_key_words)
            dataset_file['valid'] += find_files(search_path, [d, 'valid', task], exclude_key=['inference', 'train.'] + filter_key_words)
        else:
            dataset_file['train'] = find_files(d, ['train', task], exclude_key=['.inference', 'test.'] + filter_key_words)
            dataset_file['test'] = find_files(d, ['test', task], exclude_key=['.inference', 'train.'] + filter_key_words)
            dataset_file['valid'] = find_files(d, ['valid', task], exclude_key=['.inference', 'train.'] + filter_key_words)

    if len(dataset_file['train']) == 0:
        raise RuntimeError('{} is not an integrated dataset or not downloaded automatically,'
                           ' and it is not a path containing train/test datasets!'.format(dataset_path))
    if len(dataset_file['test']) == 0:
        print('Warning, auto_evaluate=True, however cannot find test set using for evaluating!')

    if len(dataset_path) > 1:
        print(colored('Never mixing datasets with different sentiment labels for training & inference !', 'yellow'))

    return dataset_file


# if __name__ == '__main__':
#     datasets = [ABSADatasetList.SemEval, ABSADatasetList.Restaurant15]
#     for dataset in datasets:
#         for dataset_file in detect_dataset(dataset, 'apc')['train']:
#             if '.augment' in dataset_file:
#                 continue
#             print('processing {}'.format(dataset_file))
#             data = []
#             fin = open(dataset_file, encoding='utf8', mode='r', newline='\r\n')
#             lines = fin.readlines()
#             fin.close()
#             for i in tqdm.tqdm(range(0, len(lines), 3)):
#                 lines[i] = lines[i].strip()
#                 lines[i + 1] = lines[i + 1].strip()
#                 lines[i + 2] = lines[i + 2].strip()
#
#                 data.append([lines[i], lines[i + 1], lines[i + 2]])
#
#             fout1 = open(dataset_file, encoding='utf8', mode='w')
#             fout2 = open(dataset_file.replace('train', 'valid').replace('Train', 'valid'), encoding='utf8', mode='w')
#
#             # random.shuffle(data)
#
#             set1 = data[:len(data) // 4]
#             set2 = data[len(data) // 4:]
#
#             for case in set1:
#                 for line in case:
#                     fout1.write(line + '\n')
#
#             for case in set2:
#                 for line in case:
#                     fout2.write(line + '\n')
