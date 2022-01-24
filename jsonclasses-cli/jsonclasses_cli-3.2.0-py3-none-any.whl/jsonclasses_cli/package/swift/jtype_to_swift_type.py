from typing import Literal
from jsonclasses.fdef import FDef, FType
from ...utils.package_utils import is_field_link


def jtype_to_swift_type(fdef: FDef, mode: Literal['C', 'U', 'R', 'Q'], is_link: bool = False) -> str:
    match fdef.ftype:
        case FType.STR:
            if mode == 'Q':
                return 'StringQuery'
            else:
                return 'String'
        case FType.INT:
            if mode == 'Q':
                return 'IntQuery'
            else:
                return 'Int'
        case FType.FLOAT:
            if mode == 'Q':
                return 'FloatQuery'
            else:
                return 'Float'
        case FType.BOOL:
            if mode == 'Q':
                return 'BoolQuery'
            else:
                return 'Bool'
        case FType.DATE:
            if mode == 'Q':
                return 'DateQuery'
            else:
                return 'Date'
        case FType.DATETIME:
            if mode == 'Q':
                return 'DateQuery'
            else:
                return 'Date'
        case FType.ENUM:
            return fdef.enum_class.__name__
        case FType.LIST:
            return '[' + jtype_to_swift_type(fdef.item_types.fdef, mode, is_field_link(fdef)) + ']'
        case FType.DICT:
            return '[String: ' + jtype_to_swift_type(fdef.item_types.fdef, mode) + ']'
        case FType.INSTANCE:
            if mode == 'R':
                return fdef.inst_cls.__name__
            elif mode == 'C':
                result = fdef.inst_cls.__name__ + 'CreateInput'
                if is_link:
                    return f'CreateOrLink<{result}>'
                return result
            elif mode == 'U':
                result = fdef.inst_cls.__name__ + 'UpdateInput'
                if is_link:
                    return f'UpdateOrLink<{result}>'
                return result
            else:
                return 'never'
        case FType.ANY:
            return 'Never'
        case FType.UNION:
            return "Never"
        case None:
            return "Never"
