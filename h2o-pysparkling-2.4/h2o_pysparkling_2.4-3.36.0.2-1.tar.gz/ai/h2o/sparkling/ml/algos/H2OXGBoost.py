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
from ai.h2o.sparkling.ml.algos.H2OTreeBasedSupervisedAlgorithm import H2OTreeBasedSupervisedAlgorithm
from ai.h2o.sparkling.ml.models.H2OXGBoostMOJOModel import H2OXGBoostMOJOModel
from ai.h2o.sparkling.ml.params.H2OXGBoostParams import H2OXGBoostParams
from ai.h2o.sparkling.ml.algos.DistributionBasedH2OTrainFramePreparation import DistributionBasedH2OTrainFramePreparation


class H2OXGBoost(H2OXGBoostParams, H2OTreeBasedSupervisedAlgorithm, DistributionBasedH2OTrainFramePreparation):

    @keyword_only
    def __init__(self,
                 monotoneConstraints={},
                 calibrationDataFrame=None,
                 ignoredCols=None,
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
                 ntrees=50,
                 maxDepth=6,
                 minRows=1.0,
                 minChildWeight=1.0,
                 learnRate=0.3,
                 eta=0.3,
                 sampleRate=1.0,
                 subsample=1.0,
                 colSampleRate=1.0,
                 colSampleByLevel=1.0,
                 colSampleRatePerTree=1.0,
                 colSampleByTree=1.0,
                 colSampleByNode=1.0,
                 maxAbsLeafnodePred=0.0,
                 maxDeltaStep=0.0,
                 scoreTreeInterval=0,
                 seed=-1,
                 minSplitImprovement=0.0,
                 gamma=0.0,
                 nthread=-1,
                 buildTreeOneNode=False,
                 saveMatrixDirectory=None,
                 calibrateModel=False,
                 maxBins=256,
                 maxLeaves=0,
                 treeMethod="auto",
                 growPolicy="depthwise",
                 booster="gbtree",
                 regLambda=1.0,
                 regAlpha=0.0,
                 quietMode=True,
                 sampleType="uniform",
                 normalizeType="tree",
                 rateDrop=0.0,
                 oneDrop=False,
                 skipDrop=0.0,
                 dmatrixType="auto",
                 backend="auto",
                 gpuId=None,
                 interactionConstraints=None,
                 scalePosWeight=1.0,
                 modelId=None,
                 nfolds=0,
                 keepCrossValidationModels=True,
                 keepCrossValidationPredictions=False,
                 keepCrossValidationFoldAssignment=False,
                 distribution="AUTO",
                 tweediePower=1.5,
                 labelCol="label",
                 weightCol=None,
                 offsetCol=None,
                 foldCol=None,
                 foldAssignment="AUTO",
                 categoricalEncoding="AUTO",
                 ignoreConstCols=True,
                 scoreEachIteration=False,
                 stoppingRounds=0,
                 maxRuntimeSecs=0.0,
                 stoppingMetric="AUTO",
                 stoppingTolerance=0.001,
                 gainsliftBins=-1,
                 exportCheckpointsDir=None,
                 aucType="AUTO"):
        Initializer.load_sparkling_jar()
        super(H2OXGBoost, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OXGBoost", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OXGBoostMOJOModel(javaModel)
