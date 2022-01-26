import argparse
import typing as t

from rlmate.argument_parser import Argument_parser


class Racetrack_parser(Argument_parser):
    def __init__(self):
        super().__init__()

        # Racetrack arguments

        racetrack = self.add_argument_group(
            "racetrack",
            inherited_args=[
                "hermes_name",
                "seed",
                "extract_all_states",
                "map_name",
                "negative_reward",
                "positive_reward",
                "step_reward",
                "gamma",
            ],
        )

        # RT args
        racetrack.add_argument(
            "map_name", type=str, help="the map to run the racetrack on"
        )

        # RT binaries
        racetrack.add_argument(
            "-n",
            "--noise",
            help="use noisy version of racetrack",
            default=False,
            action="store_true",
        )
        racetrack.add_argument(
            "-rs",
            "--random_start",
            help="start racetrack from anywhere",
            default=False,
            action="store_true",
        )
        racetrack.add_argument(
            "-rv",
            "--random_velocity",
            help="start racetrack with random velocity",
            default=False,
            action="store_true",
        )
        racetrack.add_argument(
            "-l",
            "--landmarking",
            help="use landmarking. Requires a potential file",
            default=False,
            action="store_true",
        )
        racetrack.add_argument(
            "-sww",
            "--surround_with_walls",
            help="sorround map with walls",
            default=False,
            action="store_true",
        )
        racetrack.add_argument(
            "-ct",
            "--continuous",
            help="use continiuous version of rt",
            default=False,
            action="store_true",
        )

        # RT options
        racetrack.add_argument(
            "-np",
            "--noise_probability",
            help="noise probability",
            default=0.1,
            type=float,
        )
        racetrack.add_argument(
            "-mrv",
            "--maximal_random_velocity",
            help="maximal probability used for rv",
            default=5,
            type=int,
        )
        racetrack.add_argument(
            "-wgl",
            "--width_goal_line",
            help="with of the goal line. Only applicable when spawning new lines",
            default=3,
            type=int,
        )

    # backwards compatability
    def get_namespaces(self) -> t.List[argparse.Namespace]:
        return [self.get_namespace("dqn"), self.get_namespace("racetrack")]
