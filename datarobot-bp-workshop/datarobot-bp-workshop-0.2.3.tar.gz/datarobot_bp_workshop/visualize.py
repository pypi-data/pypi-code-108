"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""

import copy
import logging

from typing import Dict, Optional, Union
from datarobot import Blueprint

from datarobot_bp_workshop.utils import PrettyString

FAILED_TO_RENDER_WITH_GRAPHVIZ = (
    "Failed to render with `graphviz`. Is `graphviz` installed to the OS?. "
    "Reverting to graphviz string instead."
)

try:
    import graphviz

    GraphvizType = graphviz.Source
except Exception:
    GraphvizType = str

try:
    from IPython.core.display import DisplayHandle

    DisplayGraphviz = DisplayHandle
except Exception:
    DisplayGraphviz = bytes


LOGGER = logging.getLogger("Visualize")


class Visualize(object):
    """ Provides visualization functionality. """

    DATA_NODE = "Data"
    PREDICT_NODE = "Predict"

    border_color = "#c4c8c9"
    node_color = "#20262a"
    predict_color = "#3ca3e8"
    tooltip_color = "#181d20"

    @classmethod
    def to_graphviz_string(
        cls,
        nodes,
        edges,
        graph_name=None,
        node_to_task_lookup=None,
        vertex_context_lookup=None,
        vertical=False,
    ) -> str:
        """ Generate a GraphViz DiGraph string from nodes and edges. """
        nodes = Visualize.format_nodes_to_draw(
            nodes_to_draw=nodes,
            node_to_task_lookup=node_to_task_lookup,
            vertex_context_lookup=vertex_context_lookup,
        )
        digraph_string = Visualize.simple_to_graphviz(
            nodes=nodes, edges=edges, graph_name=graph_name, vertical=vertical,
        )
        return digraph_string

    @classmethod
    def format_nodes_to_draw(
        cls, nodes_to_draw, node_to_task_lookup=None, vertex_context_lookup=None
    ) -> Dict[str, str]:
        """
        Given nodes to use to generate a GraphViz DiGraph string, format them
        such that they are styled as expected to look familiar to the DataRobot UI.
        """
        node_to_task_lookup = node_to_task_lookup or {}
        output = copy.deepcopy(nodes_to_draw)
        for node_to_draw in output:
            if node_to_draw["label"] == "Prediction":
                node_to_draw["label"] = cls.PREDICT_NODE
            node_to_draw["color"] = '"{}"'.format(cls.border_color)
            node_to_draw["fillcolor"] = (
                '"{}"'.format(cls.predict_color)
                if cls.PREDICT_NODE in [node_to_draw["id"], node_to_draw["label"]]
                else '"{}"'.format(cls.node_color)
            )
            node_to_draw["style"] = '"filled,setlinewidth(2)"'
            node_to_draw["shape"] = "box"
            node_to_draw["fontcolor"] = "white"

            cls.handle_validation(
                node_to_draw,
                node_to_task_lookup.get(node_to_draw["id"]),
                vertex_context_lookup,
            )
        return output

    @classmethod
    def handle_validation(
        cls, node_to_draw, task_id=None, vertex_context_lookup=None
    ) -> None:
        """ Add validation to the components to be used to make a graphviz string. """
        if vertex_context_lookup is None:
            return

        if task_id in vertex_context_lookup:
            errors = vertex_context_lookup[task_id].errors or []
            warnings = vertex_context_lookup[task_id].warnings or []

            if len(errors):
                node_to_draw["color"] = "red1"
            elif len(warnings):
                node_to_draw["color"] = "gold1"

            errors_text = ""
            warnings_text = ""
            if len(errors):
                errors_text += (
                    '<tr><td align="left"><font color="red1">Errors:</font>/td></tr>'
                )
                for error in errors:
                    errors_text += '<tr><td align="left"><font color="red1">{}</font></td></tr>'.format(
                        error
                    )

            if len(warnings):
                warnings_text += '<tr><td align="left"><font color="gold1">Warnings:</font></td></tr>'
                for warning in warnings:
                    warnings_text += '<tr><td align="left"><font color="gold1">- {}</font></td></tr>'.format(
                        warning
                    )

            label = node_to_draw["label"]
            node_to_draw["label"] = (
                '<<table border="0" cellborder="0" cellpadding="3" bgcolor="{node_color}">'
                "<tr>"
                '<td align="center" colspan="2">'
                '<font color="white">{label}</font>'
                "</td>"
                "</tr>"
                "{errors}"
                "{warnings}"
                "</table>>"
            ).format(
                node_color=cls.node_color,
                label=label,
                errors=errors_text,
                warnings=warnings_text,
            )

    @classmethod
    def simple_to_graphviz(cls, nodes, edges, graph_name=None, vertical=False) -> str:
        """ Get blueprint chart in graphviz DOT format.

        Returns
        -------
        unicode
            String representation of chart in graphviz DOT language.
        """
        rankdir = "TB" if vertical else "LR"
        digraph = u'digraph "Blueprint Chart" {'
        digraph += u'\n\tgraph [rankdir={}, bgcolor="#0f1315"]'.format(rankdir)
        for node in nodes:
            if not node["label"].startswith('"') and not node["label"].startswith(
                "<<table "
            ):
                node["label"] = '"{}"'.format(node["label"])
            digraph += u'\n\t{id} [{attrs}, fontname="Ubuntu"]'.format(
                id=node["id"],
                attrs=", ".join(
                    "{}={}".format(attr, node[attr])
                    for attr in (set(node.keys()) - {"id"})
                ),
            )
        for edge in edges:
            digraph += u'\n\t{id0} -> {id1} [color="#c4c8c9", weight=5]'.format(
                id0=edge[0], id1=edge[1]
            )
        if graph_name is not None:
            digraph += u'\n\tlabel="{}\n\n"'.format(graph_name)
            digraph += u'\n\tlabelloc="t"'
            digraph += u"\n\tfontcolor = white"
            digraph += u"\n\tfontsize = 18"
            digraph += u'\n\tfontname="Ubuntu"'
        digraph += u"\n}"
        return digraph

    @classmethod
    def show_dr_blueprint(cls, dr_blueprint: Blueprint) -> Optional[DisplayGraphviz]:
        """ Visualize a DataRobot Blueprint object. """
        chart = dr_blueprint.get_chart()
        return Visualize.show(
            Visualize.to_graphviz_string(
                chart.nodes, chart.edges, graph_name=dr_blueprint.model_type
            )
        )

    @classmethod
    def show(
        cls, graphviz_string: str, as_image: bool = True
    ) -> Union[DisplayGraphviz, None, GraphvizType]:
        """
        Visualize a GraphViz string.

        IPython specific drawing functionality.

        Wraps `as_image`.

        Parameters
        ----------
        graphviz_string: string
            The GraphViz string to render
        as_image: bool (Default=True)
            If enabled, will render as a PNG, otherwise will rely on IPython to display
            the `Source` directly. Rendering as a PNG is preferred as it will auto-resize
            to the size of the rendering space provided, while `Source` will overflow.
        """
        if isinstance(graphviz_string, Blueprint):
            return cls.show_dr_blueprint(graphviz_string)

        try:
            to_render = (
                cls.as_image(graphviz_string, catch_exception=False)
                if as_image
                else cls.as_graphviz(graphviz_string, catch_exception=False)
            )
        except Exception:
            LOGGER.error(FAILED_TO_RENDER_WITH_GRAPHVIZ)
            return PrettyString(graphviz_string)

        try:
            from IPython.display import Image, display

            return display(Image(to_render) if as_image else to_render)
        except Exception:
            LOGGER.error(
                "Failed to display. This method requires an IPython environment. "
                "Reverting to `as_image` or `as_graphviz` instead."
            )
            return to_render

    @classmethod
    def as_image(
        cls, graphviz_string: str, catch_exception=True
    ) -> Optional[bytes] or str:
        """
        Used to render the graph as an image.

        Simply wrap in `IPython.display.Image` to display in a notebook,
        or write it to disk.
        """
        try:
            source = cls.as_graphviz(graphviz_string)
            if isinstance(source, graphviz.Source):
                return source.pipe(format="png")
        except Exception:
            if not catch_exception:
                raise
            LOGGER.error(FAILED_TO_RENDER_WITH_GRAPHVIZ)
        return graphviz_string

    @classmethod
    def as_graphviz(cls, graphviz_string: str, catch_exception=True) -> GraphvizType:
        """
        Used to render the graph form of the blueprint using matplotlib.
        """
        try:
            import graphviz

            return graphviz.Source(graphviz_string)
        except Exception:
            if not catch_exception:
                raise
            LOGGER.error(FAILED_TO_RENDER_WITH_GRAPHVIZ)
            return graphviz_string
