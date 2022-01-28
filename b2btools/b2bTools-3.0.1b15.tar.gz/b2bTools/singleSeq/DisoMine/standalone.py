#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  standalone.py
#
#  Copyright 2017 Gabriele Orlando <orlando.gabriele89@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

from b2bTools.singleSeq.DisoMine.vector_builder.vettore_gen import build_vector
from b2bTools.singleSeq.DisoMine.torch_NN_gru_80AUC_prova import nn_pytorch
import numpy as np
import sys
import pathlib
import string, random


def standalone(seqList, dmPredictions, verbose=0):
    """
	seqList is now a list of tuples defined by (seqId, seq) which is faster.
	dmPredictions is the existing dynaMine/EFoldMine preds (done earlier).
	verbose defines the level of feedback given to the user printing messages on the standard output.
	"""

    # These are the features used in the final version
    features = 'dyna_back,psipred,ef,dyna_side'

    # Directory of this script
    scriptDir = str(pathlib.Path(__file__).parent.absolute())
    mapfilepath = scriptDir + '/map_random_name_with_seqID.tsv'
    with open(mapfilepath, 'w') as f:
        f.write('random_name\tseq_id\tdisoMine_status\n')

    # This is the window size used
    window = 4

    def check_sequences(seqList):
        """
		This method checks if all the provided sequences meet the minimum requirements:
		all the characters of the sequences are valid and the length of each sequence is greater than 20.

		If all the sequences meet the checks, a True value is returned, otherwise a error object.
		"""
        for (seqId, seq) in seqList:
            if not seq.isalpha():
                return {'error': 'invalid char in sequence {}'.format(seqId)}

            if len(seq) < 20:
                return {'error': 'sequence {} too short, minimum length is 20 amino acids'.format(seqId)}

        return True

    def load_model():
        sys.path.append(scriptDir)

        mod = nn_pytorch(cuda=False)
        # mod.load_model('{}/gru80_final.mtorch'.format(scriptDir))
        # mod.load_model('{}/conversion_attempt.mtorch'.format(scriptDir))
        mod.load_model('{}/disomine_converted.mtorch'.format(scriptDir))

        scaler = None

        return mod, scaler

    def format_output(disorder, seqList, dmPredictions):
        results = {}

        for (protID, sequence) in seqList:
            results[protID] = []

            for sequenceIndex in range(len(sequence)):
                result_tuple = (sequence[sequenceIndex], np.float64(disorder[protID][sequenceIndex]))
                results[protID].append(result_tuple)

            dmPredictions[protID]['disoMine'] = results[protID]

        return results

    def predict(seqList, dmPredictions, model, crunch=100):

        check = check_sequences(seqList)

        if not check:
            return check

        results_dict = {}
        # dyna = {}
        # side = {}
        # ef = {}
        sequence_counter = 0
        numSeqs = len(seqList)

        # Doing 100 sequences at a time with disomine
        for sequence_index in range(0, numSeqs + 1, crunch):
            if sequence_index + crunch > numSeqs:
                end = numSeqs
            else:
                end = sequence_index + crunch

            vector_crunch = []

            if verbose >= 1:
                print('starting crunch', sequence_counter)

            targets = []
            for (target, seq) in seqList[sequence_index:end]:

                diso_works = False
                base_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

                if verbose >= 2:
                    print('\tstarting target:', target)
                try:
                    disomine_results = build_vector(seq, dmPredictions[target], base_name=base_name, seqID=target,
                                                    TYPE=features, sw=window)
                    with open(mapfilepath, 'a') as f:
                        f.write('{0}\t{1}\tSuccess\n'.format(base_name, target))
                    diso_works = True

                except:
                    with open(mapfilepath, 'a') as f:
                        f.write('{0}\t{1}\tFailed\n'.format(base_name, target))
                    results_dict[target] = np.array([np.nan]*len(seq))

                if diso_works:
                    vector = np.array(disomine_results)
                    vector_crunch += [vector]
                    targets.append(target)


            sequence_counter += 1
            predictions = model.decision_function(vector_crunch)
            assert len(predictions) == len(vector_crunch)

            for target, prediction_results in zip(targets, predictions):
                # Set floor and ceiling of values not included in (0, 1)
                for value_index in range(len(prediction_results)):
                    if prediction_results[value_index] < 0:
                        prediction_results[value_index] = 0.0
                    elif prediction_results[value_index] > 1:
                        prediction_results[value_index] = 1.0

                results_dict[target] = prediction_results

        # Adding results to existing information as well here, but output is just disoMine
        results = format_output(results_dict, seqList, dmPredictions)

        return results

    # This is the main code for this def (standalone), calling other defs inside this one
    model, _scaler = load_model()
    results = predict(seqList, dmPredictions, model)

    return results


def main(args):
    # print standalone("example.fasta")
    a = leggifasta('input_files_examples/example_toy.fasta')
    a['extra_predictions'] = False
    print(standalone(a))


# from memory_profiler import memory_usage
# mem_usage = memory_usage(standalone,interval=0.01)
# print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
# print('Maximum memory usage: %s' % max(mem_usage))
# cProfile.run('standalone("example.fasta")')

if __name__ == '__main__':
    import sys

    sys.exit(main(sys.argv))
