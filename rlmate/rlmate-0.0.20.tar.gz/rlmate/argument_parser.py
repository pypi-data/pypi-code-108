import typing as t
import warnings

import sys
import argparse


def _group_hook(fn_add_argument: t.Callable, parser: "ArgumentParser", group_name: str):
    def add_argument(*args, **kwargs):
        argument = fn_add_argument(*args, **kwargs)
        parser._argument_groups[group_name].append(argument)
        return argument

    return add_argument


class ArgumentParser(argparse.ArgumentParser):
    def __init__(
        self,
        hermes_support: bool = True,
    ):

        self._argument_groups: t.Dict[str, t.List[argparse._ActionT]] = {}
        self._groups: t.Dict[str, argparse._ArgumentGroup] = {}
        self._args: argparse.Namespace = None

        super().__init__(description="Process the common RL arguments")

        if hermes_support:
            hermes = self.add_argument_group("hermes")
            hermes.add_argument(
                "hermes_name",
                type=str,
                help="the unique name determined by the hermes programm",
            )

        # common RL arguments
        common = self.add_argument_group("common")

        common.add_argument("-s", "--seed", help="random seed", default=0, type=int)
        common.add_argument(
            "-gpu",
            "--gpu",
            help="using GPU instead of CPU, if possible",
            default=False,
            action="store_true",
        )
        common.add_argument(
            "-gid", "--gpu_id", help="id of GPU to use", default=0, type=int
        )
        common.add_argument("-g", "--gamma", help="gamma", default=0.99, type=float)

    def parse(
        self,
        args: t.Optional[t.Union[str, t.List[str]]] = None,
        namespace: t.Optional[argparse.Namespace] = None,
    ) -> argparse.Namespace:
        if isinstance(args, str):
            args = args.split(" ")
        return self.parse_args(args, namespace)

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        self._args = args
        return self._args

    @property
    def args(self) -> argparse.Namespace:
        if self._args is not None:
            return self._args
        else:
            raise RuntimeError("Tried to retrieve args before parsing took place.")

    def add_argument(self, *args, groups: t.Optional[t.List[str]] = None, **kwargs):
        # warnings.warn(
        #     "It is recommended to use ArgumentParser.add_argument_group to organize your arguments into groups."
        # )
        action = super().add_argument(*args, **kwargs)
        if groups is not None:
            for group in groups:
                if group not in self._argument_groups:
                    raise ValueError(
                        f"Cannot add argument to non-existant group '{group}'"
                    )
                self._argument_groups[group].append(action)
        return action

    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group
    def add_argument_group(
        self,
        group_name: str,
        *args: t.Any,
        inherited_args: t.Optional[t.List[str]] = None,
        parent_groups: t.Optional[t.List[str]] = None,
        **kwargs: t.Any,
    ) -> argparse._ArgumentGroup:
        """Add an argument group. Accepts name and description as first and second postional argument.
        See https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument_group for further information.

        Args:
            group_name (str): The name of the new group
            inherited_args (List[str]], optional): A list of already existing argument names this group should inherit. Defaults to None.
            parent_groups (List[str]], optional): A list groups this group should inherit from. Adds all arguments of that parent to this group

        Raises:
            ValueError: If a group with that name already exists

        Returns:
            argparse._ArgumentGroup: The argument group.
        """

        group = super().add_argument_group(group_name, *args, **kwargs)
        if group.title in self._argument_groups:
            raise ValueError(
                f"Tried to argument group with name '{group.title}' that already exists!"
            )

        self._groups[group.title] = group
        self._argument_groups[group.title] = []

        if inherited_args is not None:
            inherited_args = set(inherited_args)
            for action in self._actions:
                if action.dest in inherited_args:
                    self._argument_groups[group.title].append(action)

        if parent_groups is not None:
            for parent_name in parent_groups:
                if parent_name not in self._groups:
                    raise ValueError(
                        f"Cannot add non-existant group '{parent_name}' as parent group!"
                    )
                parent = self._groups[parent_name]
                parent.add_argument = _group_hook(
                    parent.add_argument, self, group.title
                )

        # this hooks into group.add_argument
        # s.t. every time an argument is added the parser
        # stores that argument in a dictionary mapping group names
        # to arguments belonging to that group
        group.add_argument = _group_hook(group.add_argument, self, group.title)

        return group

    def get_namespace(self, group_name: str) -> argparse.Namespace:
        """Fetch group specific-arguments

        Args:
            group_name (str): The name of the argument group.

        Raises:
            ValueError: If no argument group with that name exists.

        Returns:
            argparse.Namespace: A name space containing the arguments specific to the given group.
        """
        if group_name not in self._argument_groups:
            raise ValueError(f"Unknown argument group: {group_name}")
        return argparse.Namespace(
            **{
                arg.dest: getattr(self.args, arg.dest)
                for arg in self._argument_groups[group_name]
            }
        )

    def get_namespaces(self, *group_names: str) -> t.List[argparse.Namespace]:
        if len(group_names) == 0:
            group_names = [
                gn
                for gn in self._argument_groups.keys()
                if gn not in {"positional arguments", "optional arguments"}
            ]
        return list(self.get_namespace(group_name) for group_name in group_names)


