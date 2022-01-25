from colored import fore

from idem.exec.init import ExecReturn


def display(hub, data):
    """
    Display the data from an idem run
    """
    if not isinstance(data, ExecReturn):
        return hub.output.nested.display(data)

    if not data.result:
        return fore.RED + str(data.comment)
    else:
        return hub.output.nested.display(data.ret)
