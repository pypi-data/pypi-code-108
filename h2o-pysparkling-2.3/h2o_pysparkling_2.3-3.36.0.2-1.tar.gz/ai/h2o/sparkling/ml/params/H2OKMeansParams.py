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
from ai.h2o.sparkling.ml.params.HasUserPoints import HasUserPoints
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols


class H2OKMeansParams(HasUserPoints, HasIgnoredCols, Params):

    ##
    # Param definitions
    ##
    maxIterations = Param(
        Params._dummy(),
        "maxIterations",
        """Maximum training iterations (if estimate_k is enabled, then this is for each inner Lloyds iteration)""",
        H2OTypeConverters.toInt())

    standardize = Param(
        Params._dummy(),
        "standardize",
        """Standardize columns before computing distances""",
        H2OTypeConverters.toBoolean())

    seed = Param(
        Params._dummy(),
        "seed",
        """RNG Seed""",
        H2OTypeConverters.toInt())

    init = Param(
        Params._dummy(),
        "init",
        """Initialization mode""",
        H2OTypeConverters.toEnumString("hex.kmeans.KMeans$Initialization"))

    estimateK = Param(
        Params._dummy(),
        "estimateK",
        """Whether to estimate the number of clusters (<=k) iteratively and deterministically.""",
        H2OTypeConverters.toBoolean())

    clusterSizeConstraints = Param(
        Params._dummy(),
        "clusterSizeConstraints",
        """An array specifying the minimum number of points that should be in each cluster. The length of the constraints array has to be the same as the number of clusters.""",
        H2OTypeConverters.toNullableListInt())

    k = Param(
        Params._dummy(),
        "k",
        """The max. number of clusters. If estimate_k is disabled, the model will find k centroids, otherwise it will find up to k centroids.""",
        H2OTypeConverters.toInt())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

    nfolds = Param(
        Params._dummy(),
        "nfolds",
        """Number of folds for K-fold cross-validation (0 to disable or >= 2).""",
        H2OTypeConverters.toInt())

    keepCrossValidationModels = Param(
        Params._dummy(),
        "keepCrossValidationModels",
        """Whether to keep the cross-validation models.""",
        H2OTypeConverters.toBoolean())

    keepCrossValidationPredictions = Param(
        Params._dummy(),
        "keepCrossValidationPredictions",
        """Whether to keep the predictions of the cross-validation models.""",
        H2OTypeConverters.toBoolean())

    keepCrossValidationFoldAssignment = Param(
        Params._dummy(),
        "keepCrossValidationFoldAssignment",
        """Whether to keep the cross-validation fold assignment.""",
        H2OTypeConverters.toBoolean())

    foldCol = Param(
        Params._dummy(),
        "foldCol",
        """Column with cross-validation fold index assignment per observation.""",
        H2OTypeConverters.toNullableString())

    foldAssignment = Param(
        Params._dummy(),
        "foldAssignment",
        """Cross-validation fold assignment scheme, if fold_column is not specified. The 'Stratified' option will stratify the folds based on the response variable, for classification problems.""",
        H2OTypeConverters.toEnumString("hex.Model$Parameters$FoldAssignmentScheme"))

    categoricalEncoding = Param(
        Params._dummy(),
        "categoricalEncoding",
        """Encoding scheme for categorical features""",
        H2OTypeConverters.toEnumString("hex.Model$Parameters$CategoricalEncodingScheme"))

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
    def getMaxIterations(self):
        return self.getOrDefault(self.maxIterations)

    def getStandardize(self):
        return self.getOrDefault(self.standardize)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getInit(self):
        return self.getOrDefault(self.init)

    def getEstimateK(self):
        return self.getOrDefault(self.estimateK)

    def getClusterSizeConstraints(self):
        return self.getOrDefault(self.clusterSizeConstraints)

    def getK(self):
        return self.getOrDefault(self.k)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getNfolds(self):
        return self.getOrDefault(self.nfolds)

    def getKeepCrossValidationModels(self):
        return self.getOrDefault(self.keepCrossValidationModels)

    def getKeepCrossValidationPredictions(self):
        return self.getOrDefault(self.keepCrossValidationPredictions)

    def getKeepCrossValidationFoldAssignment(self):
        return self.getOrDefault(self.keepCrossValidationFoldAssignment)

    def getFoldCol(self):
        return self.getOrDefault(self.foldCol)

    def getFoldAssignment(self):
        return self.getOrDefault(self.foldAssignment)

    def getCategoricalEncoding(self):
        return self.getOrDefault(self.categoricalEncoding)

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
    def setMaxIterations(self, value):
        return self._set(maxIterations=value)

    def setStandardize(self, value):
        return self._set(standardize=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setInit(self, value):
        return self._set(init=value)

    def setEstimateK(self, value):
        return self._set(estimateK=value)

    def setClusterSizeConstraints(self, value):
        return self._set(clusterSizeConstraints=value)

    def setK(self, value):
        return self._set(k=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setNfolds(self, value):
        return self._set(nfolds=value)

    def setKeepCrossValidationModels(self, value):
        return self._set(keepCrossValidationModels=value)

    def setKeepCrossValidationPredictions(self, value):
        return self._set(keepCrossValidationPredictions=value)

    def setKeepCrossValidationFoldAssignment(self, value):
        return self._set(keepCrossValidationFoldAssignment=value)

    def setFoldCol(self, value):
        return self._set(foldCol=value)

    def setFoldAssignment(self, value):
        return self._set(foldAssignment=value)

    def setCategoricalEncoding(self, value):
        return self._set(categoricalEncoding=value)

    def setIgnoreConstCols(self, value):
        return self._set(ignoreConstCols=value)

    def setScoreEachIteration(self, value):
        return self._set(scoreEachIteration=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
