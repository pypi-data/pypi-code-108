class ModelRepository:
    def __init__(self, url, branch=None, access_token=None):
        self.url = url
        self.branch = branch if branch is not None else "main"
        self.access_token = access_token

    def __repr__(self):
        res = "{}("
        res += "\n      url={}"
        res += "\n      branch={}"
        res += "\n    )"
        return res.format(
            self.__module__ + "." + self.__class__.__name__,
            repr(self.url),
            repr(self.branch),
        )


class ModelParams:
    def __init__(self, url, upload=False, credentials=None):
        self.url = url
        self.upload = upload
        self.credentials = credentials

    def __repr__(self):
        res = "{}("
        res += "\n      url={}"
        res += "\n    )"
        return res.format(
            self.__module__ + "." + self.__class__.__name__, repr(self.url),
        )


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
        res = "{}("
        res += "\n  id={}"
        res += "\n  name={}"
        res += "\n  repository={}"
        res += "\n  params={}"
        res += "\n)"
        return res.format(
            self.__module__ + "." + self.__class__.__name__,
            repr(self.id),
            repr(self.name),
            repr(self.repository),
            repr(self.params),
        )

    def delete(self):
        self.project._session._delete(f"api/model/{self.id}/{self.project.id}")
