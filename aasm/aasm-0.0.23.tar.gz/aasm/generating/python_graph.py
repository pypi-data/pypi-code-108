from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.generating.python_code import PythonCode
from aasm.intermediate.graph import (AgentConstantAmount, AgentPercentAmount,
                                     ConnectionConstantAmount,
                                     ConnectionDistNormalAmount,
                                     StatisticalGraph)

if TYPE_CHECKING:
    from aasm.intermediate.graph import Graph


class PythonGraph(PythonCode):
    def __init__(self, indent_size: int, graph: Graph):
        super().__init__(indent_size)
        if graph:
            self.add_required_imports()
            self.add_newlines(2)
            self.generate_graph(graph)

    def add_required_imports(self) -> List[str]:
        self.add_line('import random')
        self.add_line('import uuid')
        self.add_line('import numpy')
        
    def generate_graph(self, graph: Graph) -> None:
        if isinstance(graph, StatisticalGraph):
            self.add_statistical_graph(graph)

    def add_statistical_graph(self, graph: StatisticalGraph) -> None:
        self.add_line('def generate_graph_structure(domain):')
        self.indent_right()

        if not graph.agents:
            self.add_line('return []')
            self.indent_left()
            return
        
        num_agents = []
        for agent in graph.agents.values():
            if isinstance(agent.amount, AgentConstantAmount):
                self.add_line(f'_num_{agent.name} = {agent.amount.value}')
            elif isinstance(agent.amount, AgentPercentAmount):
                self.add_line(f'_num_{agent.name} = round({agent.amount.value} / 100 * {graph.size})')
            num_agents.append(f'_num_{agent.name}')
        self.add_line(f'num_agents = {" + ".join(num_agents)}')

        self.add_line('random_id = str(uuid.uuid4())[:5]')
        self.add_line('jids = [f"{i}_{random_id}@{domain}" for i in range(num_agents)]')

        self.add_line('agents = []')
        self.add_line('next_agent_idx = 0')
        for agent in graph.agents.values():
            self.add_line(f'for _ in range(_num_{agent.name}):')
            self.indent_right()
            if isinstance(agent.connections, ConnectionDistNormalAmount):
                self.add_line(f'num_connections = int(numpy.random.normal({agent.connections.mean}, {agent.connections.std_dev}))')
            elif isinstance(agent.connections, ConnectionConstantAmount):
                self.add_line(f'num_connections = {agent.connections.value}')
            self.add_line('num_connections = max(min(num_connections, len(jids) - 1), 0)')
            self.add_line('jid = jids[next_agent_idx]')
            self.add_line('agents.append({')
            self.indent_right()
            self.add_line('"jid": jid,')
            self.add_line(f'"type": "{agent.name}",')
            self.add_line('"connections": random.sample([other_jid for other_jid in jids if other_jid != jid], num_connections),')
            self.indent_left()
            self.add_line('})')
            self.add_line('next_agent_idx += 1')
            self.indent_left()
        
        self.add_line('return agents')
        self.indent_left()
