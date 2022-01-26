from typing import Any, Awaitable, Callable


def apply_func_on_object_recursively(obj: Any, f: Callable, apply_on_key_dict: bool = False) -> Any:
    """Recursively apply a callable to a JSON-like tree of objects (i.e. a combination of dictionaries and lists)"""
    if isinstance(obj, list):
        return [apply_func_on_object_recursively(value, f, apply_on_key_dict) for value in obj]
    if isinstance(obj, tuple):  # pylint: disable=no-else-return
        return tuple(  # pylint: disable=consider-using-generator
            [apply_func_on_object_recursively(value, f, apply_on_key_dict) for value in obj]
        )
    elif isinstance(obj, dict):
        return {
            apply_func_on_object_recursively(key, f, apply_on_key_dict)
            if apply_on_key_dict
            else key: apply_func_on_object_recursively(value, f, apply_on_key_dict)
            for key, value in obj.items()
        }
    else:
        return f(obj)


async def apply_async_func_on_object_recursively(
    obj: Any, f: Callable[..., Awaitable[Any]], **kwargs
) -> Any:
    if isinstance(obj, list):
        return [await apply_async_func_on_object_recursively(value, f, **kwargs) for value in obj]

    if isinstance(obj, tuple):
        return tuple(  # pylint: disable=consider-using-generator
            [await apply_async_func_on_object_recursively(value, f, **kwargs) for value in obj]
        )

    if isinstance(obj, dict):
        keys = obj.keys()
        values = [
            await apply_async_func_on_object_recursively(v, f, **kwargs) for v in obj.values()
        ]
        return {key: values[num] for num, key in enumerate(keys)}

    return await f(obj, **kwargs)
