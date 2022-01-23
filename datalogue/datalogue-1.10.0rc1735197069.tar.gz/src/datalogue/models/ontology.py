import itertools
from typing import Dict, List, Optional, Union
from uuid import UUID

from datalogue.dtl_utils import _parse_list
from datalogue.errors import DtlError
from datalogue.models.permission import OntologyPermission
from datalogue.models.scope_level import Scope


class OntologyNode:
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        children: List["OntologyNode"] = [],
        id: Optional[UUID] = None,
    ):

        if not isinstance(name, str):
            raise DtlError("name should be string in OntologyNode")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in OntologyNode")

        if not isinstance(children, List):
            raise DtlError("children should be list in OntologyNode")

        if id is not None and not isinstance(id, UUID):
            raise DtlError("id should be uuid in OntologyNode")

        self.name = name
        self.description = description
        self.children = children
        self.id = id

    def __eq__(self, other: "OntologyNode"):
        if isinstance(self, other.__class__):
            return (
                self.name == other.name
                and self.description == other.description
                and self.children == other.children
                and self.id == other.id
            )
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(id= {self.id}, name= {self.name!r})"

    @staticmethod
    def as_payload(ontology_node: "OntologyNode") -> Union[DtlError, dict]:
        payload = {
            "name": ontology_node.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology_node.children)),
        }

        if ontology_node.id is not None:
            payload["node_id"] = str(ontology_node.id)

        if ontology_node.description is not None:
            payload["description"] = ontology_node.description

        return payload

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, "OntologyNode"]:
        id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        children = payload.get("children")

        if children is None:
            children = []
        else:
            children = _parse_list(OntologyNode.from_payload)(children)

        return OntologyNode(name, description, children, id)


class Ontology:
    def __init__(
        self, name: str, description: Optional[str] = None, tree: List[OntologyNode] = [], id: Optional[UUID] = None,
    ):

        if not isinstance(name, str):
            raise DtlError("name should be string in Ontology")

        if description is not None and not isinstance(description, str):
            raise DtlError("description should be string in Ontology")

        if not isinstance(tree, List):
            raise DtlError("tree should be list in Ontology")

        if id is not None and not isinstance(id, UUID):
            raise DtlError("id should be uuid in Ontology")

        self.name = name
        self.description = description
        self.tree = tree
        self.id = id

    def __eq__(self, other: "Ontology"):
        if isinstance(self, other.__class__):
            return (
                self.name == other.name
                and self.description == other.description
                and self.tree == other.tree
                and self.id == other.id
            )
        return False

    def __repr__(self):
        def print_nodes(tree, output=[], level=0):
            for n in tree:
                padding = "   " * level
                if level == 0:
                    output.append(padding + n.name)
                else:
                    output.append(padding + "|___" + n.name)
                for c in n.children:
                    print_nodes([c], output, level=level + 1)
            return output

        first_line = f"Ontology(id= {self.id}, name= {self.name!r}, description= {self.description!r})" + "\n"
        return "\n".join(print_nodes(self.tree, [first_line]))

    def leaves(self) -> List[OntologyNode]:
        def iterate(node: OntologyNode) -> List[OntologyNode]:
            if not node.children:
                return [node]
            else:
                return list(itertools.chain(*map(lambda n: iterate(n), node.children)))

        return list(itertools.chain(*map(lambda n: iterate(n), self.tree)))

    @staticmethod
    def _as_payload(ontology: "Ontology") -> Union[DtlError, dict]:
        payload = {
            "name": ontology.name,
            "children": list(map(lambda n: OntologyNode.as_payload(n), ontology.tree)),
        }

        if ontology.description is not None:
            payload["description"] = ontology.description

        return payload

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Ontology"]:
        id = UUID(payload.get("id"))
        name = payload.get("name")
        description = payload.get("description")
        tree = payload.get("tree")
        if tree is None:
            tree = []
        else:
            tree = _parse_list(OntologyNode.from_payload)(payload["tree"])
        return Ontology(name, description, tree, id=id)

    @staticmethod
    def _create_body_for_sharing(target_id: UUID, target_type: Scope, permission: OntologyPermission) -> Dict:

        if not isinstance(target_type, Scope):
            return DtlError(
                f"'{target_type}' should be a type of '{Scope.__name__}' and must be in: {list(map(str, Scope))}"
            )

        if not isinstance(permission, OntologyPermission):
            return DtlError(
                f"'{permission}' should be a type of '{OntologyPermission.__name__}' and must be in: {list(map(str, OntologyPermission))}"
            )

        body = {}

        body["organizations"] = None
        body["groups"] = None
        body["users"] = None

        if target_type == Scope.User:
            body["users"] = {str(target_id): permission.value}
        elif target_type == Scope.Group:
            body["groups"] = {str(target_id): permission.value}
        elif target_type == Scope.Organization:
            body["organizations"] = {str(target_id): permission.value}
        return body

    @staticmethod
    def _create_body_for_unsharing(target_id: UUID, target_type: Scope, permission: str) -> Dict:

        if not isinstance(target_type, Scope):
            return DtlError(
                f"'{target_type}' should be a type of '{Scope.__name__}' and must be in: {list(map(str, Scope))}"
            )

        body = {}

        body["organizations"] = None
        body["groups"] = None
        body["users"] = None

        if target_type == Scope.User:
            body["users"] = {str(target_id): permission}
        elif target_type == Scope.Group:
            body["groups"] = {str(target_id): permission}
        elif target_type == Scope.Organization:
            body["organizations"] = {str(target_id): permission}
        return body


