"""Class for handling zotero.sqlite database connection, queries, and visualization"""
# pylint: disable=too-few-public-methods,too-many-locals
import os
import sqlite3
from sys import platform
from itertools import combinations, product
import pandas as pd
import networkx as nx


class DB:
    """
    Interface layer for zotero.sqlite database.
    Relies on the assumption that the entire database is small enough
    to load into memory without issue.

    Tables are loaded from disk the first time they are accessed.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or guess_db_path()
        validate_db_path(self.db_path)

        self._conn = sqlite3.connect(self.db_path)
        self._data = {}

        tables_query = \
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        table_names = self.query_df(tables_query).T.values.tolist()[0]
        self.tables = {n: self.query_table_columns(n) for n in table_names}

        collection_names_query = \
            "SELECT distinct collectionName FROM collections"
        self.collection_names = self.query_df(
            collection_names_query).T.values.tolist()[0]

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        return self._data.get(key, self.load_table(key))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._conn is not None:
            self.close()

    def close(self):
        """Close database connection"""
        self._conn.close()

    def load_table(self, name: str) -> pd.DataFrame:
        """Load a whole table from disk

        :param name: Name of table
        :type name: str
        :return: Table contents
        :rtype: pd.DataFrame
        """
        if name in self.tables:
            self._data[name] = self.query_df("select * from %s" % name)
        else:
            raise KeyError("No such table: %s" % name)
        return self._data[name]

    def query_df(self, query: str) -> pd.DataFrame:
        """Return the result of a query as a DataFrame

        :param query: String containing SQL query
        :type query: str
        :return: DataFrame of result
        :rtype: pd.DataFrame
        """

        table = self._conn.cursor().execute(query)  # str sanitization via cursor
        cols = [x[0] for x in table.description]
        df = pd.DataFrame(zip(*table), index=cols).transpose()
        return df

    def query_table_columns(self, name: str) -> list:
        """Get list of column names for a table

        :param name: Name of table
        :type name: str
        :return: List of columns
        :rtype: list
        """
        query = f"PRAGMA table_info('{name}')"
        cols = self.query_df(query)["name"].values.tolist()
        return cols

    def build_creator_graph(self, collection: str) -> nx.MultiGraph:
        """Build a graph data structure of collaborative work

        :param collection: Zotero Collection name
        :type collection: str
        :return: MultiGraph with Creator objects as nodes and 1 edge per collaboration
        :rtype: nx.MultiGraph
        """
        # Get data
        collection_id = self.query_df(
            "select collectionID from collections where collectionName = '%s'" % collection)["collectionID"].values[0]
        collection_items = self.query_df(
            "select distinct itemID from collectionItems where collectionID = %d" % collection_id)["itemID"].values
        creators_table = self["creators"]
        initials = [(x + " ")[0] for x in creators_table["firstName"].values]
        creator_names = [initial + ". " + lastname for initial,
                         lastname in zip(initials, creators_table["lastName"])]
        creator_map = {i: Creator(name=n, creator_id=i) for i, n in zip(
            creators_table["creatorID"], creator_names)}

        # Build graph
        g = nx.MultiGraph()
        for item_id in collection_items:
            item_creator_ids = self.query_df(
                "select creatorID from itemCreators where itemID = %d" % item_id)["creatorID"].values
            item_creators = [creator_map[i] for i in item_creator_ids]
            for c in item_creators:
                c.count += 1
                if c not in g.nodes:
                    g.add_node(c)
            g.add_edges_from(combinations(item_creators, 2))

        # Contract nodes with duplicate names
        duplicate_names = {n for n in creator_names
                           if creator_names.count(n) > 1}
        for name in duplicate_names:
            nodes = [n for n in g.nodes if str(n) == name]
            for u, v in product(nodes[0:1], nodes[1:]):
                u += v  # Combine stats
                g = nx.contracted_nodes(g, u, v, self_loops=False)
        return g


class Creator:
    """Content-creator data for use as a graph node"""

    def __init__(self, name, creator_id):
        self.name = name
        self.id = creator_id
        self.count = 0
        self.contracted_ids = []

    def __str__(self):  # For labeling in networkx embedding
        return self.name

    def __add__(self, other):  # For contracting duplicates
        self.count += other.count
        self.contracted_ids.append(other.id)
        return self


def guess_db_path():
    """Guess location of zotero.sqlite based on operating system"""
    if any([x in platform.lower() for x in ["linux", "darwin"]]):
        db_path = os.path.join(os.path.expanduser("~"),
                               "Zotero", "zotero.sqlite")
    elif "windows" in platform.lower():
        db_path = os.path.join(os.path.expandvars("% HOMEPATH %"),
                               "Zotero", "zotero.sqlite")
    else:
        error_string = "Unable to resolve database location on OS %s ." % platform
        error_string += "\nYou will need to supply the path as an argument."
        raise NotImplementedError(error_string)

    return db_path


def validate_db_path(db_path: str):
    """Check if the database file exists

    :param db_path: Path to zotero.sqlite
    :type db_path: str
    :raises FileNotFoundError: Raised if database does not exist
    """
    if not os.path.isfile(db_path):
        error_string = "Did not locate zotero.sqlite database at %s ." % db_path
        error_string += "\nYou will need to supply the path as an argument."
        raise FileNotFoundError(error_string)
