from __future__ import annotations

from typing import Dict


class AgentAmount:
    def __init__(self, value: str):
        self.value = value

    def print(self) -> None:
        print(f'AgentAmount value = {self.value}')


class AgentConstantAmount(AgentAmount):
    def __init__(self, value: str):
        super().__init__(value)

    def print(self) -> None:
        print('AgentConstantAmount')
        super().print()


class AgentPercentAmount(AgentAmount):
    def __init__(self, value: str):
        super().__init__(value)

    def print(self) -> None:
        print('AgentPercentAmount')
        super().print()


class ConnectionAmount:
    ...


class ConnectionConstantAmount(ConnectionAmount):
    def __init__(self, value: str):
        self.value = value
    
    def print(self) -> None:
        print(f'ConnectionConstantAmount value = {self.value}')


class ConnectionDistNormalAmount(ConnectionAmount):
    def __init__(self, mean: str, std_dev: str):
        self.mean = mean
        self.std_dev = std_dev

    def print(self) -> None:
        print(f'ConnectionDistNormalAmount mean = {self.mean}, std_dev = {self.std_dev}')


class StatisticalAgent:
    def __init__(self, name: str, amount: AgentAmount, connections: ConnectionAmount):
        self.name = name
        self.amount = amount
        self.connections = connections

    def print(self) -> None:
        print(f'StatisticalAgent name = {self.name}')
        self.amount.print()
        self.connections.print()


class Graph:
    def __init__(self):
        self.size = None

    def set_size(self, size: int) -> None:
        self.size = size

    def is_size_defined(self) -> bool:
        return self.size is not None

    def print(self) -> None:
        print(f'Graph size = {self.size}')


class StatisticalGraph(Graph):
    def __init__(self):
        super().__init__()
        self.agents: Dict[str, StatisticalAgent] = {}

    def add_agent(self, agent: StatisticalAgent) -> None:
        self.agents[agent.name] = agent

    def is_agent_defined(self, agent_type: str) -> bool:
        return agent_type in self.agents

    def is_agent_percent_amount_used(self) -> bool:
        for agent in self.agents.values():
            if isinstance(agent.amount, AgentPercentAmount):
                return True
        return False

    def print(self) -> None:
        super().print()
        print('StatisticalGraph')
        for agent in self.agents.values():
            agent.print()
