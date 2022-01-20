# -*- coding: utf-8 -*-
import h5py
import numpy as np


class CellExpReader(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.exp_len = 0
        self.gene_num = 0
        self.cell_num = 0
        self.genes = None
        self.cells = None
        self.rows = None
        self.cols = None
        self.count = None
        self.positions = None
        self._init()

    def _init(self):
        with h5py.File(self.filepath, mode='r') as h5f:
            self.genes = np.array(h5f['cellBin']['gene']['geneName'])
            self.cols = np.array(h5f['cellBin']['cellExp']['geneID'])
            self.count = np.array(h5f['cellBin']['cellExp']['count'])
            self.exp_len = self.cols.shape[0]
            self.gene_num = self.genes.shape[0]
            x = np.array(h5f['cellBin']['cell']['x'],  dtype='uint32')
            y = np.array(h5f['cellBin']['cell']['y'],  dtype='uint32')

            self.cell_num = len(x)
            self.positions = np.zeros((self.cell_num, 2))
            self.positions[:, 0] = x
            self.positions[:, 1] = y

            self.cells = np.array(x, dtype='uint64')
            self.cells = np.bitwise_or(
                np.left_shift(self.cells, 32), y)

            gene_counts = np.array((h5f['cellBin']['cell']['geneCount']))
            self.rows = np.zeros((self.exp_len, ), dtype='uint32')

            exp_index = 0
            for i in range(gene_counts.shape[0]):
                for index in range(gene_counts[i]):
                    self.rows[exp_index] = i
                    exp_index += 1
