from subprocess import call

def execute(command, split=" "):
    """
        Helper method to call shell commands

        :param command: (str) Shell command as a string
        :param split: (str) Character used to split string (Default: " ")

        :return: subprocess calling command
    """
    return call(command.split(split))