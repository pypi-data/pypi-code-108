import glob, os, json
import numpy as np
from dynaMine.analysis.parsers import DynaMineRelatedFileParsers

class mapPredToMSA(DynaMineRelatedFileParsers):

  predictionTypes = ('backbone','coil','helix','ppII','sheet','sidechain','earlyFoldProb')

  gapCode = "-"

  def getPredictionFileName(self, seqId, predictionType):

    # This needs to be redefined for other predictions in a subclass!

    subDir = "dynaMineResults/{}/{}_uniref90.clu/{}_uniref90.clu_{}.pred"
    #subDir = "dynaMineResults/{}/{}_uniref90_msa/{}_uniref90_msa_{}.pred"

    predictionFileName = subDir.format(seqId,seqId,seqId,predictionType)

    return predictionFileName

  def doMapping(self,msaDir):

    alignFiles = glob.glob("{}/*.clustal".format(msaDir))

    for alignFile in alignFiles:

      uniprotId = os.path.split(alignFile)[1].replace("_uniref90.clustal","")
      #uniprotId = os.path.split(alignFile)[1].replace("_uniref90_msa.txt","")

      if uniprotId != 'P0DTC9':
        continue

      # Get alignment info
      # Is dictionary with {seqId: alignment} entries
      seqAlignments = self.readAlignments(alignFile,resetAlignRefSeqID=True)

      # Get predictions
      predictions = {}
      print("Working on {}".format(uniprotId))
      for predictionType in self.predictionTypes:

        predFile = self.getPredictionFileName(uniprotId,predictionType)

        assert os.path.exists(predFile), "File missing {}".format(predFile)

        predictions[predictionType] = self.readDynaMineMultiEntry(predFile)

      # Map them
      alignedPredictions = {}
      for predictionType in self.predictionTypes:
        alignedPredictions[predictionType] = {}

      allSeqIds = list(seqAlignments.keys())
      allSeqIds.sort()

      if uniprotId not in allSeqIds:
        print('Key ID missing for {}!'.format(uniprotId))
        continue

      sequenceInfo = {}

      for seqId in allSeqIds:

        alignment = seqAlignments[seqId]
        seqIndex = 0

        sequenceInfo[seqId] = []

        for predictionType in self.predictionTypes:
          alignedPredictions[predictionType][seqId] = []

        for alignIndex in range(len(alignment)):
          if alignment[alignIndex] == self.gapCode:
            for predictionType in self.predictionTypes:
              alignedPredictions[predictionType][seqId].append(None)
          else:
            resName = predictions['backbone'][seqId][seqIndex][0]

            assert resName == alignment[alignIndex] or resName == 'X', "Amino acid code mismatch {}-{}".format(resName,alignment[alignIndex])

            sequenceInfo[seqId].append(alignment[alignIndex])

            for predictionType in self.predictionTypes:
              (resName,predValue) = predictions[predictionType][seqId][seqIndex]
              alignedPredictions[predictionType][seqId].append(predValue)
            seqIndex += 1

      alignedPredictions['sequence'] = sequenceInfo

      distribKeys = ('median','thirdQuartile','firstQuartile','topOutlier','bottomOutlier')
      numDistribKeys = len(distribKeys)

      # Now generate the info for quartiles, ... based on the alignRefSeqID, first entry in alignment file
      refSeqPredictionDistribs = {}
      for predictionType in self.predictionTypes:
        refSeqPredictionDistribs[predictionType] = {self.alignRefSeqID: []}
        for distribKey in distribKeys:
          refSeqPredictionDistribs[predictionType][distribKey] = []

      self.alignRefSeqID = uniprotId
      refSeqAlignment = seqAlignments[self.alignRefSeqID]
      refSeqIndex = 0
      for alignIndex in range(len(refSeqAlignment)):
        if refSeqAlignment[alignIndex] == self.gapCode:
          continue
        else:
          for predictionType in self.predictionTypes:
            predValues = [alignedPredictions[predictionType][seqId][alignIndex] for seqId in allSeqIds if alignedPredictions[predictionType][seqId][alignIndex] != None]

            distribInfo = self.getDistribInfo(predValues)

            refSeqPredictionDistribs[predictionType][self.alignRefSeqID].append(alignedPredictions[predictionType][self.alignRefSeqID][alignIndex])

            for i in range(numDistribKeys):
              refSeqPredictionDistribs[predictionType][distribKeys[i]].append(distribInfo[i])

          refSeqPredictionDistribs['sequence'] = sequenceInfo[self.alignRefSeqID]

          refSeqIndex += 1

      # Ready, dump to JSON
      self.dumpJsonToFile(refSeqPredictionDistribs,"Disomine_byAlignment/{}_forRefSeq.json".format(self.alignRefSeqID))
      self.dumpJsonToFile(alignedPredictions,"Disomine_byAlignment/{}_fullAlignment.json".format(self.alignRefSeqID))

  def dumpJsonToFile(self,dictToDump, outFile):

      with open(outFile, 'w+') as outfile:
        json.dump(dictToDump, outfile, indent=4)

  def getDistribInfo(self,valueList, outlierConstant = 1.5):

    median = np.median(valueList)
    upper_quartile = np.percentile(valueList, 75)
    lower_quartile = np.percentile(valueList, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant

    return (median, upper_quartile, lower_quartile,upper_quartile + IQR,lower_quartile - IQR)

if __name__ == '__main__':

  mps = mapPredToMSA()

  mps.doMapping("sars-cov-2/msa_200408")
  #mps.doMapping("sars-cov-2-msa_files")


