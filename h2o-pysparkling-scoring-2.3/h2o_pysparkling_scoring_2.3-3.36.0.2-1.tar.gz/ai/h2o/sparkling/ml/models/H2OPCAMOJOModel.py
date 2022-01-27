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

from ai.h2o.sparkling.ml.models.H2ODimReductionMOJOModel import H2ODimReductionMOJOModel
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters
from ai.h2o.sparkling.ml.params.HasIgnoredColsOnMOJO import HasIgnoredColsOnMOJO


class H2OPCAMOJOModel(H2ODimReductionMOJOModel, HasIgnoredColsOnMOJO):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OPCAMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OPCAMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OPCAMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getTransform(self):
        value = self._java_obj.getTransform()
        return value


    def getPcaMethod(self):
        value = self._java_obj.getPcaMethod()
        return value


    def getPcaImpl(self):
        value = self._java_obj.getPcaImpl()
        return value


    def getK(self):
        value = self._java_obj.getK()
        return value


    def getMaxIterations(self):
        value = self._java_obj.getMaxIterations()
        return value


    def getSeed(self):
        value = self._java_obj.getSeed()
        return value


    def getUseAllFactorLevels(self):
        value = self._java_obj.getUseAllFactorLevels()
        return value


    def getComputeMetrics(self):
        value = self._java_obj.getComputeMetrics()
        return value


    def getImputeMissing(self):
        value = self._java_obj.getImputeMissing()
        return value


    def getIgnoreConstCols(self):
        value = self._java_obj.getIgnoreConstCols()
        return value


    def getScoreEachIteration(self):
        value = self._java_obj.getScoreEachIteration()
        return value


    def getMaxRuntimeSecs(self):
        value = self._java_obj.getMaxRuntimeSecs()
        return value


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


    def getImportance(self):
        value = self._java_obj.getImportance()
        return H2OTypeConverters.scalaToPythonDataFrame(value)


    def getEigenvectors(self):
        value = self._java_obj.getEigenvectors()
        return H2OTypeConverters.scalaToPythonDataFrame(value)


    def getObjective(self):
        value = self._java_obj.getObjective()
        return value
