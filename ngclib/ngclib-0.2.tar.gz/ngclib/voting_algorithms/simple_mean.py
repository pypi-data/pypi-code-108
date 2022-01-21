from nwgraph import Message, Node
from typing import List

def simpleMean(node: Node, messages: List[Message]) -> Message:
	return messages.mean(dim=0)
