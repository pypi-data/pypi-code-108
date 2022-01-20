import asyncio
import inspect
import json
import pickle
from types import MethodType
from typing import Any, Callable, Dict, List, Optional, Union, get_origin

from starlette.background import BackgroundTasks
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from spell.serving.exceptions import InvalidPredictor
from spell.serving.responses import create_pickle_response, wrap_response
from spell.serving.types import (
    APIResponse,
    PredictorMethod,
    PrepareResponse,
)


class Endpoint:
    """This class wraps a function intended to respond to Requests and translates the request into
    arguments and the return into a Response

    The attributes are the name of the parameter which should accept the content, request, or tasks
    """

    __slots__ = ["func", "content", "tasks", "request", "is_instancemethod", "_is_async"]

    def __init__(
        self,
        func: Callable,
        content: Optional[str] = None,
        tasks: Optional[str] = None,
        request: Optional[str] = None,
        is_instancemethod: bool = True,
    ) -> None:
        # content is a special attribute which, unlike the other two cannot be set by decorators
        self.func = func
        self.content = content
        self.tasks = tasks
        self.request = request
        self.is_instancemethod = is_instancemethod
        self._is_async = asyncio.iscoroutinefunction(func)

    def bind(self, instance: Any) -> None:
        """This binds the function held in the Endpoint to a class instance."""
        if self.is_instancemethod:
            self.func = MethodType(self.func, instance)

    # For some reason, __call__ doesn't work because Starlette thinks this class is now an
    # Application, and it passes in the entire ASGI scope and 3 other variables
    async def call(self, request: Request, convert_to_response: bool = True) -> Union[Response, APIResponse]:
        content, tasks = await self.extract_json(request)
        ret, tasks = await self.execute(content, request=request, tasks=tasks)
        if convert_to_response:
            return await wrap_response(ret, tasks=tasks)
        else:
            return ret, tasks

    async def extract_json(self, request: Request) -> PrepareResponse:
        if self.content:
            try:
                json_content = await request.json()
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Request must contain a JSON object")
        else:
            json_content = None
        tasks = BackgroundTasks() if self.tasks else None
        return json_content, tasks

    async def execute(
        self,
        content: Any,
        request: Optional[Request] = None,
        tasks: Optional[BackgroundTasks] = None,
    ) -> APIResponse:
        if tasks is None and self.tasks:
            tasks = BackgroundTasks()
        kwargs = self.make_arg_dict(content, request, tasks)
        if self._is_async:
            return await self.func(**kwargs), tasks
        return self.func(**kwargs), tasks

    def make_arg_dict(self, payload: Any, request: Request, tasks: Optional[BackgroundTasks]) -> Dict[str, Any]:
        kwargs = {}
        if self.content:
            kwargs[self.content] = payload
        if self.request:
            kwargs[self.request] = request
        if self.tasks:
            kwargs[self.tasks] = tasks
        return kwargs

    @classmethod
    def from_func(cls, func: PredictorMethod, min_args: int, is_staticmethod: bool, is_classmethod: bool):
        """This constructor takes a function and intropects its function signature to construct an endpoint.

        In the process it ensures that the function conforms to the API specified for an argument
        """
        func_name = func.__name__

        func_args = inspect.getfullargspec(func).args
        annotations = cls._get_annotations(func, func_name)
        self_param = cls._get_self_param_name(func_name, func_args, annotations, min_args, is_staticmethod)
        # Check happens afer self param has been removed from func_args
        if len(func_args) < min_args:
            raise InvalidPredictor(f"{func_name} function must have at least {min_args} arguments")

        # Get all the args which do not have annotations
        # The set operation also ignores the return annotation
        unaccounted_args = set(func_args) - set(annotations)

        # Find all the params which are indicated using decorators
        params = getattr(func, "__injected_params__", cls(func))
        # Ensure that just using params from decorators are valid
        params.validate(self_param)

        # Merge the parameters from decorators with the parameters from endpoints

        # For all the params indicated in the decorators, ensure that it's in the set of
        # non-annotated params and remove it from that set because it has been accounted for
        for param in (params.tasks, params.request):
            if param is not None and param not in annotations:
                if param in unaccounted_args:
                    unaccounted_args.remove(param)
                else:
                    raise InvalidPredictor(
                        f"A decorator is expecting an argument named {param}, but it was not "
                        f"found in the signature for {func_name}"
                    )
        for param, type_ in annotations.items():
            if issubclass(type_, BackgroundTasks):
                if params.tasks and params.tasks != param:
                    raise InvalidPredictor(
                        f"Found both annotation and decorator for background tasks in signature for {func_name}"
                    )
                params.tasks = param
            elif issubclass(type_, Request):
                if params.request and params.request != param:
                    raise InvalidPredictor(
                        f"Found both annotation and decorator for full request in signature for {func_name}"
                    )
                params.request = param
            # Handle JSON content annotations using dict or list
            elif issubclass(get_origin(type_) or type_, (dict, list)):
                params.content = param

        # Any args remaining in unaccounted args should be the min params, like
        # (self, payload) for predict
        if len(unaccounted_args) > min_args:
            raise InvalidPredictor(
                f"Found ({unaccounted_args}) extra arguments in {func_name} function. "
                f"{func_name} expects at least {min_args} arguments. All additional "
                "arguments must have a type annotation or use decorators to indicate their "
                "use."
            )
        elif len(unaccounted_args) == min_args and min_args == 1:
            params.content = unaccounted_args.pop()
        params.is_instancemethod = not (is_staticmethod or is_classmethod)
        return params

    @staticmethod
    def _get_annotations(func: PredictorMethod, func_name: str) -> Dict[str, Any]:
        annotations = func.__annotations__
        if len(set(annotations.values())) != len(annotations):
            raise InvalidPredictor(f"All annotations in {func_name} must be unique")
        annotations.pop("return", None)
        return annotations

    @staticmethod
    def _get_self_param_name(
        func_name: str,
        func_args: List[str],
        annotations: Dict[str, Any],
        min_args: int,
        is_staticmethod: bool,
    ) -> Optional[str]:
        """Gets the self/cls param name and removes it from the
        funcion arguments list and the annotations dict"""
        # If the function is not a staticmethod, then we need to ignore the first parameter
        self_param = None
        if not is_staticmethod:
            if func_args:
                self_param = func_args.pop(0)
            elif min_args == 0:
                # example: health() rather than health(self)
                raise InvalidPredictor(
                    f"Expected a self or cls argument in {func_name} but found none. Add a self "
                    "or cls argument or mark as a staticmethod"
                )
            if self_param in annotations:
                annotations.pop(self_param)
        return self_param

    def validate(self, self_param: str) -> None:
        # Check that the param names don't refer to the same param
        if self.tasks is not None and self.tasks == self.request:
            raise InvalidPredictor(
                "Both request and background tasks are using the same parameter name " f"{self.request}"
            )

        # Check that the params do not refer to the self/cls param we are ignoring
        if self_param:
            if self.tasks == self_param:
                raise InvalidPredictor(f"Background tasks parameter cannot refer to {self_param}")
            if self.request == self_param:
                raise InvalidPredictor(f"Full request parameter cannot refer to {self_param}")


