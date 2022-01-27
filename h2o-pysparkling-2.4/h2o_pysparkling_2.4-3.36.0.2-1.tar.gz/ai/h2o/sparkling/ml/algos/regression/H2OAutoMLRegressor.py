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

from warnings import warn
from pyspark import keyword_only
from ai.h2o.sparkling import Initializer
from ai.h2o.sparkling.ml.Utils import Utils
from ai.h2o.sparkling.ml.algos.H2OAutoML import H2OAutoML


class H2OAutoMLRegressor(H2OAutoML):

    @keyword_only
    def __init__(self,
                 ignoredCols=None,
                 leaderboardDataFrame=None,
                 blendingDataFrame=None,
                 columnsToCategorical=[],
                 keepBinaryModels=False,
                 withContributions=False,
                 dataFrameSerializer="ai.h2o.sparkling.utils.JSONDataFrameSerializer",
                 withLeafNodeAssignments=False,
                 namedMojoOutputColumns=True,
                 convertInvalidNumbersToNa=False,
                 detailedPredictionCol="detailed_prediction",
                 validationDataFrame=None,
                 featuresCols=[],
                 predictionCol="prediction",
                 convertUnknownCategoricalLevelsToNa=False,
                 splitRatio=1.0,
                 monotoneConstraints={},
                 withStageResults=False,
                 projectName=None,
                 nfolds=-1,
                 balanceClasses=False,
                 classSamplingFactors=None,
                 maxAfterBalanceSize=5.0,
                 keepCrossValidationPredictions=False,
                 keepCrossValidationModels=False,
                 keepCrossValidationFoldAssignment=False,
                 exportCheckpointsDir=None,
                 labelCol="label",
                 foldCol=None,
                 weightCol=None,
                 sortMetric="AUTO",
                 seed=-1,
                 maxModels=0,
                 maxRuntimeSecs=0.0,
                 maxRuntimeSecsPerModel=0.0,
                 stoppingRounds=3,
                 stoppingMetric="AUTO",
                 stoppingTolerance=-1.0,
                 excludeAlgos=None,
                 includeAlgos=["GLM", "DRF", "GBM", "DeepLearning", "StackedEnsemble", "XGBoost"],
                 exploitationRatio=-1.0):
        Initializer.load_sparkling_jar()
        super(H2OAutoML, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.regression.H2OAutoMLRegressor", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()
