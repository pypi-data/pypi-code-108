import importlib

api_prefix = 'deepomatic.oef.'
api_proto_prefix = api_prefix + 'protos.'
proto_suffix = '_pb2'


# -----------------------------------------------------------------------------#

def convert_module_path(path):
    """
    Takes a normalized module `path` and convert it to a specialized path of type `to_type`
    Args:
        path (string): a module path

    Returns:
        string: The specialized module path.
    """
    return api_proto_prefix + path + proto_suffix


# -----------------------------------------------------------------------------#

def load_class(module, classes):
    """Load class from module path and a list of nested classes"""
    class_container = importlib.import_module(module)
    for c in classes:
        class_container = getattr(class_container, c)
    return class_container


# -----------------------------------------------------------------------------#

def load_proto_class_from_protobuf_descriptor(descriptor):
    """
    Given a protobuf message descriptor, return its associated class: either the protobuf or the serializer
    """
    # We first extract the class name: careful as it may be nested messages.
    # For exemple: descriptor.full_name is `deepomatic.oef.models.image.backbones.EfficientNetBackbone.Version`
    # descriptor.file.package is `deepomatic.oef.models.image.backbones`
    # So field_type is `EfficientNetBackbone.Version`
    namespace_prefix = descriptor.file.package + '.'
    assert descriptor.full_name.startswith(namespace_prefix), "Field type should normally start with '{}'".format(namespace_prefix)
    classes = descriptor.full_name.replace(descriptor.file.package + '.', '')

    # Find the module name
    module_path = descriptor.file.name
    assert module_path.endswith('.proto'), "File type should normally end with '.proto'"
    module_path = module_path.replace('.proto', '').replace('/', '.')  # order matters for the replace
    assert module_path.startswith(api_proto_prefix), "Package should normally start with '{}'".format(api_proto_prefix)
    module_path = module_path.replace(api_proto_prefix, '')

    module_path = convert_module_path(module_path)
    return load_class(module_path, classes.split('.'))

# -----------------------------------------------------------------------------#
