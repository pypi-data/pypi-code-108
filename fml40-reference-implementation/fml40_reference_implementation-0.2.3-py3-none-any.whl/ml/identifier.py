"""This modules provides the ID class which can be used to build S3I
specific identifiers."""

import uuid


class ID:
    """Define primitive variable type ID."""

    def __init__(self, identifier=""):
        """Constructs an ID object with the given identifier.

        :param identifier: Proposal of the identifier

        """

        # TODO validate identifier
        is_valid = self.is_valid_uuid(identifier.replace("s3i:", ""))
        if identifier != "" and is_valid:
            self.__identifier = identifier
        else:
            self.__identifier = "s3i:{}".format(uuid.uuid4())

    @property
    def identifier(self):
        """Returns the identifier.

        :returns: Identifier
        :rtype: str

        """

        return self.__identifier

    @staticmethod
    def is_valid_uuid(uuid_to_test, version=4):
        """Returns true if uuid_to_test is a valid uuid, otherwise return
        false.

        :param uuid_to_test: Uuid to be tested
        :param version: Uuid version
        :returns: Test result
        :rtype: bool

        """

        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test
