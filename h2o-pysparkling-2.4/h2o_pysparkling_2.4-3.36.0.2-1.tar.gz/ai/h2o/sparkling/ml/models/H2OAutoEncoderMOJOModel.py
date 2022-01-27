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

from ai.h2o.sparkling.ml.models.H2OAutoEncoderMOJOBase import H2OAutoEncoderMOJOBase
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters
from ai.h2o.sparkling.ml.params.HasIgnoredColsOnMOJO import HasIgnoredColsOnMOJO


class H2OAutoEncoderMOJOModel(H2OAutoEncoderMOJOBase, HasIgnoredColsOnMOJO):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OAutoEncoderMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OAutoEncoderMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OAutoEncoderMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getActivation(self):
        value = self._java_obj.getActivation()
        return value


    def getHidden(self):
        value = self._java_obj.getHidden()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getEpochs(self):
        value = self._java_obj.getEpochs()
        return value


    def getTrainSamplesPerIteration(self):
        value = self._java_obj.getTrainSamplesPerIteration()
        return value


    def getTargetRatioCommToComp(self):
        value = self._java_obj.getTargetRatioCommToComp()
        return value


    def getSeed(self):
        value = self._java_obj.getSeed()
        return value


    def getAdaptiveRate(self):
        value = self._java_obj.getAdaptiveRate()
        return value


    def getRho(self):
        value = self._java_obj.getRho()
        return value


    def getEpsilon(self):
        value = self._java_obj.getEpsilon()
        return value


    def getRate(self):
        value = self._java_obj.getRate()
        return value


    def getRateAnnealing(self):
        value = self._java_obj.getRateAnnealing()
        return value


    def getRateDecay(self):
        value = self._java_obj.getRateDecay()
        return value


    def getMomentumStart(self):
        value = self._java_obj.getMomentumStart()
        return value


    def getMomentumRamp(self):
        value = self._java_obj.getMomentumRamp()
        return value


    def getMomentumStable(self):
        value = self._java_obj.getMomentumStable()
        return value


    def getNesterovAcceleratedGradient(self):
        value = self._java_obj.getNesterovAcceleratedGradient()
        return value


    def getInputDropoutRatio(self):
        value = self._java_obj.getInputDropoutRatio()
        return value


    def getHiddenDropoutRatios(self):
        value = self._java_obj.getHiddenDropoutRatios()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getL1(self):
        value = self._java_obj.getL1()
        return value


    def getL2(self):
        value = self._java_obj.getL2()
        return value


    def getMaxW2(self):
        value = self._java_obj.getMaxW2()
        return value


    def getInitialWeightDistribution(self):
        value = self._java_obj.getInitialWeightDistribution()
        return value


    def getInitialWeightScale(self):
        value = self._java_obj.getInitialWeightScale()
        return value


    def getLoss(self):
        value = self._java_obj.getLoss()
        return value


    def getScoreInterval(self):
        value = self._java_obj.getScoreInterval()
        return value


    def getScoreTrainingSamples(self):
        value = self._java_obj.getScoreTrainingSamples()
        return value


    def getScoreValidationSamples(self):
        value = self._java_obj.getScoreValidationSamples()
        return value


    def getScoreDutyCycle(self):
        value = self._java_obj.getScoreDutyCycle()
        return value


    def getQuietMode(self):
        value = self._java_obj.getQuietMode()
        return value


    def getScoreValidationSampling(self):
        value = self._java_obj.getScoreValidationSampling()
        return value


    def getOverwriteWithBestModel(self):
        value = self._java_obj.getOverwriteWithBestModel()
        return value


    def getUseAllFactorLevels(self):
        value = self._java_obj.getUseAllFactorLevels()
        return value


    def getStandardize(self):
        value = self._java_obj.getStandardize()
        return value


    def getDiagnostics(self):
        value = self._java_obj.getDiagnostics()
        return value


    def getCalculateFeatureImportances(self):
        value = self._java_obj.getCalculateFeatureImportances()
        return value


    def getFastMode(self):
        value = self._java_obj.getFastMode()
        return value


    def getForceLoadBalance(self):
        value = self._java_obj.getForceLoadBalance()
        return value


    def getReplicateTrainingData(self):
        value = self._java_obj.getReplicateTrainingData()
        return value


    def getSingleNodeMode(self):
        value = self._java_obj.getSingleNodeMode()
        return value


    def getShuffleTrainingData(self):
        value = self._java_obj.getShuffleTrainingData()
        return value


    def getMissingValuesHandling(self):
        value = self._java_obj.getMissingValuesHandling()
        return value


    def getSparse(self):
        value = self._java_obj.getSparse()
        return value


    def getAverageActivation(self):
        value = self._java_obj.getAverageActivation()
        return value


    def getSparsityBeta(self):
        value = self._java_obj.getSparsityBeta()
        return value


    def getMaxCategoricalFeatures(self):
        value = self._java_obj.getMaxCategoricalFeatures()
        return value


    def getReproducible(self):
        value = self._java_obj.getReproducible()
        return value


    def getExportWeightsAndBiases(self):
        value = self._java_obj.getExportWeightsAndBiases()
        return value


    def getMiniBatchSize(self):
        value = self._java_obj.getMiniBatchSize()
        return value


    def getElasticAveraging(self):
        value = self._java_obj.getElasticAveraging()
        return value


    def getElasticAveragingMovingRate(self):
        value = self._java_obj.getElasticAveragingMovingRate()
        return value


    def getElasticAveragingRegularization(self):
        value = self._java_obj.getElasticAveragingRegularization()
        return value


    def getWeightCol(self):
        value = self._java_obj.getWeightCol()
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


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


