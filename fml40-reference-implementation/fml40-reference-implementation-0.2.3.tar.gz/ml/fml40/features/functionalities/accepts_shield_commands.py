from ml.ml40.features.functionalities.functionality import Functionality


class AcceptsShieldCommands(Functionality):
    """This functionality signalizes that the thing's shield can be moved remotely
    via S3I-B messages ."""

    def __init__(self, namespace="fml40", name="", identifier="", parent=None):
        """Initializes the object.

        :param name:  Object name
        :param identifier: Identifier

        """
        super().__init__(
            namespace=namespace, name=name, identifier=identifier, parent=parent
        )

    def shieldDown(self, speed):
        """roll down the winch with specified speed

        :param speed: speed
        :type speed: float
        """
        print("shield moves down with the speed {}".format(speed))

    def shieldUp(self, speed):
        """
        roll up the winch with specified speed

        :param speed: speed
        :type speed: float
        """
        print("shield moves up with the speed {}".format(speed))
