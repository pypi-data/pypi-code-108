from random import randint
from typing import List

# Global constants
SCHEDULE_LENGTH = 24


def get_schedule_min(
        *_: object,
        predicted_flexibility_potential_negative: List[int],
        predicted_schedule: List[int]
) -> List[int]:
    schedule_min: List[int] = []

    for x, y in \
            zip(predicted_schedule, predicted_flexibility_potential_negative):
        schedule_min.append(x - y)

    return schedule_min


def get_schedule_max(
        *_: object,
        predicted_flexibility_potential_positive: List[int],
        predicted_schedule: List[int]
) -> List[int]:
    schedule_max: List[int] = []

    for x, y in zip(predicted_schedule,
                    predicted_flexibility_potential_positive):
        schedule_max.append(x + y)

    return schedule_max


def get_filtered_activation_starts(
        *_: object,
        activation_starts: List[int]
) -> List[int]:
    # Make sure there are no starts following each other immediately
    activation_starts_filtered: List[int] = []
    for activation_start_index in \
            get_activation_start_indices(activation_starts=activation_starts):
        if activation_start_index + 1 == len(activation_starts):
            # We are at the last activation start
            # So use the last activation start
            # If it is the only one
            if len(activation_starts_filtered) == 0:
                activation_starts_filtered.append(activation_starts[-1])
                continue

        # Non-last activation start
        activation_start_current = activation_starts[activation_start_index]
        activation_start_previous = \
            activation_starts[activation_start_index - 1]
        if activation_start_previous == activation_start_current:
            # The previous activation start was at the same time step already
            # So skip this one
            continue
        activation_starts_filtered.append(
            activation_starts[activation_start_index])
    activation_starts = activation_starts_filtered

    return activation_starts


def get_activation_start_indices(
        *_: object,
        activation_starts: List[int]
) -> List[int]:
    activation_start_indices: List[int] = []

    for activation_start_index in range(len(activation_starts)):
        activation_start_indices.append(activation_start_index)

    return activation_start_indices


def get_activation_ends(
        *_: object,
        activation_starts: List[int]
) -> List[int]:
    activation_ends: List[int] = []

    for activation_start_index in get_activation_start_indices(
            activation_starts=activation_starts):
        activation_start_current = activation_starts[activation_start_index]

        if activation_start_current == SCHEDULE_LENGTH - 1:
            # The current activation starts at the last time step
            # So take itself as end for a 1-step
            end_candidate = SCHEDULE_LENGTH - 1
            activation_ends.append(end_candidate)
            break

        end_min = activation_start_current
        if activation_start_index == len(activation_starts) - 1:
            # We are at the last activation start
            # So the maximum end is the length of the time steps
            end_max = SCHEDULE_LENGTH - 1
        else:
            # We are not at the last activation start
            # So the maximum end is before the next activation start time step
            activation_start_next = \
                activation_starts[activation_start_index + 1]
            end_max = activation_start_next - 1
        print(f'end_min {end_min}')
        print(f'end_max {end_max}')
        if end_min == end_max:
            # The activation can only last for one time step
            end_candidate = end_max
        else:
            # The activation can last one or more time steps
            end_candidate = randint(a=end_min, b=end_max)

        activation_ends.append(end_candidate)

    return activation_ends


def get_random_activation_starts(
        *_: object,
        limit_count_activation: int
) -> List[int]:
    activation_starts: List[int] = sorted([
        randint(a=0, b=SCHEDULE_LENGTH - 1)
        for _ in range(limit_count_activation)
    ])

    return activation_starts
