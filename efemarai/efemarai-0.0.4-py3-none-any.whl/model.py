class ModelRepository:
    def __init__(self, url, branch=None, access_token=None):
        self.url = url
        self.branch = branch if branch is not None else "main"
        self.access_token = access_token

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n      url={self.url}"
        res += f"\n      branch={self.branch}"
        res += "\n    )"
        return res


class ModelParams:
    def __init__(self, url, upload=False, credentials=None):
        self.url = url
        self.upload = upload
        self.credentials = credentials

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n      url={self.url}"
        res += f"\n    )"
        return res


class Model:
    @staticmethod
    def create(project, name, repository, params):
        if name is None or repository is None or params is None:
            return None

        repository = ModelRepository(**repository)
        params = ModelParams(**params)

        session = project._session
        response = session._put(
            f"api/model/undefined/{project.id}",
            json={
                "name": name,
                "repository_url": repository.url,
                "branch": repository.branch,
                "access_token": repository.access_token,
                "model_url": params.url,
                "upload_params": params.upload,
                "projectId": project.id,
            },
        )
        model_id = response["id"]

        if params.upload:
            session._upload(params.url, f"api/model/{model_id}/upload")

        return Model(project, model_id, name, repository, params)

    def __init__(self, project, id, name, repository, params):
        self.project = project
        self.id = id
        self.name = name
        self.repository = repository
        self.params = params

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  repository={self.repository}"
        res += f"\n  params={self.params}"
        res += f"\n)"
        return res

    def delete(self):
        self.project._session._delete(f"api/model/{self.id}/{self.project.id}")
