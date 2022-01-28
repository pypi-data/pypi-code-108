from .data_processing import DataControlBlock
from .data_preprocessing import DataPreprocessor
from .data_transformation import DataTransformer
from .evaluations import Evaluation
from .exploratory_data_analysis import ExploratoryDataAnalysis
from .exploratory_data_analysis import Counting
from .probability import Probability as Prob

_dp = DataPreprocessor()
time_splitor = _dp.time_splitor
DataTransformer = DataTransformer()

def Probability(distribution='poisson', params:dict=None, simulate:dict=False):
    prob = Prob(distribution)
    if params is None:
        return prob.parameter_manual()
    else:
        prob.insert_params(params)

    if simulate is False:
        return prob.probability
    elif simulate is True:
        print(prob.probability)
        return prob.simulate(prob.params)
    elif isinstance(simulate, dict):
        return prob.simulate(simulate)
    else:
        return prob.probability

def DataProcessor(frames):
    return DataControlBlock(frames)

def EDA(frame, save=False, path='ExploratoryDataAnalysis', verbose=True):
    return ExploratoryDataAnalysis(frame=frame, save=save, path=path, verbose=verbose)

def counting(frame, view='table', save=False, path=None):
    counter = Counting(frame=frame)
    frame = counter.CountUniqueValues(view=view, save=save, path=path)
    return frame
