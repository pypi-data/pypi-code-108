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
from ai.h2o.sparkling.ml.params.HasCalibrationDataFrame import HasCalibrationDataFrame
from ai.h2o.sparkling.ml.params.HasValidationLabelCol import HasValidationLabelCol


class H2OIsolationForestParams(HasCalibrationDataFrame, HasValidationLabelCol, Params):

    ##
    # Param definitions
    ##
    sampleSize = Param(
        Params._dummy(),
        "sampleSize",
        """Number of randomly sampled observations used to train each Isolation Forest tree. Only one of parameters sample_size and sample_rate should be defined. If sample_rate is defined, sample_size will be ignored.""",
        H2OTypeConverters.toInt())

    sampleRate = Param(
        Params._dummy(),
        "sampleRate",
        """Rate of randomly sampled observations used to train each Isolation Forest tree. Needs to be in range from 0.0 to 1.0. If set to -1, sample_rate is disabled and sample_size will be used instead.""",
        H2OTypeConverters.toFloat())

    mtries = Param(
        Params._dummy(),
        "mtries",
        """Number of variables randomly sampled as candidates at each split. If set to -1, defaults (number of predictors)/3.""",
        H2OTypeConverters.toInt())

    contamination = Param(
        Params._dummy(),
        "contamination",
        """Contamination ratio - the proportion of anomalies in the input dataset. If undefined (-1) the predict function will not mark observations as anomalies and only anomaly score will be returned. Defaults to -1 (undefined).""",
        H2OTypeConverters.toFloat())

    ntrees = Param(
        Params._dummy(),
        "ntrees",
        """Number of trees.""",
        H2OTypeConverters.toInt())

    maxDepth = Param(
        Params._dummy(),
        "maxDepth",
        """Maximum tree depth (0 for unlimited).""",
        H2OTypeConverters.toInt())

    minRows = Param(
        Params._dummy(),
        "minRows",
        """Fewest allowed (weighted) observations in a leaf.""",
        H2OTypeConverters.toFloat())

    seed = Param(
        Params._dummy(),
        "seed",
        """Seed for pseudo random number generator (if applicable)""",
        H2OTypeConverters.toInt())

    buildTreeOneNode = Param(
        Params._dummy(),
        "buildTreeOneNode",
        """Run on one node only; no network overhead but fewer cpus used. Suitable for small datasets.""",
        H2OTypeConverters.toBoolean())

    colSampleRatePerTree = Param(
        Params._dummy(),
        "colSampleRatePerTree",
        """Column sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleRateChangePerLevel = Param(
        Params._dummy(),
        "colSampleRateChangePerLevel",
        """Relative change of the column sampling rate for every level (must be > 0.0 and <= 2.0)""",
        H2OTypeConverters.toFloat())

    scoreTreeInterval = Param(
        Params._dummy(),
        "scoreTreeInterval",
        """Score the model after every so many trees. Disabled if set to 0.""",
        H2OTypeConverters.toInt())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

    categoricalEncoding = Param(
        Params._dummy(),
        "categoricalEncoding",
        """Encoding scheme for categorical features""",
        H2OTypeConverters.toEnumString("hex.Model$Parameters$CategoricalEncodingScheme"))

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

    stoppingRounds = Param(
        Params._dummy(),
        "stoppingRounds",
        """Early stopping based on convergence of stopping_metric. Stop if simple moving average of length k of the stopping_metric does not improve for k:=stopping_rounds scoring events (0 to disable)""",
        H2OTypeConverters.toInt())

    maxRuntimeSecs = Param(
        Params._dummy(),
        "maxRuntimeSecs",
        """Maximum allowed runtime in seconds for model training. Use 0 to disable.""",
        H2OTypeConverters.toFloat())

    stoppingMetric = Param(
        Params._dummy(),
        "stoppingMetric",
        """Metric to use for early stopping (AUTO: logloss for classification, deviance for regression and anonomaly_score for Isolation Forest). Note that custom and custom_increasing can only be used in GBM and DRF with the Python client.""",
        H2OTypeConverters.toEnumString("hex.ScoreKeeper$StoppingMetric"))

    stoppingTolerance = Param(
        Params._dummy(),
        "stoppingTolerance",
        """Relative tolerance for metric-based stopping criterion (stop if relative improvement is not at least this much)""",
        H2OTypeConverters.toFloat())

    exportCheckpointsDir = Param(
        Params._dummy(),
        "exportCheckpointsDir",
        """Automatically export generated models to this directory.""",
        H2OTypeConverters.toNullableString())

    ##
    # Getters
    ##
    def getSampleSize(self):
        return self.getOrDefault(self.sampleSize)

    def getSampleRate(self):
        return self.getOrDefault(self.sampleRate)

    def getMtries(self):
        return self.getOrDefault(self.mtries)

    def getContamination(self):
        return self.getOrDefault(self.contamination)

    def getNtrees(self):
        return self.getOrDefault(self.ntrees)

    def getMaxDepth(self):
        return self.getOrDefault(self.maxDepth)

    def getMinRows(self):
        return self.getOrDefault(self.minRows)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getBuildTreeOneNode(self):
        return self.getOrDefault(self.buildTreeOneNode)

    def getColSampleRatePerTree(self):
        return self.getOrDefault(self.colSampleRatePerTree)

    def getColSampleRateChangePerLevel(self):
        return self.getOrDefault(self.colSampleRateChangePerLevel)

    def getScoreTreeInterval(self):
        return self.getOrDefault(self.scoreTreeInterval)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getCategoricalEncoding(self):
        return self.getOrDefault(self.categoricalEncoding)

    def getIgnoredCols(self):
        return self.getOrDefault(self.ignoredCols)

    def getIgnoreConstCols(self):
        return self.getOrDefault(self.ignoreConstCols)

    def getScoreEachIteration(self):
        return self.getOrDefault(self.scoreEachIteration)

    def getStoppingRounds(self):
        return self.getOrDefault(self.stoppingRounds)

    def getMaxRuntimeSecs(self):
        return self.getOrDefault(self.maxRuntimeSecs)

    def getStoppingMetric(self):
        return self.getOrDefault(self.stoppingMetric)

    def getStoppingTolerance(self):
        return self.getOrDefault(self.stoppingTolerance)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    ##
    # Setters
    ##
    def setSampleSize(self, value):
        return self._set(sampleSize=value)

    def setSampleRate(self, value):
        return self._set(sampleRate=value)

    def setMtries(self, value):
        return self._set(mtries=value)

    def setContamination(self, value):
        return self._set(contamination=value)

    def setNtrees(self, value):
        return self._set(ntrees=value)

    def setMaxDepth(self, value):
        return self._set(maxDepth=value)

    def setMinRows(self, value):
        return self._set(minRows=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setBuildTreeOneNode(self, value):
        return self._set(buildTreeOneNode=value)

    def setColSampleRatePerTree(self, value):
        return self._set(colSampleRatePerTree=value)

    def setColSampleRateChangePerLevel(self, value):
        return self._set(colSampleRateChangePerLevel=value)

    def setScoreTreeInterval(self, value):
        return self._set(scoreTreeInterval=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setCategoricalEncoding(self, value):
        return self._set(categoricalEncoding=value)

    def setIgnoredCols(self, value):
        return self._set(ignoredCols=value)

    def setIgnoreConstCols(self, value):
        return self._set(ignoreConstCols=value)

    def setScoreEachIteration(self, value):
        return self._set(scoreEachIteration=value)

    def setStoppingRounds(self, value):
        return self._set(stoppingRounds=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setStoppingMetric(self, value):
        return self._set(stoppingMetric=value)

    def setStoppingTolerance(self, value):
        return self._set(stoppingTolerance=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