class DataRef:
    def __init__(self, node_id: Union[str, UUID], path_list: List[List[str]]):
        self.node_id = node_id
        self.path_list = path_list


class Mapping:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def __repr__(self):
        return f"{self.__class__.__name__}(name= {self.name}, path= {self.path})"

    def __eq__(self, other):
        if isinstance(other, Mapping):
            return self.name == other.name and self.path == other.path
        return False

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, "Mapping"]:
        name = payload.get("name")
        if not isinstance(name, str):
            return DtlError("'name' parameter is required for Mapping")

        path = payload.get("path")
        if not isinstance(path, str):
            return DtlError("'path' parameter is required for Mapping")

        return Mapping(name, path)


class ClassMapping:
    def __init__(
        self, class_id: UUID, source_mappings: List[Mapping], destination_mappings: List[Mapping],
    ):
        self.class_id = class_id
        self.source_mappings = source_mappings
        self.destination_mappings = destination_mappings

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(class_id= {self.class_id}, source_mappings= {self.source_mappings!r}, "
            f"destination_mappings= {self.destination_mappings!r})"
        )

    def __eq__(self, other):
        if isinstance(other, ClassMapping):
            return (
                self.class_id == other.class_id
                and self.source_mappings == other.source_mappings
                and self.destination_mappings == other.destination_mappings
            )
        return False

    @staticmethod
    def from_payload(payload: dict) -> Union[DtlError, "ClassMapping"]:
        class_id = payload.get("classId")
        if not isinstance(class_id, str):
            return DtlError("'classId' should be a UUID in ClassMapping")
        class_id = UUID(class_id)

        source_mappings = payload.get("sourceMappings")
        if not isinstance(source_mappings, List):
            return DtlError("'sourceMappings' should be a List in ClassMapping")
        source_mappings = _parse_list(Mapping.from_payload)(source_mappings)

        destination_mappings = payload.get("destinationMappings")
        if not isinstance(destination_mappings, List):
            return DtlError("'destinationMappings' should be a List in ClassMapping")
        destination_mappings = _parse_list(Mapping.from_payload)(destination_mappings)

        return ClassMapping(class_id, source_mappings, destination_mappings)
