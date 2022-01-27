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

from ai.h2o.sparkling.ml.models.H2OGLRMMOJOBase import H2OGLRMMOJOBase
from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters


class H2OGLRMMOJOModel(H2OGLRMMOJOBase):

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OGLRMMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OGLRMMOJOModel(javaModel)


    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [H2OGLRMMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


    def getTransform(self):
        value = self._java_obj.getTransform()
        return value


    def getK(self):
        value = self._java_obj.getK()
        return value


    def getLoss(self):
        value = self._java_obj.getLoss()
        return value


    def getMultiLoss(self):
        value = self._java_obj.getMultiLoss()
        return value


    def getLossByCol(self):
        value = self._java_obj.getLossByCol()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getPeriod(self):
        value = self._java_obj.getPeriod()
        return value


    def getRegularizationX(self):
        value = self._java_obj.getRegularizationX()
        return value


    def getRegularizationY(self):
        value = self._java_obj.getRegularizationY()
        return value


    def getGammaX(self):
        value = self._java_obj.getGammaX()
        return value


    def getGammaY(self):
        value = self._java_obj.getGammaY()
        return value


    def getMaxIterations(self):
        value = self._java_obj.getMaxIterations()
        return value


    def getMaxUpdates(self):
        value = self._java_obj.getMaxUpdates()
        return value


    def getInitStepSize(self):
        value = self._java_obj.getInitStepSize()
        return value


    def getMinStepSize(self):
        value = self._java_obj.getMinStepSize()
        return value


    def getSeed(self):
        value = self._java_obj.getSeed()
        return value


    def getInit(self):
        value = self._java_obj.getInit()
        return value


    def getSvdMethod(self):
        value = self._java_obj.getSvdMethod()
        return value


    def getLoadingName(self):
        value = self._java_obj.getLoadingName()
        return value


    def getRepresentationName(self):
        value = self._java_obj.getRepresentationName()
        return value


    def getExpandUserY(self):
        value = self._java_obj.getExpandUserY()
        return value


    def getImputeOriginal(self):
        value = self._java_obj.getImputeOriginal()
        return value


    def getRecoverSvd(self):
        value = self._java_obj.getRecoverSvd()
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


    def getMaxRuntimeSecs(self):
        value = self._java_obj.getMaxRuntimeSecs()
        return value


    def getExportCheckpointsDir(self):
        value = self._java_obj.getExportCheckpointsDir()
        return value


    def getIterations(self):
        value = self._java_obj.getIterations()
        return value


    def getUpdates(self):
        value = self._java_obj.getUpdates()
        return value


    def getObjective(self):
        value = self._java_obj.getObjective()
        return value


    def getAvgChangeObj(self):
        value = self._java_obj.getAvgChangeObj()
        return value


    def getStepSize(self):
        value = self._java_obj.getStepSize()
        return value


    def getArchetypes(self):
        value = self._java_obj.getArchetypes()
        return H2OTypeConverters.scalaToPythonDataFrame(value)


    def getSingularVals(self):
        value = self._java_obj.getSingularVals()
        return H2OTypeConverters.scalaArrayToPythonArray(value)


    def getEigenvectors(self):
        value = self._java_obj.getEigenvectors()
        return H2OTypeConverters.scalaToPythonDataFrame(value)


    def getImportance(self):
        value = self._java_obj.getImportance()
        return H2OTypeConverters.scalaToPythonDataFrame(value)
