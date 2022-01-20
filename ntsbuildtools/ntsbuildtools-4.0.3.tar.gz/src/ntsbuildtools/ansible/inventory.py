from configparser import ConfigParser

class InventoryNode:
    """Class to store node names and parent/children relationships"""

    def __init__(self, name):
        """Initializes the ConfigNode class

        Args: a name for the node
        """
        self.name = name
        self.children = set()
        self.parents = set()
        self.type = None
        # remove the children suffix. This makes things easier in the long run
        if name.endswith(":children"):
            self.name = name.replace(":children", "")

    def get_children(self):
        """Return the set of children for this node."""
        return self.children

    def has_children(self):
        if self.children:
            return True
        return False

    def add_child(self, child):
        """Add a child to this nodes children."""
        self.children.add(child)

    def get_parents(self):
        """Return the set of parents for this node."""
        return self.parents

    def add_parent(self, parent):
        """Add a parent to this nodes parents."""
        self.parents.add(parent)

    def get_ancestors(self, ancestors):
        """Return a list of ancestors of this node"""
        for p in self.get_parents():
            ancestors.append(p)
            p.get_ancestors(ancestors)
        return ancestors

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class InventoryTree:
    def __init__(self, path=None):
        """Represents an Ansible Inventory file and enables traversing and querying the Inventory.

        Args:
            path (str, optional): The path to the Ansible Inventory config file, e.g. your 
                                  project's `inventory/hosts` file. Defaults to None.
        """
        self.cfg = ConfigParser(allow_no_value=True)
        if path:
            self.cfg.read(path)
        self.root = set()
        self.nodes = set()
        self.add_nodes()
        self._build_tree()

    def add_nodes(self):
        """Add all nodes to the tree."""
        for sec in self.cfg.sections():
            node = InventoryNode(sec)
            if not self.get_node(node.name):
                self.nodes.add(node)
            for option in self.cfg.options(sec):
                child_node = InventoryNode(option)
                if not self.get_node(child_node.name):
                    self.nodes.add(child_node)

    def get_node(self, name):
        """Find node in this tree"""
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def _build_tree(self):
        """Iterate through all of the sections, and build each parent-child relationship for each node."""
        for sec in self.cfg.sections():
            tmp_sec = sec
            if sec.endswith(":children"):
                tmp_sec = sec.replace(":children", "")
            # in this context, the section is always the parent node
            parent_node = self.get_node(tmp_sec)
            parent_node.type = 'internal'
            self.root.add(parent_node)
            for option in self.cfg.options(sec):
                child_node = self.get_node(option)
                parent_node.add_child(child_node)
                child_node.add_parent(parent_node)
                if child_node.has_children():
                    child_node.type = 'internal'
                else:
                    child_node.type = 'edge'
            # remove any of this parents children.
            tmp_root = self.root.copy()
            for node in tmp_root:
                if node in parent_node.get_children():
                    self.root.remove(node)