class BatchEndpoint:
    __slots__ = ["process_endpoint"]

    def __init__(self, process_endpoint: Endpoint) -> None:
        self.process_endpoint = process_endpoint

    def bind(self, instance: Any) -> None:
        self.process_endpoint.bind(instance)

    async def process(self, request: Request) -> Response:
        try:
            content = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request must contain a JSON object")
        response, tasks = await self.process_endpoint.execute(content)
        return await create_pickle_response(response, tasks)


class PreparedBatchEndpoint(BatchEndpoint):
    __slots__ = ["prepare_endpoint"]

    def __init__(self, prepare_endpoint: Endpoint, process_endpoint: Endpoint) -> None:
        super().__init__(process_endpoint)
        self.prepare_endpoint = prepare_endpoint

    def bind(self, instance: Any) -> None:
        self.prepare_endpoint.bind(instance)
        super().bind(instance)

    async def prepare(self, request: Request) -> Response:
        content, tasks = await self.prepare_endpoint.call(request, convert_to_response=False)
        # Indicating the user raised a status error. In this case, we want to pass it along directly
        if isinstance(content, Response) and 400 <= content.status_code <= 599:
            return content
        return await create_pickle_response(content, tasks)

    async def process(self, request: Request) -> Response:
        try:
            content = pickle.loads(await request.body())
        except pickle.PickleError as e:
            return PlainTextResponse(f"Body could not be unpickled. {e}", status_code=400)
        response, tasks = await self.process_endpoint.execute(content)
        return await create_pickle_response(response, tasks)
