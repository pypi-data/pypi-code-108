from b2bTools.singleSeq.DynaMine.Predictor import DynaMine
from b2bTools.singleSeq.EFoldMine.Predictor import EFoldMine
from b2bTools.singleSeq.DisoMine.Predictor import DisoMine
from b2bTools.singleSeq.Agmata.Predictor import Agmata

from b2bTools.general.Io import B2bIo

# TODO: Here access all predictions, or at least those asked for!

class MineSuite(B2bIo):

  scriptName = "b2bTools.singleSeq.Predictor"

  def __init__(self):

    print("Initializing DynaMine...", end=' ')
    self.dynaMine = DynaMine()

    print("Initialising EFoldMine...")
    self.eFoldMine = EFoldMine()

    print("Initialising DisoMine...")
    self.disoMine = DisoMine()

    print("Initialising Agmata...")
    self.agmata = Agmata()

    print("Done.")

    # Additional info for writing files
    self.infoTexts = list(set(self.dynaMine.infoTexts + self.eFoldMine.infoTexts + self.disoMine.infoTexts + self.agmata.infoTexts))
    self.infoTexts.sort()

    self.references = list(set(self.dynaMine.references + self.eFoldMine.references + self.disoMine.references + self.agmata.references))
    self.references.sort()

    self.version = "DynaMine {}, EFoldMine {}, DisoMine {}, Agmata {}".format(self.dynaMine.version,self.eFoldMine.version,self.disoMine.version, self.agmata.version)


    self.informationPerPredictor = self.dynaMine.informationPerPredictor.copy()
    self.informationPerPredictor.update(self.eFoldMine.informationPerPredictor)
    self.informationPerPredictor.update(self.disoMine.informationPerPredictor)
    self.informationPerPredictor.update(self.agmata.informationPerPredictor)

    #self.references = ['doi: 10.1038/ncomms3741 (2013)', 'doi: 10.1093/nar/gku270 (2014)', 'doi: 10.1038/s41598-017-08366-3 (2017)']

  def predictSeqs(self, seqs, predTypes = ('eFoldMine', 'disoMine', 'agmata')):

    self.seqs = seqs

    # DynaMine - always needs to be run
    self.dynaMine.predictSeqs(seqs)
    self.allPredictions = self.dynaMine.allPredictions

    if 'eFoldMine' in predTypes or 'disoMine' in predTypes:
      # EFoldMine
      self.eFoldMine.predictSeqs(seqs, dynaMinePreds=self.dynaMine.allPredictions)
      # This needs cleaning up!
      # TODO double-check that dynamine preds are not messed up!
      self.allPredictions = self.eFoldMine.allPredictions

    if 'disoMine' in predTypes:
      # DisoMine
      self.disoMine.allPredictions = self.allPredictions
      self.disoMine.predictSeqs(seqs)

      # TODO should also pull Psipred predictions if agmata requested, save time!

    if 'agmata' in predTypes:
      self.agmata.allPredictions = self.allPredictions
      self.agmata.predictSeqs(self.seqs)
