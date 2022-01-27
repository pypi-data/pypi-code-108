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
from ai.h2o.sparkling.ml.algos.H2OSupervisedAlgorithm import H2OSupervisedAlgorithm
from ai.h2o.sparkling.ml.models.H2OCoxPHMOJOModel import H2OCoxPHMOJOModel
from ai.h2o.sparkling.ml.params.H2OCoxPHParams import H2OCoxPHParams


class H2OCoxPH(H2OCoxPHParams, H2OSupervisedAlgorithm):

    @keyword_only
    def __init__(self,
                 ignoredCols=None,
                 interactionPairs=None,
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
                 withStageResults=False,
                 startCol=None,
                 stopCol=None,
                 stratifyBy=None,
                 ties="efron",
                 init=0.0,
                 lreMin=9.0,
                 maxIterations=20,
                 interactionsOnly=None,
                 interactions=None,
                 useAllFactorLevels=False,
                 singleNodeMode=False,
                 modelId=None,
                 labelCol="label",
                 weightCol=None,
                 offsetCol=None,
                 exportCheckpointsDir=None):
        Initializer.load_sparkling_jar()
        super(H2OCoxPH, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OCoxPH", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OCoxPHMOJOModel(javaModel)
