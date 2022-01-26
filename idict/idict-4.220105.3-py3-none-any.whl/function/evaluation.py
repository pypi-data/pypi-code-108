#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
from sklearn.model_selection import train_test_split


# TODO (minor): enforce versions by runtime checking (sklearn etc)


def split(
    input=["X", "y"],
    output=["Xtr", "Xts", "ytr", "yts"],
    config={"test_size": 0.33, "shuffle": True, "stratify": "y", "random_state": 0},
    **kwargs,
):
    r"""
    >>> from idict import idict, let
    >>> d = idict.fromtoy() >> split
    >>> d.show(colored=False)
    {
        "Xtr": "→(input output config X y)",
        "Xts": "→(input output config X y)",
        "ytr": "→(input output config X y)",
        "yts": "→(input output config X y)",
        "_history": "idict--------------sklearn-1.0.1---split",
        "X": "«{'attr1': {0: 5.1, 1: 1.1, 2: 6.1, 3: 1.1, 4: 3.1, 5: 4.7, 6: 9.1, 7: 8.3, 8: 9.1, 9: 2.5, 10: 7.1, 11: 0.1, 12: 2.1, 13: 0.1, 14: 5.1, 15: 31.1, 16: 1.1, 17: 2.2, 18: 3.1, 19: 1.1}, 'attr2': {0: 6.4, 1: 2.5, 2: 3.6, 3: 3.5, 4: 2.5, 5: 4.9, 6: 3.5, 7: 2.9, 8: 7.2, 9: 4.5, 10: 6.6, 11: 4.3, 12: 0.1, 13: 4.0, 14: 4.5, 15: 4.7, 16: 3.2, 17: 8.5, 18: 2.5, 19: 8.5}}»",
        "y": "«[0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1]»",
        "_id": "8eGk98oY-ZJCTDqlI6cQpv.ScL12.0.1---split",
        "_ids": {
            "Xtr": "sgAswz-TNQOyqNXEOZlDdPMGJzavRgf.FjBFx6Ju",
            "Xts": "fb8kj0bb0D8DvZUHPGTTPC8buLIAQJv-25ZHJT65",
            "ytr": "o.tZeOrqlsvd7-ms6Z6utR3HQEYTPTaN-srQovsp",
            "yts": "tt1iyOwF1N9Tp.sODMi2quhOW.3lgptmlmIDeVur",
            "_history": "ZqK23fzMQapVz7mHUEsdIioxfe8T8UDYYiQGy-y4",
            "X": "md_cb8b0c76becc1de32236764e91e8e457e826f (content: 34_1738c83af436029507def2710bc5125f58d0e)",
            "y": "Kp_697ef70c1a293f50ed352ea5775bba6d9b1f4 (content: S0_b6360d62ccafa275d4051dfd02b939104feac)"
        }
    }
    >>> d.yts
    array([1, 0, 1, 0, 0, 0, 1])
    """
    # Multidynamic input is only detected when the kwargs index is also indexed by something.
    multidynamic_input = {}
    for i, _ in enumerate(input):
        multidynamic_input[input[i]] = kwargs[input[i]]

    if "stratify" in config and isinstance(config["stratify"], str):
        if config["stratify"] not in input:  # pragma: no cover
            raise Exception(f"Missing field {config['stratify']} for stratification.")
        config["stratify"] = multidynamic_input[config["stratify"]]
    result = train_test_split(*multidynamic_input.values(), **config)
    out = {k: v for k, v in zip(output, result)}
    # Multidynamic output cannot be detected, so it can only be defined as metadata.
    return out


split.metadata = {
    "id": "idict--------------sklearn-1.0.1---split",
    "name": "split",
    "description": "Split data in two sets.",
    "parameters": ...,
    "code": ...,
    "output": {"fields": [], "auto": ["_history"], "meta": [], "dynamic": ["output"]},
}
