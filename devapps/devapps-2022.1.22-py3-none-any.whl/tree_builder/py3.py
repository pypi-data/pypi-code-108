def cls_with_meta(mc, attrs):
    class _tree_builder_intermediate_(metaclass=mc):
        pass

    for k, v in attrs.items():
        setattr(_tree_builder_intermediate_, k, v)
    return _tree_builder_intermediate_
