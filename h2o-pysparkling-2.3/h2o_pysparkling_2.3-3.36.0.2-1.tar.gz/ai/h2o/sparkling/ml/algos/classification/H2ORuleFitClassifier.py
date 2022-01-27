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
from ai.h2o.sparkling.ml.algos.H2ORuleFit import H2ORuleFit


class H2ORuleFitClassifier(H2ORuleFit):

    @keyword_only
    def __init__(self,
                 offsetCol=None,
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
                 seed=-1,
                 algorithm="AUTO",
                 minRuleLength=3,
                 maxRuleLength=3,
                 maxNumRules=-1,
                 modelType="RULES_AND_LINEAR",
                 ruleGenerationNtrees=50,
                 removeDuplicates=True,
                 lambdaValue=None,
                 modelId=None,
                 distribution="AUTO",
                 labelCol="label",
                 weightCol=None,
                 aucType="AUTO"):
        Initializer.load_sparkling_jar()
        super(H2ORuleFit, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.classification.H2ORuleFitClassifier", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()
