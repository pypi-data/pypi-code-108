from typing import Any, Dict, NamedTuple, Optional, Tuple

import jsonpickle

from jetpack.proto.runtime.v1alpha1 import remote_pb2


def encode_result(result: Any) -> remote_pb2.RemoteCallResponse:
    response = remote_pb2.RemoteCallResponse()
    response.json_results = jsonpickle.encode(result)
    return response


def decode_result(response: remote_pb2.RemoteCallResponse) -> Any:
    return jsonpickle.decode(response.json_results)


# FuncArgs is used by jsonpickle to capture the arguments to an RPC
# TODO: Consider using inspect.BoundArguments instead of defining our own type.
FuncArgs = NamedTuple(
    "FuncArgs",
    [("args", Optional[Tuple[Any, ...]]), ("kwargs", Optional[Dict[str, Any]])],
)


def encode_args(
    args: Optional[Tuple[Any, ...]], kwargs: Optional[Dict[str, Any]]
) -> str:
    result: str = jsonpickle.encode(FuncArgs(args=args, kwargs=kwargs))
    return result


def decode_args(
    encoded_args: str,
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
    func_args: FuncArgs = jsonpickle.decode(encoded_args)
    return func_args.args or (), func_args.kwargs or {}
