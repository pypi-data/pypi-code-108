# Copyright 2021 Q-CTRL Pty Ltd & Q-CTRL Inc. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import logging
from typing import (
    Dict,
    List,
    Optional,
)

from gql import Client
from graphql import (
    DocumentNode,
    FieldNode,
    NameNode,
    ObjectValueNode,
    OperationDefinitionNode,
    SelectionSetNode,
    ValueNode,
    VariableDefinitionNode,
    VariableNode,
    print_ast,
)
from graphql.pyutils import FrozenList

from .base import BaseQuery

LOGGER = logging.getLogger(__name__)


class MultiQuery(BaseQuery):
    """Used to combine multiple queries into a
    single document.
    """

    name: str = None

    def __init__(self, client: Client, *queries: List[BaseQuery]):
        super().__init__(client)
        self._queries = list(queries)

    def add_query(self, query: BaseQuery):
        """Adds a query to be added to the
        executed document.
        """
        self._queries.append(query)

    def _get_query_document(self):

        if not self._queries:
            raise ValueError("no queries found")

        if len(self._queries) == 1:
            document = self._queries[0].get_query_document()
            document = self._transform_sub_query_document(0, document)
            return document

        documents = []

        for index, query in enumerate(self._queries):
            document = query.get_query_document()
            document = self._transform_sub_query_document(index, document)
            documents.append(document)

        combined_document = _merge_operation_documents(documents, self.name)
        LOGGER.debug("combined_document: %s", print_ast(combined_document))
        return combined_document

    def _transform_sub_query_document(  # pylint:disable=no-self-use
        self, index: int, document: DocumentNode  # pylint:disable=unused-argument
    ) -> DocumentNode:
        """Optional hook which can be used by
        a sub class to transform the sub query
        documents before merging.
        """
        return document

    def _format_response(self, response, document) -> List[Dict]:
        result = []

        for key in self._get_document_response_keys(document):

            if key not in response:
                raise ValueError(f"expected response key not found: {key}")

            result.append(response[key])

        return result


def _find_variable_nodes(value_node: ValueNode) -> List[VariableNode]:
    """Recursively collects VariableNode objects
    within the given value node.
    """
    result = []

    if isinstance(value_node, VariableNode):
        result.append(value_node)

    # can contain nested variable nodes
    if isinstance(value_node, ObjectValueNode):
        for object_field_node in value_node.fields:
            result += _find_variable_nodes(object_field_node.value)

    return result


def _suffix_document(doc: DocumentNode, suffix: str):
    """Attach a suffix to the variable names and retrieval
    keys for the given document. This function can be used
    in preparation for combining multiple instances of the
    same document.
    """
    variables: Dict[str, List[VariableNode]] = {}
    field_nodes: List[FieldNode] = []

    for definition_node in doc.definitions:

        for variable_definition_node in definition_node.variable_definitions:
            variable_name = variable_definition_node.variable.name.value

            if variable_name in variables:
                raise ValueError(
                    f"duplicate variable name in document: {variable_name}"
                )

            variables[variable_name] = [variable_definition_node.variable]

        for field_node in definition_node.selection_set.selections:

            if not isinstance(field_node, FieldNode):
                raise TypeError(f"unhandled node type: {field_node}")

            field_nodes.append(field_node)

            # find references to variables in field arguments
            for argument_node in field_node.arguments:

                for variable_node in _find_variable_nodes(argument_node.value):
                    variable_name = variable_node.name.value

                    if variable_name not in variables:
                        raise ValueError(f"undefined variable name: {variable_name}")

                    variables[variable_name].append(variable_node)

    # update alias for field nodes with suffix
    for field_node in field_nodes:
        if not field_node.alias:
            field_node.alias = NameNode(value=field_node.name.value)

        field_node.alias.value = f"{field_node.alias.value}_{suffix}"

    # update variables names with suffix, including references
    for variable_name, variable_nodes in variables.items():
        new_variable_name = f"{variable_name}_{suffix}"

        for variable_node in variable_nodes:
            variable_node.name.value = new_variable_name


def _check_unique_variables(variable_definition_nodes: List[VariableDefinitionNode]):
    """Checks that the variable name is unique across all
    variable definition nodes.
    """
    variable_names = set()

    for node in variable_definition_nodes:
        if node.variable.name.value in variable_names:
            raise ValueError(f"duplicate variable: {node.variable.name.value}")

        variable_names.add(node.variable.name.value)


def _check_unique_retrieval_keys(field_nodes: List[FieldNode]):
    """Checks that the retrieval key (name or alias) is unique
    across all field nodes.
    """
    keys = set()

    for node in field_nodes:
        key = node.alias.value if node.alias else node.name.value

        if key in keys:
            raise ValueError(f"duplicate retrieval key: {key}")

        keys.add(key)


def _merge_operation_documents(
    documents: List[DocumentNode], name: Optional[str] = None
) -> DocumentNode:
    """Combines multiple documents into a new, single document with
    multiple queries. Variable names must be unique across all
    documents. The retrieval key (name or alias) of all selections
    must be unique across all documents.

    Parameters
    ----------
    documents: List[DocumentNode]
        list of GraphQL documents to be merged.

    name: Optional[str]
        name of the combined document.

    Returns
    -------
    DocumentNode
        the combined GraphQL document.

    Raises
    ------
    ValueError
        any validation errors.
    TypeError
        unhandled GraphQL node types.
    """

    if not documents:
        raise ValueError("no documents provided")

    if len(documents) == 1:
        raise ValueError("unable to merge single document")

    operation_type = None  # used to check consistent operation type
    variable_definition_nodes = []
    field_nodes = []

    # for each doc to be merged
    for doc in documents:
        assert isinstance(doc, DocumentNode)

        for definition_node in doc.definitions:

            if not isinstance(definition_node, OperationDefinitionNode):
                raise TypeError(f"unhandled DefinitionNode: {definition_node}")

            if operation_type is None:
                operation_type = definition_node.operation

            elif definition_node.operation != operation_type:
                raise ValueError(
                    "unable to merge different operation types; found"
                    f" {definition_node.operation}, expected {operation_type}"
                )

            # collect variable definitions
            for variable_definition_node in definition_node.variable_definitions:
                variable_definition_nodes.append(variable_definition_node)

            # collect field nodes
            for selection_node in definition_node.selection_set.selections:
                if not isinstance(selection_node, FieldNode):
                    raise TypeError(f"unhandled SelectionNode: {selection_node}")

                field_nodes.append(selection_node)

    # validation for merged document
    _check_unique_variables(variable_definition_nodes)
    _check_unique_retrieval_keys(field_nodes)

    # build node for combined document
    operation_definition_node = OperationDefinitionNode(
        operation=operation_type,
        variable_definitions=FrozenList(variable_definition_nodes),
        selection_set=SelectionSetNode(selections=FrozenList(field_nodes)),
    )

    if name:
        operation_definition_node.name = NameNode(value=name)

    return DocumentNode(definitions=FrozenList([operation_definition_node]))
