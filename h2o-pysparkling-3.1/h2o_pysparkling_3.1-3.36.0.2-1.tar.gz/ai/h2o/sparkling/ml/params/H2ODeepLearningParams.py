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
from ai.h2o.sparkling.ml.params.HasInitialBiases import HasInitialBiases
from ai.h2o.sparkling.ml.params.HasInitialWeights import HasInitialWeights
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols
from ai.h2o.sparkling.ml.params.HasDeprecatedVariableImportances import HasDeprecatedVariableImportances
from ai.h2o.sparkling.ml.params.HasDeprecatedAutoencoder import HasDeprecatedAutoencoder


class H2ODeepLearningParams(HasInitialBiases, HasInitialWeights, HasIgnoredCols, HasDeprecatedVariableImportances, HasDeprecatedAutoencoder, Params):

    ##
    # Param definitions
    ##
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

    activation = Param(
        Params._dummy(),
        "activation",
        """Activation function.""",
        H2OTypeConverters.toEnumString("hex.deeplearning.DeepLearningModel$DeepLearningParameters$Activation"))

    hidden = Param(
        Params._dummy(),
        "hidden",
        """Hidden layer sizes (e.g. [100, 100]).""",
        H2OTypeConverters.toListInt())

    epochs = Param(
        Params._dummy(),
        "epochs",
        """How many times the dataset should be iterated (streamed), can be fractional.""",
        H2OTypeConverters.toFloat())

    trainSamplesPerIteration = Param(
        Params._dummy(),
        "trainSamplesPerIteration",
        """Number of training samples (globally) per MapReduce iteration. Special values are 0: one epoch, -1: all available data (e.g., replicated training data), -2: automatic.""",
        H2OTypeConverters.toInt())

    targetRatioCommToComp = Param(
        Params._dummy(),
        "targetRatioCommToComp",
        """Target ratio of communication overhead to computation. Only for multi-node operation and train_samples_per_iteration = -2 (auto-tuning).""",
        H2OTypeConverters.toFloat())

    seed = Param(
        Params._dummy(),
        "seed",
        """Seed for random numbers (affects sampling) - Note: only reproducible when running single threaded.""",
        H2OTypeConverters.toInt())

    adaptiveRate = Param(
        Params._dummy(),
        "adaptiveRate",
        """Adaptive learning rate.""",
        H2OTypeConverters.toBoolean())

    rho = Param(
        Params._dummy(),
        "rho",
        """Adaptive learning rate time decay factor (similarity to prior updates).""",
        H2OTypeConverters.toFloat())

    epsilon = Param(
        Params._dummy(),
        "epsilon",
        """Adaptive learning rate smoothing factor (to avoid divisions by zero and allow progress).""",
        H2OTypeConverters.toFloat())

    rate = Param(
        Params._dummy(),
        "rate",
        """Learning rate (higher => less stable, lower => slower convergence).""",
        H2OTypeConverters.toFloat())

    rateAnnealing = Param(
        Params._dummy(),
        "rateAnnealing",
        """Learning rate annealing: rate / (1 + rate_annealing * samples).""",
        H2OTypeConverters.toFloat())

    rateDecay = Param(
        Params._dummy(),
        "rateDecay",
        """Learning rate decay factor between layers (N-th layer: rate * rate_decay ^ (n - 1).""",
        H2OTypeConverters.toFloat())

    momentumStart = Param(
        Params._dummy(),
        "momentumStart",
        """Initial momentum at the beginning of training (try 0.5).""",
        H2OTypeConverters.toFloat())

    momentumRamp = Param(
        Params._dummy(),
        "momentumRamp",
        """Number of training samples for which momentum increases.""",
        H2OTypeConverters.toFloat())

    momentumStable = Param(
        Params._dummy(),
        "momentumStable",
        """Final momentum after the ramp is over (try 0.99).""",
        H2OTypeConverters.toFloat())

    nesterovAcceleratedGradient = Param(
        Params._dummy(),
        "nesterovAcceleratedGradient",
        """Use Nesterov accelerated gradient (recommended).""",
        H2OTypeConverters.toBoolean())

    inputDropoutRatio = Param(
        Params._dummy(),
        "inputDropoutRatio",
        """Input layer dropout ratio (can improve generalization, try 0.1 or 0.2).""",
        H2OTypeConverters.toFloat())

    hiddenDropoutRatios = Param(
        Params._dummy(),
        "hiddenDropoutRatios",
        """Hidden layer dropout ratios (can improve generalization), specify one value per hidden layer, defaults to 0.5.""",
        H2OTypeConverters.toNullableListFloat())

    l1 = Param(
        Params._dummy(),
        "l1",
        """L1 regularization (can add stability and improve generalization, causes many weights to become 0).""",
        H2OTypeConverters.toFloat())

    l2 = Param(
        Params._dummy(),
        "l2",
        """L2 regularization (can add stability and improve generalization, causes many weights to be small.""",
        H2OTypeConverters.toFloat())

    maxW2 = Param(
        Params._dummy(),
        "maxW2",
        """Constraint for squared sum of incoming weights per unit (e.g. for Rectifier).""",
        H2OTypeConverters.toFloat())

    initialWeightDistribution = Param(
        Params._dummy(),
        "initialWeightDistribution",
        """Initial weight distribution.""",
        H2OTypeConverters.toEnumString("hex.deeplearning.DeepLearningModel$DeepLearningParameters$InitialWeightDistribution"))

    initialWeightScale = Param(
        Params._dummy(),
        "initialWeightScale",
        """Uniform: -value...value, Normal: stddev.""",
        H2OTypeConverters.toFloat())

    loss = Param(
        Params._dummy(),
        "loss",
        """Loss function.""",
        H2OTypeConverters.toEnumString("hex.deeplearning.DeepLearningModel$DeepLearningParameters$Loss"))

    scoreInterval = Param(
        Params._dummy(),
        "scoreInterval",
        """Shortest time interval (in seconds) between model scoring.""",
        H2OTypeConverters.toFloat())

    scoreTrainingSamples = Param(
        Params._dummy(),
        "scoreTrainingSamples",
        """Number of training set samples for scoring (0 for all).""",
        H2OTypeConverters.toInt())

    scoreValidationSamples = Param(
        Params._dummy(),
        "scoreValidationSamples",
        """Number of validation set samples for scoring (0 for all).""",
        H2OTypeConverters.toInt())

    scoreDutyCycle = Param(
        Params._dummy(),
        "scoreDutyCycle",
        """Maximum duty cycle fraction for scoring (lower: more training, higher: more scoring).""",
        H2OTypeConverters.toFloat())

    classificationStop = Param(
        Params._dummy(),
        "classificationStop",
        """Stopping criterion for classification error fraction on training data (-1 to disable).""",
        H2OTypeConverters.toFloat())

    regressionStop = Param(
        Params._dummy(),
        "regressionStop",
        """Stopping criterion for regression error (MSE) on training data (-1 to disable).""",
        H2OTypeConverters.toFloat())

    quietMode = Param(
        Params._dummy(),
        "quietMode",
        """Enable quiet mode for less output to standard output.""",
        H2OTypeConverters.toBoolean())

    scoreValidationSampling = Param(
        Params._dummy(),
        "scoreValidationSampling",
        """Method used to sample validation dataset for scoring.""",
        H2OTypeConverters.toEnumString("hex.deeplearning.DeepLearningModel$DeepLearningParameters$ClassSamplingMethod"))

    overwriteWithBestModel = Param(
        Params._dummy(),
        "overwriteWithBestModel",
        """If enabled, override the final model with the best model found during training.""",
        H2OTypeConverters.toBoolean())

    useAllFactorLevels = Param(
        Params._dummy(),
        "useAllFactorLevels",
        """Use all factor levels of categorical variables. Otherwise, the first factor level is omitted (without loss of accuracy). Useful for variable importances and auto-enabled for autoencoder.""",
        H2OTypeConverters.toBoolean())

    standardize = Param(
        Params._dummy(),
        "standardize",
        """If enabled, automatically standardize the data. If disabled, the user must provide properly scaled input data.""",
        H2OTypeConverters.toBoolean())

    diagnostics = Param(
        Params._dummy(),
        "diagnostics",
        """Enable diagnostics for hidden layers.""",
        H2OTypeConverters.toBoolean())

    calculateFeatureImportances = Param(
        Params._dummy(),
        "calculateFeatureImportances",
        """Compute variable importances for input features (Gedeon method) - can be slow for large networks.""",
        H2OTypeConverters.toBoolean())

    fastMode = Param(
        Params._dummy(),
        "fastMode",
        """Enable fast mode (minor approximation in back-propagation).""",
        H2OTypeConverters.toBoolean())

    forceLoadBalance = Param(
        Params._dummy(),
        "forceLoadBalance",
        """Force extra load balancing to increase training speed for small datasets (to keep all cores busy).""",
        H2OTypeConverters.toBoolean())

    replicateTrainingData = Param(
        Params._dummy(),
        "replicateTrainingData",
        """Replicate the entire training dataset onto every node for faster training on small datasets.""",
        H2OTypeConverters.toBoolean())

    singleNodeMode = Param(
        Params._dummy(),
        "singleNodeMode",
        """Run on a single node for fine-tuning of model parameters.""",
        H2OTypeConverters.toBoolean())

    shuffleTrainingData = Param(
        Params._dummy(),
        "shuffleTrainingData",
        """Enable shuffling of training data (recommended if training data is replicated and train_samples_per_iteration is close to #nodes x #rows, of if using balance_classes).""",
        H2OTypeConverters.toBoolean())

    missingValuesHandling = Param(
        Params._dummy(),
        "missingValuesHandling",
        """Handling of missing values. Either MeanImputation or Skip.""",
        H2OTypeConverters.toEnumString("hex.deeplearning.DeepLearningModel$DeepLearningParameters$MissingValuesHandling"))

    sparse = Param(
        Params._dummy(),
        "sparse",
        """Sparse data handling (more efficient for data with lots of 0 values).""",
        H2OTypeConverters.toBoolean())

    averageActivation = Param(
        Params._dummy(),
        "averageActivation",
        """Average activation for sparse auto-encoder. #Experimental""",
        H2OTypeConverters.toFloat())

    sparsityBeta = Param(
        Params._dummy(),
        "sparsityBeta",
        """Sparsity regularization. #Experimental""",
        H2OTypeConverters.toFloat())

    maxCategoricalFeatures = Param(
        Params._dummy(),
        "maxCategoricalFeatures",
        """Max. number of categorical features, enforced via hashing. #Experimental""",
        H2OTypeConverters.toInt())

    reproducible = Param(
        Params._dummy(),
        "reproducible",
        """Force reproducibility on small data (will be slow - only uses 1 thread).""",
        H2OTypeConverters.toBoolean())

    exportWeightsAndBiases = Param(
        Params._dummy(),
        "exportWeightsAndBiases",
        """Whether to export Neural Network weights and biases to H2O Frames.""",
        H2OTypeConverters.toBoolean())

    miniBatchSize = Param(
        Params._dummy(),
        "miniBatchSize",
        """Mini-batch size (smaller leads to better fit, larger can speed up and generalize better).""",
        H2OTypeConverters.toInt())

    elasticAveraging = Param(
        Params._dummy(),
        "elasticAveraging",
        """Elastic averaging between compute nodes can improve distributed model convergence. #Experimental""",
        H2OTypeConverters.toBoolean())

    elasticAveragingMovingRate = Param(
        Params._dummy(),
        "elasticAveragingMovingRate",
        """Elastic averaging moving rate (only if elastic averaging is enabled).""",
        H2OTypeConverters.toFloat())

    elasticAveragingRegularization = Param(
        Params._dummy(),
        "elasticAveragingRegularization",
        """Elastic averaging regularization strength (only if elastic averaging is enabled).""",
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

    quantileAlpha = Param(
        Params._dummy(),
        "quantileAlpha",
        """Desired quantile for Quantile regression, must be between 0 and 1.""",
        H2OTypeConverters.toFloat())

    huberAlpha = Param(
        Params._dummy(),
        "huberAlpha",
        """Desired quantile for Huber/M-regression (threshold between quadratic and linear loss, must be between 0 and 1).""",
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
    def getBalanceClasses(self):
        return self.getOrDefault(self.balanceClasses)

    def getClassSamplingFactors(self):
        return self.getOrDefault(self.classSamplingFactors)

    def getMaxAfterBalanceSize(self):
        return self.getOrDefault(self.maxAfterBalanceSize)

    def getActivation(self):
        return self.getOrDefault(self.activation)

    def getHidden(self):
        return self.getOrDefault(self.hidden)

    def getEpochs(self):
        return self.getOrDefault(self.epochs)

    def getTrainSamplesPerIteration(self):
        return self.getOrDefault(self.trainSamplesPerIteration)

    def getTargetRatioCommToComp(self):
        return self.getOrDefault(self.targetRatioCommToComp)

    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getAdaptiveRate(self):
        return self.getOrDefault(self.adaptiveRate)

    def getRho(self):
        return self.getOrDefault(self.rho)

    def getEpsilon(self):
        return self.getOrDefault(self.epsilon)

    def getRate(self):
        return self.getOrDefault(self.rate)

    def getRateAnnealing(self):
        return self.getOrDefault(self.rateAnnealing)

    def getRateDecay(self):
        return self.getOrDefault(self.rateDecay)

    def getMomentumStart(self):
        return self.getOrDefault(self.momentumStart)

    def getMomentumRamp(self):
        return self.getOrDefault(self.momentumRamp)

    def getMomentumStable(self):
        return self.getOrDefault(self.momentumStable)

    def getNesterovAcceleratedGradient(self):
        return self.getOrDefault(self.nesterovAcceleratedGradient)

    def getInputDropoutRatio(self):
        return self.getOrDefault(self.inputDropoutRatio)

    def getHiddenDropoutRatios(self):
        return self.getOrDefault(self.hiddenDropoutRatios)

    def getL1(self):
        return self.getOrDefault(self.l1)

    def getL2(self):
        return self.getOrDefault(self.l2)

    def getMaxW2(self):
        return self.getOrDefault(self.maxW2)

    def getInitialWeightDistribution(self):
        return self.getOrDefault(self.initialWeightDistribution)

    def getInitialWeightScale(self):
        return self.getOrDefault(self.initialWeightScale)

    def getLoss(self):
        return self.getOrDefault(self.loss)

    def getScoreInterval(self):
        return self.getOrDefault(self.scoreInterval)

    def getScoreTrainingSamples(self):
        return self.getOrDefault(self.scoreTrainingSamples)

    def getScoreValidationSamples(self):
        return self.getOrDefault(self.scoreValidationSamples)

    def getScoreDutyCycle(self):
        return self.getOrDefault(self.scoreDutyCycle)

    def getClassificationStop(self):
        return self.getOrDefault(self.classificationStop)

    def getRegressionStop(self):
        return self.getOrDefault(self.regressionStop)

    def getQuietMode(self):
        return self.getOrDefault(self.quietMode)

    def getScoreValidationSampling(self):
        return self.getOrDefault(self.scoreValidationSampling)

    def getOverwriteWithBestModel(self):
        return self.getOrDefault(self.overwriteWithBestModel)

    def getUseAllFactorLevels(self):
        return self.getOrDefault(self.useAllFactorLevels)

    def getStandardize(self):
        return self.getOrDefault(self.standardize)

    def getDiagnostics(self):
        return self.getOrDefault(self.diagnostics)

    def getCalculateFeatureImportances(self):
        return self.getOrDefault(self.calculateFeatureImportances)

    def getFastMode(self):
        return self.getOrDefault(self.fastMode)

    def getForceLoadBalance(self):
        return self.getOrDefault(self.forceLoadBalance)

    def getReplicateTrainingData(self):
        return self.getOrDefault(self.replicateTrainingData)

    def getSingleNodeMode(self):
        return self.getOrDefault(self.singleNodeMode)

    def getShuffleTrainingData(self):
        return self.getOrDefault(self.shuffleTrainingData)

    def getMissingValuesHandling(self):
        return self.getOrDefault(self.missingValuesHandling)

    def getSparse(self):
        return self.getOrDefault(self.sparse)

    def getAverageActivation(self):
        return self.getOrDefault(self.averageActivation)

    def getSparsityBeta(self):
        return self.getOrDefault(self.sparsityBeta)

    def getMaxCategoricalFeatures(self):
        return self.getOrDefault(self.maxCategoricalFeatures)

    def getReproducible(self):
        return self.getOrDefault(self.reproducible)

    def getExportWeightsAndBiases(self):
        return self.getOrDefault(self.exportWeightsAndBiases)

    def getMiniBatchSize(self):
        return self.getOrDefault(self.miniBatchSize)

    def getElasticAveraging(self):
        return self.getOrDefault(self.elasticAveraging)

    def getElasticAveragingMovingRate(self):
        return self.getOrDefault(self.elasticAveragingMovingRate)

    def getElasticAveragingRegularization(self):
        return self.getOrDefault(self.elasticAveragingRegularization)

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

    def getQuantileAlpha(self):
        return self.getOrDefault(self.quantileAlpha)

    def getHuberAlpha(self):
        return self.getOrDefault(self.huberAlpha)

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

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    def getAucType(self):
        return self.getOrDefault(self.aucType)

    ##
    # Setters
    ##
    def setBalanceClasses(self, value):
        return self._set(balanceClasses=value)

    def setClassSamplingFactors(self, value):
        return self._set(classSamplingFactors=value)

    def setMaxAfterBalanceSize(self, value):
        return self._set(maxAfterBalanceSize=value)

    def setActivation(self, value):
        return self._set(activation=value)

    def setHidden(self, value):
        return self._set(hidden=value)

    def setEpochs(self, value):
        return self._set(epochs=value)

    def setTrainSamplesPerIteration(self, value):
        return self._set(trainSamplesPerIteration=value)

    def setTargetRatioCommToComp(self, value):
        return self._set(targetRatioCommToComp=value)

    def setSeed(self, value):
        return self._set(seed=value)

    def setAdaptiveRate(self, value):
        return self._set(adaptiveRate=value)

    def setRho(self, value):
        return self._set(rho=value)

    def setEpsilon(self, value):
        return self._set(epsilon=value)

    def setRate(self, value):
        return self._set(rate=value)

    def setRateAnnealing(self, value):
        return self._set(rateAnnealing=value)

    def setRateDecay(self, value):
        return self._set(rateDecay=value)

    def setMomentumStart(self, value):
        return self._set(momentumStart=value)

    def setMomentumRamp(self, value):
        return self._set(momentumRamp=value)

    def setMomentumStable(self, value):
        return self._set(momentumStable=value)

    def setNesterovAcceleratedGradient(self, value):
        return self._set(nesterovAcceleratedGradient=value)

    def setInputDropoutRatio(self, value):
        return self._set(inputDropoutRatio=value)

    def setHiddenDropoutRatios(self, value):
        return self._set(hiddenDropoutRatios=value)

    def setL1(self, value):
        return self._set(l1=value)

    def setL2(self, value):
        return self._set(l2=value)

    def setMaxW2(self, value):
        return self._set(maxW2=value)

    def setInitialWeightDistribution(self, value):
        return self._set(initialWeightDistribution=value)

    def setInitialWeightScale(self, value):
        return self._set(initialWeightScale=value)

    def setLoss(self, value):
        return self._set(loss=value)

    def setScoreInterval(self, value):
        return self._set(scoreInterval=value)

    def setScoreTrainingSamples(self, value):
        return self._set(scoreTrainingSamples=value)

    def setScoreValidationSamples(self, value):
        return self._set(scoreValidationSamples=value)

    def setScoreDutyCycle(self, value):
        return self._set(scoreDutyCycle=value)

    def setClassificationStop(self, value):
        return self._set(classificationStop=value)

    def setRegressionStop(self, value):
        return self._set(regressionStop=value)

    def setQuietMode(self, value):
        return self._set(quietMode=value)

    def setScoreValidationSampling(self, value):
        return self._set(scoreValidationSampling=value)

    def setOverwriteWithBestModel(self, value):
        return self._set(overwriteWithBestModel=value)

    def setUseAllFactorLevels(self, value):
        return self._set(useAllFactorLevels=value)

    def setStandardize(self, value):
        return self._set(standardize=value)

    def setDiagnostics(self, value):
        return self._set(diagnostics=value)

    def setCalculateFeatureImportances(self, value):
        return self._set(calculateFeatureImportances=value)

    def setFastMode(self, value):
        return self._set(fastMode=value)

    def setForceLoadBalance(self, value):
        return self._set(forceLoadBalance=value)

    def setReplicateTrainingData(self, value):
        return self._set(replicateTrainingData=value)

    def setSingleNodeMode(self, value):
        return self._set(singleNodeMode=value)

    def setShuffleTrainingData(self, value):
        return self._set(shuffleTrainingData=value)

    def setMissingValuesHandling(self, value):
        return self._set(missingValuesHandling=value)

    def setSparse(self, value):
        return self._set(sparse=value)

    def setAverageActivation(self, value):
        return self._set(averageActivation=value)

    def setSparsityBeta(self, value):
        return self._set(sparsityBeta=value)

    def setMaxCategoricalFeatures(self, value):
        return self._set(maxCategoricalFeatures=value)

    def setReproducible(self, value):
        return self._set(reproducible=value)

    def setExportWeightsAndBiases(self, value):
        return self._set(exportWeightsAndBiases=value)

    def setMiniBatchSize(self, value):
        return self._set(miniBatchSize=value)

    def setElasticAveraging(self, value):
        return self._set(elasticAveraging=value)

    def setElasticAveragingMovingRate(self, value):
        return self._set(elasticAveragingMovingRate=value)

    def setElasticAveragingRegularization(self, value):
        return self._set(elasticAveragingRegularization=value)

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

    def setQuantileAlpha(self, value):
        return self._set(quantileAlpha=value)

    def setHuberAlpha(self, value):
        return self._set(huberAlpha=value)

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

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)

    def setAucType(self, value):
        return self._set(aucType=value)
