'''
Test the N-way tree class
'''

from datastruct.NWayTree import Node

def test1():
    # Test walking sample tree:
    # root-----------+-------------+
    # c1--+---+      c2--+---+     c3--+---+
    # d11 d12 d13    d21 d22 d23   d31 d32 d33--+----+
    #                                      e331 e332 e333
    
    root = Node('root')
    c1 = Node('c1', parent = root)
    c2 = Node('c2', parent = root)
    c3 = Node('c3', parent = root)
    d11 = Node('d11', parent = c1)
    d12 = Node('d12', parent = c1)
    d13 = Node('d13', parent = c1)
    d21 = Node('d21', parent = c2)
    d22 = Node('d22', parent = c2)
    d23 = Node('d23', parent = c2)
    d31 = Node('d31', parent = c3)
    d32 = Node('d32', parent = c3)
    d33 = Node('d33', parent = c3)
    e331 = Node('e331', parent = d33)
    e332 = Node('e331', parent = d33)
    e333 = Node('e331', parent = d33)

    print("\ndepth first pre-order:")
    for node in root.depthFirst(includeRoot = True, postOrder = False):
        print(node.name)

    print("\ndepth first post-order:")
    for node in root.depthFirst(includeRoot = True, postOrder = True):
        print(node.name)
    
    print("\nbreadth first:")    
    for node in root.breadthFirst(includeRoot = True):
        print(node.name)

def test2():
    # Test a simpler tree for post-order = RPN calculator:
    # '2 * (3 + 4)' should represent as (2 (3 4 +) *)
    #
    # *
    # 2 +
    #   3 4 

    root = Node('*')
    p1 = Node('2', parent = root)
    p2 = Node('+', parent = root)
    p21 = Node('3', parent = p2)
    p22 = Node('4', parent = p2)

    print("\ndepth first post-order:")
    for node in root.depthFirst(includeRoot = True, postOrder = True):
        print(node.name)

