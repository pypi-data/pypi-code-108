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
from ai.h2o.sparkling.ml.params.HasLeaderboardDataFrame import HasLeaderboardDataFrame
from ai.h2o.sparkling.ml.params.HasBlendingDataFrame import HasBlendingDataFrame


class H2OAutoMLInputParams(HasIgnoredCols, HasLeaderboardDataFrame, HasBlendingDataFrame, Params):

    ##
    # Param definitions
    ##
    labelCol = Param(
        Params._dummy(),
        "labelCol",
        """Response column""",
        H2OTypeConverters.toString())

    foldCol = Param(
        Params._dummy(),
        "foldCol",
        """Fold column (contains fold IDs) in the training frame. These assignments are used to create the folds for cross-validation of the models.""",
        H2OTypeConverters.toNullableString())

    weightCol = Param(
        Params._dummy(),
        "weightCol",
        """Weights column in the training frame, which specifies the row weights used in model training.""",
        H2OTypeConverters.toNullableString())

    sortMetric = Param(
        Params._dummy(),
        "sortMetric",
        """Metric used to sort leaderboard""",
        H2OTypeConverters.toEnumString("ai.h2o.sparkling.ml.utils.H2OAutoMLSortMetric"))

    ##
    # Getters
    ##
    def getLabelCol(self):
        return self.getOrDefault(self.labelCol)

    def getFoldCol(self):
        return self.getOrDefault(self.foldCol)

    def getWeightCol(self):
        return self.getOrDefault(self.weightCol)

    def getSortMetric(self):
        return self.getOrDefault(self.sortMetric)

    ##
    # Setters
    ##
    def setLabelCol(self, value):
        return self._set(labelCol=value)

    def setFoldCol(self, value):
        return self._set(foldCol=value)

    def setWeightCol(self, value):
        return self._set(weightCol=value)

    def setSortMetric(self, value):
        return self._set(sortMetric=value)
