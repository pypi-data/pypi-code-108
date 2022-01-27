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
from ai.h2o.sparkling.ml.features.H2OWord2VecBase import H2OWord2VecBase
from ai.h2o.sparkling.ml.models.H2OWord2VecMOJOModel import H2OWord2VecMOJOModel
from ai.h2o.sparkling.ml.params.H2OWord2VecParams import H2OWord2VecParams


class H2OWord2Vec(H2OWord2VecParams, H2OWord2VecBase):

    @keyword_only
    def __init__(self,
                 preTrained=None,
                 columnsToCategorical=[],
                 inputCol=None,
                 keepBinaryModels=False,
                 dataFrameSerializer="ai.h2o.sparkling.utils.JSONDataFrameSerializer",
                 convertInvalidNumbersToNa=False,
                 outputCol="Word2Vec__output",
                 validationDataFrame=None,
                 convertUnknownCategoricalLevelsToNa=False,
                 splitRatio=1.0,
                 vecSize=100,
                 windowSize=5,
                 sentSampleRate=0.001,
                 normModel="HSM",
                 epochs=5,
                 minWordFreq=5,
                 initLearningRate=0.025,
                 wordModel="SkipGram",
                 modelId=None,
                 maxRuntimeSecs=0.0,
                 exportCheckpointsDir=None):
        Initializer.load_sparkling_jar()
        super(H2OWord2Vec, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.features.H2OWord2Vec", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OWord2VecMOJOModel(javaModel)
