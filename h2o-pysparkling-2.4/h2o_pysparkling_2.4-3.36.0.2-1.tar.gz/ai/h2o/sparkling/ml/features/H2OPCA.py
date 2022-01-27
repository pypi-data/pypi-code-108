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
from ai.h2o.sparkling.ml.features.H2ODimReductionEstimator import H2ODimReductionEstimator
from ai.h2o.sparkling.ml.models.H2OPCAMOJOModel import H2OPCAMOJOModel
from ai.h2o.sparkling.ml.params.H2OPCAParams import H2OPCAParams


class H2OPCA(H2OPCAParams, H2ODimReductionEstimator):

    @keyword_only
    def __init__(self,
                 ignoredCols=None,
                 columnsToCategorical=[],
                 keepBinaryModels=False,
                 dataFrameSerializer="ai.h2o.sparkling.utils.JSONDataFrameSerializer",
                 convertInvalidNumbersToNa=False,
                 outputCol="PCA__output",
                 validationDataFrame=None,
                 convertUnknownCategoricalLevelsToNa=False,
                 inputCols=[],
                 splitRatio=1.0,
                 transform="NONE",
                 pcaMethod="GramSVD",
                 pcaImpl="MTJ_EVD_SYMMMATRIX",
                 k=1,
                 maxIterations=1000,
                 seed=-1,
                 useAllFactorLevels=False,
                 computeMetrics=True,
                 imputeMissing=False,
                 modelId=None,
                 ignoreConstCols=True,
                 scoreEachIteration=False,
                 maxRuntimeSecs=0.0,
                 exportCheckpointsDir=None):
        Initializer.load_sparkling_jar()
        super(H2OPCA, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.features.H2OPCA", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OPCAMOJOModel(javaModel)
