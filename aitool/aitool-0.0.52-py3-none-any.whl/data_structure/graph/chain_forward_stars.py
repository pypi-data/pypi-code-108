# -*- coding: UTF-8 -*-
# @Time    : 2020/10/26
# @Author  : xiangyuejia@qq.com
from typing import Any, List, Callable


class Node:
    def __init__(self, name: Any, info: Any = None) -> None:
        """
        The *Node* in the graph must have a *name* and can have an additional *info* of any structure.
        The *name* and *info* must support the **=** operation.
        *name* is not the primary of *Node*.
        图谱中的节点Node必须有一个name，并可以带有一个额外的任意结构的info。
        name和info必须支持=操作。
        name并不是Node的标识符。
        :param name: the name of node
        :param info: the additional information
        """
        self.name = name
        self.info = info


class Edge:
    """
    Defines the structure of Edge.
    定义了Edge的结构。
    """
    def __init__(self, end: int, pre: int, name: Any = None, info: Any = None) -> None:
        """
        The *Edge* in the graph must have an *end*, a *pre*, a *name* and can have an additional *info* of any structure.
        The *name* and *info* must support the **=** operation.
        *name* is not the primary key of *Edge*.
        图谱中的边Edge必须有一个end，一个pre，一个name，并可以带有一个额外的任意结构的info。
        name和info必须支持=操作。
        name并不是Edge的主键。
        :param end: the index of end note in
        :param pre:
        :param name:
        :param info:
        """
        self.end = end
        self.pre = pre
        self.name = name
        self.info = info


def is_edge_selected(edge: Edge, select_names: List[Any]):
    if edge.name in select_names:
        return True
    return False


class Piece:
    def __init__(
            self,
            node_begin: Any,
            node_end: Any,
            relation: Any,
            node_begin_info: Any = None,
            node_end_info: Any = None,
            relation_info: Any = None,
    ):
        self.node_begin = node_begin
        self.node_end = node_end
        self.relation = relation
        self.node_begin_info = node_begin_info
        self.node_end_info = node_end_info
        self.relation_info = relation_info


def reform_data(data: List[Any]) -> List[Piece]:
    reformed_data = []
    for d in data:
        if isinstance(d, list):
            if len(d) == 3:
                reformed_data.append(Piece(d[0], d[2], d[1]))
            elif len(d) == 6:
                reformed_data.append(Piece(d[0], d[2], d[1], d[3], d[5], d[4]))
            else:
                raise ValueError
        if isinstance(d, dict):
            if 'node_begin' not in d: raise ValueError
            if 'node_end' not in d: raise ValueError
            if 'relation' not in d: raise ValueError
            if 'node_begin_info' not in d: d['node_begin_info'] = None
            if 'node_end_info' not in d: d['node_end_info'] = None
            if 'relation_info' not in d: d['relation_info'] = None
            reformed_data.append(Piece(d['node_begin'], d['node_end'], d['relation'],
                                       d['node_begin_info'], d['node_end_info'], d['relation_info']))
    return reformed_data


