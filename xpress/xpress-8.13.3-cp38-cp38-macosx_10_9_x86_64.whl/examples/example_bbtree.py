# This example shows how to visualize the BB tree of a problem after
# (partially) solving it.
#
# Note: assumes all branches are binary
#
# (C) Fair Isaac Corp., 1983-2021

import networkx as nx
import xpress as xp
import time

from matplotlib import pyplot as plt


def message_addtime (prob, data, msg, info):
    """Message callback example: print a timestamp before the message from the optimizer"""
    if msg:
        for submsg in msg.split('\n'):
            print("{0:6.3f}: [{2:+4d}] {1}".format(time.time() - start_time, submsg, info))


def postorder_count(node):
    """Recursively count nodes to compute the cardinality of a subtree for
    each node"""

    card = 0

    if node in left.keys():  # see if node has a left key
        postorder_count(left[node])
        card += card_subtree[left[node]]

    if node in right.keys():
        postorder_count(right[node])
        card += card_subtree[right[node]]

    card_subtree[node] = 1 + card


def setpos(T, node, curpos, st_width, depth):

    """
    Set position depending on cardinality of each subtree
    """

    # Special condition: we are at the root
    if node == 1:
        T.add_node(node, pos=(0.5, 1))

    # Use a convex combination of subtree comparison and
    # depth to assign a width to each subtree
    alpha = .1

    if node in left.keys():

        # X position in the graph should not just depend on depth,
        # otherwise we'd see a long and thin subtree and it would just
        # look like a path

        leftwidth = st_width * (alpha * .5 + (1 - alpha) *
                                card_subtree[left[node]] /
                                card_subtree[node])
        leftpos = curpos - (st_width - leftwidth) / 2

        T.add_node(left[node], pos=(leftpos, - depth))
        T.add_edge(node, left[node])
        setpos(T, left[node], leftpos, leftwidth, depth + 1)

    if node in right.keys():

        rightwidth = st_width * (alpha * .5 + (1 - alpha) *
                                 card_subtree[right[node]] /
                                 card_subtree[node])
        rightpos = curpos + (st_width - rightwidth) / 2

        T.add_node(right[node], pos=(rightpos, - depth))
        T.add_edge(node, right[node])
        setpos(T, right[node], rightpos, rightwidth, depth + 1)


def storeBBnode(prob, Tree, parent, newnode, branch):

    # Tree is the callback data, and it's equal to T
    if branch == 0:
        left[parent] = newnode
    else:
        right[parent] = newnode


T = nx.Graph()

left = {}
right = {}
card_subtree = {}
pos = {}

start_time = time.time()

p = xp.problem()
p.addcbmessage(message_addtime)

p.read('sampleprob.mps.gz')
p.addcbnewnode(storeBBnode, T, 100)
p.controls.maxnode = 40000  # Limit the number of nodes inserted in the graph
p.solve()

postorder_count(1)  # assign card_subtree to each node

# determine the position of each node
# depending on subtree cardinalities
setpos(T, 1, 0.5, 1, 0)

pos = nx.get_node_attributes(T, 'pos')

nx.draw(T, pos)  # create BB tree representation
plt.show()       # display it; you can zoom indefinitely and see all subtrees
