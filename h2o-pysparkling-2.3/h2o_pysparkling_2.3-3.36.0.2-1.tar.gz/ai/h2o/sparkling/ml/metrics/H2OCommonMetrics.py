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


class H2OCommonMetrics:

    def __init__(self, java_obj):
        self._java_obj = java_obj

    def getDescription(self):
        """
        Optional description for this scoring run (to note out-of-bag, sampled data, etc.).
        """
        value = self._java_obj.getDescription()
        return value

    def getScoringTime(self):
        """
        The time in mS since the epoch for the start of this scoring run.
        """
        value = self._java_obj.getScoringTime()
        return value

    def getMSE(self):
        """
        The Mean Squared Error of the prediction for this scoring run.
        """
        value = self._java_obj.getMSE()
        return value

    def getRMSE(self):
        """
        The Root Mean Squared Error of the prediction for this scoring run.
        """
        value = self._java_obj.getRMSE()
        return value

    def getNobs(self):
        """
        Number of observations.
        """
        value = self._java_obj.getNobs()
        return value

    def getCustomMetricName(self):
        """
        Name of custom metric.
        """
        value = self._java_obj.getCustomMetricName()
        return value

    def getCustomMetricValue(self):
        """
        Value of custom metric.
        """
        value = self._java_obj.getCustomMetricValue()
        return value
