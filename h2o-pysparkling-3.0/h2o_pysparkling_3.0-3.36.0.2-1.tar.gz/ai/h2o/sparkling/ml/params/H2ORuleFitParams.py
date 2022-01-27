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
from ai.h2o.sparkling.ml.params.HasUnsupportedOffsetCol import HasUnsupportedOffsetCol
from ai.h2o.sparkling.ml.params.HasIgnoredCols import HasIgnoredCols


class H2ORuleFitParams(HasUnsupportedOffsetCol, HasIgnoredCols, Params):

    ##
    # Param definitions
    ##
    seed = Param(
        Params._dummy(),
        "seed",
        """Seed for pseudo random number generator (if applicable).""",
        H2OTypeConverters.toInt())

    algorithm = Param(
        Params._dummy(),
        "algorithm",
        """The algorithm to use to generate rules.""",
        H2OTypeConverters.toEnumString("hex.rulefit.RuleFitModel$Algorithm"))

    minRuleLength = Param(
        Params._dummy(),
        "minRuleLength",
        """Minimum length of rules. Defaults to 3.""",
        H2OTypeConverters.toInt())

    maxRuleLength = Param(
        Params._dummy(),
        "maxRuleLength",
        """Maximum length of rules. Defaults to 3.""",
        H2OTypeConverters.toInt())

    maxNumRules = Param(
        Params._dummy(),
        "maxNumRules",
        """The maximum number of rules to return. defaults to -1 which means the number of rules is selected 
by diminishing returns in model deviance.""",
        H2OTypeConverters.toInt())

    modelType = Param(
        Params._dummy(),
        "modelType",
        """Specifies type of base learners in the ensemble.""",
        H2OTypeConverters.toEnumString("hex.rulefit.RuleFitModel$ModelType"))

    ruleGenerationNtrees = Param(
        Params._dummy(),
        "ruleGenerationNtrees",
        """Specifies the number of trees to build in the tree model. Defaults to 50.""",
        H2OTypeConverters.toInt())

    removeDuplicates = Param(
        Params._dummy(),
        "removeDuplicates",
        """Whether to remove rules which are identical to an earlier rule. Defaults to true.""",
        H2OTypeConverters.toBoolean())

    lambdaValue = Param(
        Params._dummy(),
        "lambdaValue",
        """Lambda for LASSO regressor.""",
        H2OTypeConverters.toNullableListFloat())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

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

    def getAlgorithm(self):
        return self.getOrDefault(self.algorithm)

    def getMinRuleLength(self):
        return self.getOrDefault(self.minRuleLength)

    def getMaxRuleLength(self):
        return self.getOrDefault(self.maxRuleLength)

    def getMaxNumRules(self):
        return self.getOrDefault(self.maxNumRules)

    def getModelType(self):
        return self.getOrDefault(self.modelType)

    def getRuleGenerationNtrees(self):
        return self.getOrDefault(self.ruleGenerationNtrees)

    def getRemoveDuplicates(self):
        return self.getOrDefault(self.removeDuplicates)

    def getLambdaValue(self):
        return self.getOrDefault(self.lambdaValue)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getDistribution(self):
        return self.getOrDefault(self.distribution)

    def getLabelCol(self):
        return self.getOrDefault(self.labelCol)

    def getWeightCol(self):
        return self.getOrDefault(self.weightCol)

    def getAucType(self):
        return self.getOrDefault(self.aucType)

    ##
    # Setters
    ##
    def setSeed(self, value):
        return self._set(seed=value)

    def setAlgorithm(self, value):
        return self._set(algorithm=value)

    def setMinRuleLength(self, value):
        return self._set(minRuleLength=value)

    def setMaxRuleLength(self, value):
        return self._set(maxRuleLength=value)

    def setMaxNumRules(self, value):
        return self._set(maxNumRules=value)

    def setModelType(self, value):
        return self._set(modelType=value)

    def setRuleGenerationNtrees(self, value):
        return self._set(ruleGenerationNtrees=value)

    def setRemoveDuplicates(self, value):
        return self._set(removeDuplicates=value)

    def setLambdaValue(self, value):
        return self._set(lambdaValue=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setDistribution(self, value):
        return self._set(distribution=value)

    def setLabelCol(self, value):
        return self._set(labelCol=value)

    def setWeightCol(self, value):
        return self._set(weightCol=value)

    def setAucType(self, value):
        return self._set(aucType=value)
