from datetime import datetime
from typing import List

import attr
from attr.validators import instance_of
from copy import deepcopy

from mosaik_schedule_flocker.schedule_flocker.model.electricity_value import \
    ElectricityValue


@attr.s
class ElectricitySchedule:
    id = attr.ib()  # no validator cause it may be string or int
    unit_type: str = attr.ib(validator=instance_of(str))
    subnet: int = attr.ib(validator=instance_of(int))
    electricity_values: List[ElectricityValue] = attr.ib(
        validator=instance_of(List))

    def ___append__(self, value):
        self.electricity_values.append(value)

    @property
    def electricity_schedule_dict(self):
        for idx in range(len(self.electricity_values)):
            if isinstance(self.electricity_values[idx], dict):
                self.electricity_values[idx] = self.electricity_values[idx]
            else:
                self.electricity_values[idx] = \
                    deepcopy(self.electricity_values[idx].__dict__)
        es_dict = deepcopy(self.__dict__)
        es_dict['electricitySchedule'] = deepcopy(
            es_dict['electricity_values'])
        del es_dict['electricity_values']
        es_dict['unitType'] = deepcopy(es_dict['unit_type'])
        del es_dict['unit_type']
        return es_dict

    def __getitem__(self, item):
        if item == 'id':
            return self.id
        elif item == 'unit_type' or item == 'unitType':
            return self.unit_type
        elif item == 'subnet':
            return self.subnet
        elif item == 'electricityValue' or 'electricity_values' or \
                'electricitySchedule':
            return self.electricity_values
        elif isinstance(item, int):
            return self.electricity_values[item]

    def __len__(self):
        return len(self.electricity_values)

    def values(self):
        return self.electricity_values_as_list()

    @property
    def start(self):
        first_electricity_value_start: datetime = \
            min(
                electricity_value.startTime
                for electricity_value in self.electricity_values
            )

        return first_electricity_value_start

    # noqa
    def keys(self):
        return ['id', 'unit_type', 'unitType', 'subnet', 'electricityValue',
                'electricity_values',
                'electricitySchedule']

    def electricity_values_as_list(self):
        values = []
        for val in self.electricity_values:
            values.append(val.value)
        return values
