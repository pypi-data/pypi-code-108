from datetime import datetime

from mosaik_schedule_flocker.schedule_flocker.core.config import \
    ScheduleFlockGeneratorConfig


def get_mock_flocker_config(idx):
    start_date = datetime.strptime(
        "2018-05-08T13:43:00+0100",
        "%Y-%m-%dT%H:%M:%S%z")
    predicted_schedule = list([
        1, 2, 6, 2, 3, 5, 8, 2, 3, 6, 2, 9, 2, 7, 3, 7, 5, 7, 3, 8, 1, 7, 5, 6
    ])
    predicted_flexibility_potential_negative = list([
        2, 6, 2, 8, 5, 7, 3, 6, 3, 6, 7, 2, 8, 2, 8, 7, 5, 1, 2, 4, 3, 6, 8, 9
    ])
    predicted_flexibility_potential_positive = list([
        5, 2, 7, 2, 4, 1, 7, 3, 5, 9, 3, 5, 2, 8, 9, 3, 1, 5, 2, 5, 2, 7, 9, 3
    ])
    limit_power_production = 42
    limit_power_consumption = -42
    limit_energy_production = 20
    limit_energy_consumption = -20
    limit_count_activation = 3
    limit_size_flock = 10
    limit_time_generation = 5

    unit_type = 'PV'
    unit_id = "Unit-" + str(idx)

    schedule_flock_generator_config = \
        ScheduleFlockGeneratorConfig(
            start_date=start_date,
            predicted_schedule=predicted_schedule,
            predicted_flexibility_potential_negative=
            predicted_flexibility_potential_negative,
            predicted_flexibility_potential_positive=
            predicted_flexibility_potential_positive,
            limit_power_production=limit_power_production,
            limit_power_consumption=limit_power_consumption,
            limit_energy_production=limit_energy_production,
            limit_energy_consumption=limit_energy_consumption,
            limit_count_activation=limit_count_activation,
            limit_size_flock=limit_size_flock,
            limit_time_generation=limit_time_generation,
            unit_type=unit_type,
            unit_id=unit_id
        )

    return schedule_flock_generator_config
