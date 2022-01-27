import time
import os
import json

class B2bIo:

  references = [] # Defined in subclass for 'traditional' dynaMine file format output

  #
  # File reading
  #

  def readFasta(self, fileName):

    """
    Reads a FASTA file - from dynaMine.predictor.parsers import DynaMineFileParsers

    :param fileName: Path to the FASTA file
    :return: List of (seqId,sequenceString) tuples
    """

    print("Reading FASTA file {}...".format(fileName))

    # Bypassing FC; much faster to do like this...
    fin = open(fileName)
    lines = fin.readlines()
    fin.close()

    # Quick FASTA read, handles multiple line sequences
    seqs = []
    seqId = None
    sequence = ""
    for line in lines:
      if line.startswith(">"):
        # Consolidate
        if seqId:
          seqs.append((seqId, sequence))
        cols = line.split()
        seqId = self.convertSeqId(cols[0][1:])
        sequence = ""
      elif line.strip():
        sequence += line.strip().replace(' ', '')
    if seqId:
      seqs.append((seqId, sequence))

    return seqs

  def writeFasta(self, fastaFileName, sequences):

    fout = open(fastaFileName, 'w')

    for (seqId, sequence) in sequences:
      fout.write(">{} {}\n".format(seqId, seqId))
      fout.write("{}\n\n".format(sequence))

    fout.close()

  def convertSeqId(self,seqId):

    # Possibility to subclass for nicer identifiers (e.g. uniprot default ones)

    return seqId

  #
  # Wrapper defs for predictions
  #

  def predictFromFasta(self, fastaFile, testMode=False):

    """
    Get predictions in relation to a FASTA file. Prediction type defined by subclass
    :param fastaFile: Path to a FASTA file
    :return: Predictions for a subclass (as stored in allPredictions)
    """

    print("Reading input fasta...", end=' ')
    seqs = self.readFasta(fastaFile)

    if testMode:
       seqs = seqs[:5]

    self.predictSeqs(seqs)

    return self.allPredictions

  def predictSeqs(self,seqs):

    # Defined in subclass
    pass

  #
  # Writing 'classic' DynaMine format files
  #

  def writeAllPredictions(self, identifier, outputDir='dynaMineResults'):

    """
    Writes out all available predictions with identifier as base name into outputDir.
    :param identifier: Base name for the output files
    :keyword outputDir: Default is dynaMineResults/, can be reset to wherever
    :return: None
    """

    if not os.path.exists(outputDir):
      os.makedirs(outputDir)

    seqIds = list(self.allPredictions.keys())
    predictionTypes = list(self.allPredictions[seqIds[0]].keys())
    for predictionType in predictionTypes:
      filePath = os.path.join(outputDir,"{}_{}.pred".format(identifier,predictionType))
      self.writePredictionFile(filePath,predictionType)

  def writePredictionFile(self, outFile, predictionType):

    """
    Write out the predictions to the 'old' DynaMine format.
    Assumes that self.allPredictions is set by a subclass!
    :param outFile: Name of the output file
    :param predictionType: Prediction type (backbone, coil, earlyFolding, ...)
    :return: None
    """

    seqIds = list(self.allPredictions.keys())
    seqIds.sort()

    date = time.strftime("%Y.%m.%d_%H.%M.%S")

    referencesText = self.getPredFileReferences()
    infoText = self.getPredFileInfoText(predictionType)

    (pathName, baseName) = os.path.split(outFile)
    if pathName and not os.path.exists(pathName):
      os.makedirs(pathName)

    fout = open(outFile, 'w')

    for seqId in seqIds:
      fout.write(self.getPredFileHeader().format(infoText, seqId, date, referencesText))

      # TODO: Enable writing out discrete value (or category for backbone?)
      for predInfo in self.allPredictions[seqId][predictionType]:
        fout.write("{}	{:7.3f}\n".format(predInfo[0], predInfo[1]))

    fout.close()

  def getPredFileInfoText(self,predictionType):

    predFileInfoText = """* {:<48s} *\n""".format("{} predictions v{}".format(predictionType, self.version))
    predFileInfoText += "* {:<48s} *\n".format("")
    for infoText in self.infoTexts:
      predFileInfoText += "* {:<48s} *\n".format(infoText)

    return predFileInfoText[:-1]

  def getPredFileReferences(self):

    refText = ""
    for refDoi in self.references:
      refText += "* {:<48s} *\n".format(refDoi)

    return refText[:-1]

  def getPredFileHeader(self):

    predFileHeader = """
****************************************************
{}
*                                                  *
* for {:<45s}*
* on {:<46s}*
*                                                  *
* If you use these data please cite:               *
{}
****************************************************
"""

    return predFileHeader

  #
  # Multiple sequence alignment reading code
  #

  def readAlignments(self, fileName, fileType=None, resetAlignRefSeqID=False, gapCode='-'):

    # This is the gap code used in the alignment file
    self.gapCode = gapCode

    # Reset if required
    if resetAlignRefSeqID:
      self.alignRefSeqID = None

    # Read the file
    fin = open(fileName)
    lines = fin.readlines()
    fin.close()

    # Check which type of alignment file
    if not fileType:
      numLines = len(lines)
      if lines[0].count("CLUSTAL"):
        fileType = "CLUSTAL"
      elif lines[0].startswith("# STOCKHOLM"):
        fileType = 'STOCKHOLM'
      else:
        fastaCount = balibaseCount = psiCount = blastCount = emptyLine = 0
        for line in lines:
          if line.startswith(">"):
            fastaCount += 1
          elif line.startswith("//"):
            balibaseCount += 1
          elif len(line.split()) == 2:
            psiCount += 1
          elif line.startswith("Query") or line.startswith("Sbjct"):
            blastCount += 1
          elif not line.strip():
            emptyLine += 1

        if fastaCount > balibaseCount and fastaCount > blastCount:
          if fileName.endswith('a3m'):
            fileType = 'A3M'
          else:
            fileType = 'FASTA'
        elif blastCount:
          fileType = 'Blast'
        elif balibaseCount:
          fileType = 'BaliBase'
        elif psiCount == numLines - emptyLine:
          fileType = 'PSI'
        else:
          # Check for PHYLIP format
          cols = lines[0].split()
          if len(cols) == 2 and cols[0].isdigit() and cols[1].isdigit():
            fileType = 'PHYLIP'

    assert fileType, "Alignment file not recognised"

    print("Reading {} alignment...".format(fileType))

    self.alignRefSeqID = None
    if fileType == 'CLUSTAL':
      seqAlignments = self.readAlignmentsClustal(lines)
    elif fileType == 'FASTA':
      seqAlignments = self.readAlignmentsFasta(lines)
    elif fileType == 'BaliBase':
      seqAlignments = self.readAlignmentsBalibase(lines)
    elif fileType == 'PSI':
      seqAlignments = self.readAlignmentsPSI(lines)
    elif fileType == 'A3M':
      seqAlignments = self.readAlignmentsA3M(lines)
    elif fileType == 'Blast':
      seqAlignments = self.readAlignmentsBlast(lines)
    elif fileType == 'PHYLIP':
      seqAlignments = self.readAlignmentsPHYLIP(lines)
    elif fileType == 'STOCKHOLM':
      seqAlignments = self.readAlignmentsStockholm(lines)

    return seqAlignments

  def readAlignmentsFasta(self, lines):

    """
    FASTA file alignment
    """

    startReading = True
    seqAlignments = {}

    for line in lines:

      cols = line.split()

      if cols:

        if cols[0].startswith('>'):
          seqId = self.getSeqIdKey(cols[0][1:])
          if not self.alignRefSeqID:
            self.alignRefSeqID = seqId
        else:
          if seqId not in seqAlignments.keys():
            seqAlignments[seqId] = cols[0].upper()
          else:
            # Multiline FASTA
            seqAlignments[seqId] += cols[0].upper()

      else:
        self.setEmptyLineVars()

    return seqAlignments

  def readAlignmentsA3M(self, lines):

    """
    A3M file alignment, need some magic here to align things decently
    """

    startReading = True
    sequences = {}

    for line in lines:

      cols = line.split()

      if cols:

        if cols[0].startswith('>'):
          seqId = self.getSeqIdKey(cols[0][1:])
          if not self.alignRefSeqID:
            self.alignRefSeqID = seqId
        else:
          if seqId not in sequences.keys():
            sequences[seqId] = cols[0]
          else:
            # Multiline FASTA
            sequences[seqId] += cols[0]

      else:
        self.setEmptyLineVars()

    # Now reset sequence indexing. Not trivial, have to track numbering per sequence
    seqIndexes = {}
    seqAlignments = {}

    seqIds = sequences.keys()
    numSeqs = len(seqIds)
    for seqId in seqIds:
      seqIndexes[seqId] = 0
      seqAlignments[seqId] = ""

    # Base on first sequence, is reference!
    while seqIndexes[self.alignRefSeqID] < len(sequences[self.alignRefSeqID]):
      currentColChars = "".join([sequences[seqId][seqIndexes[seqId]] for seqId in seqIds])

      # Clean, no inserts
      if currentColChars == currentColChars.upper():
        for i in range(numSeqs):
          seqAlignments[seqIds[i]] += currentColChars[i]
          seqIndexes[seqIds[i]] += 1
      else:
        for i in range(numSeqs):
          if currentColChars[i].islower():
            seqAlignments[seqIds[i]] += currentColChars[i].upper()
            seqIndexes[seqIds[i]] += 1
          else:
            seqAlignments[seqIds[i]] += self.gapCode

    return seqAlignments

  def readAlignmentsBlast(self, lines):

    print("Warning: BLAST format, not the full sequences in the alignment!")

    sequences = {}
    sequencesQuery = {}

    refQuerySeqId = ""

    maxQueryLen = 0

    for line in lines:

      cols = line.split()

      if cols:

        if cols[0].startswith('>'):
          seqId = self.getSeqIdKey(cols[0][1:])
          if not refQuerySeqId:
            refQuerySeqId = seqId
        elif cols[0].startswith("Query") and cols[0][-1] != '=':
          if seqId not in sequences.keys():
            seqStart = int(cols[1])

            sequences[seqId] = self.gapCode * (seqStart - 1) + ""
            sequencesQuery[seqId] = "X" * (seqStart - 1) + cols[2]
          else:
            sequencesQuery[seqId] += cols[2]
        elif cols[0].startswith("Sbjct"):
          sequences[seqId] += cols[2]

      else:
        self.setEmptyLineVars()

    # Also track query sequence
    self.alignRefSeqID = 'query'
    sequences[self.alignRefSeqID] = sequencesQuery[refQuerySeqId].replace(self.gapCode, "")
    sequencesQuery[self.alignRefSeqID] = sequences['query']
    querySeqLen = len(sequencesQuery[self.alignRefSeqID])

    seqLens = {}

    # Pad all other query seqs, might be bits missing at the end
    for seqId in sequencesQuery.keys():
      seqLens[seqId] = len(sequences[seqId])

    maxSeqLen = max(seqLens.values())

    for seqId in sequencesQuery.keys():
      if len(sequencesQuery[seqId]) < maxSeqLen:
        seqLenDiff = (maxSeqLen - len(sequencesQuery[seqId])) + 1
        sequencesQuery[seqId] += "X" * seqLenDiff
        sequences[seqId] += self.gapCode * seqLenDiff

    # Now reset sequence indexing. Not trivial, have to track numbering per sequence
    seqIndexes = {}

    seqAlignments = {}

    seqIds = sequences.keys()
    numSeqs = len(seqIds)
    for seqId in seqIds:
      seqIndexes[seqId] = 0
      seqAlignments[seqId] = ""

    # Base on query sequence, is reference!
    while max(seqIndexes.values()) <= maxSeqLen:

      # Inserts in query means that all alignments that DO NOT have an insert here need one
      try:
        currentColCharsQuery = "".join([sequencesQuery[seqId][seqIndexes[seqId]] for seqId in seqIds])
      except:
        for seqId in seqIds:
          # if seqIndexes[seqId] == len(sequencesQuery[seqId]):
          print("{:<40s} {} {} {}".format(seqId, seqIndexes[seqId], len(sequencesQuery[seqId]), len(sequences[seqId])))
        raise

      if currentColCharsQuery.count(self.gapCode):
        for i in range(numSeqs):
          seqId = seqIds[i]
          if currentColCharsQuery[i] == self.gapCode:
            try:
              seqAlignments[seqId] += sequences[seqId][seqIndexes[seqId]]
              seqIndexes[seqId] += 1

            except:
              print(
                "{:<40s} {} {} {}".format(seqId, seqIndexes[seqId], len(sequencesQuery[seqId]), len(sequences[seqId])))
              raise

          else:
            seqAlignments[seqId] += self.gapCode

      else:
        for i in range(numSeqs):
          seqId = seqIds[i]
          try:
            seqAlignments[seqId] += sequences[seqId][seqIndexes[seqId]]
            seqIndexes[seqId] += 1
          except:
            print(
              "{:<40s} {} {} {}".format(seqId, seqIndexes[seqId], len(sequencesQuery[seqId]), len(sequences[seqId])))
            raise

    return seqAlignments

  def readAlignmentsBalibase(self, lines):

    """
    BaliBase alignment
    """

    startReading = False
    seqAlignments = {}

    for line in lines:

      if line.startswith("//"):
        startReading = True
        continue

      if startReading:
        cols = line.split()

        if cols:
          seqId = self.getSeqIdKey(cols[0])
          alignment = ''.join(cols[1:])

          if not self.alignRefSeqID:
            self.alignRefSeqID = seqId

          if seqId not in seqAlignments.keys():
            seqAlignments[seqId] = ""

          seqAlignments[seqId] += alignment

        else:
          self.setEmptyLineVars()

    return seqAlignments

  def readAlignmentsClustal(self, lines, uniqueSeqs=False):

    """
    CLUSTAL files

    If uniqueSeqs is True, will add extra suffix to overlapping identifiers occuring more than once, so they end up separately
    """

    startReading = False
    seqAlignments = {}

    for line in lines:

      if line.startswith("CLUSTAL"):
        startReading = True
        continue

      if startReading:
        cols = line.split()

        if cols:
          if len(cols) in (2, 3):

            # Ignore lines with annotation information
            if cols[0][0].count('*') or cols[0][0].count(":") or cols[0][0].count(".") or cols[0].isdigit():
              continue

            seqId = self.getSeqIdKey(cols[0])

            if uniqueSeqs and seqId in seqAlignments.keys():
              for i in range(99):
                newSeqId = "{}_{}".format(seqId, i)
                if newSeqId not in seqAlignments.keys():
                  seqId = newSeqId
                  break

            if not self.validSeqId(seqId):
              continue

            if not self.alignRefSeqID:
              self.alignRefSeqID = seqId

            alignment = cols[1]

            if seqId not in seqAlignments.keys():
              seqAlignments[seqId] = ""

            seqAlignments[seqId] += alignment

        else:
          self.setEmptyLineVars()

    return seqAlignments

  def readAlignmentsPSI(self, lines):

    """
    PSI file alignment
    """

    seqAlignments = {}

    for i in range(len(lines)):

      line = lines[i]

      if not line.strip():
        continue

      (seqId, sequence) = line.split()

      seqId = self.getSeqIdKey(seqId)

      if not self.alignRefSeqID:
        self.alignRefSeqID = seqId

      # For some reason additional - at beginning of sequence for target protein
      if i == 0 and sequence[0] == self.gapCode:
        sequence = sequence[1:]

      if seqId not in seqAlignments.keys():
        seqAlignments[seqId] = ""

      seqAlignments[seqId] += sequence

    return seqAlignments

  def readAlignmentsPHYLIP(self, lines):

    """
    PSI file alignment
    """

    seqAlignments = {}

    seqCounterToId = {}
    seqCounter = 0
    seqStartIndex = 51

    fileInfo = lines[0].split()
    (totalSeqs, seqAlignLen) = [int(count) for count in fileInfo]

    for i in range(1, len(lines)):

      line = lines[i].strip()

      if not line:
        seqCounter = 0
        seqStartIndex = 0

      else:

        sequence = line[seqStartIndex:].replace(" ", "")

        if i <= totalSeqs:
          seqId = self.getSeqIdKey(line[:seqStartIndex].strip())
          seqCounterToId[seqCounter] = seqId
          if not self.alignRefSeqID:
            self.alignRefSeqID = seqId
          seqAlignments[seqId] = ""

        else:
          seqId = seqCounterToId[seqCounter]

        seqAlignments[seqId] += sequence

        seqCounter += 1

    assert totalSeqs == len(seqAlignments), "Mismatch in number of sequences detected and reported"
    assert seqAlignLen == len(seqAlignments[seqId]), "Mismatch in length of alignment detected and reported"

    return seqAlignments

  def readAlignmentsStockholm(self, lines):

    """
    STOCKHOLM alignment file
    """

    seqAlignments = {}

    for line in lines:

      cols = line.split()

      if cols:
        if not cols[0].startswith('#') and not cols[0].startswith("//"):
          seqId = self.getSeqIdKey(cols[0])
          if not self.alignRefSeqID:
            self.alignRefSeqID = seqId
          seqAlignments[seqId] = cols[1].upper()

    return seqAlignments

  def setEmptyLineVars(self):

    # Custom function for subclasses
    pass

  def validSeqId(self, seqId):

    # Checks whether this is a valid sequence ID, can be used for filtering in subclasses
    return True

  def getSeqIdKey(self, seqId):

    # Make a good sequence ID from what's found in the alignment file; used in subclass
    return seqId

  def writeFastaFromAlignment(self, alignFile, outFastaFile):

    #
    # Writes a FASTA file from an alignment
    #

    seqAlignments = self.readAlignments(alignFile)

    self.writeFastaFromSeqAlignmentDict(seqAlignments, outFastaFile)

  def writeFastaFromSeqAlignmentDict(self, seqAlignments, outFastaFile):

    #
    # Writes a FASTA file from an alignment
    #

    seqIds = seqAlignments.keys()
    seqIds.sort()

    fout = open(outFastaFile, 'w')
    for seqId in seqIds:
      fout.write(">{}\n".format(seqId))
      fout.write("{}\n".format(seqAlignments[seqId].replace(self.gapCode, '')))
    fout.close()

  #
  # JSON dumps
  #

  def getAllPredictionsJson(self, identifier, limitPrecision=True):

    """
    Creates JSON string with all available predictions with identifier as base name
    :param identifier: Base name for the output files
    :return: JSON with full information for all predictions done in the subclass
    """

    jsonData = {
      'creation_date': time.strftime("%Y-%m-%dT%H:%M:%S"),
      'id': identifier,
      'information': self.informationPerPredictor,
      'results': []
    }

    seqIds = list(self.allPredictions.keys())
    seqIds.sort()

    predictionTypes = list(self.allPredictions[seqIds[0]].keys())

    for seqId in seqIds:
      sequence = ''.join([resInfo[0] for resInfo in self.allPredictions[seqId][predictionTypes[0]]])
      seqInfo = {'proteinID': seqId, 'sequence': sequence}

      for predictionType in predictionTypes:
        seqInfo[predictionType] = [resInfo[1] for resInfo in self.allPredictions[seqId][predictionType]]
        #print(seqId,predictionType,type(seqInfo[predictionType][0]),seqInfo[predictionType])

      jsonData['results'].append(seqInfo)

    # Limit precision in output, 3 decimals is plenty for this. Doesn't seem to work on Python3.7 any more
    if limitPrecision:
      json.encoder.FLOAT_REPR = lambda o: format(o, '.3f')

    return(json.dumps(jsonData, sort_keys=True, indent=4, separators=(',', ': ')))

  #
  # NEF file handling
  #

  def readNefFile(self,fileName):

    """
    :param fileName: Input NEF file path
    :return: File object with info, if read, otherwise None.
    """

    from .bmrb import File as starReader

    # Note that this nmrStar reader is generic STAR, not specifically for NMR-STAR.
    # If this works, could also be an NMR-STAR file!
    origNefFile = starReader.File(verbosity=2, filename=fileName)

    #
    # Read NEF file (in STAR format)
    #

    if origNefFile.read():
      print("  Error reading NEF file ")
      return None

    return origNefFile

  def readNefFileSequenceShifts(self,fileName):

    """

    Note: this reader is limited, as it only handles the sequence and chemical shift information.
    It will need to be extended for other data types, if that should become necessary.

    :param fileName: Input NEF file path
    :return: dictionary with chainCode as key, then a list of sequence codes (pos 0) and a list of and shift information (pos 1)
    """

    origNefFile = self.readNefFile(fileName)

    sequenceInfo = {}

    if origNefFile:

      #
      # Go through the data in the file
      #

      seqCodeToIndex = {}
      seqSerialToIndex = {}

      currentSaveFrame = None

      for origSaveFrame in origNefFile.datanodes:

        # This is the title of the saveframe
        # print origSaveFrame.title

        for tagtable in origSaveFrame.tagtables:

          if tagtable.free:

            # This is for values directly associated with saveframe, only one value per tagname

            for tagIndex in range(len(tagtable.tagnames)):

              tagName = tagtable.tagnames[tagIndex]
              tagValue = tagtable.tagvalues[tagIndex][0]  # Only one value, always!

              # print tagName, tagValue

              if tagName.endswith('sf_category'):
                currentSaveFrame = tagValue
                # print currentSaveFrame

          else:

            # This is a loop with multiple rows of values for the tags
            # Have to loop over the value index to get rows out

            # print("Table with tags {}".format(",".join(tagtable.tagnames)))
            tags = [tagName.split('.')[-1] for tagName in tagtable.tagnames]

            # print tags

            numTagIndexes = len(tagtable.tagnames)

            # Reading the sequence, comes first
            if currentSaveFrame == 'nef_molecular_system':
              # Using first tag index (0) to get number of data value rows in loop
              seqListIndex = 0
              for valueIndex in range(len(tagtable.tagvalues[0])):
                dataRow = {}
                for tagIndex in range(numTagIndexes):
                  tagValue = tagtable.tagvalues[tagIndex][valueIndex]
                  dataRow[tags[tagIndex]] = tagValue

                chainCode = dataRow['chain_code']
                if chainCode not in sequenceInfo.keys():
                  sequenceInfo[chainCode] = []
                  seqListIndex = 0

                sequenceInfo[chainCode].append((dataRow, []))  # Second list will hold shifts

                seqCodeToIndex[(chainCode,dataRow['sequence_code'])] = seqListIndex
                seqSerialToIndex[(chainCode,dataRow['index'])] = seqListIndex
                seqListIndex += 1

            elif currentSaveFrame == 'nef_chemical_shift_list':
              # print(seqCodeToIndex)

              # Reading shift info and linking to full sequence information
              # Put in a hack below to deal with badly formatted NEF files

              seqCodesValid = True
              for valueIndex in range(len(tagtable.tagvalues[0])):
                dataRow = {}
                for tagIndex in range(numTagIndexes):
                  tagValue = tagtable.tagvalues[tagIndex][valueIndex]
                  dataRow[tags[tagIndex]] = tagValue

                # print(dataRow)
                chainCode = dataRow['chain_code']
                seqCode = dataRow['sequence_code']

                if (chainCode,seqCode) not in seqCodeToIndex.keys():
                  seqCodesValid = False

              # Now read full file
              for valueIndex in range(len(tagtable.tagvalues[0])):
                dataRow = {}
                for tagIndex in range(numTagIndexes):
                  tagValue = tagtable.tagvalues[tagIndex][valueIndex]
                  dataRow[tags[tagIndex]] = tagValue

                # print(dataRow)
                chainCode = dataRow['chain_code']
                seqCode = dataRow['sequence_code']
                if seqCodesValid:
                  seqListIndex = seqCodeToIndex[(chainCode,seqCode)]
                else:
                  # Is really the index here, badly formatted NEF file
                  seqListIndex = seqSerialToIndex[(chainCode,seqCode)]

                # Adding relevant shift info to file, removing redundant stuff first
                del (dataRow['chain_code'])
                del (dataRow['residue_name'])
                del (dataRow['sequence_code'])
                sequenceInfo[chainCode][seqListIndex][-1].append(dataRow)

    return sequenceInfo

  #
  # NMR-STAR file handling
  #

  def readNmrStarProject(self,fileName):

    """
    :param filenNme:  Input NMR-STAR file path
    :return: file content connected to nmrStarFile object
    """

    from b2bTools.general.ccpn.format.nmrStar.projectIO import NmrStarProjectFile

    nmrStarFile = NmrStarProjectFile(fileName)
    readStatus = nmrStarFile.read(verbose=1)

    if not readStatus or not nmrStarFile.sequenceFiles:
      # Not a valid file, reset to None
      nmrStarFile = None

    return nmrStarFile

  def readNmrStarSequenceShifts(self,fileName, original_numbering=True):

    """
    :param fileName: Input NMR-STAR file path
    :param original_numbering: If set to True (Boolean), will retain original sequence code numbering
    :return: dictionary with sequence and shift information
    """

    # Legacy hack for web server side code
    if type(original_numbering) == type(""):
      original_numbering = eval(original_numbering)

    nmrStarFile = self.readNmrStarProject(fileName)

    sequenceInfo = {}

    if nmrStarFile and nmrStarFile.sequenceFiles:

      seqCodeToIndex = {}
      seqSerialToIndex = {}

      # Get protein sequence data out
      chainCodes = 'ABCDEFGHIJKLM'
      chainCodeIndex = 0

      molCodeToChainCode = {}
      seqOffset = 0
      for seqFile in nmrStarFile.sequenceFiles:
        for seq in seqFile.sequences:
          if seq.molType != 'polymer':
            continue
          # print(dir(seq))
          if seq.molName not in molCodeToChainCode.keys():
            currentChainCode = chainCodes[chainCodeIndex]
            molCodeToChainCode[seq.molName] = currentChainCode
            chainCodeIndex += 1

          chainCode = molCodeToChainCode[seq.molName]
          sequenceInfo[chainCode] = []

          valueIndex = 0
          for sequenceEl in seq.elements:
            if original_numbering and hasattr(sequenceEl,'authorSeqCode') and sequenceEl.authorSeqCode != None:
              seqNumber = sequenceEl.authorSeqCode
              if sequenceEl.seqCode == 1:
                seqOffset = int(sequenceEl.authorSeqCode) - 1
            else:
              seqNumber = sequenceEl.seqCode

            # Converting to NEF-like structure here
            dataRow = {'index': sequenceEl.seqCode, 'chain_code': currentChainCode, 'sequence_code': seqNumber, 'residue_name': sequenceEl.code3Letter}

            sequenceInfo[chainCode].append((dataRow, []))

            seqCodeToIndex[dataRow['sequence_code']] = valueIndex
            seqSerialToIndex[dataRow['index']] = valueIndex

            valueIndex += 1

      # Get chemical shift data, bunching all together here in assumption only one saveframe for this
      for chemShiftFile in nmrStarFile.chemShiftFiles:
        for chemShift in chemShiftFile.chemShifts:
          if chemShift.molCode in molCodeToChainCode.keys():
            chainCode = molCodeToChainCode[chemShift.molCode]
          else:
            chainCode = 'A'

          if original_numbering:
            seqNumber = chemShift.seqCode + seqOffset
          else:
            seqNumber = chemShift.seqCode

          dataRow = {'atom_name': chemShift.atomName, 'value': chemShift.value, 'value_uncertainty': chemShift.valueError}

          # print(dataRow)
          seqCode = seqNumber
          seqIndex = seqCodeToIndex[seqNumber]
          sequenceInfo[chainCode][seqIndex][-1].append(dataRow)

    return sequenceInfo

  def convertNmrStarToNef(self,fileName):

    # Legacy code from web server, works only for shifts and sequence info!!

    # Get protein sequence data out
    chainCodes = 'ABCDEFGHIJKLM'
    chainCodeIndex = 0


    sequenceData = StringIO()


    molCodeToChainCode = {}
    seqOffset = 0
    for seqFile in nmrStarFile.sequenceFiles:
      for seq in seqFile.sequences:
        if seq.molType != 'polymer':
          continue
        # print(dir(seq))
        if seq.molName not in molCodeToChainCode.keys():
          currentChainCode = chainCodes[chainCodeIndex]
          molCodeToChainCode[seq.molName] = currentChainCode
          chainCodeIndex += 1
        for sequenceEl in seq.elements:
          if original_numbering == 'True' and sequenceEl.authorSeqCode != None:
            seqNumber = sequenceEl.authorSeqCode
            if sequenceEl.seqCode == 1:
              seqOffset = int(sequenceEl.authorSeqCode) - 1
          else:
            seqNumber = sequenceEl.seqCode

            dataRow = {'index': sequenceEl.seqCode, 'chain_code': currentChainCode, 'sequence_code': seqNumber, 'residue_name': sequenceEl.code3Letter}

          sequenceData.write(
            "                {:4d}  {:s} {:4d} {:3s}  .     .\n".format(sequenceEl.seqCode, currentChainCode,
                                                                        int(seqNumber), sequenceEl.code3Letter))

    # Get chemical shift data, bunching all together here in assumption only one saveframe for this


    shiftData = StringIO()


    for chemShiftFile in nmrStarFile.chemShiftFiles:
      for chemShift in chemShiftFile.chemShifts:
        if chemShift.molCode in molCodeToChainCode.keys():
          chainCode = molCodeToChainCode[chemShift.molCode]
        else:
          chainCode = 'A'

        if original_numbering == 'True':
          seqNumber = chemShift.seqCode + seqOffset
        else:
          seqNumber = chemShift.seqCode

        shiftData.write(
          "                {:s}   {:4d}    {:3s}   {:4s}  {:7.2f}    {:5.2f}\n".format(chainCode, int(seqNumber),
                                                                                       chemShift.resLabel,
                                                                                       chemShift.atomName,
                                                                                       chemShift.value,
                                                                                       chemShift.valueError))
