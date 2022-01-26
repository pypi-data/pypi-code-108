from .singleSeq.DynaMine.Predictor import DynaMine
from .singleSeq.EFoldMine.Predictor import EFoldMine
from .singleSeq.DisoMine.Predictor import DisoMine
import numpy as np
import json

#
# @Luciano: This script might be better incorporated on the web end itself, also for error catching!
#

def predictSeqs(seqs, extra_predictions):

    """
    :param seqs:
    :param extra_predictions:
    :return:
    """

    # NOTE Wim: this has to change, only run what is required! Need to discuss how to do the bookkeeping here...


    dm = DynaMine()
    dm.predictSeqs(seqs)
    efm = EFoldMine()
    efm.predictSeqs(seqs)
    de = DisoMine()
    de.allPredictions = efm.allPredictions
    de.predictSeqs(seqs)

    out=[]
    for protID in range(len(seqs)):
        entry={}
        entry['proteinID']=json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['proteinID']
        entry['sequence']=json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['sequence']
        entry['disomine']=np.array(json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['disoMine'])

        if extra_predictions:
            entry['efoldmine']=np.array(json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['earlyFolding'])
            entry['backbone']=np.array(json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['backbone'])
            entry['sidechain']=np.array(json.loads(de.getAllPredictionsJson('Disomine'))['results'][protID]['sidechain'])
            assert len(entry['sequence'])==len(entry['disomine'])==len(entry['efoldmine'])==len(entry['sidechain'])==len(entry['backbone'])
        out+=[entry]

    return {'results':out}
