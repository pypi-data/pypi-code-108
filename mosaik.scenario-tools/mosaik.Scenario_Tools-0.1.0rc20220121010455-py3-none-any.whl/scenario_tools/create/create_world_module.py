import mosaik


def create_world(
    *,
    mosaik_port=5555,
    mosaik_host='127.0.0.1',
    sim_config,
    start_timeout=5,
    stop_timeout=5
):
    """
    Create a mosaik world object.

    :param mosaik_port: Network port to use for mosaik communications
    :param mosaik_host: Host for mosaik to listen on for connections
    :param sim_config: Configuration to pass to mosaik's world object
    :param start_timeout: Time to wait for simulators to start
    :param stop_timeout: Time to for simulators to stop

    :return: mosaik world object created with the given configuration
    """
    mosaik_config = {
        'addr': (mosaik_host, mosaik_port),
        'start_timeout': start_timeout,  # seconds
        'stop_timeout': stop_timeout,  # seconds
    }
    world = mosaik.scenario.World(
        sim_config=sim_config,
        mosaik_config=mosaik_config
    )

    return world
