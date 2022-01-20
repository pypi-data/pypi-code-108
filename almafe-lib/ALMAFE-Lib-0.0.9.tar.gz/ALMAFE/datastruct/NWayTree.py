'''
Implement an N-way tree.
This implementation is not very efficient.  
Replaced in project ALMA EDM Oracle with a purpose-built one based on dicts.
'''

class Node():
    def __init__(self, name, attrs = None, parent = None):
        '''
        Constructor
        :param name: str key for searching
        :param attrs: dict of all attributes other than name
        :param parent: Node to make this a child of
        '''
        try:
            self.name = str(name)
        except (AttributeError, TypeError):
            raise AssertionError('name parameter must be convertible to str')

        # list of child nodes:
        self.children = []
        # dict of other attributes: 
        self.attrs = attrs if attrs else {}
        if parent:
            # make this a child of the specified parent:
            try:
                parent.children.append(self)
            except (AttributeError, TypeError):
                raise AssertionError('parent parameter must be a Node or None')
    
    def find(self, name, includeRoot = True):
        '''
        Search for a node at or below this one with the specified name, using a breadth-first traversal.
        :param name: str node name to find
        :return the found node or None
        '''
        try:
            name = str(name)
        except (AttributeError, TypeError):
            raise AssertionError('name parameter must be convertible to str')
        for node in self.breadthFirst(includeRoot = includeRoot):
            if name == node.name:
                return node
        return None
    
    def findDF(self, name, includeRoot = True):
        '''
        search for a Node at or below this one with the specified name, using a depth-first pre-order traversal
        :param name: str node name to find
        :return the found node or None
        '''
        try:
            name = str(name)
        except (AttributeError, TypeError):
            raise AssertionError('name parameter must be convertible to str')
        for node in self.depthFirst(includeRoot = includeRoot):
            if name == node.name:
                return node
        return None
    
    def depthFirst(self, includeRoot = True, postOrder = False):
        '''
        Generator for recursive depth-first traversal of the tree
        :param includeRoot: if False, suppress yeilding the node where the traversal started.
        :param postOrder: if True, visit the root node last. 
        '''
        # PreOrder - visit the root node first:
        if includeRoot and not postOrder:
            yield self
        # Depth-first: recursively traverse children, always including root node:
        for child in self.children:
            for node in child.depthFirst(includeRoot = True, postOrder = postOrder):
                yield node
        # PostOrder - visit the root node last:
        if includeRoot and postOrder:
            yield self
        
    def breadthFirst(self, includeRoot = True):
        '''
        Generator for recursive breadth-first traversal of the tree
        Level-order: visit the root node first.
        :param includeRoot: if False, suppress yeilding the node where the traversal started.
        '''
        # Level-order - visit the root node first:
        if includeRoot:
            yield self
        # Breadth-first - visit each child node:
        for child in self.children:
            yield child 
        # Breadth-first - recursively traverse children, suppressing each child's root node:
        for child in self.children:
            for node in child.breadthFirst(includeRoot = False):
                yield node
