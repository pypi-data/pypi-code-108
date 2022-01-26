from typing import List, Union, Optional, Dict

from datalogue.models.permission import (
    Permission,
    Scope,
    SharePermission,
    ObjectType,
    UnsharePermission,
)
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.pipeline import *
from datalogue.models.pipeline_behavior import *
from datalogue.models.job import Job
from datalogue.errors import DtlError, _invalid_pagination_params
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dateutil.tz import UTC
from datalogue.dtl_utils import _parse_list, ResponseStream
from pyarrow import csv, Table

from datalogue.models.pipeline_template import PipelineTemplate
from datalogue.models.datastore import VoidDef
from datalogue.clients.datastore import DatastoreClient


class PipelineClient:
    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"
        self.template = _TemplateClient(http_client)

    def create(self, name: str, pipeline_def: PipelineDef, is_resilient: bool = False) -> Union[DtlError, Pipeline]:
        """
        Creates a Pipeline with unique id
        
        :param is_resilient: True if the job of this pipeline will be retried
        :param name: String, a name for your pipeline
        :param pipeline_def: PipelineDef is the definition of the Pipeline
        :return: created Pipeline if successful, DtlError if failed
        """
        payload = {
            "name": str(name),
            "definition": pipeline_def._as_payload(),
            "resilient": is_resilient,
        }

        res = self.http_client.make_authed_request(self.service_uri + "/streams", HttpMethod.POST, payload)

        if isinstance(res, DtlError):
            return DtlError("Encountered an error while creating the pipeline", res)

        return Pipeline._from_payload(res)

    def get(self, pipeline_id: Union[str, UUID]) -> Union[DtlError, Pipeline]:
        """
        Retrieves a Pipeline
        
        :param pipeline_id: id of Pipeline to be retrieved
        :return: Pipeline if successful, DtlError if failed
        """
        uri = f"{self.service_uri}/streams/{str(pipeline_id)}"
        res = self.http_client.execute_authed_request(uri, HttpMethod.GET)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            return Pipeline._from_payload(res.json())
        if res.status_code == 400:
            payload = res.json()
            reason = payload.get("error", payload.get("message"))
            return DtlError(
                f"Encountered an error while getting the pipeline! pipeline_id: {pipeline_id}, reason: {reason}"
            )
        else:
            return self.http_client._handle_status_code(uri, res)

    def update(
        self,
        pipeline_id: Union[str, UUID],
        name: Optional[str] = None,
        pipeline_def: Optional[PipelineDef] = None,
        is_resilient: Optional[bool] = None,
    ) -> Union[DtlError, Pipeline]:
        """
        Updates the Pipeline's configuration

        :param pipeline_id: id of Pipeline to update
        :param name: updated name of Pipeline (Optional)
        :param pipeline_def: updated definition of Pipeline (Optional)
        :return: updated Pipeline if successful, DtlError if failed
        """
        payload = {}

        if name is not None:
            payload["name"] = str(name)

        if pipeline_def is not None:
            payload["definition"] = pipeline_def._as_payload()

        if is_resilient is not None:
            payload["resilient"] = is_resilient

        res = self.http_client.make_authed_request(
            f"{self.service_uri}/streams/{str(pipeline_id)}", HttpMethod.POST, payload
        )

        if isinstance(res, DtlError):
            return DtlError(f"Encountered an error while updating the pipeline for {pipeline_id}", res,)

        return Pipeline._from_payload(res)

    def delete(self, pipeline_id: Union[str, UUID]) -> Union[DtlError, bool]:
        """
        Deletes all instances of Pipeline

        :param pipeline_id: id of Pipeline to be deleted
        :return: True if successful, DtlError if failed
        """
        uri = f"{self.service_uri}/streams/{str(pipeline_id)}"
        res = self.http_client.execute_authed_request(uri, HttpMethod.DELETE)
        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            return True
        elif res.status_code == 400:
            payload = res.json()
            return DtlError(
                f'Encountered an error while deleting the pipeline! pipeline_id: {pipeline_id}, reason: {payload["error"]}'
            )
        else:
            return self.http_client._handle_status_code(uri, res)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Pipeline]]:
        """
        Retrieves a paginated array of Pipelines

        :param page: page of Pipeline list to return
        :param item_per_page: number of Pipelines to return per page
        :return: Array of Pipelines if successful, DtlError if failed
        """
        params = {"page": str(page), "size": str(item_per_page)}

        res = self.http_client.make_authed_request(f"{self.service_uri}/streams", HttpMethod.GET, params=params)

        if isinstance(res, DtlError):
            return DtlError(f"Encountered an error while listing pipelines", res)

        return _parse_list(Pipeline._from_payload)(res)

    def orchestrate(self, pipeline_id: Union[str, UUID], wait_on: List[Union[str, UUID]] = []) -> Union[DtlError, Job]:
        """
        Orchestrate the running of a pipeline to trigger after the success of one or more separate jobs

        :param :pipeline_id: id of the pipeline to be run
        :param :wait_on: id(s) of jobs which need to successfully finish before the specified pipeline will run.
        Default value is empty string which means if user does not define, there will be no dependencies
        :return: Returns Job object or error
        """
        params = {"wait_on": wait_on}

        res = self.http_client.make_authed_request(
            f"{self.service_uri}/streams/{pipeline_id}/orchestrate", HttpMethod.POST, params=params,
        )

        if isinstance(res, DtlError):
            return res

        jobs = _parse_list(Job._from_payload_v1)(res)
        if isinstance(jobs, DtlError):
            return jobs
        elif len(jobs) == 0:
            return DtlError("Encountered an issue! There should be at least one job!")
        else:
            # API returns main jobs and additional jobs per target to be analyzed once this stream is completed.
            # In SDK, we're returning only the main job to the user
            return jobs[0]

    def schedule(
        self,
        pipeline_id: Union[str, UUID],
        run_date: datetime,
        frequency: Optional[timedelta] = None,
        abort_if_overlong: bool = False,
    ) -> Union[DtlError, Job]:
        """
        Schedules the pipeline to run at the given date

        :param pipeline_id: UUID id of the pipeline to schedule
        :param date: datetime for scheduling
        :param frequency: interval value (e.g float) with period (e.g hours) after which a job will be repeated
        :param abort_if_overlong: if True, avoids running a job cycle if previous cycle is running. (False by default)
        :return: Returns Job object or error
        """
        uri = f"{self.service_uri}/streams/{pipeline_id}/schedule"
        payload = {
            "runDate": run_date.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "abortIfOverlong": abort_if_overlong,
        }
        if frequency is not None:
            payload.update({"intervalInSec": frequency.total_seconds()})
        res = self.http_client.execute_authed_request(uri, HttpMethod.POST, payload)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            jobs = _parse_list(Job._from_payload_v1)(res.json())
            if isinstance(jobs, DtlError):
                return jobs
            elif len(jobs) == 0:
                return DtlError("Encountered an issue! There should be at least one job!")
            else:
                return jobs[0]
        elif res.status_code == 400:
            payload = res.json()
            return DtlError(
                f'Encountered an error while scheduling the pipeline! pipeline_id: {pipeline_id}, reason: {payload["error"]}'
            )
        else:
            return self.http_client._handle_status_code(uri, res)

    def run(self, pipeline_id: Union[str, UUID]) -> Union[DtlError, Job]:
        """
        Runs the pipeline right now

        :param pipeline_id: id of the pipeline to run
        :return: Returns Job object or error
        """

        uri = f"{self.service_uri}/streams/{pipeline_id}/run"

        res = self.http_client.execute_authed_request(uri, HttpMethod.POST)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            jobs = _parse_list(Job._from_payload_v1)(res.json())
            if isinstance(jobs, DtlError):
                return jobs
            elif len(jobs) == 0:
                return DtlError("Encountered an issue! There should be at least one job!")
            else:
                return jobs[0]
        elif res.status_code == 400:
            payload = res.json()
            return DtlError(
                f'Encountered an error while scheduling the pipeline! pipeline_id: {pipeline_id}, reason: {payload["error"]}'
            )
        else:
            return self.http_client._handle_status_code(uri, res)

    # #TODO we need to use sth else than target_id to differentiate definitions
    def preview(self, source_id: Union[str, UUID], transformations: List[Transformation] = [], size: int = 10) -> Union[
        DtlError, Table]:
        """
        Returns the preview of the source data against the transformations applied.
        :param source_id: id for the source dataset
        :param transformations: a list of transformations
        :param size: the size of the output table, in records
        """
        # create a dummy target_ds object
        source_object = DatastoreClient(self.http_client)
        source_ds = source_object.get(source_id)
        target_ds = Datastore("Dummy target datasource object", VoidDef(), datastore_id=uuid4())
        # build pipeline definition for the source data  to be previewed
        pipeline_def = PipelineDef.simple_builder(source_datastore=source_ds,
                                                  transformation_list=transformations,
                                                  destination_datastore=target_ds,
                                                  prepend_structure=False)
        params = {"size": size, "file-format": "Csv", "sample-store-id": str(target_ds.id)}
        res = self.http_client.make_authed_request(
            f"{self.service_uri}/streams/samples",
            HttpMethod.POST,
            body=pipeline_def._as_payload(),
            params=params,
            stream=True,
        )
        if isinstance(res, DtlError):
            return res
        response_stream = ResponseStream(res.iter_content(1024))
        return csv.read_csv(response_stream)

    def templatize(self, pipeline_id: Union[str, UUID]) -> Union[DtlError, PipelineTemplate]:
        """
        Generate a PipelineTemplate with logic matching that of the specified pipeline,
        and with an auto-generated name.
        Once generated, the PipelineTemplate can be tweaked with any automatic or user
        defined-variables as desired, or saved directly to the backend via
        dtl.pipeline.template.create()

        :param pipeline_id: id of the pipeline for which a template is to be generated
        :return: PipelineTemplate object with auto-generated name if successful,
        DtlError otherwise
        """
        uri = f"{self.service_uri}/streams/{pipeline_id}/templatize"

        res = self.http_client.make_authed_request(uri, HttpMethod.POST)

        if isinstance(res, DtlError):
            return res

        else:
            pipeline_name = res.get("streamName")
            template_name = f"Pipeline Template from: {pipeline_name} ({pipeline_id})"
            template_yaml = res.get("templateYaml")
            template_obj = PipelineTemplate(template_name, template_yaml)
            return template_obj

    def update_schedule(
        self,
        pipeline_id: Union[str, UUID],
        run_date: Optional[datetime] = None,
        frequency: Optional[timedelta] = None,
        abort_if_overlong: Optional[bool] = None
    ) -> Union[DtlError, Job]:

        """
        Updates the schedule for a pipeline.
        The next scheduled job will reflect the new schedule for the given pipeline ID. Pipelines running on a recurring
        schedule will retain their parent job ID and the update will affect all future runs of the pipeline.

        :param pipeline_id: UUID id of the pipeline to schedule
        :param run_date: optional, datetime for scheduling
        :param frequency: optional, interval value (e.g float) with period (e.g hours) after which a job will be repeated
        :param abort_if_overlong: optional, if True, avoids running a job cycle if previous cycle is running. (False by default)
        :return: Returns Job object or error
        :return: First scheduled job of the pipeline’s running if
        successful, or DtlError if failed
        """

        url = f"{self.service_uri}/streams/{str(pipeline_id)}/schedule"

        payload = {}
        if run_date is not None:
            payload.update({"runDate": run_date.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")})
        if frequency is not None:
            payload.update({"intervalInSec": frequency.total_seconds()})
        if abort_if_overlong is not None:
            payload.update({"abortIfOverlong": abort_if_overlong})
        if not payload:
            return DtlError("Please specify one of these params: 'run_date', 'frequency' or 'abort_if_overlong'")

        rsp = self.http_client.make_authed_request(url, HttpMethod.PATCH, payload)

        if isinstance(rsp, DtlError):
            return DtlError(f"Encountered an error while updating pipeline schedule: {rsp.message}")

        updated_job = Job._from_payload(rsp)
        return updated_job


class _TemplateClient:
    """
    Client to interact with Pipeline Templates
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, pipeline_template: PipelineTemplate, validate: bool = True) -> Union[DtlError, PipelineTemplate]:
        """
        Create and validate the structure of a pipeline template

        :param pipeline_template: a local pipeline template, to be created
        and saved on the platform
        :param validate: can be set to False to opt-out of template
        validation upon creation. Otherwise, the argument of
        dummy_input_map in the PipelineTemplate object will be used to
        complete the template
        :return: Returns created PipelineTemplate if successful, or DtlError if failed
        """

        if validate is False:
            pipeline_template.dummy_input_map = None

        if validate is True and pipeline_template.dummy_input_map is None:
            return DtlError("dummy_input_map must have key -> value if 'validate' argument is True")

        res = self.http_client.make_authed_request(
            f"{self.service_uri}/templates", HttpMethod.POST, pipeline_template._as_payload(),
        )

        if isinstance(res, DtlError):
            return res

        return PipelineTemplate._from_payload(res)

    def update(
        self,
        id: Union[str, UUID],
        name: Optional[str] = None,
        template: Optional[str] = None,
        dummy_input_map: Optional[Dict[str, str]] = None,
        validate: bool = True,
    ) -> Union[DtlError, PipelineTemplate]:
        """
        Update a template's name and/or template by its ID.
        :param id: id of the template to be updated
        :param name : optional, new name of the template
        :param template: optional, new template to update the existing template
        :param dummy_input_map:  an example of data that will be used to
        validate this template upon creation, unless disabled upon the
        creation step
        :param validate: can be set to False to opt-out of template
        validation upon update. Otherwise, the argument of
        dummy_input_map will be used to
        complete the template
        :return: Returns an updated template if successful, ors DtlError if failed
        """
        req_body = {}
        if name is not None:
            req_body["name"] = name
        if template is not None:
            req_body["template"] = template
        if dummy_input_map is not None:
            req_body["dummy_input_map"] = dummy_input_map

        if validate is False:
            req_body["dummy_input_map"] = None
        if validate is True and dummy_input_map is None:
            return DtlError("dummy_input_map must have key -> value if 'validate' argument is True")
        if dummy_input_map is not None and template is None:
            return DtlError("template must be supplied for dummy_input_map validation")

        res = self.http_client.make_authed_request(f"{self.service_uri}/templates/{str(id)}", HttpMethod.PUT, req_body)

        if isinstance(res, DtlError):
            return res

        return PipelineTemplate._from_payload(res)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[PipelineTemplate]]:
        """
        List all templates.

        :param page: page to be retrieved
        :param item_per_page: number of templates to be put in a page
        :return: Returns a List of all the available templates if successful, or DtlError if failed
        """
        req_params = {}
        if isinstance(page, int) and page > 0:
            req_params["page"] = page
        else:
            return _invalid_pagination_params("page")
        if isinstance(item_per_page, int) and item_per_page > 0:
            req_params["size"] = item_per_page
        else:
            return _invalid_pagination_params("item_per_page")
        res = self.http_client.make_authed_request(f"{self.service_uri}/templates", HttpMethod.GET, params=req_params)
        if isinstance(res, DtlError):
            return res

        return _parse_list(PipelineTemplate._from_payload)(res)

    def get(self, id: Union[str, UUID]) -> Union[DtlError, PipelineTemplate]:
        """
        Retrieve a template by its ID.
        :param id: the id of the template to be retrieved locally
        :return: Returns a template if successful, or a DtlError if failed
        """
        res = self.http_client.make_authed_request(f"{self.service_uri}/templates/{str(id)}", HttpMethod.GET)
        if isinstance(res, DtlError):
            return res

        return PipelineTemplate._from_payload(res)

    def delete(self, id: Union[str, UUID]) -> Union[DtlError, bool]:
        """
        Delete a template by its ID.
        :param id: id of the template to be deleted
        :return: True if successful, or DtlError if failed
        """
        res = self.http_client.execute_authed_request(f"{self.service_uri}/templates/{str(id)}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 204:
            return True
        else:
            return DtlError(res.text)

    def share(
        self, id: UUID, target_id: UUID, target_type: Scope, permission: Permission
    ) -> Union[SharePermission, DtlError]:
        """
        Extends Permissions for Pipeline to another User or Group
        
        :param id: id of Pipeline to be shared
        :param target_type: User or Group, as an enumeration of Scope
        :param target_id: id of the Permission-receiving User or Group
        :param permission: level of Permissions to share (Read, Write, or Share), as an enumeration of Permission
        :return: SharePermission if successful, DtlError if failed
        """

        url = f"{self.service_uri}/templates/{str(id)}/shares?targetType={str(target_type.value)}&targetId={str(target_id)}&permission={str(permission.value)}"
        rsp = self.http_client.execute_authed_request(url, HttpMethod.POST)

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return SharePermission(object_type=ObjectType.PipelineTemplate).from_payload(rsp.json())
        else:
            return DtlError(rsp.text)

    def unshare(
        self, id: UUID, target_id: UUID, target_type: Scope, permission: Permission
    ) -> Union[UnsharePermission, DtlError]:
        """
        Withdraws Permissions for Pipeline with another User or Group
        
        :param id: id of Pipeline to be unshared
        :param target_type: User or Group, as an enumeration of Scope
        :param target_id: id of the Permission-withdrawn User or Group
        :param permission: level of Permissions to unshare (Read, Write, or Share), as an enumeration of Permission
        :return: UnsharePermission if successful, DtlError if failed
        """

        url = f"{self.service_uri}/templates/{str(id)}/shares?targetType={str(target_type.value)}&targetId={str(target_id)}&permission={str(permission.value)}"
        rsp = self.http_client.execute_authed_request(url, HttpMethod.DELETE)

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return UnsharePermission(object_type=ObjectType.PipelineTemplate).from_payload(rsp.json())
        else:
            return DtlError(rsp.text)

    def validate(self, id: UUID, dummy_input_map: Dict[str, str]) -> Union[bool, DtlError]:
        """
        Validate if an existing pipeline template compiles, with a supplied map of values.
        :param id: id of the template that is to be validated
        :param dummy_input_map: an example of data that will be used to
        validate the existing template
        :return: Returns True if template is valid, or DtlError if the validation was unsuccessful
        """
        url = f"{self.service_uri}/templates/{str(id)}/validate"
        rsp = self.http_client.execute_authed_request(url, HttpMethod.POST, dummy_input_map)

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return True
        else:
            return DtlError(rsp.text)

    def generate_pipeline(
        self, pipeline_template_id: Union[str, UUID], pipeline_name: str, input_map: Dict[str, str],
    ) -> Union[Pipeline, DtlError]:
        """
        Generate a pipeline by providing the missing inputs and their
        mapping to an existing pipeline template

        The correct number and mapping of inputs must be provided to the
        template—i.e. for a template with a {{local_path}}, a mapping of
        {"local_path" : "/data/source.csv"} would be appropriate

        :param pipeline_template_id: id of the pipeline template
        :param pipeline_name: name of the pipeline to be generated
        :param input_map: a mapping of inputs to be slotted into the template,
        following moustache distinction <https://mustache.github.io/mustache.5.html>
        :return: the newly created Pipeline if successful, or DtlError if
        failed
        """
        url = f"{self.service_uri}/templates/{str(pipeline_template_id)}/pipeline"
        payload = {"name": pipeline_name, "inputMap": input_map}
        rsp = self.http_client.make_authed_request(url, HttpMethod.POST, payload)

        if isinstance(rsp, DtlError):
            return DtlError(f"Encountered an error while generating pipeline from template: {rsp.message}")

        return Pipeline._from_payload(rsp)

    def run(
        self, pipeline_template_id: Union[str, UUID], pipeline_name: str, input_map: Dict[str, str],
    ) -> Union[DtlError, Job]:
        """
        Run a pipeline completed by providing the missing inputs and their
        mapping to an existing pipeline template

        The correct number and mapping of inputs must be provided to the
        template—i.e. for a template with a {{local_path}}, a mapping of
        {"local_path" : "/data/source.csv"} would be appropriate

        :param pipeline_template_id: id of the pipeline template
        :param pipeline_name: name of the pipeline to be run
        :param input_map: a mapping of inputs to be slotted into the template,
        following moustache distinction <https://mustache.github.io/mustache.5.html>
        :return: a Job generated by running the completed pipeline if
        successful, or DtlError if failed
        """

        url = f"{self.service_uri}/templates/{str(pipeline_template_id)}/run"
        payload = {"name": pipeline_name, "inputMap": input_map}

        rsp = self.http_client.make_authed_request(url, HttpMethod.POST, payload)

        if isinstance(rsp, DtlError):
            return DtlError(f"Encountered an error while running pipeline from template: {rsp.message}")

        jobs = _parse_list(Job._from_payload_v1)(rsp)
        if len(jobs) == 0:
            return DtlError("Encountered an issue! There should be at least one job!")
        else:
            return jobs[0]

    def schedule(
        self,
        pipeline_template_id: Union[str, UUID],
        pipeline_name: str,
        input_map: Dict[str, str],
        run_date: datetime,
        frequency: Optional[timedelta] = None,
        abort_if_overlong: bool = False,
    ) -> Union[DtlError, Job]:

        """
        Schedule a template to generate jobs, optionally following a
        recurrent frequency

        :param pipeline_template_id: id of the pipeline template
        :param pipeline_name: name of the pipeline to be run
        :param input_map: a mapping of inputs to be slotted into the
        template, following moustache distinction
        :param run_date: localized date at which to schedule the job
        :param frequency: frequency of subsequent re-runnings, via the
        timedelta class
        :param abort_if_overlong: defaults to run a subsequent running if
        a current job is still running
        :return: First scheduled job of the pipeline’s running if
        successful, or DtlError if failed
        """

        url = f"{self.service_uri}/templates/{str(pipeline_template_id)}/schedule"

        payload = {
            "name": pipeline_name,
            "runDate": run_date.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "inputMap": input_map,
            "abortIfOverlong": abort_if_overlong,
        }

        if frequency is not None:
            payload.update({"intervalInSec": frequency.total_seconds()})

        rsp = self.http_client.make_authed_request(url, HttpMethod.POST, payload)

        if isinstance(rsp, DtlError):
            return DtlError(f"Encountered an error while running pipeline from template: {rsp.message}")

        jobs = _parse_list(Job._from_payload_v1)(rsp)
        if len(jobs) == 0:
            return DtlError("Encountered an issue! There should be at least one job!")
        else:
            return jobs[0]
