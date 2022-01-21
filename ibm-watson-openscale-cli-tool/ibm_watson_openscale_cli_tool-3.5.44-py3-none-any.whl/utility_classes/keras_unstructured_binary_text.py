# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from numpy import zeros


def read_lines(file_location):
    train_lines = []
    with open(file_location) as f:
        for line in f.readlines():
            train_lines.append(line)
    return train_lines


def split_lines(lines):
    data = []
    labels = []
    for line in lines:
        label_part, data_part = line.split(',')
        data.append(data_part)
        labels.append(label_part)
    return data, labels


def vectorize_sequences(sequences, dimension=4000):
    results = zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.
    return results


def vectorize_labels(labels):
    results = zeros(len(labels))
    for i, label in enumerate(labels):
        if label.lower() == 'spam':
            results[i] = 1
    return results


def format_scoring_input(lines_list, tokenizer):
    tokenized_messages = tokenizer.texts_to_sequences(lines_list)
    vectorized_messages = vectorize_sequences(tokenized_messages)
    return vectorized_messages.tolist()
