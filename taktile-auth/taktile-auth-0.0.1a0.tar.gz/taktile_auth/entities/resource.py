import typing as t

import pydantic
import yaml

from taktile_auth.enums import Wildcard


def is_full_wildcard(v):
    assert v == "*" or "*" not in v
    return v


def is_partial_wildcard(v):
    assert v.count("*") <= 1  # Check if last character is *
    return v


def is_full_specified(v):
    assert "*" not in v
    return v


WILDCARD_CHECK = {
    Wildcard.allowed: is_full_wildcard,
    Wildcard.partial: is_partial_wildcard,
    Wildcard.not_allowed: is_full_specified,
}


class Resource(pydantic.BaseModel):
    def __hash__(self):
        return hash(tuple(self.__dict__.values()))


class ResourceDefinition(pydantic.BaseModel):
    resource_name: str
    args: t.Dict[str, Wildcard]

    def get_resource(self) -> Resource:
        fields = {field_name: (str, "*") for field_name in self.args.keys()}
        validators = {
            f"{field_name}_validator": (
                pydantic.validator(field_name, allow_reuse=True)(
                    WILDCARD_CHECK[check]
                )
            )
            for field_name, check in self.args.items()
        }
        return pydantic.create_model(
            self.resource_name,
            **fields,
            __validators__=validators,
            __base__=Resource,
        )


# TODO - Add Load Functions
with open("assets/resources.yaml", "rb") as f:  # TODO - Use Pathlib
    resources = yaml.safe_load(f)

RESOURCES: t.Dict[str, ResourceDefinition] = {}
for resource_name, args in resources.items():
    RESOURCES[resource_name] = ResourceDefinition(
        resource_name=resource_name, args=args
    )
