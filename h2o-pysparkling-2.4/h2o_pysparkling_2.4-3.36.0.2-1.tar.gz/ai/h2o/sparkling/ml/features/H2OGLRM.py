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
from ai.h2o.sparkling.ml.features.H2OGLRMBase import H2OGLRMBase
from ai.h2o.sparkling.ml.models.H2OGLRMMOJOModel import H2OGLRMMOJOModel
from ai.h2o.sparkling.ml.params.H2OGLRMParams import H2OGLRMParams


class H2OGLRM(H2OGLRMParams, H2OGLRMBase):

    @keyword_only
    def __init__(self,
                 userX=None,
                 userY=None,
                 lossByColNames=None,
                 columnsToCategorical=[],
                 keepBinaryModels=False,
                 maxScoringIterations=100,
                 dataFrameSerializer="ai.h2o.sparkling.utils.JSONDataFrameSerializer",
                 convertInvalidNumbersToNa=False,
                 outputCol="GLRM__output",
                 validationDataFrame=None,
                 reconstructedCol="GLRM__reconstructed",
                 convertUnknownCategoricalLevelsToNa=False,
                 inputCols=[],
                 splitRatio=1.0,
                 withReconstructedCol=False,
                 transform="NONE",
                 k=1,
                 loss="Quadratic",
                 multiLoss="Categorical",
                 lossByCol=None,
                 period=1,
                 regularizationX="None",
                 regularizationY="None",
                 gammaX=0.0,
                 gammaY=0.0,
                 maxIterations=1000,
                 maxUpdates=2000,
                 initStepSize=1.0,
                 minStepSize=1.0E-4,
                 seed=-1,
                 init="PlusPlus",
                 svdMethod="Randomized",
                 loadingName=None,
                 representationName=None,
                 expandUserY=True,
                 imputeOriginal=False,
                 recoverSvd=False,
                 modelId=None,
                 ignoredCols=None,
                 ignoreConstCols=True,
                 scoreEachIteration=False,
                 maxRuntimeSecs=0.0,
                 exportCheckpointsDir=None):
        Initializer.load_sparkling_jar()
        super(H2OGLRM, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.features.H2OGLRM", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OGLRMMOJOModel(javaModel)
