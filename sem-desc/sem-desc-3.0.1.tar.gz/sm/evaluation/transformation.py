from typing import Set
from sm.outputs.semantic_model import SemanticModel, ClassNode


class SemModelTransformation:
    @classmethod
    def replace_class_nodes_by_subject_columns(
        cls, sm: SemanticModel, id_props: Set[str]
    ):
        """Replace a class node by its subject column (if have). One class node must have maximum one subject column"""
        rm_nodes = []
        for cnode in sm.iter_nodes():
            if isinstance(cnode, ClassNode):
                inedges = sm.in_edges(cnode.id)
                outedges = sm.out_edges(cnode.id)
                id_edges = [
                    outedge for outedge in outedges if outedge.abs_uri in id_props
                ]
                if len(id_edges) == 0:
                    continue
                if len(id_edges) > 1:
                    raise Exception(
                        f"Assuming one class node only has one subject column. Node: {cnode.id} have {len(outedges)} subject columns: {outedges}"
                    )

                id_edge = id_edges[0]

                # update edges
                for inedge in inedges:
                    sm.remove_edge(inedge.id)
                    inedge.target = id_edge.target
                    sm.add_edge(inedge)
                for outedge in outedges:
                    sm.remove_edge(outedge.id)
                    outedge.source = id_edge.target
                    sm.add_edge(outedge)
                sm.remove_edge(id_edge.id)
                rm_nodes.append(cnode.id)
        for uid in rm_nodes:
            sm.remove_node(uid)

    @classmethod
    def remove_isolated_nodes(cls, sm: SemanticModel):
        rm_nodes = []
        for n in sm.iter_nodes():
            if sm.degree(n.id) == 0:
                rm_nodes.append(n.id)
        for uid in rm_nodes:
            sm.remove_node(uid)
