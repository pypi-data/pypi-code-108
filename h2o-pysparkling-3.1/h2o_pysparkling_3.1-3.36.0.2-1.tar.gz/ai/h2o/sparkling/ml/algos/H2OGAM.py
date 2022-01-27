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
from ai.h2o.sparkling.ml.algos.H2OSupervisedAlgorithmWithFoldColumn import H2OSupervisedAlgorithmWithFoldColumn
from ai.h2o.sparkling.ml.models.H2OGAMMOJOModel import H2OGAMMOJOModel
from ai.h2o.sparkling.ml.params.H2OGAMParams import H2OGAMParams
from ai.h2o.sparkling.ml.algos.FamilyBasedH2OTrainFramePreparation import FamilyBasedH2OTrainFramePreparation


class H2OGAM(H2OGAMParams, H2OSupervisedAlgorithmWithFoldColumn, FamilyBasedH2OTrainFramePreparation):

    @keyword_only
    def __init__(self,
                 ignoredCols=None,
                 betaConstraints=None,
                 gamCols=None,
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
                 seed=-1,
                 family="AUTO",
                 tweedieVariancePower=0.0,
                 tweedieLinkPower=0.0,
                 theta=0.0,
                 solver="AUTO",
                 alphaValue=None,
                 lambdaValue=None,
                 startval=None,
                 lambdaSearch=False,
                 earlyStopping=True,
                 nlambdas=-1,
                 standardize=False,
                 missingValuesHandling="MeanImputation",
                 nonNegative=False,
                 maxIterations=-1,
                 betaEpsilon=1.0E-4,
                 objectiveEpsilon=-1.0,
                 gradientEpsilon=-1.0,
                 objReg=-1.0,
                 link="family_default",
                 intercept=True,
                 prior=-1.0,
                 coldStart=False,
                 maxActivePredictors=-1,
                 interactions=None,
                 balanceClasses=False,
                 classSamplingFactors=None,
                 maxAfterBalanceSize=5.0,
                 maxConfusionMatrixSize=20,
                 computePValues=False,
                 removeCollinearCols=False,
                 numKnots=None,
                 scale=None,
                 bs=None,
                 keepGamCols=False,
                 standardizeTpGamCols=False,
                 scaleTpPenaltyMat=False,
                 knotIds=None,
                 modelId=None,
                 nfolds=0,
                 keepCrossValidationModels=True,
                 keepCrossValidationPredictions=False,
                 keepCrossValidationFoldAssignment=False,
                 labelCol="label",
                 weightCol=None,
                 offsetCol=None,
                 foldCol=None,
                 foldAssignment="AUTO",
                 ignoreConstCols=True,
                 scoreEachIteration=False,
                 stoppingRounds=0,
                 maxRuntimeSecs=0.0,
                 stoppingMetric="AUTO",
                 stoppingTolerance=0.001,
                 customMetricFunc=None,
                 exportCheckpointsDir=None,
                 aucType="AUTO"):
        Initializer.load_sparkling_jar()
        super(H2OGAM, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OGAM", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OGAMMOJOModel(javaModel)
