from shyft.dashboard.base.ports import (Receiver, Sender, connect_ports)
"""
Example: Send a number from a sender to a receiver and print it to console
"""


def _receive_number(obj: int) -> None:  # create a simple receiving function
    """
    create a simple receiving function to receive and int and print it

    Parameters
    ----------
    obj: int to print
    """
    print("received ", obj)

# create a receiver port
receive_number = Receiver(parent='parent', name='receiver_A', func=_receive_number, signal_type=int)

# create a sender port
# Note: the signal_type=int matches the type annotation of obj in the receive_func_simple
send_number = Sender(parent='parent', name='sender_A', signal_type=int)

# connect the 2 ports
connect_ports(port_sender=send_number, port_receiver=receive_number)

# send a number --> receive it, and print it to console
send_number(20)
