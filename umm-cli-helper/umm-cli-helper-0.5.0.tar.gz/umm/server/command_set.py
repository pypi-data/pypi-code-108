import os
from typing import List

import yaml

from umm.server.command import Command


class CommandSet:
    """
    Args:
        commands: list of commands to manage as set

    Attributes:
        command_dict: dictionary for accessing the commands by id
        tag_dict: dictionary mapping tags to commands
    """

    def __init__(self, commands: List[Command]):
        tags_dict = {}
        for c in commands:
            for tag in c.tags:
                if tag in tags_dict:
                    tags_dict[tag].append(c.id)
                else:
                    tags_dict[tag] = [c.id]

        self.command_dict = {c.id: c for c in commands}
        self.tags_dict = tags_dict

    def add(self, command: Command):
        """
        Args:
            command: Command to be added to object
        Returns:
            None
        """
        self.command_dict[command.id] = command
        for tag in command.tags:
            if tag in self.tags_dict:
                self.tags_dict[tag].append(command.id)
            else:
                self.tags_dict[tag] = [command.id]

    def get_candidates(self, tags: List[str]):
        """
        Args:
            tags: list of strings to query for commands with
        Returns:
            None
        """
        candidates = {}
        for tag in tags:
            command_ids = self.tags_dict.get(tag, [])
            for id in command_ids:
                candidates[id] = candidates.get(id, 0) + 1

        candidates_sorted = sorted(
            [
                (tag_count, self.command_dict[id].freq, id)
                for id, tag_count in candidates.items()
            ],
            reverse=True,
        )

        return [self.command_dict[id] for _, _, id in candidates_sorted]

    def increment_freq(self, id: str):
        """
        Args:
            id: command id to increment freq for
        Returns:
            None
        """
        self.command_dict[id].freq += 1

    def max_freq(self):
        """
        Args:
            None
        Returns:
            max `freq` of `Command`s
        """
        freqs = [0]
        for c in self.command_dict.values():
            freqs.append(c.freq)
        return max(freqs)

    def lower_freq(self):
        """
        Args:
            None
        Returns:
            None
        """
        for c in self.command_dict.values():
            c.freq = c.freq // 2

    def write_down(self):
        """
        Args:
            None
        Returns:
            None
        """
        root = os.path.expanduser("~")
        target_folder = os.path.join(root, ".umm")
        tmp_file_name = os.path.join(target_folder, "tmp_commands.yaml")
        file_name = os.path.join(target_folder, "commands.yaml")

        if self.max_freq() >= 100:
            self.lower_freq()

        serialize_dict = dict(
            commands={id: c.__dict__ for id, c in self.command_dict.items()}
        )

        with open(tmp_file_name, "w") as f:
            yaml.dump(serialize_dict, f)

        if os.path.exists(file_name):
            os.remove(file_name)
        os.rename(tmp_file_name, file_name)
