import logging
import os
from collections import defaultdict
from typing import List, Union

import numpy as np
from numpy.random import seed
from tableschema import Table, Schema

from tsfaker.exceptions import ResourceMissing, EmptyForeignKeyResource


class ForeignKeyCatalog:
    def __init__(self, resource_name_to_path_or_schema=None, low_memory=False, limit_fk=False):
        self.resource_name_to_path_or_schema = resource_name_to_path_or_schema or dict()
        self.catalog_remaining_uses = self.set_catalog_remaining_uses()
        self.catalog = dict()
        self.low_memory = low_memory
        self.limit_fk = limit_fk or 10 ** 10

    def set_catalog_remaining_uses(self) -> dict:
        catalog_remaining_uses = defaultdict(int)
        for resource_name, schema in self.resource_name_to_path_or_schema.items():
            if not isinstance(schema, Schema):
                continue
            for foreign_key in schema.foreign_keys:
                resource_key = self._get_resource_key(resource_name=foreign_key['reference']['resource'],
                                                      resource_fields=foreign_key['reference']['fields'])
                catalog_remaining_uses[resource_key] += 1
        return catalog_remaining_uses

    def get_foreign_key_values(self, resource_name, resource_fields) -> np.ndarray:
        """ Return a numpy array with foreign key values for resource_name and resource_fields

        :param resource_name: name of the foreign table
        :param resource_fields: name of the fields in foreign table
        :return:
        """
        logging.debug("Get foreign key values for resource {}:{}".format(resource_name, resource_fields))
        resource_key = self._get_resource_key(resource_name, resource_fields)
        self.catalog_remaining_uses[resource_key] -= 1

        if self._get_resource_path(resource_name) in self.catalog:
            return self._get_foreign_key_values_from_catalog(resource_key)
        else:
            return self._get_foreign_key_values_from_resource(resource_name, resource_fields)

    def _get_foreign_key_values_from_resource(self, resource_name, resource_fields):
        table = Table(self._get_resource_path(resource_name))
        foreign_key_values = []
        for i, keyed_row in enumerate(table.iter(keyed=True)):
            if i > self.limit_fk:
                break
            foreign_key_values.append([keyed_row[key] for key in resource_fields])
        if not foreign_key_values:
            raise EmptyForeignKeyResource("No values for resource {}:{}".format(resource_name, resource_fields))

        foreign_key_values = np.array(foreign_key_values)

        if self.catalog_remaining_uses and not self.low_memory:  # populate catalog
            resource_key = self._get_resource_key(resource_name, resource_fields)
            self.catalog[resource_key] = foreign_key_values

        return foreign_key_values

    def _get_foreign_key_values_from_catalog(self, resource_key):
        if self.catalog_remaining_uses == 0:
            return self.catalog.pop(resource_key)
        return self.catalog[resource_key]

    def _get_resource_path(self, resource_name):
        resource_path = self.resource_name_to_path_or_schema[resource_name]
        if not os.path.exists(resource_path):
            raise ResourceMissing("Resource csv file is missing '{}'. This should not happen. "
                                  "This file either existed when tsfaker was started, "
                                  "or it should have been generated before.".format(resource_path))
        return resource_path

    @staticmethod
    def _get_resource_key(resource_name, resource_fields):
        return resource_name + '__' + '+'.join(resource_fields)


class ForeignKeyGenerator:
    """ Generate a random 2D arrays with values taken from foreign keys
    """

    @staticmethod
    def to_list(str_or_list: Union[str, List[str]]) -> List[str]:
        return (str_or_list,) if isinstance(str_or_list, str) else str_or_list

    def __init__(self, nrows: int,
                 fields: Union[str, List[str]],
                 resource_name: str,
                 resource_fields: Union[str, List[str]],
                 foreign_key_catalog: ForeignKeyCatalog = None,
                 random_seed: int = 42
                 ):
        self.nrows = nrows
        self.fields = self.to_list(fields)

        self.resource_fields = self.to_list(resource_fields)

        self.foreign_key_catalog = foreign_key_catalog or ForeignKeyCatalog()
        self.foreign_key_values = self.foreign_key_catalog.get_foreign_key_values(resource_name, self.resource_fields)
        self.random_seed = random_seed
        self.array_2d = self.random_choice_2d(self.foreign_key_values, self.nrows)

    def random_choice_2d(self, array: np.ndarray, size: int) -> np.ndarray:
        seed(self.random_seed)
        random_indices = np.random.randint(array.shape[0], size=size)
        return array[random_indices, :]

    def get_column(self, field) -> np.ndarray:
        field_index = self.fields.index(field)
        return self.array_2d[:, field_index]
