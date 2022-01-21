from termcolor import colored
from ..utils.constants import LOGConstants
import colorama


class ConsoleLogger(object):
    def __init__(self):
        """Initialization constructor WidgetLogger"""
        colorama.init()
        pass

    def _get_color_for_label(self, label):
        """Get color from given label

        Args:
          label: 

        Returns:

        """
        log_attributes = [a for a in dir(LOGConstants) if not a.startswith("__")]
        attribute_values = [[LOGConstants.__dict__[key]] for key in LOGConstants.__dict__.keys() if
                            key in log_attributes]
        color = [i[0][1] for i in attribute_values if i[0][0] == label][0]
        return color

    def emit(self, label, record):
        """emit/print the message

        Args:
          label: 
          record: 

        Returns:

        """
        color = self._get_color_for_label(label)
        print(colored(label, color) + "\t" + record)
