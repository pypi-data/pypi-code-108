#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pyspark.ml.param import *
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters
from ai.h2o.sparkling.ml.params.HasPreTrained import HasPreTrained


class Word2VecParamsV3(HasPreTrained, Params):

    ##
    # Param definitions
    ##
    vecSize = Param(
        Params._dummy(),
        "vecSize",
        """Set size of word vectors""",
        H2OTypeConverters.toInt())

    windowSize = Param(
        Params._dummy(),
        "windowSize",
        """Set max skip length between words""",
        H2OTypeConverters.toInt())

    sentSampleRate = Param(
        Params._dummy(),
        "sentSampleRate",
        """Set threshold for occurrence of words. Those that appear with higher frequency in the training data
		will be randomly down-sampled; useful range is (0, 1e-5)""",
        H2OTypeConverters.toFloat())

    normModel = Param(
        Params._dummy(),
        "normModel",
        """Use Hierarchical Softmax""",
        H2OTypeConverters.toEnumString("hex.word2vec.Word2Vec$NormModel"))

    epochs = Param(
        Params._dummy(),
        "epochs",
        """Number of training iterations to run""",
        H2OTypeConverters.toInt())

    minWordFreq = Param(
        Params._dummy(),
        "minWordFreq",
        """This will discard words that appear less than <int> times""",
        H2OTypeConverters.toInt())

    initLearningRate = Param(
        Params._dummy(),
        "initLearningRate",
        """Set the starting learning rate""",
        H2OTypeConverters.toFloat())

    wordModel = Param(
        Params._dummy(),
        "wordModel",
        """The word model to use (SkipGram or CBOW)""",
        H2OTypeConverters.toEnumString("hex.word2vec.Word2Vec$WordModel"))

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

    maxRuntimeSecs = Param(
        Params._dummy(),
        "maxRuntimeSecs",
        """Maximum allowed runtime in seconds for model training. Use 0 to disable.""",
        H2OTypeConverters.toFloat())

    exportCheckpointsDir = Param(
        Params._dummy(),
        "exportCheckpointsDir",
        """Automatically export generated models to this directory.""",
        H2OTypeConverters.toNullableString())

    ##
    # Getters
    ##
    def getVecSize(self):
        return self.getOrDefault(self.vecSize)

    def getWindowSize(self):
        return self.getOrDefault(self.windowSize)

    def getSentSampleRate(self):
        return self.getOrDefault(self.sentSampleRate)

    def getNormModel(self):
        return self.getOrDefault(self.normModel)

    def getEpochs(self):
        return self.getOrDefault(self.epochs)

    def getMinWordFreq(self):
        return self.getOrDefault(self.minWordFreq)

    def getInitLearningRate(self):
        return self.getOrDefault(self.initLearningRate)

    def getWordModel(self):
        return self.getOrDefault(self.wordModel)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getMaxRuntimeSecs(self):
        return self.getOrDefault(self.maxRuntimeSecs)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    ##
    # Setters
    ##
    def setVecSize(self, value):
        return self._set(vecSize=value)

    def setWindowSize(self, value):
        return self._set(windowSize=value)

    def setSentSampleRate(self, value):
        return self._set(sentSampleRate=value)

    def setNormModel(self, value):
        return self._set(normModel=value)

    def setEpochs(self, value):
        return self._set(epochs=value)

    def setMinWordFreq(self, value):
        return self._set(minWordFreq=value)

    def setInitLearningRate(self, value):
        return self._set(initLearningRate=value)

    def setWordModel(self, value):
        return self._set(wordModel=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
