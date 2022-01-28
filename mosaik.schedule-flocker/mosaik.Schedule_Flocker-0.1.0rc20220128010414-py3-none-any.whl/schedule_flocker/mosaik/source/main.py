import mosaik_api

from mosaik_schedule_flocker.schedule_flocker.mosaik.source.flocker_source_simulator import \
    FlockerSourceSimulator


def main():
    return mosaik_api.start_simulation(
        simulator=FlockerSourceSimulator(),
        description=FlockerSourceSimulator.__name__
    )


if __name__ == '__main__':
    main()
