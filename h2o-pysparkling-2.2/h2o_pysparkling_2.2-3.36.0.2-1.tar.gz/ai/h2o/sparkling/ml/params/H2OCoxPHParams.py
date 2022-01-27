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
from ai.h2o.sparkling.ml.params.HasInteractionPairs import HasInteractionPairs


class H2OCoxPHParams(HasIgnoredCols, HasInteractionPairs, Params):

    ##
    # Param definitions
    ##
    startCol = Param(
        Params._dummy(),
        "startCol",
        """Start Time Column.""",
        H2OTypeConverters.toNullableString())

    stopCol = Param(
        Params._dummy(),
        "stopCol",
        """Stop Time Column.""",
        H2OTypeConverters.toNullableString())

    stratifyBy = Param(
        Params._dummy(),
        "stratifyBy",
        """List of columns to use for stratification.""",
        H2OTypeConverters.toNullableListString())

    ties = Param(
        Params._dummy(),
        "ties",
        """Method for Handling Ties.""",
        H2OTypeConverters.toEnumString("hex.coxph.CoxPHModel$CoxPHParameters$CoxPHTies"))

    init = Param(
        Params._dummy(),
        "init",
        """Coefficient starting value.""",
        H2OTypeConverters.toFloat())

    lreMin = Param(
        Params._dummy(),
        "lreMin",
        """Minimum log-relative error.""",
        H2OTypeConverters.toFloat())

    maxIterations = Param(
        Params._dummy(),
        "maxIterations",
        """Maximum number of iterations.""",
        H2OTypeConverters.toInt())

    interactionsOnly = Param(
        Params._dummy(),
        "interactionsOnly",
        """A list of columns that should only be used to create interactions but should not itself participate in model training.""",
        H2OTypeConverters.toNullableListString())

    interactions = Param(
        Params._dummy(),
        "interactions",
        """A list of predictor column indices to interact. All pairwise combinations will be computed for the list.""",
        H2OTypeConverters.toNullableListString())

    useAllFactorLevels = Param(
        Params._dummy(),
        "useAllFactorLevels",
        """(Internal. For development only!) Indicates whether to use all factor levels.""",
        H2OTypeConverters.toBoolean())

    singleNodeMode = Param(
        Params._dummy(),
        "singleNodeMode",
        """Run on a single node to reduce the effect of network overhead (for smaller datasets)""",
        H2OTypeConverters.toBoolean())

    modelId = Param(
        Params._dummy(),
        "modelId",
        """Destination id for this model; auto-generated if not specified.""",
        H2OTypeConverters.toNullableString())

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

    exportCheckpointsDir = Param(
        Params._dummy(),
        "exportCheckpointsDir",
        """Automatically export generated models to this directory.""",
        H2OTypeConverters.toNullableString())

    ##
    # Getters
    ##
    def getStartCol(self):
        return self.getOrDefault(self.startCol)

    def getStopCol(self):
        return self.getOrDefault(self.stopCol)

    def getStratifyBy(self):
        return self.getOrDefault(self.stratifyBy)

    def getTies(self):
        return self.getOrDefault(self.ties)

    def getInit(self):
        return self.getOrDefault(self.init)

    def getLreMin(self):
        return self.getOrDefault(self.lreMin)

    def getMaxIterations(self):
        return self.getOrDefault(self.maxIterations)

    def getInteractionsOnly(self):
        return self.getOrDefault(self.interactionsOnly)

    def getInteractions(self):
        return self.getOrDefault(self.interactions)

    def getUseAllFactorLevels(self):
        return self.getOrDefault(self.useAllFactorLevels)

    def getSingleNodeMode(self):
        return self.getOrDefault(self.singleNodeMode)

    def getModelId(self):
        return self.getOrDefault(self.modelId)

    def getLabelCol(self):
        return self.getOrDefault(self.labelCol)

    def getWeightCol(self):
        return self.getOrDefault(self.weightCol)

    def getOffsetCol(self):
        return self.getOrDefault(self.offsetCol)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    ##
    # Setters
    ##
    def setStartCol(self, value):
        return self._set(startCol=value)

    def setStopCol(self, value):
        return self._set(stopCol=value)

    def setStratifyBy(self, value):
        return self._set(stratifyBy=value)

    def setTies(self, value):
        return self._set(ties=value)

    def setInit(self, value):
        return self._set(init=value)

    def setLreMin(self, value):
        return self._set(lreMin=value)

    def setMaxIterations(self, value):
        return self._set(maxIterations=value)

    def setInteractionsOnly(self, value):
        return self._set(interactionsOnly=value)

    def setInteractions(self, value):
        return self._set(interactions=value)

    def setUseAllFactorLevels(self, value):
        return self._set(useAllFactorLevels=value)

    def setSingleNodeMode(self, value):
        return self._set(singleNodeMode=value)

    def setModelId(self, value):
        return self._set(modelId=value)

    def setLabelCol(self, value):
        return self._set(labelCol=value)

    def setWeightCol(self, value):
        return self._set(weightCol=value)

    def setOffsetCol(self, value):
        return self._set(offsetCol=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
