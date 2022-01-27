from typing import List
from typing import Union


def get_mixtures_from_mixid(mix_in: list, mixid: Union[str, List[int]]) -> list:
    if isinstance(mixid, str):
        try:
            mix_out = eval("mix_in[{}]".format(mixid))
            if not isinstance(mix_out, list):
                mix_out = [mix_out]
            return mix_out
        except NameError:
            return []

    elif isinstance(mixid, list) and all(isinstance(x, int) and x < len(mix_in) for x in mixid):
        return [mix_in[i] for i in mixid]

    return []
