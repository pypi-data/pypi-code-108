from ml.ml40.features.functionalities.functionality import Functionality


class AcceptsWinchCommands(Functionality):
    """This functionality signalizes that the thing's winch can be moved remotely
    via S3I-B messages ."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def rollDown(self, speed):
        """roll down the winch with specified speed

        :param speed: speed
        :type speed: float
        """
        print("roll down the winch with the speed {}".format(speed))

    def rollUp(self, speed):
        """
        roll up the winch with specified speed

        :param speed: speed
        :type speed: float
        """
        print("roll up the winch with the speed {}".format(speed))
