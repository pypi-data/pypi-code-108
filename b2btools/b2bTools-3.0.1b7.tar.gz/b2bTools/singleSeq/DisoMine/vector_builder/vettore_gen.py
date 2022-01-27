#!/usr/bin/env python2
# -*- coding: utf-8 -*-

prop_sw = 35

import string, random, os
from .runpsipred_single import run

### objects ###
amino_index = {'A': 1, 'C': 2, 'B': -1, 'E': 3, 'D': 4, 'G': 5, 'F': 6, 'I': 7, 'H': 8, 'K': 9, 'M': 10, 'L': 11,
               'N': 12, 'Q': 13, 'P': 14, 'S': 15, 'R': 16, 'U': -1, 'T': 17, 'W': 18, 'V': 0, 'Y': 19, 'X': -1,
               'Z': -1}


class psipred:
    # Directory of this script
    scriptDir = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, single_sequence=True):

        self.tmpfold = os.path.join(self.scriptDir, 'psipred/tmp/')

        if single_sequence:
            pass
        else:
            raise (NotImplementedError)

    def predict(self, seq, seq_ID, base_name):
        pred = []

        fasta_filename = self.tmpfold + base_name + '.fasta'
        ss2_filename = self.tmpfold + base_name + '.ss2'
        horiz_filename = self.tmpfold + base_name + '.horiz'
        ss_filename = self.tmpfold + base_name + '.ss'
        mtx_filename = self.tmpfold + base_name + '.mtx'

        with open(fasta_filename, 'w') as fasta_file:
            fasta_file.write('>{0}\n{1}'.format(seq_ID, seq))

        # Executes PSIPRED binary
        run(fasta_filename)

        # Reads the PSIPRED output file .ss2
        with open(ss2_filename, 'r') as ss2_file:
            ss2 = ss2_file.readlines()

        for i in ss2[2:]:
            a = i.strip().split()

            if len(a) > 0:
                pred += [[float(a[3]), float(a[4]), float(a[5])]]

        # Deletes the temp files
        os.system('rm {}'.format(fasta_filename))
        os.system('rm {}'.format(ss2_filename))
        os.system('rm {}'.format(horiz_filename))
        os.system('rm {}'.format(ss_filename))
        os.system('rm {}'.format(mtx_filename))

        return pred


def build_vector(seq, dmPredictions, base_name=None, seqID=None, TYPE=None, sw=None, nomeseq=None):
    vector = []
    sequence_length = len(seq)
    last = 0
    seq_nogap = seq.replace('-', '')

    for i in range(sequence_length):
        vector += [[]]

    nfeatures = 0

    for curr_fea in TYPE.split(','):
        if curr_fea.startswith('dyna') or curr_fea == 'ef':

            if curr_fea == 'dyna_coil':
                v_dyna = [dmPredictions['coil']]
            elif curr_fea == 'dyna_sheet':
                v_dyna = [dmPredictions['sheet']]
            elif curr_fea == 'dyna_helix':
                v_dyna = [dmPredictions['helix']]
            elif curr_fea == 'dyna_side':
                v_dyna = [dmPredictions['sidechain']]
            elif curr_fea == 'dyna_back':
                v_dyna = [dmPredictions['backbone']]
            elif curr_fea == 'ef':
                v_dyna = [dmPredictions['earlyFolding']]

            effect = 0  ## We could remove it and only use vector_index. Validate hypothesis.

            for vector_index in range(len(vector)):
                if seq[vector_index] != '-':
                    # print i
                    for s in range(-sw, sw + 1):
                        if effect + s < 0:
                            vector[vector_index] += [0]
                        elif effect + s >= len(seq_nogap):
                            vector[vector_index] += [0]
                        else:
                            vector[vector_index] += [v_dyna[0][effect + s][1]]

                    effect += 1
                    last = i

        elif 'psipred' == curr_fea:
            psidpred_runner = psipred()
            v_psipred = psidpred_runner.predict(seq_nogap, seqID, base_name=base_name)
            effect = 0

            for vector_index in range(len(vector)):
                if seq[vector_index] != '-':
                    for s in range(-sw, sw + 1):
                        if effect + s < 0:
                            vector[vector_index] += [0] * 3
                        elif effect + s >= len(seq_nogap):
                            vector[vector_index] += [0] * 3
                        else:
                            vector[vector_index] += v_psipred[effect + s]

                    effect += 1
                    last = i

        else:
            print((curr_fea, 'IS NOT A FEATURE'))
            assert False

    for sequence_index in range(sequence_length):
        if seq[sequence_index] == '-' or seq[sequence_index] == '.':
            vector[sequence_index] += ['-'] * nfeatures

    return vector
