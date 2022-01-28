from pprint import pformat


###############################################################################

class ModelArguments(object):
    """
    A class used by model_generator.py and model_list.py to store all the parameters
    and default parameters of a specific model.
    """

    def __init__(self, display_name, default_args):
        self._display_name = display_name
        self._default_args = default_args

    @property
    def display_name(self):
        return self._display_name

    @property
    def default_args(self):
        return self._default_args

    def __repr__(self):
        """
        This is used to generate model_list.py: it allows us to generate Python code to
        self-load an intance of this class.
        """
        # We use pprint() because str() does not produce stable dumps
        return '@{}("{}", {})@'.format(self.__class__.__name__,
                                       self._display_name,
                                       pformat(self.default_args, width=99999))


###############################################################################
