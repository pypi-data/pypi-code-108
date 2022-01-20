"""
Validator for core__calculateOptimization mutation.
"""

from qctrlcommons.exceptions import QctrlFieldError
from qctrlcommons.node.registry import NODE_REGISTRY
from qctrlcommons.validation.base import BaseMutationInputValidator
from qctrlcommons.validation.messages import Messages


class CalculateOptimizationValidator(BaseMutationInputValidator):
    """
    Validator for core__calculateOptimization mutation.
    """

    properties = {"optimizationCount": {"type": "number", "exclusiveMinimum": 0}}

    def check_cost_in_graph(self, input_: dict):  # pylint:disable=no-self-use
        """Expect the cost node to be in the graph.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """
        if input_["costNodeName"] not in input_["graph"]["operations"]:
            raise QctrlFieldError(
                message="Cost node must be present in graph.",
                fields=["costNodeName", "graph"],
            )

    def check_output_node_names(self, input_: dict):  # pylint:disable=no-self-use
        """
        Checks the following:
        1. At least 1 element in `outputNodeNames`
        2. All elements in `outputNodeNames` correspond to nodes in graph.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """
        output_node_names = input_["outputNodeNames"]
        graph_operations = input_["graph"]["operations"]

        if len(output_node_names) < 1:
            raise QctrlFieldError(
                message=Messages(
                    field_name="outputNodeNames", minimum=1, items="node name"
                ).min_items,
                fields=["outputNodeNames"],
            )
        for node_name in output_node_names:
            if node_name not in graph_operations:
                raise QctrlFieldError(
                    message=f"The requested output node name '{node_name}' is not"
                    + " present in the graph.",
                    fields=["outputNodeNames"],
                )

    def check_optimizable_variables(self, input_: dict):  # pylint:disable=no-self-use
        """
        Checks that optimizable variables are present in the input graph.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """
        graph_operations = input_["graph"]["operations"]

        for operation in graph_operations.values():
            if NODE_REGISTRY.get_node_cls(
                operation["operation_name"]
            ).optimizable_variable:
                return

        raise QctrlFieldError(
            message="At least one optimization variable is required in the"
            " optimization graph.",
            fields=["graph"],
        )

    def check_initial_values(self, input_: dict):  # pylint:disable=no-self-use
        """
        Check non-default initial values.

        Parameters
        ----------
        input_ : dict
            The GraphQL input.

        Raises
        ------
        QctrlFieldError
            Validation check failed.
        """

        initial_values = []
        graph_operations = input_["graph"]["operations"]

        for operation in graph_operations.values():
            node = NODE_REGISTRY.get_node_cls(operation["operation_name"])
            if (
                node.optimizable_variable
                and operation["kwargs"].get("initial_values") is not None
            ):
                initial_values.append(operation["kwargs"]["initial_values"])

        if len(initial_values) != 0:
            for val in initial_values[1:]:
                if not isinstance(val, type(initial_values[0])):
                    raise QctrlFieldError(
                        message="Non-default initial values of optimization variables in the graph"
                        " must all either be an array or a list of arrays.",
                        fields=["Graph"],
                    )

            if isinstance(initial_values[0], list):
                for val in initial_values[1:]:
                    if len(val) != len(initial_values[0]):
                        raise QctrlFieldError(
                            message="Lists of initial values of optimization variables must have "
                            "the same length.",
                            fields=["Graph"],
                        )
