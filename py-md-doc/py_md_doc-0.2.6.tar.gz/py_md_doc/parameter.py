import re


class Parameter:
    """
    A parameter in a function.
    """

    def __init__(self, name: str, description: str, def_str: str):
        """
        :param name: The name of the parameter.
        :param description: A description of the parameter.
        :param def_str: The function definition string.
        """

        """:field
        The name of the parameter.
        """
        self.name: str = name

        self.description: str = description

        """:field
        The type of parameter. If there isn't type hinting in `def_str`, this is an empty string.
        """
        self.param_type: str = ""
        # Get the parameter type from the def string.
        param_type = re.search(name + r":(.*?)[:|=|\)]", def_str)
        if param_type is not None:
            param_type = param_type.group(1)
            if "]" in param_type:
                self.param_type = param_type.split("]")[0] + "]"
            else:
                self.param_type = param_type.split(",")[0]
        """:field
        If the parameter is optional, this is its default value. Otherwise, it's an empty string. 
        """
        self.default_value: str = ""
        no_type = def_str.replace(":", "").replace(self.param_type, "")
        default_value = re.search(self.name + r"[ ]{0,1}=(.*?)[,|\)]", no_type)
        if default_value is not None:
            self.default_value = default_value.group(1).strip()
