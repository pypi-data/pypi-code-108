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
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols


class H2OPCAParams(HasIgnoredCols, Params):

    ##
    # Param definitions
    ##
    transform = Param(
        Params._dummy(),
        "transform",
        """Transformation of training data""",
        H2OTypeConverters.toEnumString("hex.DataInfo$TransformType"))

    pcaMethod = Param(
        Params._dummy(),
        "pcaMethod",
        """Specify the algorithm to use for computing the principal components: GramSVD - uses a distributed computation of the Gram matrix, followed by a local SVD; Power - computes the SVD using the power iteration method (experimental); Randomized - uses randomized subspace iteration method; GLRM - fits a generalized low-rank model with L2 loss function and no regularization and solves for the SVD using local matrix algebra (experimental)""",
        H2OTypeConverters.toEnumString("hex.pca.PCAModel$PCAParameters$Method"))

    pcaImpl = Param(
        Params._dummy(),
        "pcaImpl",
        """Specify the implementation to use for computing PCA (via SVD or EVD): MTJ_EVD_DENSEMATRIX - eigenvalue decompositions for dense matrix using MTJ; MTJ_EVD_SYMMMATRIX - eigenvalue decompositions for symmetric matrix using MTJ; MTJ_SVD_DENSEMATRIX - singular-value decompositions for dense matrix using MTJ; JAMA - eigenvalue decompositions for dense matrix using JAMA. References: JAMA - http://math.nist.gov/javanumerics/jama/; MTJ - https://github.com/fommil/matrix-toolkits-java/""",
        H2OTypeConverters.toEnumString("hex.pca.PCAImplementation"))

    k = Param(
        Params._dummy(),
        "k",
        """Rank of matrix approximation""",
        H2OTypeConverters.toInt())

    maxIterations = Param(
        Params._dummy(),
        "maxIterations",
        """Maximum training iterations""",
        H2OTypeConverters.toInt())

    seed = Param(
        Params._dummy(),
        "seed",
        """RNG seed for initialization""",
        H2OTypeConverters.toInt())

    useAllFactorLevels = Param(
        Params._dummy(),
        "useAllFactorLevels",
        """Whether first factor level is included in each categorical expansion""",
        H2OTypeConverters.toBoolean())

    computeMetrics = Param(
        Params._dummy(),
        "computeMetrics",
        """Whether to compute metrics on the training data""",
        H2OTypeConverters.toBoolean())

    imputeMissing = Param(
        Params._dummy(),
        "imputeMissing",
        """Whether to impute missing entries with the column mean""",
        H2OTypeConverters.toBoolean())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

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

    def getPcaMethod(self):
        return self.getOrDefault(self.pcaMethod)

    def getPcaImpl(self):
        return self.getOrDefault(self.pcaImpl)

    def getK(self):
        return self.getOrDefault(self.k)

    def getMaxIterations(self):
        return self.getOrDefault(self.maxIterations)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getUseAllFactorLevels(self):
        return self.getOrDefault(self.useAllFactorLevels)

    def getComputeMetrics(self):
        return self.getOrDefault(self.computeMetrics)

    def getImputeMissing(self):
        return self.getOrDefault(self.imputeMissing)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

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

    def setPcaMethod(self, value):
        return self._set(pcaMethod=value)

    def setPcaImpl(self, value):
        return self._set(pcaImpl=value)

    def setK(self, value):
        return self._set(k=value)

    def setMaxIterations(self, value):
        return self._set(maxIterations=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setUseAllFactorLevels(self, value):
        return self._set(useAllFactorLevels=value)

    def setComputeMetrics(self, value):
        return self._set(computeMetrics=value)

    def setImputeMissing(self, value):
        return self._set(imputeMissing=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setIgnoreConstCols(self, value):
        return self._set(ignoreConstCols=value)

    def setScoreEachIteration(self, value):
        return self._set(scoreEachIteration=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
