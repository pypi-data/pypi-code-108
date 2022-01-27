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
from ai.h2o.sparkling.ml.metrics.H2OCommonMetrics import H2OCommonMetrics


class H2OMultinomialMetrics(H2OCommonMetrics):

    def __init__(self, java_obj):
        self._java_obj = java_obj

    def getR2(self):
        """
        The R^2 for this scoring run.
        """
        value = self._java_obj.getR2()
        return value

    def getHitRatioTable(self):
        """
        The hit ratio table for this scoring run.
        """
        value = self._java_obj.getHitRatioTable()
        return H2OTypeConverters.scalaToPythonDataFrame(value)

    def getConfusionMatrix(self):
        """
        The ConfusionMatrix object for this scoring run.
        """
        value = self._java_obj.getConfusionMatrix()
        return H2OTypeConverters.scalaToPythonDataFrame(value)

    def getLogloss(self):
        """
        The logarithmic loss for this scoring run.
        """
        value = self._java_obj.getLogloss()
        return value

    def getMeanPerClassError(self):
        """
        The mean misclassification error per class.
        """
        value = self._java_obj.getMeanPerClassError()
        return value

    def getAUC(self):
        """
        The average AUC for this scoring run.
        """
        value = self._java_obj.getAUC()
        return value

    def getPRAUC(self):
        """
        The average precision-recall AUC for this scoring run.
        """
        value = self._java_obj.getPRAUC()
        return value

    def getMultinomialAUCTable(self):
        """
        The multinomial AUC values.
        """
        value = self._java_obj.getMultinomialAUCTable()
        return H2OTypeConverters.scalaToPythonDataFrame(value)

    def getMultinomialPRAUCTable(self):
        """
        The multinomial PR AUC values.
        """
        value = self._java_obj.getMultinomialPRAUCTable()
        return H2OTypeConverters.scalaToPythonDataFrame(value)
