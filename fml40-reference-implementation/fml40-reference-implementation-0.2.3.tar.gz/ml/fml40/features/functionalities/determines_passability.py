"""This module implements the class DeterminesPassability."""

from datetime import date

from ml.ml40.features.functionalities.functionality import Functionality


class DeterminesPassability(Functionality):
    """This functionality signalizes that the passability can be
    calculated."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name: Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def isPassableNow(self, input: float) -> bool:
        """Returns true if this object can be passed with the given weight
        input, otherwise returns false.

        :param input: Weight of the thing that should pass this object
        :rtype: bool
        """
        pass

    def maxPassableWeightNow(self) -> float:
        """Returns the maximal weight of an object that can pass this object
        at the moment.

        :returns: Maximal weight
        :rtype: bool
        """
        pass

    def maxPassableWeightOnDate(self, date: date) -> float:
        """Returns the maximal weight of an object that can pass this object
        at the given date.

        :param date: Specifies the date
        :returns: Maximal weight
        :rtype: bool
        """
        pass

    def willBePassable(self, input: float) -> date:
        """Returns the next date this object is passable.

        :param input: Weight that should pass this object
        :returns: Date
        :rtype: date
        """
        pass
