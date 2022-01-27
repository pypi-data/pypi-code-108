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

from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.ml.metrics.H2OCommonMetrics import H2OCommonMetrics
from ai.h2o.sparkling.ml.metrics.H2OBinomialMetrics import H2OBinomialMetrics
from ai.h2o.sparkling.ml.metrics.H2OBinomialGLMMetrics import H2OBinomialGLMMetrics
from ai.h2o.sparkling.ml.metrics.H2ORegressionMetrics import H2ORegressionMetrics
from ai.h2o.sparkling.ml.metrics.H2ORegressionGLMMetrics import H2ORegressionGLMMetrics
from ai.h2o.sparkling.ml.metrics.H2ORegressionCoxPHMetrics import H2ORegressionCoxPHMetrics
from ai.h2o.sparkling.ml.metrics.H2OMultinomialMetrics import H2OMultinomialMetrics
from ai.h2o.sparkling.ml.metrics.H2OMultinomialGLMMetrics import H2OMultinomialGLMMetrics
from ai.h2o.sparkling.ml.metrics.H2OOrdinalMetrics import H2OOrdinalMetrics
from ai.h2o.sparkling.ml.metrics.H2OOrdinalGLMMetrics import H2OOrdinalGLMMetrics
from ai.h2o.sparkling.ml.metrics.H2OAnomalyMetrics import H2OAnomalyMetrics
from ai.h2o.sparkling.ml.metrics.H2OClusteringMetrics import H2OClusteringMetrics
from ai.h2o.sparkling.ml.metrics.H2OAutoEncoderMetrics import H2OAutoEncoderMetrics
from ai.h2o.sparkling.ml.metrics.H2OGLRMMetrics import H2OGLRMMetrics
from ai.h2o.sparkling.ml.metrics.H2OPCAMetrics import H2OPCAMetrics


class H2OMetricsFactory:

    def __init__(self, javaObject):
        self._java_obj = javaObject

    @staticmethod
    def fromJavaObject(javaObject):
        if javaObject is None:
            return None
        elif javaObject.getClass().getSimpleName() == "H2OCommonMetrics":
            return H2OCommonMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OBinomialMetrics":
            return H2OBinomialMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OBinomialGLMMetrics":
            return H2OBinomialGLMMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2ORegressionMetrics":
            return H2ORegressionMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2ORegressionGLMMetrics":
            return H2ORegressionGLMMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2ORegressionCoxPHMetrics":
            return H2ORegressionCoxPHMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OMultinomialMetrics":
            return H2OMultinomialMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OMultinomialGLMMetrics":
            return H2OMultinomialGLMMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OOrdinalMetrics":
            return H2OOrdinalMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OOrdinalGLMMetrics":
            return H2OOrdinalGLMMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OAnomalyMetrics":
            return H2OAnomalyMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OClusteringMetrics":
            return H2OClusteringMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OAutoEncoderMetrics":
            return H2OAutoEncoderMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OGLRMMetrics":
            return H2OGLRMMetrics(javaObject)
        elif javaObject.getClass().getSimpleName() == "H2OPCAMetrics":
            return H2OPCAMetrics(javaObject)
        else:
            return H2OCommonMetrics(javaObject)
