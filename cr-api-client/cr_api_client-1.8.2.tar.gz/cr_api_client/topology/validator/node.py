# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
import re
from enum import Enum
from ipaddress import ip_address
from ipaddress import ip_interface
from ipaddress import IPv4Address
from ipaddress import IPv4Interface
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import PositiveInt
from pydantic import validator

from cr_api_client.topology.validator.common import NotEmptyList
from cr_api_client.topology.validator.common import NotEmptyStr
from cr_api_client.topology.validator.common import RoleEnum


class TypeEnum(str, Enum):
    VIRTUAL_MACHINE = "virtual_machine"
    DOCKER = "docker"
    PHYSICAL_MACHINE = "physical_machine"
    HOST_MACHINE = "host_machine"
    ROUTER = "router"
    SWITCH = "switch"
    PHYSICAL_GATEWAY = "physical_gateway"


def check_roles(roles: Optional[Set[RoleEnum]]) -> Optional[Set[RoleEnum]]:
    if roles is not None and len(roles) == 0:
        raise ValueError("'roles' field must not be empty")
    return roles


class RouteType:
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(
        cls, value: str
    ) -> Tuple[Union[IPv4Interface, IPv4Address], Union[IPv4Interface, IPv4Address]]:
        if not isinstance(value, str):
            raise TypeError("string required")
        m = re.fullmatch("(.+) -> (.+)", value)
        if not m:
            raise ValueError("invalid route format")
        return ip_interface(m[1].strip()), ip_address(m[2].strip())

    # def __repr__(self): TODO
    #     return f'Route({super().__repr__()})'


class Node(BaseModel):
    type: TypeEnum
    name: NotEmptyStr
    active: bool = True


class VirtualMachine(Node):
    basebox_id: Optional[NotEmptyStr]
    basebox_vagrant: Optional[NotEmptyStr]
    memory_size: PositiveInt = Field(4096)
    nb_proc: PositiveInt = Field(1)
    roles: Set[RoleEnum]

    # validators
    _check_roles = validator("roles", allow_reuse=True)(check_roles)

    @validator('basebox_id')
    def check_id_or_vagrant(cls, basebox_id, values):
        if not values.get('basebox_vagrant') and not basebox_id:
            raise ValueError('either basebox_id or basebox_vagrant is required')
        return basebox_id

    @validator('basebox_id')
    def check_id_and_vagrant(cls, basebox_id, values):
        if values.get('basebox_vagrant') and basebox_id:
            raise ValueError('basebox_id and basebox_vagrant can not be present together')
        return basebox_id


class Docker(Node):
    base_image: NotEmptyStr
    memory_size: PositiveInt = Field(4096)
    nb_proc: PositiveInt = Field(1)
    roles: Set[RoleEnum]

    # validators
    _check_roles = validator("roles", allow_reuse=True)(check_roles)


class PhysicalMachine(Node):
    roles: Optional[Set[RoleEnum]]

    # validators
    _check_roles = validator("roles", allow_reuse=True)(check_roles)


class HostMachine(Node):
    pass


class Router(Node):
    routes: Optional[NotEmptyList[RouteType]]


class Switch(Node):
    pass


class PhysicalGateway(Node):
    pass


class NodeType:
    _node_types = {
        TypeEnum.VIRTUAL_MACHINE: VirtualMachine,
        TypeEnum.DOCKER: Docker,
        TypeEnum.ROUTER: Router,
        TypeEnum.SWITCH: Switch,
        TypeEnum.PHYSICAL_GATEWAY: PhysicalGateway,
        TypeEnum.PHYSICAL_MACHINE: PhysicalMachine,
        TypeEnum.HOST_MACHINE: HostMachine,
    }

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Dict[str, Any]) -> Node:
        node = Node(**value)
        return cls._node_types[node.type](**value)  # type: ignore

    # def __repr__(self): TODO
    #     return f'NodeType({super().__repr__()})'
