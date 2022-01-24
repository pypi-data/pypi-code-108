from enum import Enum

from efemarai.dataset import Dataset
from efemarai.domain import Domain
from efemarai.model import Model, ModelParams, ModelRepository


class ProblemType(Enum):
    Classification = "Classification"
    ObjectDetection = "ObjectDetection"
    SemanticSegmentation = "SemanticSegmentation"


class Project:
    @staticmethod
    def create(session, name, description, problem_type):
        if name is None or problem_type not in ProblemType:
            return None

        response = session._put(
            "api/project",
            json={
                "name": name,
                "description": description,
                "problem_type": problem_type,
            },
        )
        return Project(self, response["id"], name, description, problem_type)

    def __init__(self, session, id, name, description, problem_type):
        self._session = session
        self.id = id
        self.name = name
        self.description = description
        self.problem_type = ProblemType[problem_type]

    def __repr__(self):
        res = "{}("
        res += "\n  id={}"
        res += "\n  name={}"
        res += "\n  description={}"
        res += "\n  problem_type={}"
        res += "\n)"
        return res.format(
            self.__module__ + "." + self.__class__.__name__,
            repr(self.id),
            repr(self.name),
            repr(self.description),
            repr(self.problem_type),
        )

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

    def run_stress_test(self, name, model, dataset, domain):
        if isinstance(model, str):
            model = self.model(model)

        if isinstance(dataset, str):
            dataset = self.dataset(dataset)

        if isinstance(domain, str):
            domain = self.domain(domain)

        response = self._session._post(
            "api/runTest",
            json={
                "name": name,
                "model": model.id,
                "dataset": dataset.id,
                "domain": domain.id,
                "project": self.id,
                "samples_per_run": 10,
                "run_count": 2,
                "concurrent_runs": 1,
            },
        )
        return response["id"]

    def delete(self):
        # TODO: add endpoint for deleting a project

        for domain in self.domains:
            domain.delete()

        for dataset in self.datasets:
            dataset.delete()

        for model in self.models:
            model.delete()
