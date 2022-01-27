from simple_graphql.django.types import ModelClass


class ModelAlreadyRegistered(Exception):
    def __init__(self, model_cls: ModelClass):
        super().__init__(
            f"Model {model_cls.__name__} "
            "has already been registered to the GraphQL schema"
        )


class MutationAlreadyRegistered(Exception):
    def __init__(self, name: str):
        super().__init__(
            f"Mutation {name} has already been registered to the GraphQL schema"
        )


class QueryAlreadyRegistered(Exception):
    def __init__(self, name: str):
        super().__init__(
            f"Query {name} has already been registered to the GraphQL schema"
        )


class SchemaAlreadyBuilt(Exception):
    pass
