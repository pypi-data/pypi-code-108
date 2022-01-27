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

from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OTreeBasedUnsupervisedMOJOModelParams
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters


class H2OIsolationForestMOJOModel(H2OTreeBasedUnsupervisedMOJOModelParams):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OIsolationForestMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OIsolationForestMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OIsolationForestMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getSampleSize(self):
        value = self._java_obj.getSampleSize()
        return value


    def getSampleRate(self):
        value = self._java_obj.getSampleRate()
        return value


    def getMtries(self):
        value = self._java_obj.getMtries()
        return value


    def getContamination(self):
        value = self._java_obj.getContamination()
        return value


    def getMaxDepth(self):
        value = self._java_obj.getMaxDepth()
        return value


    def getMinRows(self):
        value = self._java_obj.getMinRows()
        return value


    def getSeed(self):
        value = self._java_obj.getSeed()
        return value


    def getBuildTreeOneNode(self):
        value = self._java_obj.getBuildTreeOneNode()
        return value


    def getColSampleRatePerTree(self):
        value = self._java_obj.getColSampleRatePerTree()
        return value


    def getColSampleRateChangePerLevel(self):
        value = self._java_obj.getColSampleRateChangePerLevel()
        return value


    def getScoreTreeInterval(self):
        value = self._java_obj.getScoreTreeInterval()
        return value


    def getCategoricalEncoding(self):
        value = self._java_obj.getCategoricalEncoding()
        return value


    def getIgnoredCols(self):
        value = self._java_obj.getIgnoredCols()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


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


    def getVariableSplits(self):
        value = self._java_obj.getVariableSplits()
        return H2OTypeConverters.scalaToPythonDataFrame(value)
