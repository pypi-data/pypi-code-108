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
from ai.h2o.sparkling.ml.models.H2OGBMMOJOModel import H2OGBMMOJOModel
from ai.h2o.sparkling.ml.params.H2OGBMParams import H2OGBMParams
from ai.h2o.sparkling.ml.algos.DistributionBasedH2OTrainFramePreparation import DistributionBasedH2OTrainFramePreparation


class H2OGBM(H2OGBMParams, H2OTreeBasedSupervisedAlgorithm, DistributionBasedH2OTrainFramePreparation):

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
                 learnRate=0.1,
                 learnRateAnnealing=1.0,
                 sampleRate=1.0,
                 colSampleRate=1.0,
                 maxAbsLeafnodePred=1.7976931348623157E308,
                 predNoiseBandwidth=0.0,
                 balanceClasses=False,
                 classSamplingFactors=None,
                 maxAfterBalanceSize=5.0,
                 maxConfusionMatrixSize=20,
                 ntrees=50,
                 maxDepth=5,
                 minRows=10.0,
                 nbins=20,
                 nbinsTopLevel=1024,
                 nbinsCats=1024,
                 seed=-1,
                 buildTreeOneNode=False,
                 sampleRatePerClass=None,
                 colSampleRatePerTree=1.0,
                 colSampleRateChangePerLevel=1.0,
                 scoreTreeInterval=0,
                 minSplitImprovement=1.0E-5,
                 histogramType="AUTO",
                 calibrateModel=False,
                 checkConstantResponse=True,
                 modelId=None,
                 nfolds=0,
                 keepCrossValidationModels=True,
                 keepCrossValidationPredictions=False,
                 keepCrossValidationFoldAssignment=False,
                 distribution="AUTO",
                 tweediePower=1.5,
                 quantileAlpha=0.5,
                 huberAlpha=0.9,
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
                 customMetricFunc=None,
                 customDistributionFunc=None,
                 exportCheckpointsDir=None,
                 aucType="AUTO"):
        Initializer.load_sparkling_jar()
        super(H2OGBM, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OGBM", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OGBMMOJOModel(javaModel)
