from perceptilabs.automation.autosettings.base import SettingsEngine, InferenceRule
from perceptilabs.automation.autosettings.rules import *


DEFAULT_RULES = [
    DeepLearningFcOutputShapeFromLabels,
    ProcessReshape1DFromPrimeFactors,
    DeepLearningConvDoubleFeatureMaps,
    DataDataShouldUseLazy
]


    
    
    
