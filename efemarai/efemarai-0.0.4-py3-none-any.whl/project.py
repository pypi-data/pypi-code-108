from efemarai.dataset import Dataset
from efemarai.domain import Domain
from efemarai.model import Model, ModelParams, ModelRepository
from efemarai.problem_type import ProblemType
from efemarai.stress_test import StressTest


class Project:
    @staticmethod
    def create(session, name, description, problem_type):
        if name is None or not ProblemType.has(problem_type):
            return None

        response = session._put(
            "api/project",
            json={
                "name": name,
                "description": description,
                "problem_type": problem_type,
            },
        )
        return Project(session, response["id"], name, description, problem_type)

    def __init__(self, session, id, name, description, problem_type):
        self._session = session
        self.id = id
        self.name = name
        self.description = description
        self.problem_type = ProblemType(problem_type)

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  description={self.description}"
        res += f"\n  problem_type={self.problem_type}"
        res += f"\n)"
        return res

    @property
    def models(self):
        return [
            Model(
                self,
                model["id"],
                model["name"],
                repository=ModelRepository(
                    url=model["repository_url"],
                    branch=model["branch"],
                    access_token=model["access_token"],
                ),
                params=ModelParams(url=model["model_url"]),
            )
            for model in self._session._get(f"api/models/{self.id}")
        ]

    def model(self, name, repository=None, params=None):
        model = next((m for m in self.models if m.name == name), None)

        if model is None:
            model = Model.create(self, name, repository, params)

        return model

    @property
    def datasets(self):
        return [
            Dataset(
                self,
                dataset["id"],
                dataset["name"],
                dataset["format"],
                dataset["stage"],
                dataset["data_url"],
                dataset["annotations_url"],
            )
            for dataset in self._session._get(f"api/datasets/{self.id}")
        ]

    def dataset(
        self,
        name,
        format=None,
        stage=None,
        data_url=None,
        annotations_url=None,
        credentials=None,
        upload=False,
        num_datapoints=None,
    ):
        dataset = next((d for d in self.datasets if d.name == name), None)

        if dataset is None:
            dataset = Dataset.create(
                self,
                name,
                format,
                stage,
                data_url,
                annotations_url,
                credentials,
                upload,
                num_datapoints,
            )

        return dataset

    @property
    def domains(self):
        return [
            Domain(
                self,
                domain["id"],
                domain["name"],
                domain["transformations"],
                domain["graph"],
            )
            for domain in self._session._get(f"api/domains/{self.id}")
        ]

    def domain(self, name, transformations=None, graph=None):
        domain = next((d for d in self.domains if d.name == name), None)

        if domain is None:
            domain = Domain.create(self, name, transformations, graph)

        return domain

    @property
    def stress_tests(self):
        return [
            StressTest(
                self,
                test["id"],
                test["name"],
                test["model"]["$oid"],
                test["domain"]["$oid"],
                test["original_dataset"]["$oid"],
                test["states"][-1]["name"],
            )
            for test in self._session._get(f"api/getRuns/{self.id}")["objects"]
        ]

    def stress_test(
        self,
        name,
        model=None,
        domain=None,
        dataset=None,
        num_samples=None,
        num_runs=None,
        concurrent_runs=None,
    ):
        test = next((t for t in self.stress_tests if t.name == name), None)

        if test is None:
            test = StressTest.create(
                self,
                name,
                model,
                domain,
                dataset,
                num_samples,
                num_runs,
                concurrent_runs,
            )

        return test

    def _delete(self):
        for domain in self.domains:
            domain.delete()

        for dataset in self.datasets:
            dataset.delete()

        for model in self.models:
            model.delete()
