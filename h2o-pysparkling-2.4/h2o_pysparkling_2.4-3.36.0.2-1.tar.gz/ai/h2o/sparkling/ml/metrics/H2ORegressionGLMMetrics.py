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
from ai.h2o.sparkling.ml.metrics.H2ORegressionMetrics import H2ORegressionMetrics


class H2ORegressionGLMMetrics(H2ORegressionMetrics):

    def __init__(self, java_obj):
        self._java_obj = java_obj

    def getResidualDeviance(self):
        """
        residual deviance.
        """
        value = self._java_obj.getResidualDeviance()
        return value

    def getNullDeviance(self):
        """
        null deviance.
        """
        value = self._java_obj.getNullDeviance()
        return value

    def getAIC(self):
        """
        AIC.
        """
        value = self._java_obj.getAIC()
        return value

    def getNullDegreesOfFreedom(self):
        """
        null DOF.
        """
        value = self._java_obj.getNullDegreesOfFreedom()
        return value

    def getResidualDegreesOfFreedom(self):
        """
        residual DOF.
        """
        value = self._java_obj.getResidualDegreesOfFreedom()
        return value
