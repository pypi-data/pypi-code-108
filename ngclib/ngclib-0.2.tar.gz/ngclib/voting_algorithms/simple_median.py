from nwgraph import Message, Node
from typing import List

def simpleMedian(node:Node, messages:List[Message]) -> Message:
	return messages.median(dim=0)[0]
