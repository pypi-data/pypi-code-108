import atexit
from contextlib import suppress
from functools import wraps
from http import HTTPStatus
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from aporia.model import Model
from .api.create_model_version import run_create_model_version_query
from .config import Config
from .context import get_context, init_context, reset_context
from .errors import AporiaError, AporiaHTTPError, handle_error
from .event_loop import EventLoop
from .http_client import HttpClient
from .logging_utils import init_logger, LOGGER_NAME, set_log_level
from .types.model import ModelColor, ModelIcon

logger = logging.getLogger(LOGGER_NAME)


def safe_api_function(error_message_format: str) -> Callable:
    """Decorator that wraps a function with error handling based on global configuration.

    Args:
        error_message_format: Error message format string - will be passed to handle_error()

    Returns:
        Wrapped function
    """

    def decorator_safe_api_function(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            context = get_context()
            try:
                return func(*args, **kwargs)
            except Exception as err:
                handle_error(
                    message_format=error_message_format,
                    verbose=context.config.verbose,
                    throw_errors=context.config.throw_errors,
                    debug=context.config.debug,
                    original_exception=err,
                )

            return None

        return wrapper

    return decorator_safe_api_function


def init(
    token: Optional[str] = None,
    host: Optional[str] = None,
    environment: Optional[str] = None,
    port: Optional[int] = None,
    verbose: Optional[bool] = None,
    throw_errors: Optional[bool] = None,
    debug: Optional[bool] = None,
    http_timeout_seconds: Optional[int] = None,
):
    """Initialize the Aporia SDK.

    Args:
        token: Authentication token.
        host: Controller host.
        environment: Environment in which aporia is initialized (e.g production, staging).
        port: Controller port. Defaults to 443.
        verbose: True to enable verbose error messages. Defaults to False.
        throw_errors: True to cause errors to be raised as exceptions. Defaults to False.
        debug: True to enable debug logs and stack traces in log messages. Defaults to False.
        http_timeout_seconds: HTTP timeout in seconds. Defaults to 30.

    Notes:
        * The token, host and environment parameters are required.
        * All of the parameters here can also be defined as environment variables:
            * token -> APORIA_TOKEN
            * host -> APORIA_HOST
            * environment -> APORIA_ENVIRONMENT
            * port -> APORIA_PORT
            * verbose -> APORIA_VERBOSE
            * throw_errors -> APORIA_THROW_ERRORS
            * debug -> APORIA_DEBUG
            * http_timeout_seconds -> APORIA_HTTP_TIMEOUT_SECONDS
        * Values passed as parameters to aporia.init() override the values from
          the corresponding environment variables.
    """
    init_logger()

    logger.debug("Initializing Aporia SDK.")

    try:
        config = Config(
            token=token,
            host=host,
            environment=environment,
            port=port,
            verbose=verbose,
            throw_errors=throw_errors,
            debug=debug,
            http_timeout_seconds=http_timeout_seconds,
        )

        set_log_level(config.debug)

        event_loop = EventLoop()
        http_client = HttpClient(
            token=config.token,
            host=config.host,
            port=config.port,
            default_timeout=config.http_timeout_seconds,
        )

        init_context(http_client=http_client, event_loop=event_loop, config=config)

        atexit.register(shutdown)
        logger.debug("Aporia SDK initialized.")
    except Exception as err:
        handle_error(
            message_format="Initializing Aporia SDK failed, error: {}",
            verbose=False if verbose is None else verbose,
            throw_errors=False if throw_errors is None else throw_errors,
            debug=False if debug is None else debug,
            original_exception=err,
        )


def shutdown():
    """Shuts down the Aporia SDK.

    Notes:
        * It is advised to call flush() before calling shutdown(), to ensure that
          all of the data that was sent reaches the controller.
    """
    logger.debug("Shutting down Aporia SDK.")
    with suppress(Exception):
        reset_context()


@safe_api_function("Creating model failed, error: {}")
def create_model(
    model_id: str,
    name: str,
    description: Optional[str] = None,
    owner: Optional[str] = None,
    color: Optional[Union[ModelColor, str]] = None,
    icon: Optional[Union[ModelIcon, str]] = None,
    tags: Dict[str, str] = None,
) -> str:
    """Creates a new model.

    Args:
        model_id: A unique identifier for the new model, which will be used in all future operations
        name: A name for the new model, which will be displayed in Aporia's dashboard
        description: A description of the model
        owner: The email of the model owner
        color: A color to distinguish the model in Aporia's dashboard. Defaults to blue
        icon: An icon that indicates the model's designation. Defaults to general
        tags: A mapping of tag keys to tag values

    Returns:
        Model ID.

    Notes:
        * If this model_id already exists, NO EXCEPTION WILL BE RAISED!
          Instead, the same model ID will be returned.
    """
    context = get_context()

    try:
        response = context.event_loop.run_coroutine(
            context.http_client.post(
                url="/models",
                data={
                    "id": model_id,
                    "name": name,
                    "description": description,
                    "owner": owner,
                    "color": ModelColor(color).value if color is not None else ModelColor.BLUE,
                    "icon": ModelIcon(icon).value if icon is not None else ModelIcon.GENERAL,
                    "tags": tags,
                },
            )
        )

        return response["id"]
    except AporiaHTTPError as err:
        if err.http_status == HTTPStatus.CONFLICT:
            # This model ID already exists. We don't raise an exeption in this case.
            return model_id

        raise


@safe_api_function("Deleting model failed, error: {}")
def delete_model(model_id: str):
    """Deletes a model.

    Args:
        model_id: ID of the model to delete
    """
    context = get_context()
    context.event_loop.run_coroutine(context.http_client.delete(url=f"/models/{model_id}"))


@safe_api_function("Creating model version failed, error: {}")
def create_model_version(
    model_id: str,
    model_version: str,
    model_type: str,
    features: Dict[str, str],
    predictions: Dict[str, str],
    raw_inputs: Optional[Dict[str, str]] = None,
    metrics: Optional[Dict[str, str]] = None,
    model_data_type: Optional[str] = None,
    multiclass_labels: Optional[List[str]] = None,
    feature_importance: Optional[Dict[str, float]] = None,
) -> Optional[Model]:
    """Creates a new model version, and defines a schema for it.

    Args:
        model_id: Model identifier, as received from the Aporia dashboard.
        model_version: Model version - this can be any string that represents the model
            version, such as "v1" or a git commit hash.
        model_type: Model type (also known as objective - see notes).
        features: Schema for model features (See notes)
        predictions: Schema for prediction results (See notes)
        raw_inputs: Schema for raw inputs (See notes).
        metrics: Schema for prediction metrics (See notes).
        model_data_type: Model data type.
        multiclass_labels: Labels of multiclass or binary model
        feature_importance: Features' importance.

    Notes:
        * A schema is a dict, in which the keys are the fields you wish to report, and the
          values are the types of those fields. For example:
          ```python
            {
                "feature1": "numeric",
                "feature2": "datetime"
            }
          ```
        * The supported model types are:
            * "regression" - for regression models
            * "binary" - for binary classification models
            * "multiclass" - for multiclass classification models
        * The valid field types (and corresponding python types) are:

            | Field Type    | Python Types
            | ------------- | ------------
            | "numeric"     | float, int
            | "categorical" | int
            | "boolean"     | bool
            | "string"      | str
            | "datetime"    | datetime.datetime, or str representing a datetime in ISO-8601 format
            | "vector"      | list of floats
            | "text"        | str (to be used as free text)
        * The supported data types are:
            * "tabular"
            * "nlp"
        * The feature_importance is a mapping from feature name to it's importance (float).
          For example:
          ```python
             {
                "feature1": 1,
                "feature2": 2
             }
          ```

    Returns:
        Model object for the new version.
    """
    context = get_context()

    if len(model_id) == 0 or len(model_version) == 0:
        raise AporiaError("model_id and model_version must be non-empty strings.")

    context.event_loop.run_coroutine(
        run_create_model_version_query(
            http_client=context.http_client,
            model_id=model_id,
            model_version=model_version,
            model_type=model_type,
            model_data_type=model_data_type,
            features=features,
            predictions=predictions,
            raw_inputs=raw_inputs,
            metrics=metrics,
            multiclass_labels=multiclass_labels,
            feature_importance=feature_importance
        )
    )

    return Model(model_id=model_id, model_version=model_version)
