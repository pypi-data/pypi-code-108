#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Union, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class MessageReactions(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyrogram.raw.base.MessageReactions`.

    Details:
        - Layer: ``136``
        - ID: ``0x87b6e36``

    Parameters:
        results: List of :obj:`ReactionCount <pyrogram.raw.base.ReactionCount>`
        min (optional): ``bool``
        can_see_list (optional): ``bool``
        recent_reactons (optional): List of :obj:`MessageUserReaction <pyrogram.raw.base.MessageUserReaction>`
    """

    __slots__: List[str] = ["results", "min", "can_see_list", "recent_reactons"]

    ID = 0x87b6e36
    QUALNAME = "types.MessageReactions"

    def __init__(self, *, results: List["raw.base.ReactionCount"], min: Union[None, bool] = None, can_see_list: Union[None, bool] = None, recent_reactons: Union[None, List["raw.base.MessageUserReaction"]] = None) -> None:
        self.results = results  # Vector<ReactionCount>
        self.min = min  # flags.0?true
        self.can_see_list = can_see_list  # flags.2?true
        self.recent_reactons = recent_reactons  # flags.1?Vector<MessageUserReaction>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageReactions":
        flags = Int.read(b)
        
        min = True if flags & (1 << 0) else False
        can_see_list = True if flags & (1 << 2) else False
        results = TLObject.read(b)
        
        recent_reactons = TLObject.read(b) if flags & (1 << 1) else []
        
        return MessageReactions(results=results, min=min, can_see_list=can_see_list, recent_reactons=recent_reactons)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.min else 0
        flags |= (1 << 2) if self.can_see_list else 0
        flags |= (1 << 1) if self.recent_reactons else 0
        b.write(Int(flags))
        
        b.write(Vector(self.results))
        
        if self.recent_reactons:
            b.write(Vector(self.recent_reactons))
        
        return b.getvalue()
