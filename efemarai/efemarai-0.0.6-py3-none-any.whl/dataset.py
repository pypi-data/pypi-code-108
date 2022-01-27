class Dataset:
    @staticmethod
    def create(
        project,
        name,
        format,
        stage,
        data_url,
        annotations_url,
        credentials,
        upload,
        num_datapoints,
    ):
        if name is None or data_url is None or annotations_url is None:
            return None

        if format is not None:
            assert format in ("COCO",)
        else:
            format = "COCO"

        if stage is not None:
            assert stage in ("train", "validation", "test")
        else:
            stage = "test"

        session = project._session

        response = session._put(
            f"api/dataset/undefined/{project.id}",
            json={
                "name": name,
                "stage": stage,
                "data_url": data_url,
                "annotations_url": annotations_url,
                "access_token": credentials,
                "upload": upload,
                "projectId": project.id,
                "num_samples": num_datapoints,
            },
        )
        dataset_id = response["id"]

        if upload:
            endpoint = f"api/dataset/{dataset_id}/upload"
            session._upload(annotations_url, endpoint)
            session._upload(data_url, endpoint)
            session._post(endpoint, json={"num_samples": num_datapoints})

        return Dataset(
            project, dataset_id, name, format, stage, data_url, annotations_url
        )

    def __init__(self, project, id, name, format, stage, data_url, annotations_url):
        self.project = project
        self.id = id
        self.name = name
        self.format = format
        self.stage = stage
        self.data_url = data_url
        self.annotations_url = annotations_url

    def __repr__(self):
        res = f"{self.__module__}.{self.__class__.__name__}("
        res += f"\n  id={self.id}"
        res += f"\n  name={self.name}"
        res += f"\n  format={self.format}"
        res += f"\n  stage={self.stage}"
        res += f"\n  data_url={self.data_url}"
        res += f"\n  annotations_url={self.annotations_url}"
        res += f"\n)"
        return res

    def delete(self):
        self.project._session._delete(f"api/dataset/{self.id}/{self.project.id}")
