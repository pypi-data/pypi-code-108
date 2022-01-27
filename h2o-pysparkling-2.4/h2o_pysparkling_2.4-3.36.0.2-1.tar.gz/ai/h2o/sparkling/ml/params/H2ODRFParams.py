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
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols


class H2ODRFParams(HasCalibrationDataFrame, HasIgnoredCols, Params):

    ##
    # Param definitions
    ##
    mtries = Param(
        Params._dummy(),
        "mtries",
        """Number of variables randomly sampled as candidates at each split. If set to -1, defaults to sqrt{p} for classification and p/3 for regression (where p is the # of predictors""",
        H2OTypeConverters.toInt())

    binomialDoubleTrees = Param(
        Params._dummy(),
        "binomialDoubleTrees",
        """For binary classification: Build 2x as many trees (one per class) - can lead to higher accuracy.""",
        H2OTypeConverters.toBoolean())

    sampleRate = Param(
        Params._dummy(),
        "sampleRate",
        """Row sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    balanceClasses = Param(
        Params._dummy(),
        "balanceClasses",
        """Balance training data class counts via over/under-sampling (for imbalanced data).""",
        H2OTypeConverters.toBoolean())

    classSamplingFactors = Param(
        Params._dummy(),
        "classSamplingFactors",
        """Desired over/under-sampling ratios per class (in lexicographic order). If not specified, sampling factors will be automatically computed to obtain class balance during training. Requires balance_classes.""",
        H2OTypeConverters.toNullableListFloat())

    maxAfterBalanceSize = Param(
        Params._dummy(),
        "maxAfterBalanceSize",
        """Maximum relative size of the training data after balancing class counts (can be less than 1.0). Requires balance_classes.""",
        H2OTypeConverters.toFloat())

    maxConfusionMatrixSize = Param(
        Params._dummy(),
        "maxConfusionMatrixSize",
        """[Deprecated] Maximum size (# classes) for confusion matrices to be printed in the Logs""",
        H2OTypeConverters.toInt())

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

    nbins = Param(
        Params._dummy(),
        "nbins",
        """For numerical columns (real/int), build a histogram of (at least) this many bins, then split at the best point""",
        H2OTypeConverters.toInt())

    nbinsTopLevel = Param(
        Params._dummy(),
        "nbinsTopLevel",
        """For numerical columns (real/int), build a histogram of (at most) this many bins at the root level, then decrease by factor of two per level""",
        H2OTypeConverters.toInt())

    nbinsCats = Param(
        Params._dummy(),
        "nbinsCats",
        """For categorical columns (factors), build a histogram of this many bins, then split at the best point. Higher values can lead to more overfitting.""",
        H2OTypeConverters.toInt())

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

    sampleRatePerClass = Param(
        Params._dummy(),
        "sampleRatePerClass",
        """A list of row sample rates per class (relative fraction for each class, from 0.0 to 1.0), for each tree""",
        H2OTypeConverters.toNullableListFloat())

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

    minSplitImprovement = Param(
        Params._dummy(),
        "minSplitImprovement",
        """Minimum relative improvement in squared error reduction for a split to happen""",
        H2OTypeConverters.toFloat())

    histogramType = Param(
        Params._dummy(),
        "histogramType",
        """What type of histogram to use for finding optimal split points""",
        H2OTypeConverters.toEnumString("hex.tree.SharedTreeModel$SharedTreeParameters$HistogramType"))

    calibrateModel = Param(
        Params._dummy(),
        "calibrateModel",
        """Use Platt Scaling to calculate calibrated class probabilities. Calibration can provide more accurate estimates of class probabilities.""",
        H2OTypeConverters.toBoolean())

    checkConstantResponse = Param(
        Params._dummy(),
        "checkConstantResponse",
        """Check if response column is constant. If enabled, then an exception is thrown if the response column is a constant value.If disabled, then model will train regardless of the response column being a constant value or not.""",
        H2OTypeConverters.toBoolean())

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

    distribution = Param(
        Params._dummy(),
        "distribution",
        """Distribution function""",
        H2OTypeConverters.toEnumString("hex.genmodel.utils.DistributionFamily"))

    labelCol = Param(
        Params._dummy(),
        "labelCol",
        """Response variable column.""",
        H2OTypeConverters.toString())

    weightCol = Param(
        Params._dummy(),
        "weightCol",
        """Column with observation weights. Giving some observation a weight of zero is equivalent to excluding it from the dataset; giving an observation a relative weight of 2 is equivalent to repeating that row twice. Negative weights are not allowed. Note: Weights are per-row observation weights and do not increase the size of the data frame. This is typically the number of times a row is repeated, but non-integer values are supported as well. During training, rows with higher weights matter more, due to the larger loss function pre-factor. If you set weight = 0 for a row, the returned prediction frame at that row is zero and this is incorrect. To get an accurate prediction, remove all rows with weight == 0.""",
        H2OTypeConverters.toNullableString())

    offsetCol = Param(
        Params._dummy(),
        "offsetCol",
        """Offset column. This will be added to the combination of columns before applying the link function.""",
        H2OTypeConverters.toNullableString())

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

    gainsliftBins = Param(
        Params._dummy(),
        "gainsliftBins",
        """Gains/Lift table number of bins. 0 means disabled.. Default value -1 means automatic binning.""",
        H2OTypeConverters.toInt())

    customMetricFunc = Param(
        Params._dummy(),
        "customMetricFunc",
        """Reference to custom evaluation function, format: `language:keyName=funcName`""",
        H2OTypeConverters.toNullableString())

    exportCheckpointsDir = Param(
        Params._dummy(),
        "exportCheckpointsDir",
        """Automatically export generated models to this directory.""",
        H2OTypeConverters.toNullableString())

    aucType = Param(
        Params._dummy(),
        "aucType",
        """Set default multinomial AUC type.""",
        H2OTypeConverters.toEnumString("hex.MultinomialAucType"))

    ##
    # Getters
    ##
    def getMtries(self):
        return self.getOrDefault(self.mtries)

    def getBinomialDoubleTrees(self):
        return self.getOrDefault(self.binomialDoubleTrees)

    def getSampleRate(self):
        return self.getOrDefault(self.sampleRate)

    def getBalanceClasses(self):
        return self.getOrDefault(self.balanceClasses)

    def getClassSamplingFactors(self):
        return self.getOrDefault(self.classSamplingFactors)

    def getMaxAfterBalanceSize(self):
        return self.getOrDefault(self.maxAfterBalanceSize)

    def getMaxConfusionMatrixSize(self):
        return self.getOrDefault(self.maxConfusionMatrixSize)

    def getNtrees(self):
        return self.getOrDefault(self.ntrees)

    def getMaxDepth(self):
        return self.getOrDefault(self.maxDepth)

    def getMinRows(self):
        return self.getOrDefault(self.minRows)

    def getNbins(self):
        return self.getOrDefault(self.nbins)

    def getNbinsTopLevel(self):
        return self.getOrDefault(self.nbinsTopLevel)

    def getNbinsCats(self):
        return self.getOrDefault(self.nbinsCats)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getBuildTreeOneNode(self):
        return self.getOrDefault(self.buildTreeOneNode)

    def getSampleRatePerClass(self):
        return self.getOrDefault(self.sampleRatePerClass)

    def getColSampleRatePerTree(self):
        return self.getOrDefault(self.colSampleRatePerTree)

    def getColSampleRateChangePerLevel(self):
        return self.getOrDefault(self.colSampleRateChangePerLevel)

    def getScoreTreeInterval(self):
        return self.getOrDefault(self.scoreTreeInterval)

    def getMinSplitImprovement(self):
        return self.getOrDefault(self.minSplitImprovement)

    def getHistogramType(self):
        return self.getOrDefault(self.histogramType)

    def getCalibrateModel(self):
        return self.getOrDefault(self.calibrateModel)

    def getCheckConstantResponse(self):
        return self.getOrDefault(self.checkConstantResponse)

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

    def getDistribution(self):
        return self.getOrDefault(self.distribution)

    def getLabelCol(self):
        return self.getOrDefault(self.labelCol)

    def getWeightCol(self):
        return self.getOrDefault(self.weightCol)

    def getOffsetCol(self):
        return self.getOrDefault(self.offsetCol)

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

    def getStoppingRounds(self):
        return self.getOrDefault(self.stoppingRounds)

    def getMaxRuntimeSecs(self):
        return self.getOrDefault(self.maxRuntimeSecs)

    def getStoppingMetric(self):
        return self.getOrDefault(self.stoppingMetric)

    def getStoppingTolerance(self):
        return self.getOrDefault(self.stoppingTolerance)

    def getGainsliftBins(self):
        return self.getOrDefault(self.gainsliftBins)

    def getCustomMetricFunc(self):
        return self.getOrDefault(self.customMetricFunc)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    def getAucType(self):
        return self.getOrDefault(self.aucType)

    ##
    # Setters
    ##
    def setMtries(self, value):
        return self._set(mtries=value)

    def setBinomialDoubleTrees(self, value):
        return self._set(binomialDoubleTrees=value)

    def setSampleRate(self, value):
        return self._set(sampleRate=value)

    def setBalanceClasses(self, value):
        return self._set(balanceClasses=value)

    def setClassSamplingFactors(self, value):
        return self._set(classSamplingFactors=value)

    def setMaxAfterBalanceSize(self, value):
        return self._set(maxAfterBalanceSize=value)

    def setMaxConfusionMatrixSize(self, value):
        return self._set(maxConfusionMatrixSize=value)

    def setNtrees(self, value):
        return self._set(ntrees=value)

    def setMaxDepth(self, value):
        return self._set(maxDepth=value)

    def setMinRows(self, value):
        return self._set(minRows=value)

    def setNbins(self, value):
        return self._set(nbins=value)

    def setNbinsTopLevel(self, value):
        return self._set(nbinsTopLevel=value)

    def setNbinsCats(self, value):
        return self._set(nbinsCats=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setBuildTreeOneNode(self, value):
        return self._set(buildTreeOneNode=value)

    def setSampleRatePerClass(self, value):
        return self._set(sampleRatePerClass=value)

    def setColSampleRatePerTree(self, value):
        return self._set(colSampleRatePerTree=value)

    def setColSampleRateChangePerLevel(self, value):
        return self._set(colSampleRateChangePerLevel=value)

    def setScoreTreeInterval(self, value):
        return self._set(scoreTreeInterval=value)

    def setMinSplitImprovement(self, value):
        return self._set(minSplitImprovement=value)

    def setHistogramType(self, value):
        return self._set(histogramType=value)

    def setCalibrateModel(self, value):
        return self._set(calibrateModel=value)

    def setCheckConstantResponse(self, value):
        return self._set(checkConstantResponse=value)

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

    def setDistribution(self, value):
        return self._set(distribution=value)

    def setLabelCol(self, value):
        return self._set(labelCol=value)

    def setWeightCol(self, value):
        return self._set(weightCol=value)

    def setOffsetCol(self, value):
        return self._set(offsetCol=value)

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

    def setStoppingRounds(self, value):
        return self._set(stoppingRounds=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setStoppingMetric(self, value):
        return self._set(stoppingMetric=value)

    def setStoppingTolerance(self, value):
        return self._set(stoppingTolerance=value)

    def setGainsliftBins(self, value):
        return self._set(gainsliftBins=value)

    def setCustomMetricFunc(self, value):
        return self._set(customMetricFunc=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)

    def setAucType(self, value):
        return self._set(aucType=value)
