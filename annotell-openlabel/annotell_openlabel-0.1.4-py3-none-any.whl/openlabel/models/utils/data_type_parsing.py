from typing import Any, Tuple

import annotell.openlabel.models as OLM


def get_openlabel_type(name: str, val: Any) -> Tuple[str, OLM.DataTypeBase]:

    def isfloat(num: str) -> bool:
        try:
            float(num)
            return True
        except:  # noqa:E722
            return False

    if isinstance(val, bool):
        return "boolean", OLM.Boolean(name=name, val=val)
    elif isinstance(val, list):
        return "vec", OLM.Vec(name=name, val=val)
    elif isinstance(val, str):
        return "text", OLM.Text(name=name, val=val)
    elif isinstance(val, int):
        return "num", OLM.Num(name=name, val=val)
    elif isfloat(val):
        return "num", OLM.Num(name=name, val=float(val))

    raise NotImplementedError
