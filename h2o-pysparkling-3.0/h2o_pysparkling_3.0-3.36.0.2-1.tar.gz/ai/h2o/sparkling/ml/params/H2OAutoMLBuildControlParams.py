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


class H2OAutoMLBuildControlParams(Params):

    ##
    # Param definitions
    ##
    projectName = Param(
        Params._dummy(),
        "projectName",
        """Optional project name used to group models from multiple AutoML runs into a single Leaderboard; derived from the training data name if not specified.""",
        H2OTypeConverters.toNullableString())

    nfolds = Param(
        Params._dummy(),
        "nfolds",
        """Number of folds for k-fold cross-validation (defaults to -1 (AUTO), otherwise it must be >=2 or use 0 to disable). Disabling prevents Stacked Ensembles from being built.""",
        H2OTypeConverters.toInt())

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
        """Maximum relative size of the training data after balancing class counts (defaults to 5.0 and can be less than 1.0). Requires balance_classes.""",
        H2OTypeConverters.toFloat())

    keepCrossValidationPredictions = Param(
        Params._dummy(),
        "keepCrossValidationPredictions",
        """Whether to keep the predictions of the cross-validation predictions. This needs to be set to TRUE if running the same AutoML object for repeated runs because CV predictions are required to build additional Stacked Ensemble models in AutoML.""",
        H2OTypeConverters.toBoolean())

    keepCrossValidationModels = Param(
        Params._dummy(),
        "keepCrossValidationModels",
        """Whether to keep the cross-validated models. Keeping cross-validation models may consume significantly more memory in the H2O cluster.""",
        H2OTypeConverters.toBoolean())

    keepCrossValidationFoldAssignment = Param(
        Params._dummy(),
        "keepCrossValidationFoldAssignment",
        """Whether to keep cross-validation assignments.""",
        H2OTypeConverters.toBoolean())

    exportCheckpointsDir = Param(
        Params._dummy(),
        "exportCheckpointsDir",
        """Path to a directory where every generated model will be stored.""",
        H2OTypeConverters.toNullableString())

    ##
    # Getters
    ##
    def getProjectName(self):
        return self.getOrDefault(self.projectName)

    def getNfolds(self):
        return self.getOrDefault(self.nfolds)

    def getBalanceClasses(self):
        return self.getOrDefault(self.balanceClasses)

    def getClassSamplingFactors(self):
        return self.getOrDefault(self.classSamplingFactors)

    def getMaxAfterBalanceSize(self):
        return self.getOrDefault(self.maxAfterBalanceSize)

    def getKeepCrossValidationPredictions(self):
        return self.getOrDefault(self.keepCrossValidationPredictions)

    def getKeepCrossValidationModels(self):
        return self.getOrDefault(self.keepCrossValidationModels)

    def getKeepCrossValidationFoldAssignment(self):
        return self.getOrDefault(self.keepCrossValidationFoldAssignment)

    def getExportCheckpointsDir(self):
        return self.getOrDefault(self.exportCheckpointsDir)

    ##
    # Setters
    ##
    def setProjectName(self, value):
        return self._set(projectName=value)

    def setNfolds(self, value):
        return self._set(nfolds=value)

    def setBalanceClasses(self, value):
        return self._set(balanceClasses=value)

    def setClassSamplingFactors(self, value):
        return self._set(classSamplingFactors=value)

    def setMaxAfterBalanceSize(self, value):
        return self._set(maxAfterBalanceSize=value)

    def setKeepCrossValidationPredictions(self, value):
        return self._set(keepCrossValidationPredictions=value)

    def setKeepCrossValidationModels(self, value):
        return self._set(keepCrossValidationModels=value)

    def setKeepCrossValidationFoldAssignment(self, value):
        return self._set(keepCrossValidationFoldAssignment=value)

    def setExportCheckpointsDir(self, value):
        return self._set(exportCheckpointsDir=value)
