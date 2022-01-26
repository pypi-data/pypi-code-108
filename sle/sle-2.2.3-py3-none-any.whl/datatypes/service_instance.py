from pyasn1.type import univ, char, namedtype, constraint


class ServiceInstanceAttributeElement(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('identifier', univ.ObjectIdentifier()),
        namedtype.NamedType('siAttributeValue', char.VisibleString().subtype(
            subtypeSpec=constraint.ValueSizeConstraint(1, 256)))
    )


class ServiceInstanceAttribute(univ.SetOf):
    componentType = ServiceInstanceAttributeElement()


class ServiceInstanceIdentifier(univ.SequenceOf):
    componentType = ServiceInstanceAttribute()


def _OID(*components):
    output = []
    for x in tuple(components):
        if isinstance(x, univ.ObjectIdentifier):
            output.extend(list(x))
        else:
            output.append(int(x))

    return univ.ObjectIdentifier(output)


# hertiage version
OperationIdentifier_v1 = {
    "sagr": _OID(1, 2, 0, 9, 5, 2, 52),
    "spack": _OID(1, 2, 0, 9, 5, 2, 53),
    "fsl_fg": _OID(1, 2, 0, 9, 5, 2, 14),
    "rsl_fg": _OID(1, 2, 0, 9, 5, 2, 38),
    "cltu": _OID(1, 2, 0, 9, 5, 2, 7),
    "fsp": _OID(1, 2, 0, 9, 5, 2, 10),
    "raf": _OID(1, 2, 0, 9, 5, 2, 22),
    "rcf": _OID(1, 2, 0, 9, 5, 2, 46),
    "vcf": _OID(1, 2, 0, 9, 5, 2, 46),
    "rcfsh": _OID(1, 2, 0, 9, 5, 2, 44),
    "rocf": _OID(1, 2, 0, 9, 5, 2, 49),
    "rsp": _OID(1, 2, 0, 9, 5, 2, 40),
    "tcf": _OID(1, 2, 0, 9, 5, 2, 12),
    "tcva": _OID(1, 2, 0, 9, 5, 2, 16),
}

OperationIdentifier = {
    "sagr": _OID(1, 3, 112, 4, 3, 1, 2, 52),
    "spack": _OID(1, 3, 112, 4, 3, 1, 2, 53),
    "fsl_fg": _OID(1, 3, 112, 4, 3, 1, 2, 14),
    "rsl_fg": _OID(1, 3, 112, 4, 3, 1, 2, 38),
    "cltu": _OID(1, 3, 112, 4, 3, 1, 2, 7),
    "fsp": _OID(1, 3, 112, 4, 3, 1, 2, 10),
    "raf": _OID(1, 3, 112, 4, 3, 1, 2, 22),
    "rcf": _OID(1, 3, 112, 4, 3, 1, 2, 46),
    "vcf": _OID(1, 3, 112, 4, 3, 1, 2, 46),
    "rcfsh": _OID(1, 3, 112, 4, 3, 1, 2, 44),
    "rocf": _OID(1, 3, 112, 4, 3, 1, 2, 49),
    "rsp": _OID(1, 3, 112, 4, 3, 1, 2, 40),
    "tcf": _OID(1, 3, 112, 4, 3, 1, 2, 12),
    "tcva": _OID(1, 3, 112, 4, 3, 1, 2, 16),
}
