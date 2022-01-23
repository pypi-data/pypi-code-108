
import numpy as np

__all__ = ['NumericEncoder']


class NumericEncoder:
    def __init__(self, numeric_type = None, float_precision = None, signed = None, encoding_depth = None, character_set = None):
        self.numeric_type = numeric_type or 'float'
        self.encoding_depth = encoding_depth or 1
        self.float_precision = float_precision or 0
        self.signed = signed or False
        self.encoding_size = 0

        # Default to base64, but accept an input character set
        self.set_encoding_character_set(character_set)

        if numeric_type == 'int':
            self.float_precision = 0

        number_of_states = self.encoding_size ** self.encoding_depth

        if self.signed:
            self.max_state = int(number_of_states / 2)
            self.min_state = -1 * self.max_state
        else:
            self.max_state = (number_of_states)
            self.min_state = 0 

        if self.numeric_type == 'float':
            self.max_value = self.max_state / (10 ** self.float_precision)
            self.min_value = self.min_state / (10 ** self.float_precision)
        else:
            self.max_value = self.max_state
            self.min_value = self.min_state

    @staticmethod
    def get_base_64():
        character_set = np.concatenate([np.arange(48, 58, 1, dtype=np.uint8), np.arange(65, 91, 1, dtype=np.uint8), np.arange(97, 123, 1, dtype=np.uint8), np.asarray([45, 95], dtype=np.uint8)])
        return character_set

    @staticmethod
    def get_base_16():
        character_set = np.concatenate([np.arange(48, 58, 1, dtype=np.uint8), np.arange(65, 71, 1, dtype=np.uint8)])
        return character_set

    @staticmethod
    def get_base_91():
        character_set = np.concatenate([np.arange(48, 58, 1, dtype=np.uint8), np.arange(65, 91, 1, dtype=np.uint8), np.arange(97, 123, 1, dtype=np.uint8), np.asarray([45, 33, 35, 36, 37, 38, 40, 41, 42, 43, 44, 46, 47, 58, 59, 60, 61, 62, 63, 64, 91, 93, 94, 95, 96, 123, 124, 125, 126], dtype=np.uint8)])
        return character_set
        
    def set_encoding_character_set(self, character_set):
        if character_set is None:
            self.encoding_table = NumericEncoder.get_base_64()
        else:
            self.encoding_table = character_set
        
        self.encoding_size = len(self.encoding_table)
        self.decoding_table = np.zeros(256, dtype=np.uint8)
        for i, idx in enumerate(self.encoding_table):
            self.decoding_table[idx] = i

    def encode(self, numeric_data):
        vector = np.copy(numeric_data)
        if self.numeric_type == 'float':
            vector = vector * (10 ** self.float_precision)

        if self.signed:
            vector = vector + self.max_state

        vector = np.rint(vector).astype(np.uint64)
        encoded_bytes = np.zeros((vector.shape[0], self.encoding_depth), dtype=np.uint8)

        for i in range(self.encoding_depth):
            place_value = (self.encoding_size ** (self.encoding_depth - i - 1))
            encoded_bytes[:, i][vector >= place_value] = np.floor_divide(vector[vector >= place_value], place_value)
            vector[vector >= place_value] = vector[vector >= place_value] % place_value
        codes = np.vectorize(self.encoding_table.item)(encoded_bytes.astype(np.uint8))

        encoded = np.vectorize(chr)(codes.flatten())
        return ''.join(encoded)

    def decode(self, string):
        vector = np.frombuffer(string.encode('utf-8'), dtype=f'S1').reshape(int(len(string) / self.encoding_depth), self.encoding_depth)
        vector = np.vectorize(ord)(vector)
        vector = np.vectorize(self.decoding_table.item)(vector)

        for i in range(self.encoding_depth):
            offset = (self.encoding_size ** (self.encoding_depth - i - 1))
            vector[:, i] = vector[:, i] * offset
        vector = np.sum(vector, axis=1)

        # Adjust for signage
        if self.signed:
            vector = vector - self.max_state

        if self.numeric_type == 'float':
            vector =  np.divide(vector, (10 ** self.float_precision))

        return [x.item() for x in vector]