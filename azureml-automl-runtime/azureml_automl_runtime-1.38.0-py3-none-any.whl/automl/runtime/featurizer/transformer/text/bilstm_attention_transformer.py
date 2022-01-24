# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Bi-LSTM with Attention transformer"""
import copy
import datetime
import logging
import random
from typing import cast, Any, Dict

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TextDnnModelDownloadFailed)
from azureml.automl.core.shared.exceptions import FitException, TransformException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.featurizer.transformer.automltransformer import AutoMLTransformer
from azureml.automl.runtime.featurizer.transformer.data.automl_wordembeddings_provider import AutoMLEmbeddingsProvider
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


_logger = logging.getLogger(__name__)

pkg_dependencies_satisfied = False
try:
    import spacy
    import en_core_web_sm
    import torch
    import torch.nn.functional as func
    from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence
    pkg_dependencies_satisfied = True
except ImportError:
    pass


if pkg_dependencies_satisfied:
    en_tokenize = en_core_web_sm.load()

    class BaseModel(torch.nn.Module):
        def __init__(self, device):
            """
            The base class of the model.

            :param device: str, it can be either 'cpu' or 'gpu'
            """
            super(BaseModel, self).__init__()
            self._device = device

        def get_device_name(self):
            """
            Get device name.

            :return: str. the device name.
            """
            return self._device

        def forward(self, x):
            """
            The base forward method.

            :param x: training data.
            """
            pass

    class EarlyStopping:
        def __init__(self, patience=2, delta=0.0):
            """
            Early stopping is a form of regularization used to avoid over-fitting on the training dataset.
            Early stopping keeps track of the validation loss. If the loss stops decreasing for several epochs
            in a row, the training stops.

            :param patience: How long to wait after last time validation loss improved.
            patience is specified as number of epochs. Default is 2.
            :param delta: Minimum change in the monitored quantity to qualify as an improvement. Default is 0.0.
            """
            self._patience = patience
            self._delta = delta
            self._best_accuracy = 0.0
            self._count = 0

        def check_early_stop_train(self, valid_accuracy):
            """
            Check whether to stop the training process, given the validation accuracy.

            :param valid_accuracy: the accuracy of validation dataset.
            :return: Boolean. True means stop training, False means should continue to train.
            """
            # Already early stopped, so return True.
            if self._count >= self._patience:
                return True

            if valid_accuracy >= self._best_accuracy:
                self._best_accuracy = valid_accuracy
                self._count = 0
            elif valid_accuracy < self._best_accuracy - self._delta:
                self._count += 1
                if self._count >= self._patience:
                    return True

            return False

    class EvalResult:
        def __init__(self):
            """Init of eval result."""
            self._overall_accuracy = 0.0

        def calc(self, target, pred):
            """
            Calculate the accuracy.

            :param target: y.
            :param pred: prediction result.
            :return: the accuracy.
            """
            self._overall_accuracy = accuracy_score(pred, target)

        def __str__(self):
            """
            Represent the result as string.

            :return: string.
            """
            return "The overall accuracy is: {}".format(self._overall_accuracy)

        def get_result(self):
            """
            Get the accuracy result.

            :return: the accuracy result.
            """
            return [self._overall_accuracy]

        @staticmethod
        def _is_right_prediction(target, pred):
            """
            Check whether it is the right prediction.

            :param target: y.
            :param pred: prediction result.
            :return: boolean: true or false.
            """
            if isinstance(pred, np.int64):
                return target == pred
            return target in pred

    class Eval:
        @staticmethod
        def eval(model, x, y, batch_size, device='cpu', iter_cnt=10, top_k=1):
            """
            Do the eval function.

            :param model: the model
            :param x: the train data.
            :param y: the label data.
            :param batch_size: the batch size.
            :param device: the device string.
            :param iter_cnt: the iteration count for output the intermediate result.
            :param top_k: the top k accuracy.
            :return: accuracy result.
            """
            model.eval()
            with torch.no_grad():
                if device != 'cpu':
                    torch.cuda.empty_cache()
                pred = None
                for i, x_batch in enumerate(Batch.get_batches_x(x, batch_size)):
                    output = model(x_batch)
                    if isinstance(output, tuple):
                        output = output[0]
                    _, p = torch.topk(output, top_k)
                    pred = np.append(pred, p.cpu().numpy(), axis=0) if pred is not None else p.cpu().numpy()
                    if i % iter_cnt == 0 and device != 'cpu':
                        torch.cuda.empty_cache()
                if device != 'cpu':
                    torch.cuda.empty_cache()
                result = EvalResult()
                result.calc(y, pred)
                return result

    class Batch:
        @staticmethod
        def get_batches_x(x, batch_size):
            """
            Get batches of X

            :param x: train data.
            :param batch_size: batch size.
            :return: the batches list.
            """
            if isinstance(x, pd.Series):
                x = x.values
            x_batches, x_batch = [], []  # type: ignore
            for i in range(len(x)):
                if i % batch_size == 0 and len(x_batch) > 0:
                    x_batches.append(x_batch)
                    x_batch = []
                x_batch.append(x[i])
            if len(x_batch) > 0:
                x_batches.append(x_batch)
            return np.array(x_batches)

        @staticmethod
        def get_batches(x, y, batch_size):
            """
            Get batches of X and y.

            :param x: train data.
            :param y: label data.
            :param batch_size: the batch size.
            :return: the batch list.
            """
            if isinstance(x, pd.Series):
                x = x.values

            x_batches, y_batches, x_batch, y_batch = [], [], [], []  # type: ignore

            for i in range(len(x)):
                if i % batch_size == 0 and len(x_batch) > 0:
                    x_batches.append(x_batch)
                    y_batches.append(y_batch)
                    x_batch, y_batch = [], []
                x_batch.append(x[i])
                y_batch.append(y[i])
            if len(x_batch) > 0:
                x_batches.append(x_batch)
                y_batches.append(y_batch)
            return np.array(x_batches), np.array(y_batches)

    class Utils:
        @staticmethod
        def get_long_tensor(li, device):
            """
            Get long tensor based on the list.

            :param li: input list.
            :param device: the device.
            :return: long tensor of the list.
            """
            return torch.tensor(li, device=device, dtype=torch.long)

        @staticmethod
        def get_float_tensor(li, device):
            """
            Get float tensor based on the list.

            :param li: input list.
            :param device: the device.
            :return: float tensor of the list.
            """
            return torch.tensor(li, device=device, dtype=torch.float)

        @staticmethod
        def get_loss_tensor(loss_func, pred, y_train_batch_tensor):
            """
            Get the loss tensor based the loss function.

            :param loss_func: the loss function.
            :param pred: the prediction result.
            :param y_train_batch_tensor: the label data.
            :return: the loss tensor.
            """
            return loss_func(pred, y_train_batch_tensor)

        @staticmethod
        def get_list_loss(loss_func, output, y_train_batch, device):
            """
            Get the loss tensor based on the loss function.

            :param loss_func: the loss function.
            :param output: the
            :param y_train_batch:
            :param device:
            :return:
            """
            pred, y = Utils.unpack_list_of_list(output, y_train_batch)
            y_train_batch_tensor = Utils.get_long_tensor(list(y), device)
            return Utils.get_loss_tensor(loss_func, pred, y_train_batch_tensor)

        @staticmethod
        def unpack_list_of_list(output, y_train_batch):
            """
            Un-pack list of list.

            :param output: the tensor output.
            :param y_train_batch: the y value.
            :return: Un-packed list.
            """
            batch_num, max_length = output.size(0), output.size(1)
            pred, li, ls = [], [], []
            for y in y_train_batch:
                if len(y) > max_length:
                    y = y[0:max_length]
                li.extend(y)
                ls.append(len(y))
            for j in range(batch_num):
                pred.extend(output[j][0:ls[j]])
            return torch.stack(pred), li

    class CharEmbed(BaseModel):
        def __init__(self, char_embed_size=16, kernel_num=16, kernel_sizes=None, embed_char_num=128,
                     dropout=0.2, embed_size=50, lower_case=True, device='cpu'):
            """
            The char embed model.

            :param char_embed_size: the char embed size.
            :param kernel_num: the kernel number.
            :param kernel_sizes: the kernel size.
            :param embed_char_num: the char number.
            :param dropout: the dropout.
            :param embed_size: the embed size.
            :param lower_case: whether to do the lower case.
            :param device: the device.
            """
            super(CharEmbed, self).__init__(device)
            if kernel_sizes is None:
                kernel_sizes = [1, 2, 3]
            self._char_embed = torch.nn.Embedding(embed_char_num, char_embed_size).to(device, torch.float)
            self._convs = torch.nn.ModuleList(
                [torch.nn.Conv2d(1, kernel_num, (K, char_embed_size)) for K in kernel_sizes]).to(device, torch.float)
            self._dropout = torch.nn.Dropout(dropout).to(device, torch.float)
            self._projection = torch.nn.Linear(len(kernel_sizes) * kernel_num, embed_size).to(device, torch.float)
            self._max_kernel_size = max(kernel_sizes)
            self._lower_case = lower_case
            self._embed_size = embed_size

        def embed_word(self, x):
            """
            Embed word.

            :param x: the word.
            :return: embedding.
            """
            # x to be a word
            if self._lower_case:
                x = x.lower()
            li = []
            for c in list(x):
                if ord(c) < 128:
                    li.append(ord(c))
            if len(li) < self._max_kernel_size:
                for i in range(self._max_kernel_size - len(li)):
                    li.append(0)
            x = Utils.get_long_tensor(li, self._device)
            return self._char_embed(x)

        def forward(self, x):
            """
            Forward function.

            :param x: input list.
            :return: embedding list.
            """
            # x to be list of word
            embeds = []
            if len(x) == 0:
                embeds.append(self.embed_word(''))
            else:
                for word in x:
                    embeds.append(self.embed_word(word))
            x = pad_sequence(embeds, True)
            x = x.unsqueeze(1)  # (batch size, 1, word length, embed_dim)
            x = [func.relu(conv(x)).squeeze(3) for conv in self._convs]  # [(1, kernel number, word length)]*len(Ks)
            x = [func.max_pool1d(i, i.size(2)).squeeze(2) for i in x]  # [(N, Co), ...]*len(Ks)
            x = torch.cat(x, 1).to(self._device, torch.float)
            return self._projection(x)

        def get_embed_dim(self):
            """
            Get embed dimension.

            :return: the embed dimension.
            """
            return self._embed_size

    class WordEmbed(BaseModel):
        def __init__(self, embeddings_name, static_embed=True, device='cpu'):
            """
            The word embed.

            :param embeddings_name: embed name.
            :param static_embed: static embed or not.
            :param device: the device name.
            """
            super(WordEmbed, self).__init__(device)
            self._word_to_idx = {}
            self._lowercase_word_to_idx = {}
            self._unknown_index = 0

            # Error classify downloading problem
            # TODO: Find more granular categories and add them to Jasmine code
            try:
                keyed_vector = AutoMLEmbeddingsProvider(embeddings_name=embeddings_name).model
            except Exception as e:
                raise FitException.from_exception(
                    e,
                    target="BiLSTMAttentionTransformer - WordEmbed",
                    reference_code=ReferenceCodes._BILSTM_INIT
                ).with_generic_msg("Exception while retrieving AutoMLEmbeddingsProvider model")

            assert keyed_vector is not None, "BiLSTMAttentionTransformer - " \
                "None keyed_vector possible caching issue"

            self._nn_embed = torch.nn.Embedding.from_pretrained(
                self._load_embed_model_from_keyed_vector(keyed_vector)).to(device, torch.float)
            if static_embed:
                self._nn_embed.weight.requires_grad = False

        def _load_embed_model_from_keyed_vector(self, keyed_vector):
            """
            Load model from CDN of keyed vector.

            :param keyed_vector: the model.
            :return: tensor of the model.
            """
            static_vectors = []
            idx = 0
            for word in keyed_vector.wv.vocab:
                v = keyed_vector[word]
                self._word_to_idx[word] = idx
                self._lowercase_word_to_idx[word.lower()] = idx
                static_vectors.append(v)
                idx += 1
            # add unknown word as average of vectors
            static_vectors.append(np.mean(static_vectors, axis=0))
            self._unknown_index = idx
            return Utils.get_float_tensor(static_vectors, self._device)

        def get_word_index(self, word):
            """
            Search the word index in the embed tensor.

            :param word: the word string.
            :return: the word index.
            """
            index = self._unknown_index
            if word in self._word_to_idx:
                index = self._word_to_idx[word]
            elif word.lower() in self._lowercase_word_to_idx:
                index = self._word_to_idx[word.lower()]
            return index

        def forward(self, tokens):
            """
            The forward method.

            :param tokens: list of tokens.
            :return: list of tensors for the tokens.
            """
            # x is list of word
            li = []
            if len(tokens) == 0:
                li = [self._unknown_index]
            else:
                for token in tokens:
                    li.append(self.get_word_index(token))
            x = Utils.get_long_tensor(li, self._device)
            return self._nn_embed(x)  # (word length, embed_dim)

        def get_embed_dim(self):
            """
            Get word embed dimension size.

            :return: word embed dimension size.
            """
            return self._nn_embed.embedding_dim

        def get_num_embed(self):
            """
            Number of the embedding. (The word count in the embed).

            :return: Number of the word embedding.
            """
            return self._nn_embed.num_embeddings

    class TextDataset:
        def __init__(self, train_file_name, test_file_name, text_col_name,
                     label_col_name, sep=',', valid_file_name=None, split_ratio=0.8):
            """
            Text Dataset for loading data (training, validation and testing).

            :param train_file_name: the train file name.
            :param test_file_name: the test file name.
            :param text_col_name: the column name of the text.
            :param label_col_name: the column name of the label.
            :param sep: the seperate chars.
            :param valid_file_name: the validation file name.
            :param split_ratio: the split ratio between train and valid.
            """
            train_df = pd.read_csv(train_file_name, sep=sep)
            self._train_x = train_df[text_col_name].values
            self._train_y = train_df[label_col_name].values
            self._split_ratio = split_ratio

            if test_file_name:
                test_df = pd.read_csv(test_file_name, sep=sep)
                self._test_x = test_df[text_col_name].values
                self._test_y = test_df[label_col_name].values
            else:
                self._train_x, self._train_y, self._test_x, self._test_y = \
                    train_test_split(self._split_ratio)
            if valid_file_name:
                valid_df = pd.read_csv(valid_file_name)
                self._valid_x = valid_df[text_col_name].values
                self._valid_y = valid_df[label_col_name].values
            else:
                self._valid_x = None
                self._valid_y = None
            self._text_col_name = text_col_name
            self._label_col_name = label_col_name
            encoder = LabelEncoder()
            self._train_y = encoder.fit_transform(self._train_y)
            self._test_y = encoder.transform(self._test_y)
            if self._valid_y is not None:
                self._valid_y = encoder.transform(self._valid_y)
            self._class_num = len(encoder.classes_)
            self._classes = encoder.classes_

        def split_train_valid_set(self, split_ratio):
            """
            To split train and valid data. It will be called during the training process.

            :param split_ratio: the split ratio.
            :return: the train and valid data.
            """
            x_train = self._train_x
            x_valid = self._valid_x
            y_train = self._train_y
            y_valid = self._valid_y

            if self._valid_x is None:
                x_train, x_valid, y_train, y_valid = \
                    train_test_split(self._train_x, self._train_y, train_size=split_ratio,
                                     stratify=self._train_y)
            return x_train, y_train, x_valid, y_valid

        def get_train_set(self):
            """
            Get the train data.

            :return: the train data.
            """
            return self._train_x, self._train_y

        def get_test_set(self):
            """
            Get the test data.

            :return: the test data.
            """
            return self._test_x, self._test_y

        def get_class_num(self):
            """
            Get the class number.

            :return: the class number.
            """
            return self._class_num

        def get_classes(self):
            """
            Get all of the classes.

            :return: all of the classes.
            """
            return self._classes

    class TextUtils:
        @staticmethod
        def tokenize(sentence, max_word_count):
            """
            Do the tokenize.

            :param sentence: the sentence.
            :param max_word_count: the maximum word count.
            :return: list of tokens.
            """
            tokens = [token.text for token in en_tokenize(u'{}'.format(sentence))]
            if max_word_count != -1 and max_word_count < len(tokens):
                tokens = tokens[0:max_word_count]
            return tokens

        @staticmethod
        def embed_sentence(x, max_word_count, word_embed, char_embed, device):
            """
            Embed sentence, the x is the string of the sentence..

            :param x: the sentence.
            :param max_word_count: the maximum word count.
            :param word_embed: word embed model.
            :param char_embed: char embed model.
            :param device: the device name.
            :return: the sentence embedding.
            """
            tokens = TextUtils.tokenize(x, max_word_count)
            return TextUtils.embed_tokens(tokens, max_word_count, word_embed, char_embed, device)

        @staticmethod
        def embed_tokens(tokens, max_word_count, word_embed, char_embed, device):
            """
            Embed list of tokens. the x is the list of strings.

            :param tokens: list of tokens.
            :param max_word_count: maximum word count.
            :param word_embed: word embed model.
            :param char_embed: char embed model.
            :param device: the device name.
            :return: the tokens embedding.
            """
            if max_word_count != -1 and max_word_count < len(tokens):
                tokens = tokens[0:max_word_count]
            x = word_embed(tokens)  # (word length, embed_dim)
            if char_embed is not None:
                lic = char_embed(tokens)
                x = torch.cat((lic, x), dim=1).to(device, dtype=torch.float)
            return x

    class TextAttentionModel(BaseModel):
        """The attention model, which used to train the classification model with Bi-LSTM and Attention"""
        def __init__(self, word_embed, class_num, layer_num=1,
                     hidden_size=300, max_word_count=-1, bidirectional=True,
                     char_embed=None, dropout=0.1, device='cpu'):
            """
            Init of text attention model.

            :param word_embed: the word embedding.
            :param class_num: the class number.
            :param layer_num: the layer number.
            :param hidden_size: the hidden size.
            :param max_word_count: maximum word count.
            :param bidirectional: whether to do the bidirectional.
            :param char_embed: char embed model.
            :param dropout: dropout value.
            :param device: the device name.
            """
            super(TextAttentionModel, self).__init__(device)
            self._hidden_size = hidden_size
            self._layer_num = layer_num
            self._word_embed = word_embed
            self._max_word_count = max_word_count
            self._char_embed = char_embed
            input_size = self._word_embed.get_embed_dim()
            if char_embed:
                input_size += char_embed.get_embed_dim()
            self._direction_num = 1
            if bidirectional:
                self._direction_num = 2
            self._lstm = torch.nn.LSTM(input_size, hidden_size, layer_num, batch_first=True,
                                       bidirectional=bidirectional).to(device, torch.float)
            self._attn = torch.nn.Linear(hidden_size * self._direction_num, 1).to(device, torch.float)
            self._dropout = torch.nn.Dropout(dropout)
            self._fc = torch.nn.Linear(hidden_size * self._direction_num, class_num).to(device, torch.float)

        def embed_sentence(self, x):
            """
            Try to Embed sentence with word embedding and char embedding. the x is a string.

            :param x: the sentence.
            :return: sentence embedding.
            """
            return TextUtils.embed_sentence(x, self._max_word_count, self._word_embed, self._char_embed, self._device)

        def forward(self, x):
            """
            Forward method.

            :param x: list of sentence.
            :return: sentence embedding.
            """
            embeds, lengths = [], []
            for sen in x:
                embed = self.embed_sentence(sen)
                embeds.append(embed)
                lengths.append(embed.size(0))
            x = pad_sequence(embeds, True)
            batch_size, max_length = x.size(0), max(lengths)
            x = pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)

            # set initial states
            h0 = torch.zeros(self._layer_num * self._direction_num, batch_size, self._hidden_size, device=self._device)
            c0 = torch.zeros(self._layer_num * self._direction_num, batch_size, self._hidden_size, device=self._device)

            # forward propagate LSTM
            out, _ = self._lstm(x, (h0, c0))  # out: tensor of shape (batch_size, seq_length, hidden_size*2)
            out, _ = pad_packed_sequence(out, batch_first=True, total_length=max_length)
            attn_weights = func.softmax(self._attn(out), dim=1).view(out.size(0), 1, -1)
            out = torch.bmm(attn_weights, out)
            out = self._dropout(out)
            # decode the hidden state of the attention step
            out = out[:, -1, :]
            return self._fc(out), out

        def resize_linear(self,
                          prev_encoder_mapping: Dict[Any, int],
                          new_encoder_mapping: Dict[Any, int],
                          device: str) -> None:
            """
            Resize the final linear layer of the model based on the new number of classes while preserving the
            weights already developed during feature sweeping.

            :param prev_encoder_mapping: The previous class to class label encoder mapping.
            :param new_encoder_mapping: The new class to class label encoder mapping.
            :param device: The device on which the tensor should be allocated to.

            Note that while it is possible for there to be classes in new_encoder_mapping and not prev_encoder_mapping,
            the reverse is not true since the feature sweeping sample was a strict subset of the input data, and we
            optionally truncate the training data during the fit method after we analyze the classes.
            """
            with torch.no_grad():
                old_weights = self._fc.weight
                old_bias = self._fc.bias

                self._fc = torch.nn.Linear(self._fc.in_features, len(new_encoder_mapping))

                for class_label in new_encoder_mapping:
                    if class_label not in prev_encoder_mapping:
                        continue  # New class. Keep default weight initialization.
                    idx = new_encoder_mapping[class_label]
                    old_idx = prev_encoder_mapping[class_label]
                    self._fc.weight[idx] = old_weights[old_idx]
                    self._fc.bias[idx] = old_bias[old_idx]
            self._fc.to(device)


