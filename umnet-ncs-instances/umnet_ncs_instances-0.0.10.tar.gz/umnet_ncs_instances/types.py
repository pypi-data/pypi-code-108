from lxml import etree
import logging
import re
import inspect


DEFAULT_NSMAP = {
            "config":"http://tail-f.com/ns/config/1.0",
            "devices":"http://tail-f.com/ns/ncs",
            "services":"http://tail-f.com/ns/ncs",
            "baseconf":"http://umnet.umich.edu/umnet-baseconf",
            "distribution":"http://umnet.umich.edu/distribution",
            "constants":"http://umnet.umich.edu/constants",
}

logging.getLogger(__name__)

class Node:
    """
    Class that generically represents an xml/yang node
    """

    _ns = None
    _name = None

    def set_ns(self, value):
        self._ns = value

    @property
    def nsmap(self):
        if self._ns:
            return {None: self._ns}
        else:
            return None

    def _pythonify(self, value: str):
        return value.replace("-", "_")

    def _xmlify(self, value: str):
        return value.replace("_", "-")


class Container(Node):
    """
    Class meant to represent a Yang container.
    Basically this is a 'Node' class that can have children.
    Only instance initializer classes are allowed to set children
    """
    def __init__(self, hide_if_empty=False):
        self._hide_if_empty = hide_if_empty

    def __setattr__(self, name, value):
        """
        Limiting who can set container children and how.
        """

        # private attributes can be set with no restriction,
        if name.startswith("_"):
            self.__dict__[name] = value
            return

        # if the attribute exists already and we're setting it as the right
        # type, that is fine too
        if name in self.__dict__ and type(self.__dict__[name]) == type(value):
            self._empty = False
            self.__dict__[name] = value
            self.__dict__[name]._name = name
            return

        caller = inspect.currentframe().f_back
        caller_info = inspect.getframeinfo(caller)
        calling_func = caller_info[2]

        # only the special ncs_instance function 'initialize_model' can set
        # children on containers
        if calling_func == "initialize_model":

            # any assigned value must be one of our special 'yang' types
            if isinstance(value, (Container, LeafList, List, Leaf)):
                self.__dict__[name] = value
                self.__dict__[name]._name = self._xmlify(name)
            else:
                raise TypeError()

        # a user can call the 'choice' function on a choice child
        elif calling_func == "choose":
            self.__dict__[name] = value

        # the user can also directly assign a value to a leaf child
        elif isinstance(self.__dict__[name], Leaf):
            self.__dict__[name].value = value
            self.__dict__[name]._name = self._xmlify(name)
            self._empty = False

        # or they can directly assign a list to a leaflist
        elif isinstance(self.__dict__[name], LeafList) and type(value) == list:
            self.__dict__[name]._values = []
            self.__dict__[name]._name = self._xmlify(name)
            self._empty = False

            # assigning each entry in our list individually
            # so that the type is checked
            for v in value:
                self.__dict__[name].append(v)



    def __getattribute__(self, name):

        """
        Overloading 'getattribute' so that if someone wants to read
        a Leaf or LeafList attribute they'll get the value
        of the Node
        """

        obj = super().__getattribute__(name)

        if isinstance(obj, Leaf):
            return self.__dict__[name].value
        if isinstance(obj, LeafList):
            return self.__dict__[name].values

        return obj

    def get_child_nodes(self):
        children = {}
        for name, obj in self.__dict__.items():
            if isinstance(obj, (Leaf, LeafList, List, Container)):
                children[name] = obj
        return children

    @property
    def is_empty(self):

        children = self.get_child_nodes()
        for child_name, child_obj in children.items():
            if getattr(child_obj, "is_empty") == False:
                return False

        return True

    def _gen_xml(self, tree: etree.Element, path_filter=None):
        """
        Adds itself as an element to an existing etree object
        """

        # skip if we're filtering and this node doesn't match
        if path_filter and path_filter["name"] != self._name:
            return

        # also skip if this container is empty and we're supposed
        # to hide on empty
        if self._hide_if_empty and self.is_empty:
            return

        # otherwise add ourself as a sub element, moving along the
        # path filter if applicable
        xml_container = etree.SubElement(tree, self._name, nsmap=self.nsmap)
        if path_filter:
            path_filter = path_filter[1::]

        children = self.get_child_nodes()
        for child_name, child_obj in children.items():
            if not (path_filter) or (path_filter and path_filter["name"] == child_name):
                child_obj._gen_xml(xml_container, path_filter)


