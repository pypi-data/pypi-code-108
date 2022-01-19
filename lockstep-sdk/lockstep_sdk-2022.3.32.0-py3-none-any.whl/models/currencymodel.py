#
# Lockstep Software Development Kit for Python
#
# (c) 2021-2022 Lockstep, Inc.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
# @author     Ted Spence <tspence@lockstep.io>
# @copyright  2021-2022 Lockstep, Inc.
# @version    2022.3
# @link       https://github.com/Lockstep-Network/lockstep-sdk-python
#


from dataclasses import dataclass

"""
Represents an ISO-4217 currency code definition
"""
@dataclass
class CurrencyModel:
    alphaCode: str = None
    numericCode: str = None
    currencyName: str = None
    minorUnit: int = None
    symbol: str = None

