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

from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OTreeBasedSupervisedMOJOModelParams
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters
from ai.h2o.sparkling.ml.params.HasMonotoneConstraintsOnMOJO import HasMonotoneConstraintsOnMOJO
from ai.h2o.sparkling.ml.params.HasIgnoredColsOnMOJO import HasIgnoredColsOnMOJO


class H2OGBMMOJOModel(H2OTreeBasedSupervisedMOJOModelParams, HasMonotoneConstraintsOnMOJO, HasIgnoredColsOnMOJO):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OGBMMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OGBMMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OGBMMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getLearnRate(self):
        value = self._java_obj.getLearnRate()
        return value


    def getLearnRateAnnealing(self):
        value = self._java_obj.getLearnRateAnnealing()
        return value


    def getSampleRate(self):
        value = self._java_obj.getSampleRate()
        return value


    def getColSampleRate(self):
        value = self._java_obj.getColSampleRate()
        return value


    def getMaxAbsLeafnodePred(self):
        value = self._java_obj.getMaxAbsLeafnodePred()
        return value


    def getPredNoiseBandwidth(self):
        value = self._java_obj.getPredNoiseBandwidth()
        return value


    def getBalanceClasses(self):
        value = self._java_obj.getBalanceClasses()
        return value


    def getClassSamplingFactors(self):
        value = self._java_obj.getClassSamplingFactors()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getMaxAfterBalanceSize(self):
        value = self._java_obj.getMaxAfterBalanceSize()
        return value


    def getMaxConfusionMatrixSize(self):
        value = self._java_obj.getMaxConfusionMatrixSize()
        return value


    def getMaxDepth(self):
        value = self._java_obj.getMaxDepth()
        return value


    def getMinRows(self):
        value = self._java_obj.getMinRows()
        return value


    def getNbins(self):
        value = self._java_obj.getNbins()
        return value


    def getNbinsTopLevel(self):
        value = self._java_obj.getNbinsTopLevel()
        return value


    def getNbinsCats(self):
        value = self._java_obj.getNbinsCats()
        return value


    def getSeed(self):
        value = self._java_obj.getSeed()
        return value


    def getBuildTreeOneNode(self):
        value = self._java_obj.getBuildTreeOneNode()
        return value


    def getSampleRatePerClass(self):
        value = self._java_obj.getSampleRatePerClass()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getColSampleRatePerTree(self):
        value = self._java_obj.getColSampleRatePerTree()
        return value


    def getColSampleRateChangePerLevel(self):
        value = self._java_obj.getColSampleRateChangePerLevel()
        return value


    def getScoreTreeInterval(self):
        value = self._java_obj.getScoreTreeInterval()
        return value


    def getMinSplitImprovement(self):
        value = self._java_obj.getMinSplitImprovement()
        return value


    def getHistogramType(self):
        value = self._java_obj.getHistogramType()
        return value


    def getCalibrateModel(self):
        value = self._java_obj.getCalibrateModel()
        return value


    def getCheckConstantResponse(self):
        value = self._java_obj.getCheckConstantResponse()
        return value


    def getNfolds(self):
        value = self._java_obj.getNfolds()
        return value


    def getKeepCrossValidationModels(self):
        value = self._java_obj.getKeepCrossValidationModels()
        return value


    def getKeepCrossValidationPredictions(self):
        value = self._java_obj.getKeepCrossValidationPredictions()
        return value


    def getKeepCrossValidationFoldAssignment(self):
        value = self._java_obj.getKeepCrossValidationFoldAssignment()
        return value


    def getDistribution(self):
        value = self._java_obj.getDistribution()
        return value


    def getTweediePower(self):
        value = self._java_obj.getTweediePower()
        return value


    def getQuantileAlpha(self):
        value = self._java_obj.getQuantileAlpha()
        return value


    def getHuberAlpha(self):
        value = self._java_obj.getHuberAlpha()
        return value


    def getLabelCol(self):
        value = self._java_obj.getLabelCol()
        return value


    def getWeightCol(self):
        value = self._java_obj.getWeightCol()
        return value


    def getFoldCol(self):
        value = self._java_obj.getFoldCol()
        return value


    def getFoldAssignment(self):
        value = self._java_obj.getFoldAssignment()
        return value


    def getCategoricalEncoding(self):
        value = self._java_obj.getCategoricalEncoding()
        return value


    def getIgnoreConstCols(self):
        value = self._java_obj.getIgnoreConstCols()
        return value


    def getScoreEachIteration(self):
        value = self._java_obj.getScoreEachIteration()
        return value


    def getStoppingRounds(self):
        value = self._java_obj.getStoppingRounds()
        return value


    def getMaxRuntimeSecs(self):
        value = self._java_obj.getMaxRuntimeSecs()
        return value


    def getStoppingMetric(self):
        value = self._java_obj.getStoppingMetric()
        return value


    def getStoppingTolerance(self):
        value = self._java_obj.getStoppingTolerance()
        return value


    def getGainsliftBins(self):
        value = self._java_obj.getGainsliftBins()
        return value


    def getCustomMetricFunc(self):
        value = self._java_obj.getCustomMetricFunc()
        return value


    def getCustomDistributionFunc(self):
        value = self._java_obj.getCustomDistributionFunc()
        return value


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


    def getAucType(self):
        value = self._java_obj.getAucType()
        return value


