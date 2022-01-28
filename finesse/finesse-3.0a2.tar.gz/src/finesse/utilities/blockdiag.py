import sys
import io
import networkx
import re

from finesse.components.node import NodeType
from finesse.components import Connector, SignalGenerator, Wire

from functools import reduce


def dfs_edges_to_paths(a, b):
    if b[-1] in ("forward", "nontree"):
        if b[0] == b[1]:
            return a

        if len(a) == 0:
            a.append([b[0]])
        if b[0] != a[-1][-1]:
            a.append([b[0]])

        a[-1].append(b[1])

    return a


def get_loops_network(model):
    """Reduces a Model network down to an electronic loop network.

    This can be used for drawing diagrams or computing loops if needed.
    """
    net = networkx.digraph.DiGraph()

    is_electric = lambda x: all(p.type == NodeType.ELECTRICAL for p in x.ports)
    in_sig = set()
    out_optics = set()
    in_optics = set()

    for el in model.elements.values():
        if isinstance(el, Connector):
            conn_elec_ports = tuple(
                p.type == NodeType.ELECTRICAL for p in el.ports if p.is_connected
            )
            if len(conn_elec_ports) > 1 and all(conn_elec_ports):
                if isinstance(el, SignalGenerator):
                    if is_electric(el.node.component):
                        OUT = el.node.port.full_name
                    else:
                        OUT = "__in_optics_" + el.node.port.full_name
                        in_optics.add(OUT)

                    in_sig.add(el.name)
                    net.add_edge(
                        el.name,
                        OUT,
                        owner=el,
                        port_A=None,
                        port_B=el.node.port.full_name,
                    )
                elif isinstance(el, Wire):
                    A_electric = is_electric(el.nodeA.component)
                    B_electric = is_electric(el.nodeA.component)

                    if A_electric:
                        IN = el.nodeA.component.name
                    else:
                        IN = "__out_optics_" + el.nodeA.port_name
                        out_optics.add(IN)

                    if B_electric:
                        OUT = el.nodeB.component.name
                    else:
                        OUT = "__in_optics_" + el.nodeB.port_name
                        in_optics.add(OUT)

                    net.add_edge(
                        IN,
                        OUT,
                        owner=el,
                        port_A=el.nodeA.port_name,
                        port_B=el.nodeB.port_name,
                    )
                else:
                    net.add_node(el.name, owner=el)

    # Change where multiple edges are combined into a summing node
    for n in tuple(net.nodes):
        in_edges = tuple(net.in_edges(n))
        if len(in_edges) > 1:
            nsum = "__sum_" + n
            net.add_node(nsum)
            net.add_edge(nsum, n)
            for edge in in_edges:
                a, b = edge
                net.add_edge(a, nsum)
                net.remove_edge(a, b)

    # optic_couplings = []

    # Could add in optic-optic coupling if needed
    # for o in set(in_optics):
    #     for i in set(out_optics):
    #         optic_couplings.append((o,i))
    #         net.add_edge(o, i)
    return net, in_optics, out_optics, in_sig


def get_loops_blockdiag_code(kat, f=sys.stdout):
    re1 = re.compile(
        "(?P<sum>__sum_)*(?:__(?P<optics_dir>in|out)_optics_)*(?P<name>.*)"
    )

    net, in_optics, out_optics, in_sig = get_loops_network(kat)
    print("{", file=f)
    print("default_shape = roundedbox;", file=f)
    for n in net.nodes:
        res = re1.match(n).groupdict()
        if res is None:
            raise Exception(f"Unexpected {n}")
        if res["sum"] is not None:
            print(f"{n} [ shape = circle , label='+', width=20, height=20];", file=f)
        elif res["optics_dir"] == "out":
            print(f"{n} [ shape = beginpoint, label = '{res['name']}'];", file=f)
        elif res["optics_dir"] == "in":
            print(f"{n} [ shape = endpoint, label = '{res['name']}'];", file=f)
        else:
            print(f"{n} [ width = {40} , label = '{res['name']}'];", file=f)

    print(
        f"""
    # Inputs into the optics model
    group {{
        {" ".join(in_optics)}
    }}
    # Outputs into the optics model
    group {{
        {" ".join(out_optics)}
    }}
    """,
        file=f,
    )
    for o in set(out_optics) | set(in_sig):
        paths = reduce(
            dfs_edges_to_paths, networkx.dfs_labeled_edges(net, source=o), []
        )
        for p in paths:
            print(" -> ".join(p) + ";", file=f)

    print("}", file=f)


def display_blockdiag_output(cell, output_format="png", return_svg=False):
    import tempfile
    import blockdiag.command
    from IPython.core.displaypub import publish_display_data

    command = blockdiag.command
    mime_type = {
        "png": "image/png",
        "svg": "image/svg+xml",
    }

    with tempfile.NamedTemporaryFile(suffix=".diag", delete=True) as f:
        cell += "\n"
        f.write(cell.encode("utf-8"))
        f.flush()
        with tempfile.NamedTemporaryFile(suffix="." + output_format, delete=True) as p:
            args = ["-T", output_format, "-o", p.name, f.name]
            command.main(args=args)
            p.seek(0)
            data = p.read()

            if output_format in ["svg"]:
                data = data.decode("utf-8")

            publish_display_data({mime_type.get(output_format, "text/plain"): data})

    if return_svg:
        return data


def print_loops_blockdiag(kat):
    get_loops_blockdiag_code(kat)


def display_loops_blockdiag(kat):
    f = io.StringIO()
    get_loops_blockdiag_code(kat, f)
    display_blockdiag_output(f.getvalue())
