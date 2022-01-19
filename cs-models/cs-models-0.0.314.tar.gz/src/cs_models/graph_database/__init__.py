import os
from neo4j import GraphDatabase

uri = os.getenv("GRAPH_DB_URI", "bolt://localhost:7687")
user = os.getenv("GRAPH_DB_USER", "neo4j")
password = os.getenv("GRAPH_DB_PASSWORD", "mindgram12")


def create_driver(uri, user, password):

    def resolver(address):
        host, port = address
        if host == "x.example.com":
            yield "a.example.com", port
            yield "b.example.com", port
            yield "c.example.com", port
        else:
            yield host, port

    return GraphDatabase.driver(uri, auth=(user, password), resolver=resolver)


driver = create_driver(uri, user, password)
