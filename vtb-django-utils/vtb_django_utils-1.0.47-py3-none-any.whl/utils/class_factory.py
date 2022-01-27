def class_factory(module_name, cls_name: str, parents: tuple, members: dict = None):

    members_dict = members or {}

    cls_attrs = dict(
        __slots__=members_dict.keys(),
        __module__=module_name,
        **members_dict,
    )

    return type(cls_name, parents, cls_attrs)
