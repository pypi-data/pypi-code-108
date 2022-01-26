import tensorflow as tf
import tensorflow.keras.layers as layers
from tensorflow_core.python import keras
import numpy as np

from autoai_ts_libs.deps.tspy.ml.dl.attention import BiLSTMAttention, LSTMAttention


class LSTMSequenceAttention:
    def __init__(self):
        self.model = None
        self.max_sequence_len = None

    def fit(self, config, dataset, max_input_sequence_len, embedding_input_dim, epochs=None):
        """
        :param config: model architecture config
        :param dataset: consists of both sequences and labels; sequences represents all the sequences that we want to
        get attention on. Each entity in a sequence has to be a number (indexed value), since we cannot create an index
        given batches via generator/dataset; labels represents corresponding class labels for the sequences
        :param max_input_sequence_len: maximum possible length of any sequence in the dataset. This is needed to
        properly pad the input sequences while training
        :param max_len: maximum length of attention sequences to be returned
        :param epochs: number of epochs to train the model for
        :return:
        """
        self.max_sequence_len = max_input_sequence_len
        model = LSTMSequenceAttention.__build_model__(config, embedding_input_dim, self.max_sequence_len)
        self.model = model
        self.model.compile(optimizer=tf.keras.optimizers.Adam(), loss="sparse_categorical_crossentropy")
        self.model.fit(dataset)
        return self.model

    def get_prediction_with_highest_attention_states(self, seqs, max_attn_len):
        # todo - check shape
        # if padded_sequence.shape < 3:
        #     padded_sequence.reshape((-1, padded_sequence.shape[0], padded_sequence.shape[1]))
        prediction = self.model.predict(seqs)
        attentions = self.get_attention_map(seqs)
        res = []
        for i in range(len(attentions)):
            x = seqs[i]
            att = attentions[i]
            x = x[x != 0]
            att = att[att != 0]
            if len(att) < max_attn_len:
                seq = []
                for state in x:
                    seq.append(state.numpy())
                res.append(seq)
            else:
                max_ind = np.argpartition(att, -max_attn_len)[-max_attn_len:]
                seq = []
                for ind in max_ind:
                    seq.append(x[ind].numpy())
                res.append(seq)

        return prediction, res

    def get_predictions_with_highest_attention_states(self, config, sequences, labels, max_len, batch_size=None,
                                                      epochs=None):
        """
        :param config: model architecture config
        :param sequences: list of arrays representing all the sequences that we want to get attention on
        :param labels: list representing corresponding class labels for the sequences
        :param epochs: number of epochs to train the model for
        :param batch_size: batch size to be used when training the model
        :param max_len: maximum length of attention sequences to be returned
        :return: the truncated sequences with states that have the highest attention
        """
        # input data transformations
        idx, rev_idx = LSTMSequenceAttention.__get_sequence_index__(sequences)
        seq_len = LSTMSequenceAttention.__get_max_seq_len__(sequences)
        seqs = LSTMSequenceAttention.__get_sequence_array__(sequences, idx)
        padded_seqs = tf.keras.preprocessing.sequence.pad_sequences(seqs, padding='post')

        # build and train model
        model = LSTMSequenceAttention.__build_model__(config, len(idx) + 1, seq_len)
        model.compile(optimizer=tf.keras.optimizers.Adam(), loss="sparse_categorical_crossentropy")
        self.model = model
        if batch_size is None:
            batch_size = int(len(padded_seqs) / 100)
        if epochs is None:
            epochs = 100
        self.model.fit(padded_seqs, np.array(labels), batch_size=batch_size, epochs=epochs, shuffle=True)

        # obtain predictions
        predictions = model.predict(padded_seqs)

        # obtain attention maps
        attentions = self.get_attention_map(padded_seqs)

        # truncate each sequence to 'max_len' highest attention states and return the result
        res = []
        for i in range(len(attentions)):
            x = padded_seqs[i]
            att = attentions[i]
            x = x[x != 0]
            att = att[att != 0]
            if len(att) < max_len:
                seq = []
                for state in x:
                    seq.append(rev_idx[state])
                res.append(seq)
            else:
                max_ind = np.argpartition(att, -max_len)[-max_len:]
                seq = []
                for ind in max_ind:
                    seq.append(rev_idx[x[ind]])
                res.append(seq)
        return predictions, res

    @staticmethod
    def __build_model__(config, emb_dim, seq_len):
        input = keras.Input(shape=(None,))
        op_dim = 128
        if 'embedding_output_dim' in config.configs:
            op_dim = config.configs['embedding_output_dim']
        embedding = layers.Embedding(input_dim=emb_dim, output_dim=op_dim, input_length=seq_len, mask_zero=True)(
            input)
        embedding = layers.SpatialDropout1D(0.5)(embedding)
        x = embedding
        for layer_n in range(len(config.layers)):
            x = LSTMSequenceAttention.__get_layer__(config.layers[layer_n])(x)
        # if 'attention_units' is specified, use Attention else use BiLSTMAttention
        if 'attention_units' in config.configs:
            x, attn = LSTMAttention(units=config.configs['attention_units'])(x)
        else:
            x, attn = BiLSTMAttention(return_attention=True)(x)
        x = layers.Dropout(0.5)(x)
        out = layers.Dense(units=2, activation="softmax")(x)
        model = keras.Model(input, out)
        return model

    @staticmethod
    def __get_layer__(layer):
        if layer.type == 'LSTM':
            return layers.LSTM(layer.units, return_sequences=True)
        if layer.type == 'BidirectionalLSTM':
            return layers.Bidirectional(layers.LSTM(layer.units, return_sequences=True))

    @staticmethod
    def __get_sequence_index__(sequence_list):
        idx = {}
        rev_idx = {}
        i = 1
        for cs in sequence_list:
            for click in cs:
                if click not in idx:
                    idx[click] = i
                    rev_idx[i] = click
                    i = i + 1
        return idx, rev_idx

    @staticmethod
    def __get_max_seq_len__(sequence):
        seq_len = 0
        for s in sequence:
            if len(s) > seq_len:
                seq_len = len(s)
        return seq_len

    @staticmethod
    def __get_sequence_array__(seqs, idx):
        seqs_ind = []
        for cs in seqs:
            cs_idx = []
            for c in cs:
                cs_idx.append(idx[c])
            seqs_ind.append(cs_idx)
        return np.array(seqs_ind)

    def get_attention_map(self, input):
        # modify this if architecture is changes.
        # For example, if we remove the last dropout, should change slice to [0:-1]
        att_model_output = self.model.layers[0:-2]
        att_model = keras.Model(att_model_output[0].input, att_model_output[-1].output)
        att_model.compile(optimizer=tf.keras.optimizers.Adam(),
                          loss="sparse_categorical_crossentropy",
                          metrics=["accuracy"])
        return att_model.predict(input)[1]
