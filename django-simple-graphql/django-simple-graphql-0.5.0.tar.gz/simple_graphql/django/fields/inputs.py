import graphene
from graphql.language import ast
from graphql_relay import from_global_id


class GlobalIDInput(graphene.Scalar):
    """
    Object ID in Relay's global ID format. The object type part will be ignored,
    and instead only the numeric ID will be used. This means the right type
    of an object ID will have to be passed in, but it's not verified.
    """

    # TODO: Convert from Scalar to a Field
    # TODO: Make serialization possible
    # TODO: Validate the correct type of an object ID is passed in, preventing
    #       passing in IDs of invalid models.
    # TODO: Automatically query the model instance instead of just returning
    #       the ID.

    @staticmethod
    def serialize(value):
        raise NotImplementedError("GlobalIDInput supports no serialization")

    @staticmethod
    def parse_value(value):
        return from_global_id(value)[1]

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return GlobalIDInput.parse_value(node.value)
