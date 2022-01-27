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

from pyspark.ml.util import _jvm
from py4j.java_gateway import JavaObject
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.models.H2OMOJOSettings import H2OMOJOSettings
from ai.h2o.sparkling.ml.models.H2OMOJOModelBase import H2OMOJOModelBase
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OTreeBasedSupervisedMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OTreeBasedUnsupervisedMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OSupervisedMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OUnsupervisedMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OAlgorithmMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OFeatureMOJOModelParams
from ai.h2o.sparkling.ml.params.H2OMOJOModelParams import H2OMOJOModelParams
from ai.h2o.sparkling.ml.models.H2OXGBoostMOJOModel import H2OXGBoostMOJOModel
from ai.h2o.sparkling.ml.models.H2OGBMMOJOModel import H2OGBMMOJOModel
from ai.h2o.sparkling.ml.models.H2ODRFMOJOModel import H2ODRFMOJOModel
from ai.h2o.sparkling.ml.models.H2OGLMMOJOModel import H2OGLMMOJOModel
from ai.h2o.sparkling.ml.models.H2OGAMMOJOModel import H2OGAMMOJOModel
from ai.h2o.sparkling.ml.models.H2ODeepLearningMOJOModel import H2ODeepLearningMOJOModel
from ai.h2o.sparkling.ml.models.H2ORuleFitMOJOModel import H2ORuleFitMOJOModel
from ai.h2o.sparkling.ml.models.H2OKMeansMOJOModel import H2OKMeansMOJOModel
from ai.h2o.sparkling.ml.models.H2OCoxPHMOJOModel import H2OCoxPHMOJOModel
from ai.h2o.sparkling.ml.models.H2OIsolationForestMOJOModel import H2OIsolationForestMOJOModel
from ai.h2o.sparkling.ml.models.H2OAutoEncoderMOJOModel import H2OAutoEncoderMOJOModel
from ai.h2o.sparkling.ml.models.H2OPCAMOJOModel import H2OPCAMOJOModel
from ai.h2o.sparkling.ml.models.H2OGLRMMOJOModel import H2OGLRMMOJOModel
from ai.h2o.sparkling.ml.models.H2OWord2VecMOJOModel import H2OWord2VecMOJOModel


class H2OMOJOModelFactory:

    @staticmethod
    def createFromMojo(pathToMojo, settings=H2OMOJOSettings.default()):
        # We need to make sure that Sparkling Water classes are available on the Spark driver and executor paths
        Initializer.load_sparkling_jar()
        javaModel = _jvm().ai.h2o.sparkling.ml.models.H2OMOJOModel.createFromMojo(pathToMojo, settings.toJavaObject())
        return H2OMOJOModelFactory.createSpecificMOJOModel(javaModel)


    @staticmethod
    def createSpecificMOJOModel(javaModel):
        className = javaModel.getClass().getSimpleName()
        if className == "H2OTreeBasedSupervisedMOJOModel":
            return H2OTreeBasedSupervisedMOJOModel(javaModel)
        elif className == "H2OTreeBasedUnsupervisedMOJOModel":
            return H2OTreeBasedUnsupervisedMOJOModel(javaModel)
        elif className == "H2OSupervisedMOJOModel":
            return H2OSupervisedMOJOModel(javaModel)
        elif className == "H2OUnsupervisedMOJOModel":
            return H2OUnsupervisedMOJOModel(javaModel)
        elif className == "H2OAlgorithmMOJOModel":
            return H2OAlgorithmMOJOModel(javaModel)
        elif className == "H2OFeatureMOJOModel":
            return H2OFeatureMOJOModel(javaModel)
        elif className == "H2OXGBoostMOJOModel":
            return H2OXGBoostMOJOModel(javaModel)
        elif className == "H2OGBMMOJOModel":
            return H2OGBMMOJOModel(javaModel)
        elif className == "H2ODRFMOJOModel":
            return H2ODRFMOJOModel(javaModel)
        elif className == "H2OGLMMOJOModel":
            return H2OGLMMOJOModel(javaModel)
        elif className == "H2OGAMMOJOModel":
            return H2OGAMMOJOModel(javaModel)
        elif className == "H2ODeepLearningMOJOModel":
            return H2ODeepLearningMOJOModel(javaModel)
        elif className == "H2ORuleFitMOJOModel":
            return H2ORuleFitMOJOModel(javaModel)
        elif className == "H2OKMeansMOJOModel":
            return H2OKMeansMOJOModel(javaModel)
        elif className == "H2OCoxPHMOJOModel":
            return H2OCoxPHMOJOModel(javaModel)
        elif className == "H2OIsolationForestMOJOModel":
            return H2OIsolationForestMOJOModel(javaModel)
        elif className == "H2OAutoEncoderMOJOModel":
            return H2OAutoEncoderMOJOModel(javaModel)
        elif className == "H2OPCAMOJOModel":
            return H2OPCAMOJOModel(javaModel)
        elif className == "H2OGLRMMOJOModel":
            return H2OGLRMMOJOModel(javaModel)
        elif className == "H2OWord2VecMOJOModel":
            return H2OWord2VecMOJOModel(javaModel)
        else:
            return H2OMOJOModel(javaModel)


class WithCVModels(H2OMOJOModelFactory):
    def getCrossValidationModels(self):
        cvModels = self._java_obj.getCrossValidationModelsAsArray()
        if cvModels is None:
            return None
        elif isinstance(cvModels, JavaObject):
            return [createSpecificMOJOModel(v) for v in cvModels]
        else:
            raise TypeError("Invalid type.")


class H2OMOJOModel(H2OMOJOModelParams, H2OMOJOModelBase, WithCVModels):
    pass


class H2OAlgorithmMOJOModel(H2OAlgorithmMOJOModelParams, WithCVModels):
    pass


class H2OFeatureMOJOModel(H2OFeatureMOJOModelParams, WithCVModels):
    pass


class H2OUnsupervisedMOJOModel(H2OUnsupervisedMOJOModelParams, WithCVModels):
    pass


class H2OSupervisedMOJOModel(H2OSupervisedMOJOModelParams, WithCVModels):
    pass


class H2OTreeBasedUnsupervisedMOJOModel(H2OTreeBasedUnsupervisedMOJOModelParams, WithCVModels):
    pass


class H2OTreeBasedSupervisedMOJOModel(H2OTreeBasedSupervisedMOJOModelParams, WithCVModels):
    pass
