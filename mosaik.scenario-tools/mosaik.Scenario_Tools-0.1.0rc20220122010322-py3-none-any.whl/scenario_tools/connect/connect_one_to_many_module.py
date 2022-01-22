from typing import Set

import mosaik


def connect_one_to_many(
    *,
    source: object,
    sinks: Set[object],
    world: mosaik.scenario.World,
    attribute_pairs,
    async_requests=False,
    time_shifted=False,
    initial_data=None,
):
    """
    Connect an attribute of one mosaik entity of a mosaik world to other one's.

    This is specialized convenience method for mosaik.scenario.world.connect.

    :param world: The world to connect the entities in.
    :param source: The entity to connect the attributes from.
    :param sinks: The entities to connect the attributes to.
    :param attribute_pairs: The attribute to connect the entities with.
    :param async_requests: Indicates the asynchrony of the request
    :param time_shifted: Indicates the shifting of the attribute through time.
    :param initial_data: Data to initialize the connected attribute with.

    :return: None
    """
    for sink in sinks:
        world.connect(
            source,
            sink,
            attribute_pairs,
            async_requests=async_requests,
            time_shifted=time_shifted,
            initial_data=initial_data,
        )