class Leaf(Node):
    """
    Leaf class that takes a type in its constructor.
    """

    def __init__(self, leaf_type: type, value=None):
        self._value = value
        self._type = leaf_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) != self._type:
            raise TypeError(f"Invalid type for {value}, must be {self._type}")

        self._value = value

    @property
    def is_empty(self):
        return not (bool(self._value))

    def _gen_xml(self, tree: etree.Element, path_filter=None):
        """
        Adds itself as an element to an existing etree object
        """
        if self._value and (not (path_filter) or path_filter["name"] == self._name):

            xml_node = etree.SubElement(tree, self._name, nsmap=self.nsmap)

            # boolean needs to be expressed as lowercase for NSO to
            # accept it
            if isinstance(self._value, bool):
                xml_node.text = str(self._value).lower()
            else:
                xml_node.text = str(self._value)


class LeafList(Node):
    """
    LeafList class that takes a type in its constructor.
    Newly appended items must be of that type
    """

    def __init__(self, leaf_type: type):
        self._values = []
        self._type = leaf_type

    def append(self, value):
        if isinstance(value, self._type):
            self._values.append(value)
        else:
            raise TypeError(f"Invalid type for {value}, must be {self._type}")

    def extend(self, values: list):
        for v in values:
            self.append(v)

    def remove(self, value):
        self._values.remove(value)

    def __iter__(self):
        return iter(self._values)

    @property
    def values(self):
        return self._values

    @property
    def is_empty(self):
        return not (bool(self._values))

    def _gen_xml(self, tree: etree.Element, path_filter=None):
        """
        Adds itself as an element to an existing etree object
        """
        if self._values and (not (path_filter) or path_filter["name"] == self._name):
            for n in self._values:
                xml_node = etree.SubElement(tree, self._name, nsmap=self.nsmap)
                xml_node.text = str(n)


class List(Node):
    """
    Dict class that takes a class type in its constructor.
    Newly-appended items must be of that class.
    """

    def __init__(self, list_type: "Container", keyattr: str = "name"):
        self._class = list_type()
        self._class.initialize_model()
        self._values = {}
        self._keyattr = keyattr

        if keyattr not in self._class.__dict__:
            raise ValueError(f"{keyattr} not an attribute in {self._class}")

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):

        # item must be of the right class type
        if not (isinstance(value, self._class.__class__)):
            raise TypeError(f"Invalid value type, must be {self._class}")

        # set the key value in the object's attribute
        # as well as adding it to our list
        value.__dict__[self._keyattr] = Leaf(type(key))
        setattr(value, self._keyattr, key)
        self._values[key] = value
        self._values[key]._name = self._xmlify(self._name)

    @property
    def is_empty(self):
        return not (bool(len(self.keys())))

    def _gen_xml(self, tree: etree.Element, path_filter=None):
        """
        Adds itself as an element to an existing etree object
        """
        if path_filter and self._name != path_filter["name"]:
            return
        if path_filter:
            path_filter = path_filter[1::]

        # a list is a dict of containers
        for entry_name, entry_data in self._values.items():

            if not (path_filter) or (path_filter and path_filter["idx"] == entry_name):
                xml_list_entry = etree.SubElement(tree, self._name, nsmap=self.nsmap)
                children = entry_data.get_child_nodes()
                for name, obj in children.items():
                    obj._gen_xml(xml_list_entry, path_filter)

    def items(self):
        return self._values.items()

    def keys(self):
        return self._values.keys()

    def values(self):
        return self._values.values()

    def pop(self, key):
        return self._values.pop(key)

    def __iter__(self):
        return iter(self._values)


