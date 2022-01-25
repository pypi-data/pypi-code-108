from typing import Any

import dict_tools.data as dict_data


class ExecReturn(dict_data.NamespaceDict):
    def __init__(
        self, result: bool, ret: Any, comment: Any = None, ref: str = "", **kwargs
    ):
        """
        Exec Returns must have the keys of "result", "ret", and "comment".
        Any other values can be added to the namespace
        """
        if not isinstance(result, bool):
            raise ValueError("Got a non boolean value for exec return `result`")
        if not isinstance(ref, str):
            raise ValueError("Got a non string value for exec return `ref`")

        super().__init__(result=result, ret=ret, comment=comment, ref=ref, **kwargs)

    def __bool__(self):
        return self.result
