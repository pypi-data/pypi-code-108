import torch
import numpy as np
import torch.nn as nn
def extract_hidden_ordered(model, data_train,  feature_size, alpha, device):
    feature_size = feature_size*2
    train_length = len(data_train.dataset)
    hidden_train_tmp = torch.empty((train_length, feature_size)).to(device)
    label_train_semi = np.zeros(train_length, dtype=int)
    label_list_train = np.zeros(train_length, dtype=int)
    if alpha!=0:
        softmax = nn.Softmax(dim=1)
        mi = torch.empty(train_length).to(device)
        pre_label_list = torch.zeros(train_length).to(device)

    for ith, (ith_data, seq_len, label, semi, index) in enumerate(data_train):
        input_tensor = ith_data.to(device)
        # label_list_train = label_list_train + label
        if alpha == 0:
            # print(input_tensor.size(), len(seq_len))
            en_hi, de_out = model(input_tensor, seq_len)
            cla_pre = None
        else:
            en_hi, de_out, cla_pre = model(input_tensor, seq_len)
            cla_prob = softmax(cla_pre).detach()
            cla = torch.argmax(cla_prob, dim=-1)+1.0
            cla_prob = torch.sort(cla_prob, dim=-1)[0]

            mi[index] = cla_prob[:,-1] - cla_prob[:,-2]
            pre_label_list[index] = cla*1.0

        label_list_train[index] = np.asarray(label)
        label_train_semi[index] = semi
        hidden_train_tmp[index, :] = en_hi[0, :, :].detach()
    if device == 'cuda':
        hidden_train_tmp = hidden_train_tmp.cpu().numpy()
        if alpha != 0:
            pre_label_list = pre_label_list.cpu().numpy()
            mi = mi.cpu().numpy()
    label_list_train = label_list_train.tolist()

    if alpha == 0:
        return hidden_train_tmp,  label_list_train,  label_train_semi
    else:
        return hidden_train_tmp,  label_list_train,  label_train_semi, pre_label_list, mi

# def test_extract_hidden_iter(model, data_train, feature_size, alpha, device):
#     # feature_size = data_train.dataset.data[0].shape[1]
#     train_length = len(data_train.dataset)
#     # hidden_train_tmp = torch.empty((repeat*train_length, feature_size)).to(device)
#     label_train_semi = np.zeros(train_length, dtype=int)
#     label_train_iter = np.zeros(train_length, dtype=int)
#
#     label_list_train = np.zeros((train_length), dtype=int)
#
#     hidden_train_tmp = torch.empty(( train_length, feature_size*2)).to(device)
#
#     # hidden_array_train = np.zeros((repeat*train_length, feature_size))
#
#
#     start = train_length
#     for ith, (ith_data, seq_len, label, semi, index) in enumerate(data_train):
#
#
#         input_tensor = ith_data.to(device)
#         # label_list_train = label_list_train + label
#
#         step = ith_data.shape[0]
#         if alpha == 0:
#
#             en_hi, de_out = model(input_tensor, seq_len)
#             cla_pre = None
#         else:
#             tmp = model(input_tensor, seq_len)
#             en_hi = tmp[0]
#
#         label_list_train[start:start + step] = np.asarray(label)
#         label_train_semi[start:start + step] = semi
#         label_train_iter[start:start + step] = index
#         hidden_train_tmp[start:start + step, :] = en_hi[0, :, :].detach()
#         start = start + step
#     if device== 'cuda':
#         hidden_train_tmp = hidden_train_tmp.cpu()
#
#     return hidden_train_tmp.numpy(), label_list_train.tolist(), label_train_semi, label_train_iter
#
# class test_extract_hidden_semi2():
#     def __init__(self, model, data_train, hidden_size, alpha, device):
#
#         feature_size = hidden_size*2
#         repeat = 1
#         train_length = len(data_train.dataset)
#
#         self.hidden_train_tmp = torch.empty((repeat * train_length, feature_size)).to(device)
#         self.label_train_semi = np.zeros(repeat * train_length, dtype=int)
#         self.mi = torch.zeros(train_length).to(device)
#
#
#         self.label_list_train = np.zeros((repeat * train_length), dtype=int)
#         if alpha!=0:
#             import torch.nn as nn
#             softmax = nn.Softmax(dim=1)
#             self.pre_label_list = torch.zeros((repeat*train_length), dtype=int).to(device)
#             self.mi = torch.zeros( train_length, dtype=int).to(device)
#
#         for isample in range(repeat):
#             start = train_length * isample
#             for ith, (ith_data, seq_len, label, semi, index) in enumerate(data_train):
#                 input_tensor = ith_data.to(device)
#                 # label_list_train = label_list_train + label
#
#                 step = ith_data.shape[0]
#                 if alpha == 0:
#                     # print(input_tensor.size(), len(seq_len))
#                     en_hi, de_out = model(input_tensor, seq_len)
#                     cla_pre = None
#                 else:
#                     # cla_pre the logits output of clasifier
#                     # cla_prob the proability of the classification results
#                     # cla the class label predicted by classifier
#                     en_hi, de_out, cla_pre = model(input_tensor, seq_len)
#                     cla_prob = softmax(cla_pre)
#                     cla = torch.argmax(cla_prob, dim=-1)+1
#                     self.pre_label_list[start:start+step] = cla
#                     cla_prob = torch.sort(cla_prob, dim=-1)[0]
#                     self.mi[start:start+step] = cla_prob[:,-1] - cla_prob[:,-2]
#                 self.label_list_train[start:start + step] = np.asarray(label)
#                 self.label_train_semi[start:start + step] = semi
#                 self.hidden_train_tmp[start:start + step, :] = en_hi[0, :, :].detach()
#                 start = start + step
#         if device == 'cuda':
#             self.hidden_train_tmp = self.hidden_train_tmp.cpu().numpy()
#             if alpha!=0:
#                 self.pre_label_list = self.pre_label_list.cpu().numpy()
#         self.label_list_train = self.label_list_train.tolist()
#         self.mi = self.mi.cpu().numpy()
