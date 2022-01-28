# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from typing import Callable, Optional, Sequence, Tuple, Union


rgb_color_h = Tuple[float, float, float]
rgba_color_h = Tuple[float, float, float, float]
colormap_h = Callable[
    [Union[float, Sequence[float]]], Union[rgba_color_h, Sequence[rgba_color_h]]
]


def ColorAndAlpha(
    color: Union[str, rgb_color_h, rgba_color_h],
    NameToRGB: Callable[[str], rgb_color_h],
    /,
    *,
    convert_to_rgb: bool = False,
) -> Tuple[Union[str, rgb_color_h], Optional[float]]:
    """"""
    if (is_str := isinstance(color, str)) or (color.__len__() == 3):
        alpha = None
        if is_str and convert_to_rgb:
            color = NameToRGB(color)
    else:
        alpha = color[-1]
        color = color[:-1]

    return color, alpha


def ZeroOneValueToRGBAWithMilestones(
    value: Union[float, Sequence[float]],
    milestones: Sequence[Tuple[float, str]],
    NameToRGB: Callable[[str], rgb_color_h],
    /,
) -> Union[rgba_color_h, Sequence[rgba_color_h]]:
    """"""
    if isinstance(value, Sequence):
        return tuple(
            ZeroOneValueToRGBAWithMilestones(_vle, milestones, NameToRGB)
            for _vle in value
        )

    n_milestones = milestones.__len__()
    m_idx = 0
    while (m_idx < n_milestones) and (value > milestones[m_idx][0]):
        m_idx += 1
    if m_idx >= n_milestones:
        color = milestones[-1][1]
    elif value < milestones[m_idx][0]:
        if m_idx > 0:
            previous = m_idx - 1
        else:
            previous = 0
        interval = (milestones[previous][1], milestones[m_idx][1])
        interval = (NameToRGB(_clr) for _clr in interval)
        ratio = (value - milestones[previous][0]) / (
            milestones[m_idx][0] - milestones[previous][0]
        )
        color = tuple(
            ratio * _end + (1.0 - ratio) * _stt for _stt, _end in zip(*interval)
        )
    else:
        color = milestones[m_idx][1]

    if isinstance(color, str):
        color = NameToRGB(color)
    color = (*color, 1.0)

    return color
