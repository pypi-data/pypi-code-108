from jsonclasses.cdef import CDef
from jsonclasses_cli.utils.package_utils import to_session_input
from .codable_struct import codable_struct, codable_struct_item
from .jtype_to_swift_type import jtype_to_swift_type


def session_input(cdef: CDef) -> str:
    name = to_session_input(cdef)
    struct_items: list[str] = []
    (identities, bys) = _session_input_items(cdef)
    identities_optional = len(identities) != 1
    bys_optional = len(bys) != 1
    for (n, t) in identities.items():
        struct_item = codable_struct_item('public', 'let', n, t, identities_optional)
        struct_items.append(struct_item)
    for (n, t) in bys.items():
        struct_item = codable_struct_item('public', 'let', n, t, bys_optional)
        struct_items.append(struct_item)
    return codable_struct(name, struct_items)


def _session_input_items(cdef: CDef) -> tuple[dict[str, str], dict[str, str]]:
    identities: dict[str, str] = {}
    bys: dict[str, str] = {}
    for field in cdef.fields:
        fname = field.json_name
        ftype = jtype_to_swift_type(field.fdef, 'C')
        if field.fdef.auth_identity:
            identities[fname] = ftype
        elif field.fdef.auth_by:
            bys[field.json_name] = ftype
    return (identities, bys)