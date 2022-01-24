
from pydantic.typing import (
    Optional, List, Dict, Literal, Union
)

from net_models.inventory.InventoryModels import InventoryModel, Inventory, Host, Group
from net_models.inventory.Config import HostConfig, GroupConfig
from net_models.fields import GENERIC_OBJECT_NAME


class NornirInventoryModel(InventoryModel):

    name: GENERIC_OBJECT_NAME
    groups: Optional[List[GENERIC_OBJECT_NAME]]
    connection_options: Optional[dict]
    data: Optional[dict]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    platform: Optional[str]

    def add_group(self, group_name):
        if self.groups is None:
            self.groups = []
        if group_name not in self.groups:
            self.groups.append(group_name)



class NornirHostModel(NornirInventoryModel):

    hostname: Optional[GENERIC_OBJECT_NAME]
    data: Optional[HostConfig]




class NornirGroupModel(NornirInventoryModel):

    data: Optional[GroupConfig]


class NornirHostsFile(InventoryModel):

    hosts: Dict[GENERIC_OBJECT_NAME, NornirHostModel]

class NornirGroupsFile(InventoryModel):

    groups: Dict[GENERIC_OBJECT_NAME, NornirGroupModel]


class NornirInventory(Inventory):

    hosts: Dict[GENERIC_OBJECT_NAME, NornirHostModel]
    groups: Dict[GENERIC_OBJECT_NAME, NornirGroupModel]


def to_nornir_model(model: Union[Host, Group, Inventory]):
    nr_model = None
    if isinstance(model, Host):
        nr_model = NornirHostModel(
            name=model.name,
            data=model.config
        )
    elif isinstance(model, Group):
        nr_model =  NornirGroupModel(
            name=model.name,
            data=model.config
        )
        extra_keys = set(model.__fields_set__).difference(set(model.__fields__.keys()))
        if len(extra_keys):
            print(extra_keys)
            if nr_model.data is None:
                nr_model.data = GroupConfig()
        for k,v in model.dict().items():
            if k in extra_keys:
                setattr(nr_model.data, k, v)
    elif isinstance(model, Inventory):
        nr_model = NornirInventory(
            hosts={k:to_nornir_model(v) for k,v in model.hosts.items()},
            groups={k:to_nornir_model(v) for k,v in model.get_flat_groups().items()}
        )

        for group_name, nr_group in nr_model.groups.items():
            group = model.get_group(group_name=group_name)
            if group.children is not None:
                for child_group_name, child_group in group.children.items():
                    nr_model.groups[child_group_name].add_group(group_name)

            if group.hosts is not None:
                for host_name, host in group.hosts.items():
                    nr_model.hosts[host_name].add_group(group_name=group_name)
    return nr_model