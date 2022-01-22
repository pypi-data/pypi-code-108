#!/usr/bin/env python3
from quickspider.core.leafpool import LeafPool
import logging


class Controller:
    def __init__(self, header):
        self.logger = logging.getLogger("Controller")
        self.logger.setLevel(logging.DEBUG)
        self._header = header
        self._leaf_pool = LeafPool(header)
        self._all_nodes = self._scan_all_nodes()
        self._register_node()
        self._lookup_collect = []
        self._status = "ACTIVATED"

    def __repr__(self):
        return f"{self._all_nodes}"

    def _init_nodes(self):
        self.logger.debug("init nodes")
        for node in self._all_nodes:
            node.init()

    def _post_nodes(self):
        self.logger.debug("post nodes")
        for node in self._all_nodes:
            node.post()

    def _register_node(self):
        self.logger.debug("register nodes")
        for node in self._all_nodes:
            node._controller = self

    def walk(self, node):
        if not node:
            return
        self.logger.debug("scan nodes")
        for child in node._child:
            self.walk(child)

    def _scan_all_nodes(self):
        nodes = []

        def walk(node):
            if not node:
                return
            nodes.append(node)
            for child in node._child:
                walk(child)

        walk(self._header)
        return nodes

    def _clear_lookup_collect(self):
        self.logger.debug("clear lookup_collect")
        self._lookup_collect = []

    @staticmethod
    def activate_rec_without_leaf(node):
        if node._is_leaf():
            return
        if node.activate():
            for child in node._child:
                Controller.activate_rec_without_leaf(child)
        return

    def activate(self):
        self.logger.debug("activate")
        if self._lookup_collect:
            for node in self._lookup_collect:
                Controller.activate_rec_without_leaf(node)
            self._clear_lookup_collect()
            return
        Controller.activate_rec_without_leaf(self._header[0])

    def loop(self):
        self.logger.debug("loop")
        self._leaf_pool.loop()

    def start(self):
        self.logger.debug("start")
        self._init_nodes()
        try:
            while True:
                # self.walk(self._header)
                self.activate()
                self.loop()
                self.lookup()
                if self._status == "FINISHED":
                    break
        except Exception as e:
            print(e)
        finally:
            self._post_nodes()

    def lookup(self):
        self.logger.debug("lookup")
        self._lookup_collect = []
        for leaf in self._leaf_pool:
            self._lookup(leaf)

    def _lookup(self, node):
        if not node:
            return
        self.logger.debug(f"[LOOKUP] -> {node._name}")
        if node._is_header():
            self._status = "FINISHED"
            return
        if node in self._lookup_collect:
            return
        if node._is_leaf():
            self._lookup(node._parent)
            return
        _not_empty = node._not_empty()
        if _not_empty:
            self._lookup_collect.append(node)
        else:
            self._lookup(node._parent)
            return
