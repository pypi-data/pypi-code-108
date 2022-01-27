from pathlib import Path
from typing import Any, Dict, List, Optional
import warnings

from starlette.routing import Route

from spell.serving import BasePredictor, settings
from spell.serving.exceptions import InvalidPredictor, InvalidServerConfiguration
from spell.serving.log import get_loggers
from spell.serving.types import PredictorClass
from spell.serving.utils import import_user_predictor

logger, _error_logger = get_loggers("server")


class ModelInfo:
    __slots__ = ["name", "version"]

    def __init__(self, name=None, version=None):
        self.name = name
        self.version = version

    def path(self) -> Path:
        return Path("/model", self.name)

    def __repr__(self):
        return f"ModelInfo(name={self.name}, verison={self.version})"

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version

    # TODO(Justin): Remove the rest of this class in 0.47
    # This is a hacky way to keep (likely-unused) tuple-style accessors when transitioning to a class.

    def __hash__(self):
        warnings.warn("ModelInfo is now a class. Stable hashing will be removed in 0.47", FutureWarning)
        return hash((self.name, self.version))

    def __iter__(self):
        warnings.warn("ModelInfo is now a class. __iter__ will be removed in 0.47", FutureWarning)
        return iter((self.name, self.version))

    def __contains__(self, element):
        warnings.warn("ModelInfo is now a class. __contains__ will be removed in 0.47", FutureWarning)
        return element in (self.name, self.version)

    def __reversed__(self):
        warnings.warn("ModelInfo is now a class. reversed() will be removed in 0.47", FutureWarning)
        return reversed((self.name, self.version))

    def __len__(self):
        warnings.warn("ModelInfo is now a class. len() will be removed in 0.47", FutureWarning)
        return 2

    def __getitem__(self, i):
        warnings.warn("ModelInfo is now a class. Accessing attributes by index will be removed in 0.47", FutureWarning)
        return (self.name, self.version)[i]

    def index(self, element):
        warnings.warn("ModelInfo is now a class. index() will be removed in 0.47", FutureWarning)
        return (self.name, self.version).index(element)

    def count(self, element):
        warnings.warn("ModelInfo is now a class. count() will be removed in 0.47", FutureWarning)
        return (self.name, self.version).count(element)


class API:
    __slots__ = ["predictor_class", "predictor", "predict", "health"]

    def __init__(self, predictor_class: PredictorClass) -> None:
        self.predictor_class = predictor_class
        self.predict = predictor_class.get_predict_endpoint()
        self.health = predictor_class.get_health_endpoint()
        self.predictor = None

    @classmethod
    def from_settings(cls):
        if settings.ENTRYPOINT is None:
            raise RuntimeError("SPELL_ENTRYPOINT environment variable must be provided")
        return cls.from_entrypoint(settings.ENTRYPOINT, classname=settings.CLASSNAME)

    @classmethod
    def from_entrypoint(cls, entrypoint: Path, classname: Optional[str] = None, root: Path = Path(".")):
        import_user_predictor(entrypoint, root=root)
        predictor_class = cls.get_predictor_class(classname)
        return cls(predictor_class)

    @classmethod
    def get_predictor_class(cls, classname: Optional[str]) -> PredictorClass:
        predictors = BasePredictor.all_subclasses()
        if not predictors:
            raise InvalidPredictor("No predictors found. Make sure your predictors extend BasePredictor.")
        if not classname:
            if len(predictors) > 1:
                raise InvalidPredictor("More than one predictor found, but no classname was specified.")
            predictor_name = next(iter(predictors))
            return predictors[predictor_name]
        try:
            return predictors[classname]
        except KeyError:
            raise InvalidPredictor(
                f"No predictor named {classname} was found. The predictors found were ({', '.join(predictors)})"
            )

    def initialize_predictor(self, config: Dict[str, Any]) -> None:
        # We use a two-step initialization process, first create the API with a predictor class,
        # then initialize the prediction. We do this so that we can validate the predictor without
        # loading the entire module
        user_config = config.get("user_config", {})
        logger.debug("Initializing predictor...")
        model_info = config.get("model_info", None)
        if model_info is None:
            self.predictor_class.model_info = model_info
        elif isinstance(model_info, dict):
            self.predictor_class.model_info = ModelInfo(**model_info)
        elif isinstance(model_info, list):
            self.predictor_class.model_info = [ModelInfo(**m) for m in model_info]
        else:
            raise InvalidServerConfiguration('Config yaml "model_info" field must be either a dict or list')
        self.predictor = self.predictor_class(**user_config)
        self._bind()

    def _bind(self) -> None:
        """This is required because we need an uninitialized class to validate in the CLI"""
        self.predict.bind(self.predictor)
        self.health.bind(self.predictor)

    def get_routes(self) -> List[Route]:
        return [
            Route("/health", self.health.call, methods=["GET"]),
            Route("/ready", self.health.call, methods=["GET"]),
            Route("/predict", self.predict.call, methods=["POST"]),
        ]


class BatchedAPI(API):
    __slots__ = ["batched_endpoints", "prepare", "has_prepare"]

    def __init__(self, predictor_class: PredictorClass) -> None:
        super().__init__(predictor_class)
        self.batched_endpoints, self.has_prepare = predictor_class.get_batched_predict_endpoint()
        if self.has_prepare:
            self.prepare = self.batched_endpoints.prepare
        else:
            self.prepare = None
        self.predict = self.batched_endpoints.process

    def _bind(self) -> None:
        """This is required because we need an uninitialized class to validate in the CLI"""
        self.batched_endpoints.bind(self.predictor)
        self.health.bind(self.predictor)

    def get_routes(self) -> List[Route]:
        routes = [
            Route("/health", self.health.call, methods=["GET"]),
            Route("/ready", self.health.call, methods=["GET"]),
            Route("/predict", self.predict, methods=["POST"]),
        ]
        if self.has_prepare:
            routes.append(Route("/prepare", self.prepare, methods=["POST"]))
        return routes