class ChainForwardStars:
    def __init__(self) -> None:
        self.node_name2index: map = {}
        self.index2node_name: map = {}
        self.heads: list = []
        self.nodes: list = []
        self.edges: list = []
        self.node_count: int = 0
        self.edge_count: int = 0

    def get_node_index(self, node_name: int or str, info: Any = None) -> int:
        if node_name in self.node_name2index:
            for index in self.node_name2index[node_name]:
                if self.nodes[index].info == info:
                    return index
            return self.node_name2index[node_name]
        new_node = Node(node_name, info=info)

        if node_name in self.node_name2index:
            self.node_name2index[node_name].append(self.node_count)
        else:
            self.node_name2index[node_name] = [self.node_count]
        self.index2node_name[self.node_count] = node_name
        self.nodes.append(new_node)
        index = self.node_count
        self.node_count += 1
        self.heads.append(-1)
        return index

    def add_triple(
            self,
            node_begin_name: Any,
            node_end_name: Any,
            relation_name: Any,
            node_begin_info: Any = None,
            node_end_info: Any = None,
            relation_info: Any = None,
    ) -> None:
        index_begin = self.get_node_index(node_begin_name, info=node_begin_info)
        index_end = self.get_node_index(node_end_name, info=node_end_info)

        edge = Edge(index_end, self.heads[index_begin], name=relation_name, info=relation_info)
        self.edges.append(edge)
        self.heads[index_begin] = self.edge_count
        self.edge_count += 1

    def built(self, data: list) -> None:
        for piece in data:
            self.add_triple(
                piece.node_begin,
                piece.node_end,
                piece.relation,
                piece.node_begin_info,
                piece.node_end_info,
                piece.relation_info
            )

    def print(self) -> str:
        out_print = ''
        for i in range(self.node_count):
            out_print += ' #{}'.format(self.index2node_name[i])
            p = self.heads[i]
            while p != -1:
                out_print += '->{}'.format(self.index2node_name[self.edges[p].end])
                p = self.edges[p].pre
        return out_print.lstrip()

    def clear(self):
        self.__init__()

    def get_out_edges(self, node_index: int, index_format=True) -> List:
        out = []
        edge_index = self.heads[node_index]
        while edge_index != -1:
            if index_format:
                out.append(edge_index)
            else:
                out.append(self.edges[edge_index])
            edge_index = self.edges[edge_index].pre
        return out

    def get_all_in_neighbors(self, index_format=True) -> dict:
        out = dict()
        for i in range(self.node_count):
            p = self.heads[i]
            while p != -1:
                end_node_id = self.edges[p].end
                if index_format:
                    if end_node_id not in out:
                        out[end_node_id] = [[p, i]]
                    else:
                        out[end_node_id].append([p, i])
                else:
                    end_node = self.nodes[end_node_id]
                    begin_node = self.nodes[i]
                    if end_node not in out:
                        out[end_node] = [[self.edges[p], begin_node]]
                    else:
                        out[end_node].append([self.edges[p], begin_node])
                p = self.edges[p].pre
            if index_format:
                for j in range(self.node_count):
                    if j not in out:
                        out[j] = []
            else:
                for j in self.nodes:
                    if j not in out:
                        out[j] = []
        return out

    def get_descendants(
            self,
            node_index: int,
            edge_limit: list = None,
            edge_select: Callable = is_edge_selected,
            index_format=True
    ) -> set:
        out = set()
        visited = set()
        search_node_list = [node_index]
        while search_node_list:
            edge_index = self.heads[search_node_list[-1]]
            visited.add(edge_index)
            search_node_list = search_node_list[:-1]

            while edge_index != -1:
                if edge_limit is None or edge_select(self.edges[edge_index], edge_limit):
                    if index_format:
                        out.add(self.edges[edge_index].end)
                    else:
                        out.add(self.nodes[self.edges[edge_index].end])
                    edge_index = self.edges[edge_index].pre
                    if self.edges[edge_index].end not in visited:
                        search_node_list.append(self.edges[edge_index].end)
        return out

    def iter_nodes(self, raw=False):
        for i in range(self.node_count):
            if raw:
                out = {
                    'node_name': i,
                    'node_edge': [],
                }
            else:
                out = {
                    'node_name': self.index2node_name[i],
                    'node_edge': [],
                }
            p = self.heads[i]
            while p != -1:
                if raw:
                    out['node_edge'].append([
                        p,
                        self.edges[p].end,
                    ])
                else:
                    out['node_edge'].append([
                        self.edges[p].name,
                        self.index2node_name[self.edges[p].end],
                    ])
                p = self.edges[p].pre
            yield out


if __name__ == '__main__':
    test_case_1 = [
        [1, '1', 2],
        [2, '2', 3],
        [3, '3', 4],
        [1, '4', 3],
        [4, '5', 1],
        [1, '6', 5],
        [4, '7', 5],
        ]

    test_case_2 = [
        ['n1', 'r1', 'n2', {'kind': 'dis'}, {'kind': 'sim', 'weight': 0.92}, {'kind': 'dis'}],
        ['n2', 'r3', 'n4', {'kind': 'dis'}, {'kind': 'dif', 'id': 1}, {'kind': 'dis'}],
        ['n2', 'r2', 'n3', {'kind': 'dis'}, {'kind': 'has', 'id': 2}, {'kind': 'ato'}],
        ['n1', 'r4', 'n4', {'kind': 'dis'}, {'kind': 'dif', 'id': 3}, {'kind': 'dis'}],
    ]

    test_case_3 = [
        {'node_begin':1, 'node_end':2, 'relation':1},
        {'node_begin':2, 'node_end':3, 'relation':2},
        {'node_begin':3, 'node_end':4, 'relation':3},
        {'node_begin':1, 'node_end':3, 'relation':4},
        {'node_begin':4, 'node_end':1, 'relation':5},
        {'node_begin':1, 'node_end':5, 'relation':6},
        {'node_begin':4, 'node_end':5, 'relation':7},
    ]

    cfs = ChainForwardStars()
    cfs.built(reform_data(test_case_1))
    assert cfs.print() == '#1->5->3->2 #2->3 #3->4 #4->5->1 #5'
    print('ChainForwardStars has passed the unit test: test_case_1.')

    cfs.clear()
    cfs.built(reform_data(test_case_2))
    assert cfs.print() == '#n1->n4->n2 #n2->n3->n4 #n4 #n3'
    print('ChainForwardStars has passed the unit test: test_case_2.')

    cfs.clear()
    cfs.built(reform_data(test_case_3))
    assert cfs.print() == '#1->5->3->2 #2->3 #3->4 #4->5->1 #5'
    print('ChainForwardStars has passed the unit test: test_case_3.')