class BiLSTMAttentionTransformer(AutoMLTransformer):
    """ Starts with pretrained word embeddings, trains BiLSTM, creates embeddings tuned to data."""

    EMBEDDING_PROVIDER_KEY = "embeddings_provider"

    def __init__(self,
                 split_ratio=0.8,
                 epochs=10,
                 batch_size=128,
                 learning_rate=0.005,
                 iter_cnt=20,
                 top_k=1,
                 do_early_stopping=False,
                 embeddings_name="glove_6B_300d_word2vec",
                 device='cpu',
                 seed=None,
                 max_rows=10000):
        """
        Initiates BiLSTM transformer

        :param: embeddings_provider: Embeddings provider for the model.
        """
        super().__init__()
        self._epochs = epochs
        self._batch_size = batch_size
        self._learning_rate = learning_rate
        self.split_ratio = split_ratio
        self._iter_cnt = iter_cnt
        self._top_k = top_k
        self._device = device
        self._train_time_per_row_sec = 0.0
        self._seed = seed
        self._early_stopping = None
        self._model = None
        self.do_early_stopping = do_early_stopping
        self._embeddings_name = embeddings_name
        self._max_rows = max_rows
        self._encoder = None

    def get_params(self, deep=True):
        return {
            "split_ratio": self.split_ratio,
            "epochs": self._epochs,
            "batch_size": self._batch_size,
            "learning_rate": self._learning_rate,
            "iter_cnt": self._iter_cnt,
            "top_k": self._top_k,
            "do_early_stopping": self.do_early_stopping,
            "embeddings_name": self._embeddings_name,
            "device": self._device,
            "seed": self._seed,
            "max_rows": self._max_rows
        }

    def set_seed(self):
        random.seed(self._seed)
        np.random.seed(self._seed)
        torch.manual_seed(self._seed)

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(BiLSTMAttentionTransformer, self)._to_dict()
        dct['id'] = 'bilstm_text_dnn'

        return dct

    @staticmethod
    def split_train_valid_set(x_train, y_train, split_ratio, seed):
        try:
            return train_test_split(x_train, y_train, train_size=split_ratio, stratify=y_train, random_state=seed)
        except ValueError:
            _logger.warning("BiLSTM: Stratified split failed. Falling back to using random sampling.")
            return train_test_split(x_train, y_train, train_size=split_ratio, random_state=seed)

    def fit(self, x_train, y_train, x_valid=None, y_valid=None):
        """sci-kit learn like fit method for BiLSTM model.

        :param x_train: Numpy array containing training data
        :param y_train: Numpy array containing training labels
        :param x_valid: Numpy array containing validation data, optional
        :param y_valid: Numpy array containing validation labels, optional
        :return: Trained model object of type class TextTrain, self
        """
        if self._seed is not None:
            _logger.info("Set seed for BiLSTM to {}".format(self._seed))
            self.set_seed()
        _logger.info("---------------------------------------------------")
        _logger.info("BiLSTMAttentionTransformer.fit() called")

        # print size of train data for debugging
        _logger.info("Shape of training data = {}".format(x_train.shape))

        if isinstance(x_train, pd.Series):
            x_train = x_train.values
        if isinstance(y_train, pd.Series):
            y_train = y_train.values
        if isinstance(x_valid, pd.Series):
            x_valid = x_valid.values
        if isinstance(y_valid, pd.Series):
            y_valid = y_valid.values

        all_labels = np.append(y_train, y_valid) if y_valid is not None else y_train
        unq_classes = set(np.unique(all_labels))
        prev_encoder_mapping = None
        if self._encoder is None:
            self._encoder = LabelEncoder()
            self._encoder.fit(all_labels)
        elif not set(self._encoder.classes_).issuperset(unq_classes):
            # The new label data contains classes that we have previously not seen.
            prev_encoder_mapping = dict(zip(self._encoder.classes_, self._encoder.transform(self._encoder.classes_)))
            self._encoder = LabelEncoder()
            self._encoder.fit(all_labels)
        y_train = self._encoder.transform(y_train)
        if y_valid is not None:
            y_valid = self._encoder.transform(y_valid)

        # If the train data is small (<=5K) and we don't have valid data.
        # Disable the early stopping, so we don't lose training data.
        if len(y_train) <= 5000 and x_valid is None:
            self.do_early_stopping = False

        # If the train data is large (> 5K), reduce the maximum epoch number
        # to 7 to avoid timeout.
        if len(y_train) > 5000:
            self._epochs = min(self._epochs, 7)

        old_epochs = self._epochs
        old_length = len(y_train)

        _logger.info("Checking if data size exceeds {}".format(self._max_rows))
        if len(y_train) > self._max_rows:
            new_epochs = self._epochs * self._max_rows / len(y_train)
            self._epochs = max(int(new_epochs), 1)
            _logger.info("Reduced number of epochs from {} to {} due to "
                         "large data size".format(old_epochs, self._epochs))
            if self._epochs <= 1.0:
                new_length = int(self._max_rows * old_epochs)
                x_train = x_train[:new_length]
                y_train = y_train[:new_length]
                _logger.info("Using {} rows out of {} rows for BiLSTM training"
                             .format(new_length, old_length))
        # Enable early stopping
        if self.do_early_stopping:
            self._early_stopping = EarlyStopping(patience=2, delta=0.0)

        # Initialize BiLSTM model
        try:
            if self._model is None:
                _logger.info("Continue training parameters from the best model of previous fit")
                word_embed = WordEmbed(embeddings_name=self._embeddings_name, device=self._device)
                char_embed = CharEmbed(device=self._device)
                self._model = TextAttentionModel(word_embed,
                                                 class_num=len(unq_classes),
                                                 char_embed=char_embed,
                                                 max_word_count=32,
                                                 hidden_size=128,
                                                 layer_num=2,
                                                 bidirectional=True,
                                                 device=self._device)
            elif prev_encoder_mapping is not None:
                # We already instantiated the model, but here we observe a different class set, so we should modify
                # the final linear layer to output the correct number of class predictions.
                new_encoder_mapping = dict(zip(self._encoder.classes_,
                                               self._encoder.transform(self._encoder.classes_)))
                self._model.resize_linear(prev_encoder_mapping, new_encoder_mapping, self._device)

        except Exception as e:
            # Error classify overall initialization errors
            raise FitException._with_error(AzureMLError.create(TextDnnModelDownloadFailed, transformer='BiLSTM',
                                                               error_details=str(e),
                                                               reference_code=ReferenceCodes._BILSTM_DOWNLOAD,
                                                               target="BiLSTMAttentionTransformer"),
                                           inner_exception=e) from e

        # Prepare training and validation data
        if x_valid is None or y_valid is None:
            if self.split_ratio < 1.0:
                x_train, x_valid, y_train, y_valid = self.split_train_valid_set(x_train, y_train,
                                                                                self.split_ratio, self._seed)

        # Set up training
        optimizer = torch.optim.Adam(self._model.parameters(), lr=self._learning_rate)
        best_acc = 0.0
        ts = 0.0
        best_model = self._model
        copied = False

        try:
            for epoch in range(1, self._epochs + 1):
                current = datetime.datetime.now()

                # Error classify transform fit train problems
                try:
                    self._model.train()
                except Exception as e:
                    raise FitException.from_exception(
                        e,
                        has_pii=True,
                        target="BiLSTMAttentionTransformer",
                        reference_code=ReferenceCodes._BILSTM_FIT_TRAIN
                    ).with_generic_msg("Exception while training model for BiLSTMAttentionTransformer")

                x_batches, y_batches = Batch.get_batches(x_train, y_train, self._batch_size)
                _logger.info('epoch:{}, batches:{}'.format(epoch, len(x_batches)))
                for i in range(len(x_batches)):
                    batch_started_time = datetime.datetime.now()
                    x_train_batch, y_train_batch = x_batches[i], y_batches[i]
                    optimizer.zero_grad()
                    pred = self._model(x_train_batch)
                    if isinstance(pred, tuple):
                        pred = pred[0]
                    y_train_batch_tensor = Utils.get_long_tensor(list(y_train_batch), self._device)
                    loss = func.cross_entropy(pred, y_train_batch_tensor)
                    loss.backward()
                    optimizer.step()
                    if self._train_time_per_row_sec == 0.0:
                        batch_second = (datetime.datetime.now() - batch_started_time).total_seconds()
                        self._train_time_per_row_sec = batch_second * 1.0 / len(x_train_batch)
                        _logger.info('train time per row sec: {:.6f}'.format(self._train_time_per_row_sec))
                    # Try to print the result every 10 batches.
                    if i % self._iter_cnt == 0:
                        _logger.info('Batch[{}] - loss: {:.6f}'.format(i, loss.item()))
                        if self._device != 'cpu':
                            torch.cuda.empty_cache()
                epoch_end = datetime.datetime.now()
                _logger.info("epoch:{} takes {} seconds".format(epoch, (epoch_end - current).total_seconds()))
                ts += (epoch_end - current).total_seconds()
                if x_valid is not None:
                    valid_eval_result = Eval.eval(self._model, x_valid, y_valid, self._batch_size, self._device,
                                                  self._iter_cnt, self._top_k)
                    valid_accuracy = valid_eval_result.get_result()[0]
                    _logger.info('epoch:{}, validation accuracy: {}'.format(epoch, valid_accuracy))
                    if valid_accuracy >= best_acc:
                        best_acc = valid_accuracy
                        best_model = copy.deepcopy(self._model)
                        copied = True
                    if self._early_stopping is not None:
                        if self._early_stopping.check_early_stop_train(valid_accuracy):
                            _logger.info('early stopping the training at epoch:{}'.format(epoch))
                            break
            _logger.info('average training time in seconds: {}'.format(ts / self._epochs))
            if x_valid is not None:
                _logger.info('valid best accuracy: {:.4f}'.format(best_acc))
            if copied:
                self._model = copy.deepcopy(best_model)
            return self
        except Exception as e:
            # Error classify overall transform fit errors
            raise FitException.from_exception(
                e, target="BiLSTMAttentionTransformer fit",
                reference_code=ReferenceCodes._BILSTM_FIT
            ).with_generic_msg("Exception raised while performing fit on BiLSTMAttentionTransformer")

    def transform(self, X):
        """scikits like fit method for BiLSTM model.

        :param X: Numpy array containing data to be transformed
        :return: Output label
        """
        try:
            if isinstance(X, pd.Series):
                X = X.values

            # Error classify transform evaluation problems
            try:
                cast(TextAttentionModel, self._model).eval()
            except Exception as e:
                raise TransformException.from_exception(
                    e, has_pii=True,
                    target="BiLSTMAttentionTransformer transform - eval",
                    reference_code=ReferenceCodes._BILSTM_TRANSFORM_MODEL_EVAL).\
                    with_generic_msg("BiLSTMAttentionTransformer failed in transform.")

            with torch.no_grad():
                if self._device != 'cpu':
                    torch.cuda.empty_cache()
                pred = None
                for i, x_batch in enumerate(Batch.get_batches_x(X, self._batch_size)):
                    output = cast(TextAttentionModel, self._model)(x_batch)[1]
                    pred = np.append(pred, output.cpu().numpy(), axis=0) if pred is not None \
                        else output.cpu().numpy()
                    if i % self._iter_cnt == 0 and self._device != 'cpu':
                        torch.cuda.empty_cache()
                if self._device != 'cpu':
                    torch.cuda.empty_cache()
                return pred
        except Exception as e:
            # Error classify overall transform fit errors
            raise TransformException.from_exception(
                e, has_pii=True, target="BiLSTMAttentionTransformer transform",
                reference_code=ReferenceCodes._BILSTM_TRANSFORM).\
                with_generic_msg("BiLSTMAttentionTransformer failed in transform.")
