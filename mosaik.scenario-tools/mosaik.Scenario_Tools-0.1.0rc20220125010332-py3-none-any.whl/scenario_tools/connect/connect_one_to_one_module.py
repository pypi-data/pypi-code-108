import mosaik


def connect_one_to_one(
    *,
    world: mosaik.scenario.World,
    source: object,
    sink: object,
    attribute_pairs,
    async_requests=False,
    time_shifted=False,
    initial_data=None,
):
    """
    Connect an attribute of a mosaik entity of a mosaik world to another one's.

    This is specialized convenience method for mosaik.scenario.world.connect.

    :param world: The world to connect the entities in.
    :param source: The entity to connect the attributes from.
    :param sink: The entity to connect the attributes to.
    :param attribute_pairs: The attribute to connect the entities with.
    :param async_requests: Indicates the asynchrony of the request
    :param time_shifted: Indicates the shifting of the attribute through time.
    :param initial_data: Data to initialize the connected attribute with.

    :return: None
    """
    for _ in [0]:
        world.connect(
            source,
            sink,
            attribute_pairs,
            async_requests=async_requests,
            time_shifted=time_shifted,
            initial_data=initial_data,
        )
