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

from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OSupervisedMOJOModelParams
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters
from ai.h2o.sparkling.ml.params.HasIgnoredColsOnMOJO import HasIgnoredColsOnMOJO
from ai.h2o.sparkling.ml.params.HasGamColsOnMOJO import HasGamColsOnMOJO


class H2OGAMMOJOModel(H2OSupervisedMOJOModelParams, HasIgnoredColsOnMOJO, HasGamColsOnMOJO):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OGAMMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OGAMMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OGAMMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getFamily(self):
        value = self._java_obj.getFamily()
        return value


    def getTweedieVariancePower(self):
        value = self._java_obj.getTweedieVariancePower()
        return value


    def getTweedieLinkPower(self):
        value = self._java_obj.getTweedieLinkPower()
        return value


    def getTheta(self):
        value = self._java_obj.getTheta()
        return value


    def getSolver(self):
        value = self._java_obj.getSolver()
        return value


    def getAlphaValue(self):
        value = self._java_obj.getAlphaValue()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getLambdaValue(self):
        value = self._java_obj.getLambdaValue()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getStartval(self):
        value = self._java_obj.getStartval()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getLambdaSearch(self):
        value = self._java_obj.getLambdaSearch()
        return value


    def getEarlyStopping(self):
        value = self._java_obj.getEarlyStopping()
        return value


    def getNlambdas(self):
        value = self._java_obj.getNlambdas()
        return value


    def getStandardize(self):
        value = self._java_obj.getStandardize()
        return value


    def getMissingValuesHandling(self):
        value = self._java_obj.getMissingValuesHandling()
        return value


    def getNonNegative(self):
        value = self._java_obj.getNonNegative()
        return value


    def getMaxIterations(self):
        value = self._java_obj.getMaxIterations()
        return value


    def getBetaEpsilon(self):
        value = self._java_obj.getBetaEpsilon()
        return value


    def getObjectiveEpsilon(self):
        value = self._java_obj.getObjectiveEpsilon()
        return value


    def getGradientEpsilon(self):
        value = self._java_obj.getGradientEpsilon()
        return value


    def getObjReg(self):
        value = self._java_obj.getObjReg()
        return value


    def getLink(self):
        value = self._java_obj.getLink()
        return value


    def getIntercept(self):
        value = self._java_obj.getIntercept()
        return value


    def getPrior(self):
        value = self._java_obj.getPrior()
        return value


    def getColdStart(self):
        value = self._java_obj.getColdStart()
        return value


    def getMaxActivePredictors(self):
        value = self._java_obj.getMaxActivePredictors()
        return value


    def getInteractions(self):
        value = self._java_obj.getInteractions()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


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


    def getComputePValues(self):
        value = self._java_obj.getComputePValues()
        return value


    def getRemoveCollinearCols(self):
        value = self._java_obj.getRemoveCollinearCols()
        return value


    def getNumKnots(self):
        value = self._java_obj.getNumKnots()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getScale(self):
        value = self._java_obj.getScale()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getBs(self):
        value = self._java_obj.getBs()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getKeepGamCols(self):
        value = self._java_obj.getKeepGamCols()
        return value


    def getStandardizeTpGamCols(self):
        value = self._java_obj.getStandardizeTpGamCols()
        return value


    def getScaleTpPenaltyMat(self):
        value = self._java_obj.getScaleTpPenaltyMat()
        return value


    def getKnotIds(self):
        value = self._java_obj.getKnotIds()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


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


    def getCustomMetricFunc(self):
        value = self._java_obj.getCustomMetricFunc()
        return value


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


    def getAucType(self):
        value = self._java_obj.getAucType()
        return value


