from Configurables import DaVinci

from cbtesting.helpers import stripping

stripping_lines = [
                'StrippingBu2LLK_meLine',
                'StrippingBu2LLK_meSSLine',
                'StrippingBu2LLK_eeLine',
                'StrippingBu2LLK_eeLine2',
                'StrippingBu2LLK_eeLine3',
                'StrippingBu2LLK_eeLine4',
                'StrippingBu2LLK_mmLine',
                'StrippingBu2LLK_mmSSLine',
                'StrippingBu2LLK_eeSSLine2',
                ]
data_type = DaVinci().DataType

seq = stripping.stripping(data_type, stripping_lines)
DaVinci().UserAlgorithms = [seq]
