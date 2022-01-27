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
from ai.h2o.sparkling.ml.params.HasMonotoneConstraints import HasMonotoneConstraints
from ai.h2o.sparkling.ml.params.HasCalibrationDataFrame import HasCalibrationDataFrame
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols


class H2OXGBoostParams(HasMonotoneConstraints, HasCalibrationDataFrame, HasIgnoredCols, Params):

    ##
    # Param definitions
    ##
    ntrees = Param(
        Params._dummy(),
        "ntrees",
        """(same as n_estimators) Number of trees.""",
        H2OTypeConverters.toInt())

    maxDepth = Param(
        Params._dummy(),
        "maxDepth",
        """Maximum tree depth (0 for unlimited).""",
        H2OTypeConverters.toInt())

    minRows = Param(
        Params._dummy(),
        "minRows",
        """(same as min_child_weight) Fewest allowed (weighted) observations in a leaf.""",
        H2OTypeConverters.toFloat())

    minChildWeight = Param(
        Params._dummy(),
        "minChildWeight",
        """(same as min_rows) Fewest allowed (weighted) observations in a leaf.""",
        H2OTypeConverters.toFloat())

    learnRate = Param(
        Params._dummy(),
        "learnRate",
        """(same as eta) Learning rate (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    eta = Param(
        Params._dummy(),
        "eta",
        """(same as learn_rate) Learning rate (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    sampleRate = Param(
        Params._dummy(),
        "sampleRate",
        """(same as subsample) Row sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    subsample = Param(
        Params._dummy(),
        "subsample",
        """(same as sample_rate) Row sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleRate = Param(
        Params._dummy(),
        "colSampleRate",
        """(same as colsample_bylevel) Column sample rate (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleByLevel = Param(
        Params._dummy(),
        "colSampleByLevel",
        """(same as col_sample_rate) Column sample rate (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleRatePerTree = Param(
        Params._dummy(),
        "colSampleRatePerTree",
        """(same as colsample_bytree) Column sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleByTree = Param(
        Params._dummy(),
        "colSampleByTree",
        """(same as col_sample_rate_per_tree) Column sample rate per tree (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    colSampleByNode = Param(
        Params._dummy(),
        "colSampleByNode",
        """Column sample rate per tree node (from 0.0 to 1.0)""",
        H2OTypeConverters.toFloat())

    maxAbsLeafnodePred = Param(
        Params._dummy(),
        "maxAbsLeafnodePred",
        """(same as max_delta_step) Maximum absolute value of a leaf node prediction""",
        H2OTypeConverters.toFloat())

    maxDeltaStep = Param(
        Params._dummy(),
        "maxDeltaStep",
        """(same as max_abs_leafnode_pred) Maximum absolute value of a leaf node prediction""",
        H2OTypeConverters.toFloat())

    scoreTreeInterval = Param(
        Params._dummy(),
        "scoreTreeInterval",
        """Score the model after every so many trees. Disabled if set to 0.""",
        H2OTypeConverters.toInt())

    seed = Param(
        Params._dummy(),
        "seed",
        """Seed for pseudo random number generator (if applicable)""",
        H2OTypeConverters.toInt())

    minSplitImprovement = Param(
        Params._dummy(),
        "minSplitImprovement",
        """(same as gamma) Minimum relative improvement in squared error reduction for a split to happen""",
        H2OTypeConverters.toFloat())

    gamma = Param(
        Params._dummy(),
        "gamma",
        """(same as min_split_improvement) Minimum relative improvement in squared error reduction for a split to happen""",
        H2OTypeConverters.toFloat())

    nthread = Param(
        Params._dummy(),
        "nthread",
        """Number of parallel threads that can be used to run XGBoost. Cannot exceed H2O cluster limits (-nthreads parameter). Defaults to maximum available""",
        H2OTypeConverters.toInt())

    buildTreeOneNode = Param(
        Params._dummy(),
        "buildTreeOneNode",
        """Run on one node only; no network overhead but fewer cpus used. Suitable for small datasets.""",
        H2OTypeConverters.toBoolean())

    saveMatrixDirectory = Param(
        Params._dummy(),
        "saveMatrixDirectory",
        """Directory where to save matrices passed to XGBoost library. Useful for debugging.""",
        H2OTypeConverters.toNullableString())

    calibrateModel = Param(
        Params._dummy(),
        "calibrateModel",
        """Use Platt Scaling to calculate calibrated class probabilities. Calibration can provide more accurate estimates of class probabilities.""",
        H2OTypeConverters.toBoolean())

    maxBins = Param(
        Params._dummy(),
        "maxBins",
        """For tree_method=hist only: maximum number of bins""",
        H2OTypeConverters.toInt())

    maxLeaves = Param(
        Params._dummy(),
        "maxLeaves",
        """For tree_method=hist only: maximum number of leaves""",
        H2OTypeConverters.toInt())

    treeMethod = Param(
        Params._dummy(),
        "treeMethod",
        """Tree method""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$TreeMethod"))

    growPolicy = Param(
        Params._dummy(),
        "growPolicy",
        """Grow policy - depthwise is standard GBM, lossguide is LightGBM""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$GrowPolicy"))

    booster = Param(
        Params._dummy(),
        "booster",
        """Booster type""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$Booster"))

    regLambda = Param(
        Params._dummy(),
        "regLambda",
        """L2 regularization""",
        H2OTypeConverters.toFloat())

    regAlpha = Param(
        Params._dummy(),
        "regAlpha",
        """L1 regularization""",
        H2OTypeConverters.toFloat())

    quietMode = Param(
        Params._dummy(),
        "quietMode",
        """Enable quiet mode""",
        H2OTypeConverters.toBoolean())

    sampleType = Param(
        Params._dummy(),
        "sampleType",
        """For booster=dart only: sample_type""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$DartSampleType"))

    normalizeType = Param(
        Params._dummy(),
        "normalizeType",
        """For booster=dart only: normalize_type""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$DartNormalizeType"))

    rateDrop = Param(
        Params._dummy(),
        "rateDrop",
        """For booster=dart only: rate_drop (0..1)""",
        H2OTypeConverters.toFloat())

    oneDrop = Param(
        Params._dummy(),
        "oneDrop",
        """For booster=dart only: one_drop""",
        H2OTypeConverters.toBoolean())

    skipDrop = Param(
        Params._dummy(),
        "skipDrop",
        """For booster=dart only: skip_drop (0..1)""",
        H2OTypeConverters.toFloat())

    dmatrixType = Param(
        Params._dummy(),
        "dmatrixType",
        """Type of DMatrix. For sparse, NAs and 0 are treated equally.""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$DMatrixType"))

    backend = Param(
        Params._dummy(),
        "backend",
        """Backend. By default (auto), a GPU is used if available.""",
        H2OTypeConverters.toEnumString("hex.tree.xgboost.XGBoostModel$XGBoostParameters$Backend"))

    gpuId = Param(
        Params._dummy(),
        "gpuId",
        """Which GPU(s) to use. """,
        H2OTypeConverters.toNullableListInt())

    interactionConstraints = Param(
        Params._dummy(),
        "interactionConstraints",
        """A set of allowed column interactions.""",
        H2OTypeConverters.toNullableListListString())

    scalePosWeight = Param(
        Params._dummy(),
        "scalePosWeight",
        """Controls the effect of observations with positive labels in relation to the observations with negative labels on gradient calculation. Useful for imbalanced problems.""",
        H2OTypeConverters.toFloat())

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

    tweediePower = Param(
        Params._dummy(),
        "tweediePower",
        """Tweedie power for Tweedie regression, must be between 1 and 2.""",
        H2OTypeConverters.toFloat())

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
    def getNtrees(self):
        return self.getOrDefault(self.ntrees)

    def getMaxDepth(self):
        return self.getOrDefault(self.maxDepth)

    def getMinRows(self):
        return self.getOrDefault(self.minRows)

    def getMinChildWeight(self):
        return self.getOrDefault(self.minChildWeight)

    def getLearnRate(self):
        return self.getOrDefault(self.learnRate)

    def getEta(self):
        return self.getOrDefault(self.eta)

    def getSampleRate(self):
        return self.getOrDefault(self.sampleRate)

    def getSubsample(self):
        return self.getOrDefault(self.subsample)

    def getColSampleRate(self):
        return self.getOrDefault(self.colSampleRate)

    def getColSampleByLevel(self):
        return self.getOrDefault(self.colSampleByLevel)

    def getColSampleRatePerTree(self):
        return self.getOrDefault(self.colSampleRatePerTree)

    def getColSampleByTree(self):
        return self.getOrDefault(self.colSampleByTree)

    def getColSampleByNode(self):
        return self.getOrDefault(self.colSampleByNode)

    def getMaxAbsLeafnodePred(self):
        return self.getOrDefault(self.maxAbsLeafnodePred)

    def getMaxDeltaStep(self):
        return self.getOrDefault(self.maxDeltaStep)

    def getScoreTreeInterval(self):
        return self.getOrDefault(self.scoreTreeInterval)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getMinSplitImprovement(self):
        return self.getOrDefault(self.minSplitImprovement)

    def getGamma(self):
        return self.getOrDefault(self.gamma)

    def getNthread(self):
        return self.getOrDefault(self.nthread)

    def getBuildTreeOneNode(self):
        return self.getOrDefault(self.buildTreeOneNode)

    def getSaveMatrixDirectory(self):
        return self.getOrDefault(self.saveMatrixDirectory)

    def getCalibrateModel(self):
        return self.getOrDefault(self.calibrateModel)

    def getMaxBins(self):
        return self.getOrDefault(self.maxBins)

    def getMaxLeaves(self):
        return self.getOrDefault(self.maxLeaves)

    def getTreeMethod(self):
        return self.getOrDefault(self.treeMethod)

    def getGrowPolicy(self):
        return self.getOrDefault(self.growPolicy)

    def getBooster(self):
        return self.getOrDefault(self.booster)

    def getRegLambda(self):
        return self.getOrDefault(self.regLambda)

    def getRegAlpha(self):
        return self.getOrDefault(self.regAlpha)

    def getQuietMode(self):
        return self.getOrDefault(self.quietMode)

    def getSampleType(self):
        return self.getOrDefault(self.sampleType)

    def getNormalizeType(self):
        return self.getOrDefault(self.normalizeType)

    def getRateDrop(self):
        return self.getOrDefault(self.rateDrop)

    def getOneDrop(self):
        return self.getOrDefault(self.oneDrop)

    def getSkipDrop(self):
        return self.getOrDefault(self.skipDrop)

    def getDmatrixType(self):
        return self.getOrDefault(self.dmatrixType)

    def getBackend(self):
        return self.getOrDefault(self.backend)

    def getGpuId(self):
        return self.getOrDefault(self.gpuId)

    def getInteractionConstraints(self):
        return self.getOrDefault(self.interactionConstraints)

    def getScalePosWeight(self):
        return self.getOrDefault(self.scalePosWeight)

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

    def getTweediePower(self):
        return self.getOrDefault(self.tweediePower)

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

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    def getAucType(self):
        return self.getOrDefault(self.aucType)

    ##
    # Setters
    ##
    def setNtrees(self, value):
        return self._set(ntrees=value)

    def setMaxDepth(self, value):
        return self._set(maxDepth=value)

    def setMinRows(self, value):
        return self._set(minRows=value)

    def setMinChildWeight(self, value):
        return self._set(minChildWeight=value)

    def setLearnRate(self, value):
        return self._set(learnRate=value)

    def setEta(self, value):
        return self._set(eta=value)

    def setSampleRate(self, value):
        return self._set(sampleRate=value)

    def setSubsample(self, value):
        return self._set(subsample=value)

    def setColSampleRate(self, value):
        return self._set(colSampleRate=value)

    def setColSampleByLevel(self, value):
        return self._set(colSampleByLevel=value)

    def setColSampleRatePerTree(self, value):
        return self._set(colSampleRatePerTree=value)

    def setColSampleByTree(self, value):
        return self._set(colSampleByTree=value)

    def setColSampleByNode(self, value):
        return self._set(colSampleByNode=value)

    def setMaxAbsLeafnodePred(self, value):
        return self._set(maxAbsLeafnodePred=value)

    def setMaxDeltaStep(self, value):
        return self._set(maxDeltaStep=value)

    def setScoreTreeInterval(self, value):
        return self._set(scoreTreeInterval=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setMinSplitImprovement(self, value):
        return self._set(minSplitImprovement=value)

    def setGamma(self, value):
        return self._set(gamma=value)

    def setNthread(self, value):
        return self._set(nthread=value)

    def setBuildTreeOneNode(self, value):
        return self._set(buildTreeOneNode=value)

    def setSaveMatrixDirectory(self, value):
        return self._set(saveMatrixDirectory=value)

    def setCalibrateModel(self, value):
        return self._set(calibrateModel=value)

    def setMaxBins(self, value):
        return self._set(maxBins=value)

    def setMaxLeaves(self, value):
        return self._set(maxLeaves=value)

    def setTreeMethod(self, value):
        return self._set(treeMethod=value)

    def setGrowPolicy(self, value):
        return self._set(growPolicy=value)

    def setBooster(self, value):
        return self._set(booster=value)

    def setRegLambda(self, value):
        return self._set(regLambda=value)

    def setRegAlpha(self, value):
        return self._set(regAlpha=value)

    def setQuietMode(self, value):
        return self._set(quietMode=value)

    def setSampleType(self, value):
        return self._set(sampleType=value)

    def setNormalizeType(self, value):
        return self._set(normalizeType=value)

    def setRateDrop(self, value):
        return self._set(rateDrop=value)

    def setOneDrop(self, value):
        return self._set(oneDrop=value)

    def setSkipDrop(self, value):
        return self._set(skipDrop=value)

    def setDmatrixType(self, value):
        return self._set(dmatrixType=value)

    def setBackend(self, value):
        return self._set(backend=value)

    def setGpuId(self, value):
        return self._set(gpuId=value)

    def setInteractionConstraints(self, value):
        return self._set(interactionConstraints=value)

    def setScalePosWeight(self, value):
        return self._set(scalePosWeight=value)

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

    def setTweediePower(self, value):
        return self._set(tweediePower=value)

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

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)

    def setAucType(self, value):
        return self._set(aucType=value)
