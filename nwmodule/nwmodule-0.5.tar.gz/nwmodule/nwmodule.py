import torch as tr
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import OrderedDict
from collections.abc import Iterable
from typing import List, Union, Dict, Callable, Optional, Iterable, Any, Tuple
from types import LambdaType
from nwutils.others import topologicalSort
from nwutils.data_structures import deepCheckEqual
from nwutils.torch import getNumParams, npGetData, trGetData, trToDevice, getOptimizerStr

from abc import abstractmethod, ABC
from .serializer import NWModuleSerializer
from .logger import logger
from .callbacks import Callback, CallbackName
from .metrics import Metric, MetricWrapper, Loss
from .nwtypes import CriterionType

np.set_printoptions(precision=3, suppress=True)

# Wrapper on top of the PyTorch model. Added methods for saving and loading a state. To completly implement a PyTorch
#  model, one must define layers in the object's constructor, call setOptimizer, setCriterion and implement the
#  forward method identically like a normal PyTorch model.
class NWModule(nn.Module, ABC):
    def __init__(self, hyperParameters:Optional[Dict]=None):
        super().__init__()
        self.optimizer:Optional[optim.Optim] = None
        self.optimizerScheduler = None
        self.serializer = NWModuleSerializer(self)
        self.reset_parameters()
        self.hyperParameters = {}
        self.setHyperParameters(hyperParameters)

    # The network algorithm. This must be updated for specific networks, so the whole metric/callbacks system works
    #  just as before.
    # @param[in] trInputs The inputs of the network
    # @param[in] trLabels The labels of the network
    # @return The results of the network and the loss as given by the criterion function
    @abstractmethod
    def networkAlgorithm(self, trInputs, trLabels, isTraining:bool=False, isOptimizing:bool=False):
        pass

    def train_step(self, inputs: Any, labels: Any, is_optimizing: bool = True) -> Tuple[float, float]:
        pass

    ##### Metrics, callbacks and hyperparameters #####

    # @brief Adds hyperparameters to the dictionary. Only works if the model has not been trained yet (so we don't)
    #  update the hyperparameters post-training as it would invalidate the whole principle.
    def setHyperParameters(self, hyperParameters:Dict):
        assert self.hyperParameters == {}, "Clear the existing hyperparameters before setting them. " \
            f"- Current: \n{self.hyperParameters}.\n -New: \n{hyperParameters}"
        hyperParameters = hyperParameters if not hyperParameters is None else {}
        assert isinstance(hyperParameters, dict)
        self.hyperParameters = hyperParameters

    def invalidateTopologicalSort(self):
        # See warning for add Metrics
        self.topologicalSort = np.arange(len(self.callbacks))
        self.topologicalKeys = np.array(list(self.callbacks.keys()))[self.topologicalSort]
        self.topologicalSortDirty = True

    def addMetric(self, metricName:Union[str, CallbackName], metric:Union[Callable, Metric]):
        # partial or lambda but not metric
        if isinstance(metric, (Callable, LambdaType, Callback)) and (not isinstance(metric, Metric)): #type: ignore
            metric = MetricWrapper(metric) #type: ignore
        if not isinstance(metricName, CallbackName): #type: ignore
            metricName = CallbackName(metricName) #type: ignore
        if metricName in self.callbacks:
            raise Exception(f"Metric '{metricName}' already exists")

        metric.setName(metricName) #type: ignore
        self.callbacks[metricName] = metric
        self.invalidateTopologicalSort()

    # Sets the user provided list of metrics as callbacks and adds them to the callbacks list.
    def addMetrics(self, metrics:Dict[str, Union[Callable, Metric]]):
        assert isinstance(metrics, dict), "Metrics must be provided as Str=>Callback dictionary"

        for metricName, metric in metrics.items():
            if metricName == "Loss":
                continue
            assert metricName not in self.callbacks, f"Metric {metricName} already in callbacks list."
            self.addMetric(metricName, metric)
        # Warning, calling addMetrics will invalidate topological sort as we reset the indexes here. If there are
        #  dependencies already set using setCallbacksDependeices, it must be called again.
        self.invalidateTopologicalSort()

    def addCallback(self, callback:Callback):
        assert isinstance(callback, Callback), f"Expected only subclass of types Callback, got type {type(callback)}"
        assert callback.name not in self.callbacks, f"Callback {callback.name} already in callbacks list."
        self.callbacks[callback.name] = callback
        # Warning, calling addCallbacks will invalidate topological sort as we reset the indexes here. If there are
        #  dependencies already set using setCallbacksDependeices, it must be called again.
        # TODO: see if this is needed or we can add a new node to the existing topological sort graph
        self.invalidateTopologicalSort()

    # Adds the user provided list of callbacks to the model's list of callbacks (and metrics)
    def addCallbacks(self, callbacks:List[Callback]):
        for callback in callbacks:
            self.addCallback(callback)

    # TODO: Add clearMetrics. Store dependencies, so we can call topological sort before/after clearCallbacks.
    # Store dependencies on model store. Make clearCallbacks clear only callbacks, not metrics as well.
    def clearMetrics(self):
        metrics = [x.name for x in filter(lambda x : isinstance(x, Metric), self.callbacks.values())]
        newCallbacks = OrderedDict({})
        for key in self.callbacks:
            callback = self.callbacks[key]
            if not isinstance(callback, Metric):
                newCallbacks[key] = callback
        self.callbacks = newCallbacks
        self.invalidateTopologicalSort()

    def clearCallbacks(self):
        self.callbacks = OrderedDict()
        self.addMetric("Loss", Loss())
        self.invalidateTopologicalSort()

    # Does a topological sort on the given list of callback dependencies. This MUST be called after all addMetrics and
    #  addCallbacks are called, as these functions invalidate the topological sort.
    def setCallbacksDependencies(self, dependencies):
        # Convert strings and callbacks to CallbackNames
        convertedDependencies = {}
        for key in dependencies:
            items = dependencies[key]
            if isinstance(key, str):
                key = CallbackName(key)
            if isinstance(key, Callback):
                key = key.getName()
            convertedDependencies[key] = []
            for item in items:
                if isinstance(item, str):
                    item = CallbackName(item)
                if isinstance(item, Callback):
                    item = item.getName()
                convertedDependencies[key].append(item)

        for key in convertedDependencies:
            items = convertedDependencies[key]

            if not key in self.callbacks:
                assert False, f"Key {key} is not in callbacks ({list(self.callbacks.keys())})"

            for depKey in items:
                if not depKey in self.callbacks:
                    assert False, f"Key {depKey} of dependency {key} is not in callbacks " \
                        f"({list(self.callbacks.keys())})"

        for key in self.callbacks:
            assert isinstance(key, CallbackName)
            if not key in convertedDependencies:
                convertedDependencies[key] = []

        order = topologicalSort(convertedDependencies)
        callbacksKeys = list(self.callbacks.keys())
        self.topologicalSort = np.array([callbacksKeys.index(x) for x in order])
        self.topologicalKeys = np.array(list(self.callbacks.keys()))[self.topologicalSort]
        logger.debug("Successfully done topological sort!")

    # @brief Gets the device of the first parameter. Useful to align data with model on the same device (i.e GANs).
    #  Warning! Some models may have parameters on multiple devices (i.e. graphs with edges on multiple GPUs at a time)
    # @return The torch device the first paramter is on.
    def getDevice(self) -> tr.device:
        device = next(self.parameters()).device
        return device

    ##### Training / testing functions

    def updateOptimizer(self, trLoss, isTraining:bool, isOptimizing:bool, retain_graph=False):
        if not trLoss is None:
            if isTraining and isOptimizing:
                assert not self.getOptimizer() is None, "Set optimizer when training"
                self.getOptimizer().zero_grad()
                trLoss.backward(retain_graph=retain_graph)
                self.getOptimizer().step()
            else:
                trLoss.detach_()

    def trainReaderNumSteps(self, reader:Iterable, numSteps:int, numEpochs:int, \
        validationReader:Optional[Iterable]=None, validationNumSteps:int=None):
        from .nwtrainer import NWTrainer
        return NWTrainer(self).train(reader, numEpochs, validationReader, numSteps, validationNumSteps)

    # @param[in] reader Reader which is used to get items for numEpochs epochs, each taking len(reader) steps
    # @param[in] numEpochs The number of epochs the network is trained for
    # @param[in] validationReader Validation Reader used to validate the results. If not provided, reader
    #  parameter is used as validation as well for various callbacks (i.e. SaveModels)
    def trainReader(self, reader:Iterable, numEpochs:int, validationReader:Optional[Iterable]=None):
        validationNumSteps = None if validationReader is None else len(validationReader)
        return self.trainReaderNumSteps(reader, len(reader), numEpochs, validationReader, validationNumSteps)

    # @brief Tests the model given a reader
    # @param[in] reader The input iterator
    # @param[in] numSteps Optional params for the number of steps
    # @return The metrics as given by NWTrainer.test
    def testReader(self, reader:Iterable, numSteps:Optional[int]=None):
        from .nwtrainer import NWTrainer
        return NWTrainer(self).test(reader, numSteps)

    def metricsSummary(self) -> str:
        metrics = self.getMetrics().values()
        summaryStr = ""
        for metric in metrics:
            summaryStr += f"\n  - {metric.getName()} ({metric.getDirection()})"
        return summaryStr

    def callbacksSummary(self) -> str:
        callbacksStr = ""
        for callback in self.getCallbacks():
            callbacksStr += f"\n  - {callback.getName()}"
        return callbacksStr

    def hyperParametersSummary(self) -> str:
        hypersStr = ""
        for hyperParameter in self.hyperParameters:
            hypersStr += f"\n  - {hyperParameter}: {self.hyperParameters[hyperParameter]}"
        return hypersStr

    def getNumParams(self):
        return getNumParams(self)

    def summary(self) -> str:
        summaryStr = "[Model summary]"
        summaryStr += f"\n{str(self)}"

        numParams, numTrainable = self.getNumParams()
        summaryStr += f"\nParameters count: {numParams}. Trainable parameters: {numTrainable}."
        summaryStr += f"\nHyperparameters: {self.hyperParametersSummary()}"
        summaryStr += f"\nMetrics: {self.metricsSummary()}"
        summaryStr += f"\nCallbacks: {self.callbacksSummary()}"
        summaryStr += f"\nOptimizer: {self.getOptimizerStr()}"
        summaryStr += f"\nOptimizer Scheduler: {self.optimizerScheduler}"
        summaryStr += f"\nDevice: {self.getDevice()}"

        return summaryStr

    def __str__(self):
        return "General neural network architecture. Update __str__ in your model for more details when using summary."

    ##### Misc functions #####

    # Useful to passing numpy data but still returning backpropagable results
    def npForwardTrResult(self, *args, **kwargs):
        device = self.getDevice()
        trArgs = trToDevice(trGetData(args), device)
        trKwargs = trToDevice(trGetData(kwargs), device)
        trResult = self.forward(*trArgs, **trKwargs)
        return trResult

    # Wrapper for passing numpy arrays, converting them to torch arrays, forward network and convert back to numpy
    # @param[in] x The input, which can be a numpy array, or a list/tuple/dict of numpy arrays
    # @return y The output of the network as numpy array
    def npForward(self, *args, **kwargs):
        with tr.no_grad():
            trResult = self.npForwardTrResult(*args, **kwargs)
        npResult = npGetData(trResult)
        return npResult

    def saveWeights(self, path):
        return self.serializer.saveModel(path, stateKeys=["weights", "model_state"])

    def loadWeights(self, path, yolo=False):
        logger.debug(f"Loading weights from '{path}'")
        if yolo:
            loadedState = NWModuleSerializer.readPkl(path)
            assert "weights" in loadedState
            logger.debug("YOLO mode. No state & named params check.")
            self.serializer.doLoadWeights(loadedState["weights"], allowNamedMismatch=True)
        else:
            self.serializer.loadModel(path, stateKeys=["model_state", "weights"])

    def saveModel(self, path):
        return self.serializer.saveModel(path, stateKeys=["weights", "optimizer", \
            "history_dict", "callbacks", "model_state"])

    def loadModel(self, path):
        self.serializer.loadModel(path, stateKeys=["weights", "optimizer", "history_dict", "callbacks", "model_state"])

    def onModelSave(self):
        return self.hyperParameters

    def onModelLoad(self, state):
        # if len(self.hyperParameters.keys()) != len(state.keys()):
        # 	return False

        allKeys = set(list(self.hyperParameters.keys()) + list(state.keys()))
        for key in allKeys:
            if not key in self.hyperParameters:
                return False

            if not key in state:
                logger.debug("Warning. Model has unknown state key: %s=%s, possibly added after training. Skipping." \
                    % (key, str(self.hyperParameters[key])))
                continue
            loadedState = state[key]
            modelState = self.hyperParameters[key]

            if not deepCheckEqual(loadedState, modelState):
                return False
        return True

    def isTrainable(self):
        for param in self.parameters():
            if param.requires_grad == True:
                return True
        return False

    def reset_parameters(self):
        # Setup print message keys, callbacks & topological sort variables
        self.clearCallbacks()

        # A list that stores various information about the model at each epoch. The index in the list represents the
        #  epoch value. Each value of the list is a dictionary that holds by default only loss value, but callbacks
        #  can add more items to this (like confusion matrix or accuracy, see mnist example).
        self.trainHistory = []

        for layer in self.children():
            if isinstance(layer, Iterable):
                for i in range(len(layer)):
                    if not hasattr(layer[i], "reset_parameters"):
                        logger.debug(f"Sublayer '{layer[i]}' (type: {type(layer)}) has no reset_parameters() method")
                        continue
                    layer[i].reset_parameters()
            else:
                if not hasattr(layer, "reset_parameters"):
                    logger.debug(f"Sublayer '{layer}' (type: {type(layer)}) has no reset_parameters() method")
                    continue
                layer.reset_parameters()

    ### Getters and setters

    # Returns only the callbacks that are of subclass Callback (not metrics)
    def getCallbacks(self):
        res = list(filter(lambda x : not isinstance(x, Metric), self.callbacks.values()))
        return res

    def getMetrics(self):
        metrics = {}
        for k, v in self.callbacks.items():
            if isinstance(v, Metric):
                metrics[k] = v
        return metrics

    def getMetric(self, metricName) -> Metric:
        for key, callback in self.callbacks.items():
            if not isinstance(callback, Metric):
                continue
            if callback.name == metricName:
                return callback
        assert False, f"Metric {metricName} was not found. Use adddMetrics() properly first."

    def getTrainHistory(self):
        return self.trainHistory

    def setTrainableWeights(self, value):
        for param in self.parameters():
            param.requires_grad = value

    # Optimizer can be either a class or an object. If it's a class, it will be instantiated on all the trainable
    #  parameters, and using the arguments in the variable kwargs. If it's an object, we will just use that object,
    #  and assume it's correct (for example if we want only some parameters to be trained this has to be used)
    # Examples of usage: model.setOptimizer(nn.Adam, lr=0.01), model.setOptimizer(nn.Adam(model.parameters(), lr=0.01))
    def setOptimizer(self, optimizer, **kwargs):
        if isinstance(optimizer, optim.Optimizer):
            self.optimizer = optimizer
        else:
            trainableParams = list(filter(lambda p : p.requires_grad, self.parameters()))
            assert len(trainableParams) > 0, "Optimizer must have some trainable parameters."
            self.optimizer = optimizer(trainableParams, **kwargs)
        self.optimizer.storedArgs = kwargs

    def getOptimizer(self):
        return self.optimizer

    def getOptimizerStr(self):
        optimizer = self.getOptimizer()
        return getOptimizerStr(optimizer)

    def setOptimizerScheduler(self, scheduler, **kwargs):
        assert not self.getOptimizer() is None, "Optimizer must be set before scheduler!"
        if isinstance(scheduler, optim.lr_scheduler._LRScheduler):
            self.optimizerScheduler = scheduler
        else:
            self.optimizerScheduler = scheduler(model=self, **kwargs)
            # Some schedulers need acces to the model's object. Others, will not have this argument.
            self.optimizerScheduler.model = self
            self.optimizerScheduler.storedArgs = kwargs

    def setCriterion(self, criterion: CriterionType):
        # If getCriterion fails, then no other criterion was set. However, if it's okay (either via other setCriterion
        #  or via overriding the mothod in another class), then shout a debug log since this may be a logic bug.
        try:
            _ = self.getCriterion()
            logger.debug("Overwriting an existing criterion!")
        except Exception:
            pass
        self.criterion = criterion

    def getCriterion(self) -> CriterionType:
        if not hasattr(self, "criterion"):
            assert False, "Must be implemented"
        assert isinstance(self.criterion, Callable)
        return self.criterion