from copy import deepcopy
from datetime import timedelta, datetime

from mosaik_schedule_flocker.schedule_flocker.model.electricity_schedule \
    import ElectricitySchedule
from mosaik_schedule_flocker.schedule_flocker.model.electricity_value import \
    ElectricityValue


def fill_electricity_schedule_dict(unit_id, unit_type, schedule, date=None):
    # unit 0 : 1, 1: 14, 2: 136, 3, 4, 5, 6: 136
    start_times = [f"2020-04-17T{hr}:{minute}:00+00:00" for hr in [18, 19, 20, 21, 22, 23] for minute in
                   ['00', '15', '30', '45']]
    if date is not None:
        datetime_object = datetime.fromisoformat(date)
    step_size = 900
    values = []
    for value, start_time_str in zip(schedule, start_times):
        electricity_value = ElectricityValue(
            startTime=start_time_str,
            stepSize=step_size,
            powerActive=value,
            powerReactive=value,
        )
        values.append(deepcopy(electricity_value))
        if date is not None:
            datetime_object += timedelta(minutes=15)

    # is only necessary for isaac_source, because in simulation,
    # subnet-ids are set by simona.
    if unit_id == 'Unit-0':
        subnet = 1
    elif unit_id == 'Unit-1':
        subnet = 14
    else:
        subnet = 136

    electricity_schedule: ElectricitySchedule = ElectricitySchedule(
        electricity_values=values,
        id=unit_id,
        unit_type=unit_type,
        subnet=subnet,
    )

    return electricity_schedule
