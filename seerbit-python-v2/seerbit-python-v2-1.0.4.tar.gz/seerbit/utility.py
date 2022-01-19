"""
  Copyright (C) 2022 SeerBit
 
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
 
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 """
from seerbit.client import Client
from seerbit.exception import SeerBitError


class Utility:

    @staticmethod
    def non_null(client: Client):
        if not client:
            raise SeerBitError("Client cannot be null")

    @staticmethod
    def require_non_null(api_base, error_message):
        if not api_base:
            raise SeerBitError(error_message)
