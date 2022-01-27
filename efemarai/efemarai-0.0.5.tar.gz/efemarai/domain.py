from bson.objectid import ObjectId

class Domain:
    @staticmethod
    def create(project, name, transformations, graph):
        if name is None or name is None or transformations is None or graph is None:
            return None

        session = project._session
        response = session._put(
            f"api/domain/undefined/{project.id}",
            json={"name": name, "projectId": project.id},
        )
        domain_id = response["id"]

        operators = {
            operator["name"]: operator
            for operator in session._get("api/getDefaultOperators")
        }

        lookup_transformation_id = {}
        domain_transformations = []
        for transformation in transformations:
            tf = {
                "_id": {"$oid": str(ObjectId())},
                "name": transformation["name"],
                "operator": operators[transformation["operator"]]["_id"]["$oid"],
                "axes": transformation["axes"],
                "category": operators[transformation["operator"]]["category"],
            }
            lookup_transformation_id[tf["name"]] = tf["_id"]["$oid"]
            domain_transformations.append(tf)

        domain_graph = []
        for a, b in graph:
            domain_graph.append(
                {
                    "previous": lookup_transformation_id[a],
                    "next": lookup_transformation_id[b],
                }
            )

        session._post(
            f"api/saveDomainFlow",
            json={
                "_id": domain_id,
                "transformations": domain_transformations,
                "graph": domain_graph,
            },
        )

        return Domain(project, domain_id, name, domain_transformations, domain_graph)

    def __init__(self, project, id, name, transformations, graph):
        self.project = project
        self.id = id
        self.name = name
        self.transformations = transformations
        self.graph = graph

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  transformations={self.transformations}"
        res += f"\n  graph={self.graph}"
        res += f"\n)"
        return res

    def delete(self):
        self.project._session._delete(f"api/domain/{self.id}/{self.project.id}")
