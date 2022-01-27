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
from ai.h2o.sparkling.ml.params.HasUserX import HasUserX
from ai.h2o.sparkling.ml.params.HasUserY import HasUserY
from ai.h2o.sparkling.ml.params.HasLossByColNames import HasLossByColNames


class H2OGLRMParams(HasUserX, HasUserY, HasLossByColNames, Params):

    ##
    # Param definitions
    ##
    transform = Param(
        Params._dummy(),
        "transform",
        """Transformation of training data""",
        H2OTypeConverters.toEnumString("hex.DataInfo$TransformType"))

    k = Param(
        Params._dummy(),
        "k",
        """Rank of matrix approximation""",
        H2OTypeConverters.toInt())

    loss = Param(
        Params._dummy(),
        "loss",
        """Numeric loss function""",
        H2OTypeConverters.toEnumString("hex.genmodel.algos.glrm.GlrmLoss"))

    multiLoss = Param(
        Params._dummy(),
        "multiLoss",
        """Categorical loss function""",
        H2OTypeConverters.toEnumString("hex.genmodel.algos.glrm.GlrmLoss"))

    lossByCol = Param(
        Params._dummy(),
        "lossByCol",
        """Loss function by column (override)""",
        H2OTypeConverters.toNullableListEnumString("hex.genmodel.algos.glrm.GlrmLoss"))

    period = Param(
        Params._dummy(),
        "period",
        """Length of period (only used with periodic loss function)""",
        H2OTypeConverters.toInt())

    regularizationX = Param(
        Params._dummy(),
        "regularizationX",
        """Regularization function for X matrix""",
        H2OTypeConverters.toEnumString("hex.genmodel.algos.glrm.GlrmRegularizer"))

    regularizationY = Param(
        Params._dummy(),
        "regularizationY",
        """Regularization function for Y matrix""",
        H2OTypeConverters.toEnumString("hex.genmodel.algos.glrm.GlrmRegularizer"))

    gammaX = Param(
        Params._dummy(),
        "gammaX",
        """Regularization weight on X matrix""",
        H2OTypeConverters.toFloat())

    gammaY = Param(
        Params._dummy(),
        "gammaY",
        """Regularization weight on Y matrix""",
        H2OTypeConverters.toFloat())

    maxIterations = Param(
        Params._dummy(),
        "maxIterations",
        """Maximum number of iterations""",
        H2OTypeConverters.toInt())

    maxUpdates = Param(
        Params._dummy(),
        "maxUpdates",
        """Maximum number of updates, defaults to 2*max_iterations""",
        H2OTypeConverters.toInt())

    initStepSize = Param(
        Params._dummy(),
        "initStepSize",
        """Initial step size""",
        H2OTypeConverters.toFloat())

    minStepSize = Param(
        Params._dummy(),
        "minStepSize",
        """Minimum step size""",
        H2OTypeConverters.toFloat())

    seed = Param(
        Params._dummy(),
        "seed",
        """RNG seed for initialization""",
        H2OTypeConverters.toInt())

    init = Param(
        Params._dummy(),
        "init",
        """Initialization mode""",
        H2OTypeConverters.toEnumString("hex.genmodel.algos.glrm.GlrmInitialization"))

    svdMethod = Param(
        Params._dummy(),
        "svdMethod",
        """Method for computing SVD during initialization (Caution: Randomized is currently experimental and unstable)""",
        H2OTypeConverters.toEnumString("hex.svd.SVDModel$SVDParameters$Method"))

    loadingName = Param(
        Params._dummy(),
        "loadingName",
        """[Deprecated] Use representation_name instead.  Frame key to save resulting X.""",
        H2OTypeConverters.toNullableString())

    representationName = Param(
        Params._dummy(),
        "representationName",
        """Frame key to save resulting X""",
        H2OTypeConverters.toNullableString())

    expandUserY = Param(
        Params._dummy(),
        "expandUserY",
        """Expand categorical columns in user-specified initial Y""",
        H2OTypeConverters.toBoolean())

    imputeOriginal = Param(
        Params._dummy(),
        "imputeOriginal",
        """Reconstruct original training data by reversing transform""",
        H2OTypeConverters.toBoolean())

    recoverSvd = Param(
        Params._dummy(),
        "recoverSvd",
        """Recover singular values and eigenvectors of XY""",
        H2OTypeConverters.toBoolean())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

    ignoredCols = Param(
        Params._dummy(),
        "ignoredCols",
        """Names of columns to ignore for training.""",
        H2OTypeConverters.toNullableListString())

    ignoreConstCols = Param(
        Params._dummy(),
        "ignoreConstCols",
        """Ignore constant columns.""",
        H2OTypeConverters.toBoolean())

    scoreEachIteration = Param(
        Params._dummy(),
        "scoreEachIteration",
        """Whether to score during each iteration of model training.""",
        H2OTypeConverters.toBoolean())

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
    def getTransform(self):
        return self.getOrDefault(self.transform)

    def getK(self):
        return self.getOrDefault(self.k)

    def getLoss(self):
        return self.getOrDefault(self.loss)

    def getMultiLoss(self):
        return self.getOrDefault(self.multiLoss)

    def getLossByCol(self):
        return self.getOrDefault(self.lossByCol)

    def getPeriod(self):
        return self.getOrDefault(self.period)

    def getRegularizationX(self):
        return self.getOrDefault(self.regularizationX)

    def getRegularizationY(self):
        return self.getOrDefault(self.regularizationY)

    def getGammaX(self):
        return self.getOrDefault(self.gammaX)

    def getGammaY(self):
        return self.getOrDefault(self.gammaY)

    def getMaxIterations(self):
        return self.getOrDefault(self.maxIterations)

    def getMaxUpdates(self):
        return self.getOrDefault(self.maxUpdates)

    def getInitStepSize(self):
        return self.getOrDefault(self.initStepSize)

    def getMinStepSize(self):
        return self.getOrDefault(self.minStepSize)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getInit(self):
        return self.getOrDefault(self.init)

    def getSvdMethod(self):
        return self.getOrDefault(self.svdMethod)

    def getLoadingName(self):
        return self.getOrDefault(self.loadingName)

    def getRepresentationName(self):
        return self.getOrDefault(self.representationName)

    def getExpandUserY(self):
        return self.getOrDefault(self.expandUserY)

    def getImputeOriginal(self):
        return self.getOrDefault(self.imputeOriginal)

    def getRecoverSvd(self):
        return self.getOrDefault(self.recoverSvd)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getIgnoredCols(self):
        return self.getOrDefault(self.ignoredCols)

    def getIgnoreConstCols(self):
        return self.getOrDefault(self.ignoreConstCols)

    def getScoreEachIteration(self):
        return self.getOrDefault(self.scoreEachIteration)

    def getMaxRuntimeSecs(self):
        return self.getOrDefault(self.maxRuntimeSecs)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    ##
    # Setters
    ##
    def setTransform(self, value):
        return self._set(transform=value)

    def setK(self, value):
        return self._set(k=value)

    def setLoss(self, value):
        return self._set(loss=value)

    def setMultiLoss(self, value):
        return self._set(multiLoss=value)

    def setLossByCol(self, value):
        return self._set(lossByCol=value)

    def setPeriod(self, value):
        return self._set(period=value)

    def setRegularizationX(self, value):
        return self._set(regularizationX=value)

    def setRegularizationY(self, value):
        return self._set(regularizationY=value)

    def setGammaX(self, value):
        return self._set(gammaX=value)

    def setGammaY(self, value):
        return self._set(gammaY=value)

    def setMaxIterations(self, value):
        return self._set(maxIterations=value)

    def setMaxUpdates(self, value):
        return self._set(maxUpdates=value)

    def setInitStepSize(self, value):
        return self._set(initStepSize=value)

    def setMinStepSize(self, value):
        return self._set(minStepSize=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setInit(self, value):
        return self._set(init=value)

    def setSvdMethod(self, value):
        return self._set(svdMethod=value)

    def setLoadingName(self, value):
        return self._set(loadingName=value)

    def setRepresentationName(self, value):
        return self._set(representationName=value)

    def setExpandUserY(self, value):
        return self._set(expandUserY=value)

    def setImputeOriginal(self, value):
        return self._set(imputeOriginal=value)

    def setRecoverSvd(self, value):
        return self._set(recoverSvd=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setIgnoredCols(self, value):
        return self._set(ignoredCols=value)

    def setIgnoreConstCols(self, value):
        return self._set(ignoreConstCols=value)

    def setScoreEachIteration(self, value):
        return self._set(scoreEachIteration=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
