import concurrent.futures
import logging
import tarfile
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from gwdc_python import GWDC
from tqdm import tqdm

from .bilby_job import BilbyJob
from .event_id import EventID
from .file_reference import FileReference, FileReferenceList
from .helpers import TimeRange, Cluster
from .utils import convert_dict_keys

GWCLOUD_ENDPOINT = 'https://gwcloud.org.au/bilby/graphql'
GWCLOUD_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/job/apiv1/file/?fileId='
GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT = 'https://gwcloud.org.au/bilby/file_download/?fileId='

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class GWCloud:
    """
    GWCloud class provides an API for interacting with Bilby, allowing jobs to be submitted and acquired.

    Parameters
    ----------
    token : str
        API token for a Bilby user
    endpoint : str, optional
        URL to which we send the queries, by default GWCLOUD_ENDPOINT

    Attributes
    ----------
    client : GWDC
        Handles a lot of the underlying logic surrounding the queries
    """
    def __init__(self, token, endpoint=GWCLOUD_ENDPOINT):
        self.client = GWDC(token=token, endpoint=endpoint)
        self.request = self.client.request  # Setting shorthand for simplicity

    def start_bilby_job_from_string(self, job_name, job_description, private, ini_string, cluster=Cluster.DEFAULT):
        """Submit the parameters required to start a Bilby job, using the contents of an .ini file

        Parameters
        ----------
        job_name : str
            Name of the job to be created
        job_description : str
            Description of the job to be created
        private : bool
            True if job should be private, False if public
        ini_string : str
            The contents of a Bilby ini file
        cluster : .Cluster or str
            The name of the cluster to submit the job to

        Returns
        -------
        str
            Message received from server after job submission
        """
        query = """
            mutation NewBilbyJobFromIniString($input: BilbyJobFromIniStringMutationInput!){
                newBilbyJobFromIniString (input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        variables = {
            "input": {
                "params": {
                    "details": {
                        "name": job_name,
                        "description": job_description,
                        "private": private,
                        "cluster": cluster.value if isinstance(cluster, Cluster) else cluster
                    },
                    "iniString": {
                        "iniString": str(ini_string)
                    }
                },
            }
        }

        data = self.request(query=query, variables=variables)
        job_id = data['newBilbyJobFromIniString']['result']['jobId']
        return self.get_job_by_id(job_id)

    def start_bilby_job_from_file(self, job_name, job_description, private, ini_file, cluster=Cluster.DEFAULT):
        """Submit the parameters required to start a Bilby job, using an .ini file

        Parameters
        ----------
        job_name : str
            Name of the job to be created
        job_description : str
            Description of the job to be created
        private : bool
            True if job should be private, False if public
        ini_file : str or Path
            Path to an .ini file for running a Bilby job
        cluster : .Cluster or str
            The name of the cluster to submit the job to

        Returns
        -------
        str
            Message received from server after job submission
        """
        ini_file = Path(ini_file)
        with ini_file.open() as f:
            ini_string = f.read().strip()
            return self.start_bilby_job_from_string(job_name, job_description, private, ini_string, cluster)

    def get_preferred_job_list(self, search=""):
        """Get list of public Bilby jobs corresponding to a search of "preferred" and a time_range of "Any time"

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter public job list, by default ""

        Returns
        -------
        list
            List of BilbyJob instances for the preferred jobs corresponding to the search terms
        """
        return self.get_public_job_list(search=f"preferred lasky {search}", time_range=TimeRange.ANY)

    def _get_job_model_from_query(self, query_data):
        if not query_data:
            # logger.info('No')
            return None
        return BilbyJob(
            client=self,
            **convert_dict_keys(
                query_data,
                [
                    ('id', 'job_id'),
                ]
            )
        )

    def get_public_job_list(self, search="", time_range=TimeRange.ANY, number=100):
        """Obtains a list of public Bilby jobs, filtering based on the search terms
        and the time range within which the job was created.

        Parameters
        ----------
        search : str, optional
            Search terms by which to filter public job list, by default ""
        time_range : .TimeRange or str, optional
            Time range by which to filter job list, by default TimeRange.ANY
        number : int, optional
            Number of job results to return in one request, by default 100

        Returns
        -------
        list
            List of BilbyJob instances for the jobs corresponding to the search terms and in the specified time range
        """
        query = """
            query ($search: String, $timeRange: String, $first: Int){
                publicBilbyJobs (search: $search, timeRange: $timeRange, first: $first) {
                    edges {
                        node {
                            id
                            user
                            name
                            description
                            jobStatus {
                                name
                                date
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "search": search,
            "timeRange": time_range.value if isinstance(time_range, TimeRange) else time_range,
            "first": number
        }

        data = self.request(query=query, variables=variables)

        if not data['publicBilbyJobs']['edges']:
            logger.info('Job search returned no results.')
            return []

        return [self._get_job_model_from_query(job['node']) for job in data['publicBilbyJobs']['edges']]

    def get_job_by_id(self, job_id):
        """Get a Bilby job instance corresponding to a specific job ID

        Parameters
        ----------
        job_id : str
            ID of job to obtain

        Returns
        -------
        BilbyJob
            BilbyJob instance corresponding to the input ID
        """
        query = """
            query ($id: ID!){
                bilbyJob (id: $id) {
                    id
                    name
                    userId
                    description
                    jobStatus {
                        name
                        date
                    }
                    eventId {
                        eventId
                        triggerId
                        nickname
                        isLigoEvent
                    }
                }
            }
        """

        variables = {
            "id": job_id
        }

        data = self.request(query=query, variables=variables)

        if not data['bilbyJob']:
            logger.info('No job matching input ID was returned.')
            return None

        return self._get_job_model_from_query(data['bilbyJob'])

    def get_user_jobs(self, number=100):
        """Obtains a list of Bilby jobs created by the user, filtering based on the search terms
        and the time range within which the job was created.

        Parameters
        ----------
        number : int, optional
            Number of job results to return in one request, by default 100

        Returns
        -------
        list
            List of BilbyJob instances for the jobs corresponding to the search terms and in the specified time range
        """
        query = """
            query ($first: Int){
                bilbyJobs (first: $first){
                    edges {
                        node {
                            id
                            name
                            userId
                            description
                            jobStatus {
                                name
                                date
                            }
                            eventId {
                                eventId
                                triggerId
                                nickname
                                isLigoEvent
                            }
                        }
                    }
                }
            }
        """

        variables = {
            "first": number
        }

        data = self.request(query=query, variables=variables)

        return [self._get_job_model_from_query(job['node']) for job in data['bilbyJobs']['edges']]

    def _get_files_by_job_id(self, job_id):
        query = """
            query ($jobId: ID!) {
                bilbyResultFiles (jobId: $jobId) {
                    files {
                        path
                        isDir
                        fileSize
                        downloadToken
                    }
                    isUploadedJob
                }
            }
        """

        variables = {
            "jobId": job_id
        }

        data = self.request(query=query, variables=variables)

        file_list = FileReferenceList()
        for f in data['bilbyResultFiles']['files']:
            if f['isDir']:
                continue
            f.pop('isDir')
            file_list.append(FileReference(**convert_dict_keys(f)))

        return file_list, data['bilbyResultFiles']['isUploadedJob']

    def _get_file_map_fn(self, file_id, file_path, progress_bar, is_uploaded_job=False):
        endpoint = GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
            if not is_uploaded_job else \
            GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT

        download_url = endpoint + str(file_id)
        content = b''
        with requests.get(download_url, stream=True) as request:
            for chunk in request.iter_content(chunk_size=1024 * 16, decode_unicode=True):
                progress_bar.update(len(chunk))
                content += chunk
        return (file_path, content)

    def _get_files_by_reference(self, job_id, file_references, is_uploaded_job=False):
        """Obtains file data when provided a job ID and a FileReferenceList

        Parameters
        ----------
        job_id : str
            Job ID
        file_references : FileReferenceList
            Contains the FileReferences objects for which to download the contents

        Returns
        -------
        list
            List of tuples containing the file path and file contents as a byte string
        """
        file_ids = self._get_download_ids_from_tokens(job_id, file_references.get_tokens())
        file_paths = file_references.get_paths()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            progress = tqdm(total=file_references.get_total_bytes(), leave=True, unit='B', unit_scale=True)
            files = list(
                executor.map(
                    partial(
                        self._get_file_map_fn,
                        progress_bar=progress,
                        is_uploaded_job=is_uploaded_job
                    ), file_ids, file_paths
                )
            )
            progress.close()
            logger.info(f'All {len(file_ids)} files downloaded!')

        return files

    def _save_file_map_fn(self, file_id, file_path, progress_bar, is_uploaded_job=False):
        endpoint = GWCLOUD_FILE_DOWNLOAD_ENDPOINT \
            if not is_uploaded_job else \
            GWCLOUD_UPLOADED_JOB_FILE_DOWNLOAD_ENDPOINT

        download_url = endpoint + str(file_id)
        file_path.parents[0].mkdir(parents=True, exist_ok=True)

        with requests.get(download_url, stream=True) as request:
            with file_path.open("wb+") as f:
                for chunk in request.iter_content(chunk_size=1024 * 16):
                    progress_bar.update(len(chunk))
                    f.write(chunk)

    def _save_files_by_reference(self, job_id, file_references, root_path, preserve_directory_structure=True,
                                 is_uploaded_job=False):
        """Save files when provided a job ID and a FileReferenceList

        Parameters
        ----------
        job_id : str
            Job ID
        file_references : FileReferenceList
            Contains the FileReference objects for which to save the associated files
        root_path : str or ~pathlib.Path
            Directory into which to save the files
        preserve_directory_structure : bool, optional
            Remove any directory structure for the downloaded files, by default True

        Returns
        -------
        str
            Success message
        """
        file_ids = self._get_download_ids_from_tokens(job_id, file_references.get_tokens())
        file_paths = file_references.get_output_paths(root_path, preserve_directory_structure)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            progress = tqdm(total=file_references.get_total_bytes(), leave=True, unit='B', unit_scale=True)
            list(
                executor.map(
                    partial(
                        self._save_file_map_fn,
                        progress_bar=progress,
                        is_uploaded_job=is_uploaded_job
                    ),
                    file_ids, file_paths
                )
            )
            progress.close()
            logger.info(f'All {len(file_ids)} files saved!')

        return 'Success'

    def _get_download_id_from_token(self, job_id, file_token):
        """Get a single file download id for a file download token

        Parameters
        ----------
        job_id : str
            Job id which owns the file token

        file_token : str
            Download token for the desired file

        Returns
        -------
        str
            Download id for the desired file
        """
        return self._get_download_ids_from_tokens(job_id, [file_token])[0]

    def _get_download_ids_from_tokens(self, job_id, file_tokens):
        """Get many file download ids for a list of file download tokens

        Parameters
        ----------
        job_id : str
            Job id which owns the file token

        file_tokens : list
            Download tokens for the desired files

        Returns
        -------
        list
            List of download ids for the desired files
        """
        query = """
            mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
                generateFileDownloadIds(input: $input) {
                    result
                }
            }
        """

        variables = {
            "input": {
                "jobId": job_id,
                "downloadTokens": file_tokens
            }
        }

        data = self.request(query=query, variables=variables)

        return data['generateFileDownloadIds']['result']

    def _generate_upload_token(self):
        """Creates a new long lived upload token for use uploading jobs

        Returns
        -------
        str
            The upload token
        """
        query = """
            query GenerateBilbyJobUploadToken {
                generateBilbyJobUploadToken {
                  token
                }
            }
        """

        data = self.request(query=query)
        return data['generateBilbyJobUploadToken']['token']

    def upload_job_archive(self, description, job_archive, public=False):
        """Upload a bilby job to GWCloud by job output archive

        Parameters
        ----------
        description : str
            The description of the job to add to the database

        public : bool
            If the uploaded job should be public or not

        job_archive : str
            The path to the job output archive to upload

        Returns
        -------
        BilbyJob
            The created Bilby job
        """
        query = """
            mutation JobUploadMutation($input: UploadBilbyJobMutationInput!) {
                uploadBilbyJob(input: $input) {
                    result {
                        jobId
                    }
                }
            }
        """

        with open(job_archive, 'rb') as f:
            variables = {
                "input": {
                    "uploadToken": self._generate_upload_token(),
                    "details": {
                        "description": description,
                        "private": not public
                    },
                    "jobFile": f
                }
            }

            data = self.request(query=query, variables=variables, authorize=False)

        job_id = data['uploadBilbyJob']['result']['jobId']
        return self.get_job_by_id(job_id)

    def upload_job_directory(self, description, job_directory, public=False):
        """Upload a bilby job to GWCloud by job output directory

        Parameters
        ----------
        description : str
            The description of the job to add to the database

        public : bool
            If the uploaded job should be public or not

        job_directory : str
            The path to the job output directory to upload

        Returns
        -------
        BilbyJob
            The created Bilby job
        """

        # Generate a temporary archive of the job
        path = Path(job_directory)
        with NamedTemporaryFile(dir=job_directory, suffix='.tar.gz') as f:
            with tarfile.open(f.name, "w:gz", compresslevel=2) as tar_handle:
                for item in path.rglob("*"):
                    print(item)
                    tar_handle.add(item, arcname=item.relative_to(path), recursive=False)

            # Upload the archive
            return self.upload_job_archive(description, f.name, public)

    def create_event_id(self, event_id, trigger_id=None, nickname=None, is_ligo_event=False):
        """Create an Event ID that can be assigned to Bilby Jobs

        **INFO**:
        *Event IDs can only be created by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        trigger_id : str, optional
            Trigger ID of the event, must be of the form S123456a, by default None
        nickname : str, optional
            Common name used to identify the event, by default None
        is_ligo_event : bool, optional
            Should the event be visible to ligo users only, by default False

        Returns
        -------
        .EventID
            The created Event ID
        """
        query = """
            mutation CreateEventIDMutation($input: EventIDMutationInput!) {
                createEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id,
                "triggerId": trigger_id,
                "nickname": nickname,
                "isLigoEvent": is_ligo_event,
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['createEventId']['result'])
        return self.get_event_id(event_id=event_id)

    def update_event_id(self, event_id, trigger_id=None, nickname=None, is_ligo_event=None):
        """Create an Event ID that can be assigned to Bilby Jobs

        **INFO**:
        *Event IDs can only be updated by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        trigger_id : str, optional
            Trigger ID of the event, must be of the form S123456a, by default None
        nickname : str, optional
            Common name used to identify the event, by default None
        is_ligo_event : bool, optional
            Should the event be visible to ligo users only, by default None

        Returns
        -------
        .EventID
            The updated Event ID
        """
        query = """
            mutation UpdateEventIDMutation($input: UpdateEventIDMutationInput!) {
                updateEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id,
                "triggerId": trigger_id,
                "nickname": nickname,
                "isLigoEvent": is_ligo_event,
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['updateEventId']['result'])
        return self.get_event_id(event_id=event_id)

    def delete_event_id(self, event_id):
        """Delete an Event ID

        **INFO**:
        *Event IDs can only be deleted by a select few users.*

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456
        """
        query = """
            mutation DeleteEventIDMutation($input: DeleteEventIDMutationInput!) {
                deleteEventId (input: $input) {
                    result
                }
            }
        """
        variables = {
            "input": {
                "eventId": event_id
            }
        }
        data = self.request(query=query, variables=variables)
        logger.info(data['deleteEventId']['result'])

    def get_event_id(self, event_id):
        """Get EventID by the event_id

        Parameters
        ----------
        event_id : str
            Event ID of the form GW123456_123456

        Returns
        -------
        .EventID
            The requested Event ID
        """
        query = """
            query ($eventId: String!){
                eventId (eventId: $eventId) {
                    eventId
                    triggerId
                    nickname
                    isLigoEvent
                }
            }
        """
        if event_id == '':
            return None

        variables = {
            "eventId": event_id
        }
        data = self.request(query=query, variables=variables)
        return EventID(**convert_dict_keys(data['eventId']))

    def get_all_event_ids(self):
        """Obtain a list of all Event IDs

        Parameters
        ----------
        event_id : str
            ID of the event, must be of the form GW123456_123456

        Returns
        -------
        list
            A list of all .EventID objects
        """
        query = """
            query {
                allEventIds {
                    eventId
                    triggerId
                    nickname
                    isLigoEvent
                }
            }
        """
        data = self.request(query=query)
        return [EventID(**convert_dict_keys(event)) for event in data['allEventIds']]
