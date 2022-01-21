# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import IPvAnyInterface
from pydantic import root_validator
from pydantic import validator

from .node import Node
from .node import TypeEnum
from cr_api_client.topology.validator.common import PositiveEqualInt


class NetworkConfig(BaseModel):
    ip: Optional[Union[
        IPvAnyInterface, Literal["dynamic"]
    ]]  # If the ip is not provided it should be dynamic, however it can be left empty in the yaml file
    mac: Optional[str] = Field(regex="^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$")


class Link(BaseModel):
    switch: Node
    node: Node
    params: NetworkConfig

    @validator("switch")
    def check_is_switch(cls, v: Node):
        if v.type != TypeEnum.SWITCH:
            raise ValueError(f"must be of {TypeEnum.SWITCH} type")
        return v

    @validator("node")
    def check_is_not_switch(cls, v: Node):
        if v.type == TypeEnum.SWITCH:
            raise ValueError(f"must not be of {TypeEnum.SWITCH} type")
        return v

    @root_validator(skip_on_failure=True)
    def check_nodes_consistency(cls, values: Dict[str, Any]):
        switch, node = values["switch"], values["node"]
        if (
            switch.type == TypeEnum.VIRTUAL_MACHINE
            and node.type == TypeEnum.VIRTUAL_MACHINE
        ):
            raise ValueError("It is not possible to link two virtual machine nodes")
        return values
