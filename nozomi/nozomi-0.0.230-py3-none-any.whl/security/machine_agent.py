"""
Nozomi
Machine Agent Module
author: hugh@blinkybeach.com
"""
from nozomi.security.agent import Agent
from nozomi.ancillary.immutable import Immutable


class _MachineAgent(Agent):
    """An agent representing a Nozomi API itself"""
    def __init__(self) -> None:
        self._agent_id = 1

    def __reduce__(self):
        return (_MachineAgent, ())

    agent_id = Immutable(lambda s: s._agent_id)


MACHINE_AGENT = _MachineAgent()
