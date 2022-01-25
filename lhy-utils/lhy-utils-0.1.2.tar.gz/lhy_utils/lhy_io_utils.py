# coding: utf-8
import json
import sys
import pickle as pkl


def get_bert_path(model_name):
    system = sys.platform
    system = system.lower()
    if "linux" in system:
        bert_base = "/opt/models/bert/"
    elif "darwin" in system:
        bert_base = "/Users/lhy/Documents/bert_saved/"
    else:
        raise ValueError
    config_path = f'{bert_base}/{model_name}/bert_config.json'
    checkpoint_path = f'{bert_base}/{model_name}/bert_model.ckpt'
    dict_path = f'{bert_base}/{model_name}/vocab.txt'
    return config_path, checkpoint_path, dict_path


def read_json(j_path):
    with open(j_path, "r", encoding="utf-8") as fr:
        return json.load(fr)


def read_json_line(j_path):
    with open(j_path, "r", encoding="utf-8") as fr:
        return [json.loads(i.strip()) for i in fr.readlines()]


def write_json(j_data, j_path):
    with open(j_path, "w", encoding="utf-8") as fw:
        json.dump(j_data, fw, ensure_ascii=False, indent=4)


def write_json_line(j_data, j_path):
    with open(j_path, "w", encoding="utf-8") as fw:
        for data in j_data:
            fw.write(json.dumps(data, ensure_ascii=False) + "\n")


def save_pkl(obj, pkl_path):
    with open(pkl_path, "wb") as fwb:
        pkl.dump(obj, fwb)


def load_pkl(pkl_path):
    with open(pkl_path, "rb") as frb:
        return pkl.load(frb)
