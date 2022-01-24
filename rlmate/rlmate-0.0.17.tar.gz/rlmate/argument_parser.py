import sys
import argparse


class Argument_parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Process the common RL arguments"
        )

        # General Arguments
        self.parser.add_argument(
            "hermes_name",
            type=str,
            help="the unique name determined by the hermes programm",
        )
        self.parser.add_argument("-s", "--seed", help="seed", default=0, type=int)

        # DQN Arguments

        # # DQN binaries
        self.parser.add_argument(
            "-gpu",
            "--gpu",
            help="using gpu instead of CPU, if possible",
            default=False,
            action="store_true",
        )
        self.parser.add_argument(
            "-erb",
            "--extract_replay_buffer",
            help="extract all states added to the rb",
            default=False,
            action="store_true",
        )

        # # DQN options
        self.parser.add_argument(
            "-ne",
            "--num_episodes",
            help="number of episodes to learn from",
            default=10000,
            type=int,
        )
        self.parser.add_argument(
            "-le",
            "--length_episodes",
            help="length of episodes to learn from",
            default=100,
            type=int,
        )
        self.parser.add_argument(
            "-ce",
            "--checkpoint_episodes",
            help="number of episodes after which a checkpoint occurs",
            default=100,
            type=int,
        )
        self.parser.add_argument(
            "-ex",
            "--extract_all_states",
            help="extract all visited states",
            default=False,
            action="store_true",
        )
        self.parser.add_argument(
            "-es", "--eps_start", help="initial value of epsilon", default=1, type=float
        )
        self.parser.add_argument(
            "-ee", "--eps_end", help="final value of epsilon", default=0.001, type=float
        )
        self.parser.add_argument(
            "-ed",
            "--eps_decay",
            help="decay value for epsilon",
            default=0.999,
            type=float,
        )
        self.parser.add_argument(
            "-bfs",
            "--buffer_size",
            help="size of the replay buffer",
            default=10000,
            type=int,
        )
        self.parser.add_argument(
            "-nsv",
            "--number_state_variables",
            help="number of state variables used to describe a single state",
            default=1,
            type=int,
        )
        self.parser.add_argument(
            "-bs", "--batch_size", help="size of learning batch", default=64, type=int
        )
        self.parser.add_argument(
            "-bns",
            "--best_network_score",
            help="best possible score achieved in pre training so far",
            default=-float("inf"),
            type=float,
        )
        self.parser.add_argument(
            "-pnn",
            "--pretrained_neural_network",
            help="path to pre-trained neural network",
            default=None,
            type=str,
        )
        self.parser.add_argument(
            "-g", "--gamma", help="gamma", default=0.99, type=float
        )
        self.parser.add_argument(
            "-t", "--tau", help="softupdate factor tau", default=0.001, type=float
        )
        self.parser.add_argument(
            "-lr", "--learning_rate", help="learning rate", default=5e-4, type=float
        )
        self.parser.add_argument(
            "-ue", "--update_every", help="update every", default=10, type=float
        )
        self.parser.add_argument(
            "-nnf",
            "--neural_network_file",
            help="path to network file to use",
            default="networks.fcn",
            type=str,
        )
        self.parser.add_argument(
            "-nnw",
            "--neural_network_weights",
            help="weights for network init",
            nargs="+",
            default=None,
            type=int,
        )
        self.parser.add_argument(
            "-gid", "--gpu_id", help="id of gpu to use", default=0, type=int
        )
        self.parser.add_argument(
            "-pef",
            "--policy_extraction_frequency",
            help="fixed number of steps after which policy is extracted",
            default=0,
            type=int,
        )
        self.parser.add_argument(
            "-pr",
            "--positive_reward",
            help="reward given when successfull",
            default=100,
            type=float,
        )
        self.parser.add_argument(
            "-nr",
            "--negative_reward",
            help="reward given when failing",
            default=-100,
            type=float,
        )
        self.parser.add_argument(
            "-sr",
            "--step_reward",
            help="reward given when neither winning nor losing",
            default=0,
            type=float,
        )

        self.dqn_keys = [
            "hermes_name",
            "seed",
            "extract_all_states",
            "num_episodes",
            "length_episodes",
            "checkpoint_episodes",
            "eps_start",
            "eps_end",
            "eps_decay",
            "buffer_size",
            "batch_size",
            "best_network_score",
            "pretrained_neural network",
            "gamma",
            "tau",
            "learning_rate",
            "update_every",
            "neural_network_file",
            "neural_network_weights",
            "gpu",
            "gpu_id",
            "policy_extraction_frequency",
            "extract_replay_buffer",
        ]
        self.spec_keys = [self.dqn_keys]

    def parse(self, input=None):
        """
        Parse the given input and return the arguments.
        Args:
            input (string, optional): input to parse istead of stdargs. Defaults to None.

        Returns:
            Namespace: arguments.
        """
        if input == None:
            self.args = self.parser.parse_args()
        else:
            self.args = self.parser.parse_args(input)
        return self.args

    def get_namespaces(self):
        """
        Returns the namespaces separetely as defined by the keys in the init method.

        Returns:
            Namespace: arguments.
        """
        dicts = [{} for _ in range(len(self.spec_keys))]

        args_dict = vars(self.args)
        for key in args_dict:
            for i, keys in enumerate(self.spec_keys):
                if key in keys:
                    dicts[i][key] = args_dict[key]

        namespaces = []
        for i in range(len(self.spec_keys)):
            ap = argparse.ArgumentParser()
            d = dicts[i]
            ap.set_defaults(**d)
            namespaces.append(ap.parse_args([]))

        return namespaces
