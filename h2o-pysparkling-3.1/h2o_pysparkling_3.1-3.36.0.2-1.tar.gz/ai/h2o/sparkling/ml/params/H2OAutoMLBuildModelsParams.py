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

from pyspark.ml.param import *
from ai.h2o.sparkling.ml.params.H2OTypeConverters import H2OTypeConverters


class H2OAutoMLBuildModelsParams(Params):

    ##
    # Param definitions
    ##
    excludeAlgos = Param(
        Params._dummy(),
        "excludeAlgos",
        """A list of algorithms to skip during the model-building phase.""",
        H2OTypeConverters.toNullableListEnumString("ai.h2o.automl.Algo"))

    includeAlgos = Param(
        Params._dummy(),
        "includeAlgos",
        """A list of algorithms to restrict to during the model-building phase.""",
        H2OTypeConverters.toListEnumString("ai.h2o.automl.Algo"))

    exploitationRatio = Param(
        Params._dummy(),
        "exploitationRatio",
        """The budget ratio (between 0 and 1) dedicated to the exploitation (vs exploration) phase.""",
        H2OTypeConverters.toFloat())

    ##
    # Getters
    ##
    def getExcludeAlgos(self):
        return self.getOrDefault(self.excludeAlgos)

    def getIncludeAlgos(self):
        return self.getOrDefault(self.includeAlgos)

    def getExploitationRatio(self):
        return self.getOrDefault(self.exploitationRatio)

    ##
    # Setters
    ##
    def setExcludeAlgos(self, value):
        return self._set(excludeAlgos=value)

    def setIncludeAlgos(self, value):
        return self._set(includeAlgos=value)

    def setExploitationRatio(self, value):
        return self._set(exploitationRatio=value)
