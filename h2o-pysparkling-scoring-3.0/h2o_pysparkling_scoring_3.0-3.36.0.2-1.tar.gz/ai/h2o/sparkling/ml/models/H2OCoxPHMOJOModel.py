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


class H2OCoxPHMOJOModel(H2OSupervisedMOJOModelParams, HasIgnoredColsOnMOJO):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OCoxPHMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OCoxPHMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OCoxPHMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getStartCol(self):
        value = self._java_obj.getStartCol()
        return value


    def getStopCol(self):
        value = self._java_obj.getStopCol()
        return value


    def getStratifyBy(self):
        value = self._java_obj.getStratifyBy()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getTies(self):
        value = self._java_obj.getTies()
        return value


    def getInit(self):
        value = self._java_obj.getInit()
        return value


    def getLreMin(self):
        value = self._java_obj.getLreMin()
        return value


    def getMaxIterations(self):
        value = self._java_obj.getMaxIterations()
        return value


    def getInteractionsOnly(self):
        value = self._java_obj.getInteractionsOnly()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getInteractions(self):
        value = self._java_obj.getInteractions()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getUseAllFactorLevels(self):
        value = self._java_obj.getUseAllFactorLevels()
        return value


    def getSingleNodeMode(self):
        value = self._java_obj.getSingleNodeMode()
        return value


    def getLabelCol(self):
        value = self._java_obj.getLabelCol()
        return value


    def getWeightCol(self):
        value = self._java_obj.getWeightCol()
        return value


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


