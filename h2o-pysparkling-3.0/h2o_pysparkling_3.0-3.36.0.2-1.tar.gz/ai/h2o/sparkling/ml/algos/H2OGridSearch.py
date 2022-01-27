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
from ai.h2o.sparkling.ml.algos.H2OAlgorithm import H2OAlgorithm
from ai.h2o.sparkling.ml.params.H2OGridSearchParams import H2OGridSearchParams
from ai.h2o.sparkling.ml.algos.H2OGridSearchExtras import H2OGridSearchExtras


class H2OGridSearch(H2OGridSearchParams, H2OAlgorithm, H2OGridSearchExtras):

    @keyword_only
    def __init__(self,
                 algo=None,
                 hyperParameters={},
                 selectBestModelBy="AUTO",
                 parallelism=1,
                 seed=-1,
                 maxModels=0,
                 maxRuntimeSecs=0.0,
                 stoppingRounds=0,
                 stoppingMetric="AUTO",
                 stoppingTolerance=0.001,
                 strategy="Cartesian"):
        Initializer.load_sparkling_jar()
        super(H2OGridSearch, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OGridSearch", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()
