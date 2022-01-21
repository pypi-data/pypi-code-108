from typing import Union


class DesignVariable:
    """ A DesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 variable_type: str) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param variable_type: numerical type of a variable: either int or float
        """
        self.variable_type = variable_type
        conversion_method = int if variable_type == 'int' else float
        self.xl = conversion_method(xl)
        self.xu = conversion_method(xu)
        self.variable = variable

    def get_compact_variable_name(self) -> str:
        return self.variable

    def get_hover_text(self, value) -> str:
        if self.variable_type == 'float':
            return 'value: %.3f, range: [%.3f, %.3f]' % (value, self.xl, self.xu)
        else:
            return 'value: %d, range: [%d, %d]' % (value, self.xl, self.xu)

    def get_fraction(self, value) -> float:
        if self.xu == self.xl:
            return float('nan')
        else:
            return (value - self.xl) / (self.xu - self.xl)


class LayerDesignVariable(DesignVariable):
    """ A LayerDesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 variable_type: str,
                 layer: int) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param variable_type: numerical type of a variable: either int or float
        :param layer: layer index; this brakes the compatibility with ROXIE
        """
        super().__init__(xl, xu, variable, variable_type)
        self.layer = int(layer)

    def get_compact_variable_name(self) -> str:
        return "%s:%s" % (self.variable, int(self.layer))


class BlockDesignVariable(LayerDesignVariable):
    """ A DesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 variable_type: str,
                 layer: int,
                 bcs: Union[int, str]) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param variable_type: numerical type of a variable: either int or float
        :param layer: layer index; this brakes the compatibility with ROXIE
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        """
        super().__init__(xl, xu, variable, variable_type, layer)
        self.block = int(bcs)

    def get_compact_variable_name(self) -> str:
        return '%s:%s:%s' % (self.variable, self.layer, self.block)


class MultiBlockDesignVariable(LayerDesignVariable):
    """ A DesignVariable class for optimization purposes
    """

    def __init__(self,
                 xl: Union[int, float],
                 xu: Union[int, float],
                 variable: str,
                 variable_type: str,
                 layer: int,
                 bcs: str) -> None:
        """ A DesignVariable constructor

        :param xl: lower limit of a design variable
        :param xu: upper limit of a design variable
        :param variable: name of a design variable
        :param variable_type: numerical type of a variable: either int or float
        :param layer: layer index; this brakes the compatibility with ROXIE
        :param bcs: block index, range of indices (with -) or no block indication for global variables
        """
        super().__init__(xl, xu, variable, variable_type, layer)
        self.block_start, self.block_end = bcs.split('-')
        self.block_start, self.block_end = int(self.block_start), int(self.block_end)

    def get_compact_variable_name(self) -> str:
        return '%s:%s:%s-%s' % (self.variable, self.layer, self.block_start, self.block_end)
