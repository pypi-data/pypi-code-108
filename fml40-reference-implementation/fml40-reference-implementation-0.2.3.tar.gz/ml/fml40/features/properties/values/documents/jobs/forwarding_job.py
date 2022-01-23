from ml.ml40.features.properties.values.documents.jobs.job import Job


class ForwardingJob(Job):
    def __init__(self, namespace="fml40", name="", identifier=""):
        super().__init__(namespace=namespace, name=name, identifier=identifier)
