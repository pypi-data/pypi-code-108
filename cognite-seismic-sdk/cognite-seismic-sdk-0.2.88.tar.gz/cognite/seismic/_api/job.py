# Copyright 2019 Cognite AS

import os

from cognite.seismic._api.api import API

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos.ingest_service_messages_pb2 import StatusRequest


class JobAPI(API):
    def __init__(self, ingestion):
        super().__init__(ingestion=ingestion)

    def status(self, job_id: str = None, file_id: str = None, seismicstore_id: int = None):
        """Get the status of an ingestion job

        Args:
            job_id (str): The id of the job
            file_id (str): The id of the file being ingested
            seismicstore_id (int): The id of the seismicstore assigned to the file as part of ingestion

        Returns:
            The status of the job, including latest step performed
        """
        if job_id is not None:
            request = StatusRequest(job_id=job_id)
        elif file_id is not None:
            request = StatusRequest(file_id=file_id)
        elif seismicstore_id is not None:
            request = StatusRequest(seismicstore_id=seismicstore_id)
        else:
            raise Exception("One of 'job_id', 'file_id', 'seismicstore_id' args must be specified")

        return self.ingestion.Status(request=request)
