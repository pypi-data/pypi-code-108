class ErrorMessages:
    @staticmethod
    def not_extension(extension):
        raise TypeError("A provided extension does not inherit the base Extension class: {}".format(extension))

    @staticmethod
    def invalid_extension(extension):
        raise ValueError("A provided extension cannot be used to extend this class: {}".format(extension))

    @staticmethod
    def wrap_static(property_name):
        raise ValueError(
            ("Static class methods cannot be wrapped. "
             "The method must receive the object instance as 'self' for its first argument: {}").format(property_name))

    @staticmethod
    def duplicate_attribute(attribute_name):
        raise AttributeError(
            "The provided attribute name already exists on the target instance: {}".format(attribute_name))
