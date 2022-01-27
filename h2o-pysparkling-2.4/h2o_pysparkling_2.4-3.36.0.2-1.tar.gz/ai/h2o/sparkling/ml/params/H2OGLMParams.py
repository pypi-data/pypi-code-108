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
from ai.h2o.sparkling.ml.params.HasRandomCols import HasRandomCols
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols
from ai.h2o.sparkling.ml.params.HasPlugValues import HasPlugValues
from ai.h2o.sparkling.ml.params.HasBetaConstraints import HasBetaConstraints
from ai.h2o.sparkling.ml.params.HasInteractionPairs import HasInteractionPairs


class H2OGLMParams(HasRandomCols, HasIgnoredCols, HasPlugValues, HasBetaConstraints, HasInteractionPairs, Params):

    ##
    # Param definitions
    ##
    seed = Param(
        Params._dummy(),
        "seed",
        """Seed for pseudo random number generator (if applicable)""",
        H2OTypeConverters.toInt())

    family = Param(
        Params._dummy(),
        "family",
        """Family. Use binomial for classification with logistic regression, others are for regression problems.""",
        H2OTypeConverters.toEnumString("hex.glm.GLMModel$GLMParameters$Family"))

    randomFamily = Param(
        Params._dummy(),
        "randomFamily",
        """Random Component Family array.  One for each random component. Only support gaussian for now.""",
        H2OTypeConverters.toNullableListEnumString("hex.glm.GLMModel$GLMParameters$Family"))

    tweedieVariancePower = Param(
        Params._dummy(),
        "tweedieVariancePower",
        """Tweedie variance power""",
        H2OTypeConverters.toFloat())

    tweedieLinkPower = Param(
        Params._dummy(),
        "tweedieLinkPower",
        """Tweedie link power""",
        H2OTypeConverters.toFloat())

    theta = Param(
        Params._dummy(),
        "theta",
        """Theta""",
        H2OTypeConverters.toFloat())

    solver = Param(
        Params._dummy(),
        "solver",
        """AUTO will set the solver based on given data and the other parameters. IRLSM is fast on on problems with small number of predictors and for lambda-search with L1 penalty, L_BFGS scales better for datasets with many columns.""",
        H2OTypeConverters.toEnumString("hex.glm.GLMModel$GLMParameters$Solver"))

    alphaValue = Param(
        Params._dummy(),
        "alphaValue",
        """Distribution of regularization between the L1 (Lasso) and L2 (Ridge) penalties. A value of 1 for alpha represents Lasso regression, a value of 0 produces Ridge regression, and anything in between specifies the amount of mixing between the two. Default value of alpha is 0 when SOLVER = 'L-BFGS'; 0.5 otherwise.""",
        H2OTypeConverters.toNullableListFloat())

    lambdaValue = Param(
        Params._dummy(),
        "lambdaValue",
        """Regularization strength""",
        H2OTypeConverters.toNullableListFloat())

    lambdaSearch = Param(
        Params._dummy(),
        "lambdaSearch",
        """Use lambda search starting at lambda max, given lambda is then interpreted as lambda min""",
        H2OTypeConverters.toBoolean())

    earlyStopping = Param(
        Params._dummy(),
        "earlyStopping",
        """Stop early when there is no more relative improvement on train or validation (if provided)""",
        H2OTypeConverters.toBoolean())

    nlambdas = Param(
        Params._dummy(),
        "nlambdas",
        """Number of lambdas to be used in a search. Default indicates: If alpha is zero, with lambda search set to True, the value of nlamdas is set to 30 (fewer lambdas are needed for ridge regression) otherwise it is set to 100.""",
        H2OTypeConverters.toInt())

    scoreIterationInterval = Param(
        Params._dummy(),
        "scoreIterationInterval",
        """Perform scoring for every score_iteration_interval iterations""",
        H2OTypeConverters.toInt())

    standardize = Param(
        Params._dummy(),
        "standardize",
        """Standardize numeric columns to have zero mean and unit variance""",
        H2OTypeConverters.toBoolean())

    coldStart = Param(
        Params._dummy(),
        "coldStart",
        """Only applicable to multiple alpha/lambda values.  If false, build the next model for next set of alpha/lambda values starting from the values provided by current model.  If true will start GLM model from scratch.""",
        H2OTypeConverters.toBoolean())

    missingValuesHandling = Param(
        Params._dummy(),
        "missingValuesHandling",
        """Handling of missing values. Either MeanImputation, Skip or PlugValues.""",
        H2OTypeConverters.toEnumString("hex.glm.GLMModel$GLMParameters$MissingValuesHandling"))

    nonNegative = Param(
        Params._dummy(),
        "nonNegative",
        """Restrict coefficients (not intercept) to be non-negative""",
        H2OTypeConverters.toBoolean())

    maxIterations = Param(
        Params._dummy(),
        "maxIterations",
        """Maximum number of iterations""",
        H2OTypeConverters.toInt())

    betaEpsilon = Param(
        Params._dummy(),
        "betaEpsilon",
        """Converge if  beta changes less (using L-infinity norm) than beta esilon, ONLY applies to IRLSM solver """,
        H2OTypeConverters.toFloat())

    objectiveEpsilon = Param(
        Params._dummy(),
        "objectiveEpsilon",
        """Converge if  objective value changes less than this. Default indicates: If lambda_search is set to True the value of objective_epsilon is set to .0001. If the lambda_search is set to False and lambda is equal to zero, the value of objective_epsilon is set to .000001, for any other value of lambda the default value of objective_epsilon is set to .0001.""",
        H2OTypeConverters.toFloat())

    gradientEpsilon = Param(
        Params._dummy(),
        "gradientEpsilon",
        """Converge if  objective changes less (using L-infinity norm) than this, ONLY applies to L-BFGS solver. Default indicates: If lambda_search is set to False and lambda is equal to zero, the default value of gradient_epsilon is equal to .000001, otherwise the default value is .0001. If lambda_search is set to True, the conditional values above are 1E-8 and 1E-6 respectively.""",
        H2OTypeConverters.toFloat())

    objReg = Param(
        Params._dummy(),
        "objReg",
        """Likelihood divider in objective value computation, default is 1/nobs""",
        H2OTypeConverters.toFloat())

    link = Param(
        Params._dummy(),
        "link",
        """Link function.""",
        H2OTypeConverters.toEnumString("hex.glm.GLMModel$GLMParameters$Link"))

    randomLink = Param(
        Params._dummy(),
        "randomLink",
        """Link function array for random component in HGLM.""",
        H2OTypeConverters.toNullableListEnumString("hex.glm.GLMModel$GLMParameters$Link"))

    startval = Param(
        Params._dummy(),
        "startval",
        """double array to initialize fixed and random coefficients for HGLM, coefficients for GLM.""",
        H2OTypeConverters.toNullableListFloat())

    calcLike = Param(
        Params._dummy(),
        "calcLike",
        """if true, will return likelihood function value for HGLM.""",
        H2OTypeConverters.toBoolean())

    intercept = Param(
        Params._dummy(),
        "intercept",
        """Include constant term in the model""",
        H2OTypeConverters.toBoolean())

    HGLM = Param(
        Params._dummy(),
        "HGLM",
        """If set to true, will return HGLM model.  Otherwise, normal GLM model will be returned""",
        H2OTypeConverters.toBoolean())

    prior = Param(
        Params._dummy(),
        "prior",
        """Prior probability for y==1. To be used only for logistic regression iff the data has been sampled and the mean of response does not reflect reality.""",
        H2OTypeConverters.toFloat())

    lambdaMinRatio = Param(
        Params._dummy(),
        "lambdaMinRatio",
        """Minimum lambda used in lambda search, specified as a ratio of lambda_max (the smallest lambda that drives all coefficients to zero). Default indicates: if the number of observations is greater than the number of variables, then lambda_min_ratio is set to 0.0001; if the number of observations is less than the number of variables, then lambda_min_ratio is set to 0.01.""",
        H2OTypeConverters.toFloat())

    maxActivePredictors = Param(
        Params._dummy(),
        "maxActivePredictors",
        """Maximum number of active predictors during computation. Use as a stopping criterion to prevent expensive model building with many predictors. Default indicates: If the IRLSM solver is used, the value of max_active_predictors is set to 5000 otherwise it is set to 100000000.""",
        H2OTypeConverters.toInt())

    interactions = Param(
        Params._dummy(),
        "interactions",
        """A list of predictor column indices to interact. All pairwise combinations will be computed for the list.""",
        H2OTypeConverters.toNullableListString())

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

    computePValues = Param(
        Params._dummy(),
        "computePValues",
        """Request p-values computation, p-values work only with IRLSM solver and no regularization""",
        H2OTypeConverters.toBoolean())

    removeCollinearCols = Param(
        Params._dummy(),
        "removeCollinearCols",
        """In case of linearly dependent columns, remove some of the dependent columns""",
        H2OTypeConverters.toBoolean())

    generateScoringHistory = Param(
        Params._dummy(),
        "generateScoringHistory",
        """If set to true, will generate scoring history for GLM.  This may significantly slow down the algo.""",
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

    checkpoint = Param(
        Params._dummy(),
        "checkpoint",
        """Model checkpoint to resume training with.""",
        H2OTypeConverters.toNullableString())

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
    def getSeed(self):
        return self.getOrDefault(self.seed)

    def getFamily(self):
        return self.getOrDefault(self.family)

    def getRandomFamily(self):
        return self.getOrDefault(self.randomFamily)

    def getTweedieVariancePower(self):
        return self.getOrDefault(self.tweedieVariancePower)

    def getTweedieLinkPower(self):
        return self.getOrDefault(self.tweedieLinkPower)

    def getTheta(self):
        return self.getOrDefault(self.theta)

    def getSolver(self):
        return self.getOrDefault(self.solver)

    def getAlphaValue(self):
        return self.getOrDefault(self.alphaValue)

    def getLambdaValue(self):
        return self.getOrDefault(self.lambdaValue)

    def getLambdaSearch(self):
        return self.getOrDefault(self.lambdaSearch)

    def getEarlyStopping(self):
        return self.getOrDefault(self.earlyStopping)

    def getNlambdas(self):
        return self.getOrDefault(self.nlambdas)

    def getScoreIterationInterval(self):
        return self.getOrDefault(self.scoreIterationInterval)

    def getStandardize(self):
        return self.getOrDefault(self.standardize)

    def getColdStart(self):
        return self.getOrDefault(self.coldStart)

    def getMissingValuesHandling(self):
        return self.getOrDefault(self.missingValuesHandling)

    def getNonNegative(self):
        return self.getOrDefault(self.nonNegative)

    def getMaxIterations(self):
        return self.getOrDefault(self.maxIterations)

    def getBetaEpsilon(self):
        return self.getOrDefault(self.betaEpsilon)

    def getObjectiveEpsilon(self):
        return self.getOrDefault(self.objectiveEpsilon)

    def getGradientEpsilon(self):
        return self.getOrDefault(self.gradientEpsilon)

    def getObjReg(self):
        return self.getOrDefault(self.objReg)

    def getLink(self):
        return self.getOrDefault(self.link)

    def getRandomLink(self):
        return self.getOrDefault(self.randomLink)

    def getStartval(self):
        return self.getOrDefault(self.startval)

    def getCalcLike(self):
        return self.getOrDefault(self.calcLike)

    def getIntercept(self):
        return self.getOrDefault(self.intercept)

    def getHGLM(self):
        return self.getOrDefault(self.HGLM)

    def getPrior(self):
        return self.getOrDefault(self.prior)

    def getLambdaMinRatio(self):
        return self.getOrDefault(self.lambdaMinRatio)

    def getMaxActivePredictors(self):
        return self.getOrDefault(self.maxActivePredictors)

    def getInteractions(self):
        return self.getOrDefault(self.interactions)

    def getBalanceClasses(self):
        return self.getOrDefault(self.balanceClasses)

    def getClassSamplingFactors(self):
        return self.getOrDefault(self.classSamplingFactors)

    def getMaxAfterBalanceSize(self):
        return self.getOrDefault(self.maxAfterBalanceSize)

    def getMaxConfusionMatrixSize(self):
        return self.getOrDefault(self.maxConfusionMatrixSize)

    def getComputePValues(self):
        return self.getOrDefault(self.computePValues)

    def getRemoveCollinearCols(self):
        return self.getOrDefault(self.removeCollinearCols)

    def getGenerateScoringHistory(self):
        return self.getOrDefault(self.generateScoringHistory)

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

    def getIgnoreConstCols(self):
        return self.getOrDefault(self.ignoreConstCols)

    def getScoreEachIteration(self):
        return self.getOrDefault(self.scoreEachIteration)

    def getCheckpoint(self):
        return self.getOrDefault(self.checkpoint)

    def getStoppingRounds(self):
        return self.getOrDefault(self.stoppingRounds)

    def getMaxRuntimeSecs(self):
        return self.getOrDefault(self.maxRuntimeSecs)

    def getStoppingMetric(self):
        return self.getOrDefault(self.stoppingMetric)

    def getStoppingTolerance(self):
        return self.getOrDefault(self.stoppingTolerance)

    def getCustomMetricFunc(self):
        return self.getOrDefault(self.customMetricFunc)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    def getAucType(self):
        return self.getOrDefault(self.aucType)

    ##
    # Setters
    ##
    def setSeed(self, value):
        return self._set(seed=value)

    def setFamily(self, value):
        return self._set(family=value)

    def setRandomFamily(self, value):
        return self._set(randomFamily=value)

    def setTweedieVariancePower(self, value):
        return self._set(tweedieVariancePower=value)

    def setTweedieLinkPower(self, value):
        return self._set(tweedieLinkPower=value)

    def setTheta(self, value):
        return self._set(theta=value)

    def setSolver(self, value):
        return self._set(solver=value)

    def setAlphaValue(self, value):
        return self._set(alphaValue=value)

    def setLambdaValue(self, value):
        return self._set(lambdaValue=value)

    def setLambdaSearch(self, value):
        return self._set(lambdaSearch=value)

    def setEarlyStopping(self, value):
        return self._set(earlyStopping=value)

    def setNlambdas(self, value):
        return self._set(nlambdas=value)

    def setScoreIterationInterval(self, value):
        return self._set(scoreIterationInterval=value)

    def setStandardize(self, value):
        return self._set(standardize=value)

    def setColdStart(self, value):
        return self._set(coldStart=value)

    def setMissingValuesHandling(self, value):
        return self._set(missingValuesHandling=value)

    def setNonNegative(self, value):
        return self._set(nonNegative=value)

    def setMaxIterations(self, value):
        return self._set(maxIterations=value)

    def setBetaEpsilon(self, value):
        return self._set(betaEpsilon=value)

    def setObjectiveEpsilon(self, value):
        return self._set(objectiveEpsilon=value)

    def setGradientEpsilon(self, value):
        return self._set(gradientEpsilon=value)

    def setObjReg(self, value):
        return self._set(objReg=value)

    def setLink(self, value):
        return self._set(link=value)

    def setRandomLink(self, value):
        return self._set(randomLink=value)

    def setStartval(self, value):
        return self._set(startval=value)

    def setCalcLike(self, value):
        return self._set(calcLike=value)

    def setIntercept(self, value):
        return self._set(intercept=value)

    def setHGLM(self, value):
        return self._set(HGLM=value)

    def setPrior(self, value):
        return self._set(prior=value)

    def setLambdaMinRatio(self, value):
        return self._set(lambdaMinRatio=value)

    def setMaxActivePredictors(self, value):
        return self._set(maxActivePredictors=value)

    def setInteractions(self, value):
        return self._set(interactions=value)

    def setBalanceClasses(self, value):
        return self._set(balanceClasses=value)

    def setClassSamplingFactors(self, value):
        return self._set(classSamplingFactors=value)

    def setMaxAfterBalanceSize(self, value):
        return self._set(maxAfterBalanceSize=value)

    def setMaxConfusionMatrixSize(self, value):
        return self._set(maxConfusionMatrixSize=value)

    def setComputePValues(self, value):
        return self._set(computePValues=value)

    def setRemoveCollinearCols(self, value):
        return self._set(removeCollinearCols=value)

    def setGenerateScoringHistory(self, value):
        return self._set(generateScoringHistory=value)

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

    def setIgnoreConstCols(self, value):
        return self._set(ignoreConstCols=value)

    def setScoreEachIteration(self, value):
        return self._set(scoreEachIteration=value)

    def setCheckpoint(self, value):
        return self._set(checkpoint=value)

    def setStoppingRounds(self, value):
        return self._set(stoppingRounds=value)

    def setMaxRuntimeSecs(self, value):
        return self._set(maxRuntimeSecs=value)

    def setStoppingMetric(self, value):
        return self._set(stoppingMetric=value)

    def setStoppingTolerance(self, value):
        return self._set(stoppingTolerance=value)

    def setCustomMetricFunc(self, value):
        return self._set(customMetricFunc=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)

    def setAucType(self, value):
        return self._set(aucType=value)