class Choice(Container):
    """
    Yang 'choice' object model. Basically a specialized container where
    only some of the children are valid.

    Practically speaking, you can set attributes for any/all choices, no
    matter what you 'choose' w/the choose method. NCSInstance.gen_xml
    does validate that you have chosen which path is valid (by that we mean
    you set the choice attribute) so it knows what to output.
    """

    def __init__(self, choices: list, choice=None):
        self._choices = [self._pythonify(c) for c in choices]

        if choice:
            self.choose(choice)
        else:
            self._choice = None

        super().__init__()

    def choose(self, choice: str):
        choice = self._pythonify(choice)

        if choice not in self._choices:
            raise ValueError(f"Invalid choice {choice} for {self}")

        self._choice = choice

    @property
    def choice(self):
        return self._choice

    @property
    def choices(self):
        return self._choices

    def _gen_xml(self, tree: etree.Element, path_filter=None):
        """
        Adds itself as an element to an existing etree object
        """

        # skip if we're filtering and this node doesn't match
        if path_filter and path_filter["name"] != self._name:
            return

        # also skip if this container is empty and we're supposed
        # to hide on empty
        if self._hide_if_empty and self.is_empty:
            return

        # for choice we need to follow the 'chosen' path only.
        if self._choice:
            chosen = self.__dict__[self._choice]
            chosen._gen_xml(tree, path_filter)
        else:
            raise ValueError(f"Need to set {self._name} choice!")

class NCSObject(Container):
    """ An NCS object """

    _nsmap=DEFAULT_NSMAP
    _path="/config"

    def __init__(self, path=None, nsmap=None, hide_if_empty=False):

        if path:
            self._path = path
        if nsmap:
            self._nsmap = nsmap

        self.initialize_model()
        super().__init__(hide_if_empty=hide_if_empty)

    def _parse_xpath(self, xpath, nsmap):
        """
        Parses an inputted xpath into the start of an etree object.
        """
        pathlist = xpath.split("/")
        if pathlist[0] == '':
            pathlist = pathlist[1::]

        xml_path = []
        for node in pathlist:
            xml_entry = {"idx_name": "", "idx_value": "", "node_name": node}
            m = re.search(r"^([\w\-]+)\[([\w\-]+)=*([\w\-]*)\]", node)
            if m:
                xml_entry["node_name"] = m.group(1)
                if m.group(3):
                    xml_entry["idx_name"] = m.group(2)
                    xml_entry["idx_value"] = m.group(3)
                else:
                    xml_entry["idx_name"] = "name"
                    xml_entry["idx_value"] = m.group(2)

            if xml_entry["node_name"] in nsmap:
                xml_entry["nsmap"] = {None: nsmap[xml_entry["node_name"]]}
            else:
                xml_entry["nsmap"] = None

            xml_path.append(xml_entry)

        # first node our xml list is the root
        first_hop = xml_path.pop(0)
        self._root = etree.Element(first_hop["node_name"], nsmap=first_hop["nsmap"])
        self._tree = self._root

        if first_hop["idx_name"]:
            idx = etree.SubElement(self._tree, first_hop["idx_name"])
            idx = first_hop["idx_value"]

        for node in xml_path:
            self._tree = etree.SubElement(
                self._tree, node["node_name"], nsmap=node["nsmap"]
            )
            if node["idx_name"]:
                idx = etree.SubElement(self._tree, node["idx_name"])
                idx.text = node["idx_value"]

    def gen_xml(self, xpath=None, xpath_nsmap=None):
        """
        Generates an lxml etree object based on eitehr the xpath/nsmap
        provided during initialization, or one provided to the function
        directly
        """

        self._root = None
        self._tree = None
        # first lets start our tree based on the "path" attribute
        if xpath:
            self._parse_xpath(xpath, xpath_nsmap)
        else:
            self._parse_xpath(self._path, self._nsmap)
        
        # now we can add all of the attributes tied to the object
        # to our tree
        children = self.get_child_nodes()
        for child_name, child_obj in children.items():
            child_obj._gen_xml(self._tree)

        # convert to string
        xml_str = etree.tostring(self._root, pretty_print=True)
        xml_str = xml_str.decode("utf-8")

        # if we've got some string munging, apply it here.
        if hasattr(self, "_xml_munge"):
            for pattern, repl in self._xml_munge.items():
                xml_str = re.sub(pattern, repl, xml_str)

        return xml_str
