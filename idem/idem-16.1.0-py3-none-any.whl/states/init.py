from typing import Callable, Any, Dict

import dict_tools.differ as differ

async def run(
    hub,
    state_name:str,
    state_describe_func: Callable,
    state_describe_kwargs: Dict[str, Any],
    state_func: Callable,
    state_func_kwargs: Dict[str, Any],
    fail_on_error_before:bool = None,
    fail_on_error_after:bool = None,
    succeed_on_error_before:bool = None,
    succeed_on_error_after:bool = None,
    succeed_on_describe_before:bool=False,
    fail_on_describe_after:bool=False,
):
    assert not (fail_on_error_before is not None and succeed_on_error_before is not None), "Mutually exclusive args"
    assert not (fail_on_error_after is not None and succeed_on_error_after is not None), "Mutually exclusive args"
    try:
        before = state_describe_func(**state_describe_kwargs)
        before = await hub.pop.loop.unwrap(before)
        if before:
            raise ChildProcessError(f"Resource exists")
        if succeed_on_describe_before and before:
            return {
                "comment": f"{state_name} already complete",
                "changes": {},
                "name": state_name,
                "result": True,
            }
    except Exception as e:
        if fail_on_error_before:
            return {
                "comment": f"{e.__class__.__name__}: {e}",
                "changes": {},
                "name": state_name,
                "result": False,
            }
        elif succeed_on_error_before:
            return {
                "comment": f"{state_name} already complete: {e.__class__.__name__}: {e}",
                "changes": {},
                "name": state_name,
                "result": True,
            }
        else:
            before = {}
            comment = f"{e.__class__.__name__} while describing resource {state_describe_func} before {state_func}: {e}"

    assert isinstance(before, dict), f"Return from describe function '{state_describe_func}' is not a dict"

    try:
        ret = state_func(**state_func_kwargs)
        ret = await hub.pop.loop.unwrap(ret)
    except Exception as e:
        return {
            "comment": f"{e.__class__.__name__}: {e}",
            "changes": {},
            "name": state_name,
            "result": False,
        }

    try:
        after = state_describe_func(**state_describe_kwargs)
        after = await hub.pop.loop.unwrap(after)
        if not after:
            raise ChildProcessError(f"Resource does not exist")
        if fail_on_describe_after and after:
            return {
                "comment": comment,
                "changes": differ.deep_diff(before, after),
                "name": state_name,
                "result": False,
            }
    except Exception as e:
        if fail_on_error_after:
            return {
                "comment": f"{e.__class__.__name__}: {e}",
                "changes": {},
                "name": state_name,
                "result": False,
            }
        elif succeed_on_error_after:
            return {
                "comment": f"{state_name} completed: {e.__class__.__name__}: {e}",
                "changes": differ.deep_diff(before, {}),
                "name": state_name,
                "result": True,
            }
        else:
            after = {}
            comment = f"{e.__class__.__name__} while describing resource {state_describe_func} after {state_func}: {e}"

    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": state_name,
        "result": True,
    }
