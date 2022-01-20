from neo4j import GraphDatabase, Neo4jDriver

class Neo4JObject:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def querryFun(self,tx,q):
        tx.run(q)


    def run(self,querry):
        with self.driver.session() as session:
            session.write_transaction(self.querryFun, querry)