def add_dqn_args(parser: ArgumentParser):
    dqn_group = parser.add_argument_group(
        "dqn",
        inherited_args=[
            "hermes_name",
            "seed",
            "gamma",
            "gpu",
            "gpu_id",
            "positive_reward",
            "negative_reward",
            "step_reward",
        ],
    )
    dqn_group.add_argument(
        "-ne",
        "--num_episodes",
        help="number of episodes to learn from",
        default=10000,
        type=int,
    )
    dqn_group.add_argument(
        "-le",
        "--length_episodes",
        help="length of episodes to learn from",
        default=100,
        type=int,
    )

    dqn_group.add_argument(
        "-erb",
        "--extract_replay_buffer",
        help="extract all states added to the rb",
        default=False,
        action="store_true",
    )
    dqn_group.add_argument(
        "-ce",
        "--checkpoint_episodes",
        help="number of episodes after which a checkpoint occurs",
        default=100,
        type=int,
    )
    dqn_group.add_argument(
        "-ex",
        "--extract_all_states",
        help="extract all visited states",
        default=False,
        action="store_true",
    )
    dqn_group.add_argument(
        "-es", "--eps_start", help="initial value of epsilon", default=1, type=float
    )
    dqn_group.add_argument(
        "-ee", "--eps_end", help="final value of epsilon", default=0.001, type=float
    )
    dqn_group.add_argument(
        "-ed",
        "--eps_decay",
        help="decay value for epsilon",
        default=0.999,
        type=float,
    )
    dqn_group.add_argument(
        "-bfs",
        "--buffer_size",
        help="size of the replay buffer",
        default=10000,
        type=int,
    )
    dqn_group.add_argument(
        "-nsv",
        "--number_state_variables",
        help="number of state variables used to describe a single state",
        default=1,
        type=int,
    )
    dqn_group.add_argument(
        "-bs", "--batch_size", help="size of learning batch", default=64, type=int
    )
    dqn_group.add_argument(
        "-bns",
        "--best_network_score",
        help="best possible score achieved in pre training so far",
        default=-float("inf"),
        type=float,
    )
    dqn_group.add_argument(
        "-pnn",
        "--pretrained_neural_network",
        help="path to pre-trained neural network",
        default=None,
        type=str,
    )
    dqn_group.add_argument(
        "-t", "--tau", help="softupdate factor tau", default=0.001, type=float
    )
    dqn_group.add_argument(
        "-lr", "--learning_rate", help="learning rate", default=5e-4, type=float
    )
    dqn_group.add_argument(
        "-ue", "--update_every", help="update every", default=10, type=float
    )
    dqn_group.add_argument(
        "-nnf",
        "--neural_network_file",
        help="path to network file to use",
        default="networks.fcn",
        type=str,
    )
    dqn_group.add_argument(
        "-nnw",
        "--neural_network_weights",
        help="weights for network init",
        nargs="+",
        default=None,
        type=int,
    )
    dqn_group.add_argument(
        "-pef",
        "--policy_extraction_frequency",
        help="fixed number of steps after which policy is extracted",
        default=0,
        type=int,
    )


def add_reward_args(parser: ArgumentParser):
    reward_group = parser.add_argument_group("reward")
    reward_group.add_argument(
        "-pr",
        "--positive_reward",
        help="reward given when successfull",
        default=100,
        type=float,
    )
    reward_group.add_argument(
        "-nr",
        "--negative_reward",
        help="reward given when failing",
        default=-100,
        type=float,
    )
    reward_group.add_argument(
        "-sr",
        "--step_reward",
        help="reward given when neither winning nor losing",
        default=0,
        type=float,
    )


# TODO mark as deprecated
class Argument_parser(ArgumentParser):
    def __init__(self, hermes_support: bool = True):
        super().__init__(hermes_support)
        add_reward_args(self)
        add_dqn_args(self)
