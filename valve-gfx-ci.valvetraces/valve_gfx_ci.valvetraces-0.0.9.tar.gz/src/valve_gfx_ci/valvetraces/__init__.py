#!/usr/bin/env -S python3 -u

try:
    from functools import cached_property
except Exception:
    from backports.cached_property import cached_property
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Pool
import xml.etree.ElementTree as ET
import dataclasses
import itertools
import datetime
import base64
import hashlib
import humanize
from functools import partial
import json
import os
import re
import traceback
import requests
import argparse
import sys
import shutil
import minio
from pathlib import Path
import subprocess
from urllib.parse import urlparse
import operator
import pygit2

from enum import Enum
from PIL import Image

naturalsize = partial(humanize.naturalsize, binary=True)
ensure_dir = partial(os.makedirs, exist_ok=True)


def timeit(method):
    import time

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            exec_time = int((te - ts) * 1000)
            print(f'{method.__name__} took {exec_time} ms')

        return result

    return timed


class SanitizedFieldsMixin:
    @classmethod
    def from_api(cls, fields, **kwargs):
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}

        sanitized_kwargs = dict(fields)
        for arg in fields:
            if arg not in valid_fields:
                sanitized_kwargs.pop(arg)

        return cls(**sanitized_kwargs, **kwargs)


@dataclass
class Project(SanitizedFieldsMixin):
    id: int
    name: str
    repo_url: str = None
    project_url: str = None
    base_url_for_commits: str = None


class GitRepo:
    def __init__(self, name, repo_path):
        git_repo = os.path.join(repo_path, '.git')
        if not os.path.isdir(git_repo):
            raise ValueError(f"The path '{git_repo}' does not exist")

        self.name = name
        self.repo_path = repo_path
        self.repo = pygit2.Repository(git_repo)

    @property
    def head(self):
        return str(self.repo.head.target)

    def find_first_accessible_commits_from_head(self, commit_oids):
        top_commits = set()

        # If HEAD of the project is in the list of oids, then no
        # other commit is accessible. Return HEAD directly
        if self.head in commit_oids:
            return [self.head]

        # Create a walker, hiding all the commits under the commits of interest
        walker = self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL)

        # Restrict the commits we shall walk to the ones *above* the ones the user
        # is looking for, as we are only interested in
        for oid in commit_oids:
            try:
                walker.hide(oid)
            except (ValueError, KeyError):
                # Ignore non-existing commits
                pass

        # Look for all the commits that are accessible from HEAD until the hidden
        # commits.
        for commit in walker:
            for parent in commit.parents:
                if str(parent.oid) in commit_oids:
                    top_commits.add(str(parent.oid))

        return top_commits

    def __eq__(self, other):
        return self.name == other.name and self.repo_path == other.repo_path

    def __hash__(self):
        return hash((self.name, self.repo_path))


@dataclass
class Commit(SanitizedFieldsMixin):
    id: int
    project_id: int
    version: str


@dataclass
class GPU(SanitizedFieldsMixin):
    id: int
    pciid: str
    name: str
    metadata: dict


@dataclass
class TraceCompatibility(SanitizedFieldsMixin):
    id: int
    trace_id: int
    commit: Commit
    project: Project
    gpu_id: int
    bug_id: int
    is_working: bool
    agreement_count: int = 1

    def __str__(self):
        is_working = "GOOD" if self.is_working else "BAD"
        return f"<TraceCompat for trace id {self.trace_id} on {self.project.name}'s {self.commit.version} and gpu_id={self.gpu_id}: {is_working}>"


@dataclass
class App(SanitizedFieldsMixin):
    id: int
    name: str
    steamappid: str

    def matches(self, app_id):
        return str(self.id) == app_id or str(self.name) == app_id or str(self.steamappid) == app_id

    def __str__(self):
        return f"<App: ID={self.id}, SteamID={self.steamappid}, name={self.name}>"


class BlobType(Enum):
    UNKNOWN = 0
    TRACE = 1
    FRAME = 2

    @staticmethod
    def from_str(label):
        if label is None:
            return BlobType.UNKNOWN

        lowered = label.lower()
        if lowered == 'trace':
            return BlobType.TRACE
        elif lowered == 'frameoutput':
            return BlobType.FRAME
        else:
            return BlobType.UNKNOWN


class Blob:
    def __init__(self, blob_dict, new=True):
        self.new = new
        direct_upload = blob_dict.get("direct_upload")
        if direct_upload is not None:
            self.url = direct_upload.get('url')
            if self.url is None:
                raise ValueError("The URL is missing from the 'direct_upload' dict")

            self.headers = direct_upload.get('headers')
            if self.headers is None:
                raise ValueError("The headers are missing from the 'direct_upload' dict")

        self.signed_id = blob_dict.get("signed_id")
        if self.signed_id is None:
            raise ValueError("The signed_id is missing from the blob-creation response")

        self.record_type = BlobType.from_str(blob_dict.get("record_type"))

        if not self.new and self.record_type != BlobType.UNKNOWN:
            self.record = blob_dict.get("record")

    def upload(self, f):
        r = requests.put(self.url, headers=self.headers, data=f)
        r.raise_for_status()


@dataclass
class Trace(SanitizedFieldsMixin):
    id: int
    filename: str = None
    metadata: dict = dataclasses.field(default_factory=dict)
    obsolete: bool = False
    frames_to_capture: dict = dataclasses.field(default_factory=dict)
    graphics_api: str = None
    tracing_tool: str = None
    url: str = None
    file_size: int = 0

    @property
    def size(self):
        return self.file_size

    @property
    def machine_tags(self):
        try:
            return list(self.metadata.get("machine_tags", []))
        except Exception as e:
            print(e)
            return []

    # TODO: Work on making the traces API do server-side filtering of
    # the metadata. This seems a better interface than pulling all the
    # metadata only to discard potentially a good proportion of it
    # client-side.
    def matches_tags(self, tags, debug=False):
        machine_tags = self.machine_tags

        for wanted_tag in tags:
            found = False
            for machine_tag in machine_tags:
                if wanted_tag.match(machine_tag):
                    if debug:
                        print(f"The wanted tag {wanted_tag} matched the machine tag {machine_tag}")
                    found = True
                    break

            if found:
                continue

            if debug:
                print(f"The wanted tag {wanted_tag} was not matched")
            return False

        return True

    @property
    def human_size(self):
        return naturalsize(self.file_size)

    def filename_to_frame_id(self, filename):
        if self.tracing_tool == "apitrace":
            return str(int(filename))
        elif self.tracing_tool == "gfxrecon":
            return str(int(filename.split('_')[-1]))
        else:
            raise ValueError(f"Unknown tracing tool '{self.tracing_tool}'")

    def exec_script(self, trace_file_path, trace_job_path):
        rendered_frame_ids = ','.join([str(frame_id) for frame_id in self.frames_to_capture])

        if self.tracing_tool == "apitrace":
            cmd = "apitrace" if self.graphics_api == "OpenGL" else "apitrace.exe"

            cmdline = f'{cmd} replay --headless --snapshot={rendered_frame_ids} --snapshot-prefix="$D/" "{trace_file_path}"'
        elif self.tracing_tool == "gfxrecon":
            cmdline = f'gfxrecon-replay --screenshot-prefix "$D/" --screenshots {rendered_frame_ids} -m rebind "{trace_file_path}"'
        else:
            print("WARNING: Can't generate a cmdline for the tracing tool {self.tracing_tool} / {self.graphics_api}")
            cmdline = "/bin/false"

        return f"""#!/bin/sh
set -u

log() {{
echo "INFO $(date -u +'%F %H:%M:%S') $@"
}}

D=$(dirname "$(readlink -f "$0")")

if [ -e "$D/.started" ]; then
log "Already attempted to run {self.filename}"
exit 0
fi

date -u +'%F %H:%M:%S' > "$D/.started"

log "Replaying frames ({rendered_frame_ids}) from {self.filename} ..."
set -x
{cmdline} > "$D/exec.log" 2>&1
retval=$?
set +x

log "Finished replay for {self.filename}"

cat <<EOF  > "$D/.done"
$(date -u +'%F %H:%M:%S')
$retval
EOF
"""

    def __str__(self):
        return f"<Trace {self.id}, {self.filename}, size {self.human_size}>"


class Client:
    def __init__(self, url, username=None):
        self.url = url
        self.username = username

        self._login_cookie = None

    def login(self):
        if self._login_cookie is None:
            password = os.environ.get("VALVETRACESPASSWORD", None)
            if self.username is None or password is None:
                print("ERROR: credentials not specified for valve traces client")
                sys.exit(1)

            r = requests.post(f"{self.url}/api/v1/login", allow_redirects=False,
                              json={"user": {"username": self.username, "password": password}})
            r.raise_for_status()

            self._login_cookie = r.cookies

        return self._login_cookie

    @property
    def requests_retry_session(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get(self, path):
        headers = {'Content-type': 'application/json'}
        r = self.requests_retry_session.get(f"{self.url}{path}",
                                            allow_redirects=False,
                                            cookies=self.login(),
                                            headers=headers)

        r.raise_for_status()

        return r.json()

    def _post(self, path, params):
        err_msg = f"ERROR while executing the POST query to {self.url}{path} with the following parameters: {params}"
        try:
            r = self.requests_retry_session.post(f"{self.url}{path}",
                                                 allow_redirects=False,
                                                 cookies=self.login(),
                                                 json=params)
        except Exception as e:
            print(err_msg)
            raise e

        if r.status_code == 500:
            print(f"{err_msg}\nReturn value: {r.text}")
        elif r.status_code == 409:
            # TODO: Add an option to ignore some errors
            return r.json()

        r.raise_for_status()

        return r.json()

    def list_apps(self):
        apps = list()
        for game in self._get("/api/v1/games"):
            apps.append(App.from_api(game))

        return apps

    def create_app(self, name, steamappid=None):
        for app in self.list_apps():
            if app.name == name and app.steamappid == steamappid:
                raise ValueError(f"The app named '{name}' already exists: {app}")

        r = self._post("/api/v1/games", {"game": {"name": name, "appid": steamappid}})

        return App.from_api(r)

    def gpu_get_by_pciid(self, pciid):
        for gpu_dict in self._get("/api/v1/gpus"):
            gpu = GPU.from_api(gpu_dict)
            if gpu.pciid == pciid:
                return gpu

        return None

    def trace_list_compatibly_reports(self, gpu_pciid=None):
        url = "/api/v1/trace_compatibilities"
        if gpu_pciid:
            url += f"?pciid={gpu_pciid}"

        trace_reports = defaultdict(list)
        for tc_dict in self._get(url):
            try:
                commit_dict = tc_dict.get("commit", {})
                project = Project.from_api(commit_dict.get("project", {}))
                commit = Commit(id=commit_dict.get('id'),
                                project_id=project.id,
                                version=commit_dict.get('version'))
            except TypeError:
                print(f"WARNING: Ignoring the following compatibility report: {tc_dict}")
                continue

            report = TraceCompatibility(id=tc_dict.get('id'), gpu_id=tc_dict.get('gpu_id'),
                                        trace_id=tc_dict.get('trace_id'),
                                        commit=commit, project=project,
                                        bug_id=tc_dict.get('bug_id'),
                                        is_working=tc_dict.get('is_working'),
                                        agreement_count=tc_dict.get('agreement_count'))
            trace_reports[report.trace_id].append(report)

        return trace_reports

    def trace_report_compatibility(self, commit_id, trace_id, gpu_id, is_working, bug=None):
        params = {
            "commit_id": commit_id,
            "trace_id": trace_id,
            "gpu_id": gpu_id,
            "bug_id": bug.id if bug else None,
            "is_working": is_working
        }
        r = self._post("/api/v1/trace_compatibilities", params=params)
        return 'id' in r

    def list_traces(self, filter_machine_tags):
        tags = [re.compile(t) for t in filter_machine_tags]

        traces = list()
        for trace_blob in self._get("/api/v1/traces"):
            trace = Trace.from_api(trace_blob)

            if trace.matches_tags(tags):
                traces.append(trace)

        return traces

    def get_trace(self, trace_name):
        for trace in self.list_traces([]):
            if trace.filename == trace_name:
                return trace

        raise ValueError(f"Could not find a trace named '{trace_name}' in the service")

    def project_get_or_create(self, name, repo_url=None, project_url=None, base_url_for_commits=None):
        # Avoid race conditions in project creation by first trying to create it,
        # then if it fails, trying to find it in the list of projects.
        params = {
            "name": name,
            "repo_url": repo_url,
            "project_url": project_url,
            "base_url_for_commits": base_url_for_commits
        }
        r = self._post("/api/v1//projects", params=params)
        if 'id' in r:
            return Project.from_api(r)

        for project_dict in self._get("/api/v1/projects"):
            project = Project.from_api(project_dict)
            if project.name == name:
                return project

        raise ValueError("Failed to create or find the wanted project")

    def commit_get_or_create(self, project, version):
        # Avoid race conditions in commit creation by first trying to create it,
        # then if it fails, trying to find it in the list of commits.
        params = {
            "project_id": project.id,
            "version": version
        }
        r = self._post("/api/v1/commits", params=params)
        if 'id' in r:
            return Commit.from_api(r)

        for commit_dict in self._get("/api/v1/commits"):
            commit = Commit.from_api(commit_dict)
            if commit.project_id == project.id and commit.version == version:
                return commit

        raise ValueError("Failed to create or find the wanted object")

    def download_trace(self, trace_name, output_folder):
        trace = self.get_trace(trace_name)

        trace_path = os.path.join(output_folder, trace_name)
        with open(trace_path, 'wb') as f:
            with requests.get(trace.url, stream=True) as r:
                r.raise_for_status()
                content_length = int(r.headers.get('content-length', 0))
                print('Downloading {} of size {}'.format(
                    trace_name,
                    naturalsize(content_length) if content_length > 0 else 'Unknown'))
                total_downloaded = 0
                previous_pc_downloaded = 0
                chunk_size = 1024 * 1024
                # Reading all the available data without limiting the
                # chunk size is problematic when using SSL
                # connections. Limit the chunk size:
                # https://bugs.python.org/issue42853
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    if content_length == 0:
                        # This shouldn't happen, since the Mango
                        # server returns Content-Length, no progress
                        # info if we don't get a length back from the
                        # server
                        continue
                    total_downloaded += len(chunk)
                    pc_downloaded = int(100.0 * total_downloaded/content_length)
                    # Log roughly every 2% downloaded, or end of stream.
                    if pc_downloaded - previous_pc_downloaded >= 2 or len(chunk) < chunk_size:
                        sys.stdout.write('\rDownloaded {}/{} {:0.2f}%'.format(naturalsize(total_downloaded),
                                                                              naturalsize(content_length),
                                                                              pc_downloaded))
                        sys.stdout.flush()
                        previous_pc_downloaded = pc_downloaded
                sys.stdout.write('\n')
                sys.stdout.flush()
        return trace_path

    def _find_app(self, app_id):
        app_id = str(app_id)

        suitable_apps = []
        for app in self.list_apps():
            if app.matches(app_id):
                suitable_apps.append(app)

        if len(suitable_apps) == 1:
            return suitable_apps[0]
        elif len(suitable_apps) == 0:
            raise ValueError(f"Could not find an app named '{app_id}'")
        else:
            raise ValueError(f"Found more than one application matching the app_id '{app_id}': {suitable_apps}")

    def _data_checksum(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

            return base64.b64encode(hash_md5.digest()).decode()

    def _upload_blob(self, filepath, name, data_checksum, image_checksum=None):
        with open(filepath, "rb") as f:
            # Check the file size
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0, os.SEEK_SET)

            # Ask the website for the URL of where to upload the file
            r_blob = self._post("/rails/active_storage/direct_uploads",
                                {"blob": {"filename": name, "byte_size": file_size,
                                          "content_type": "application/octet-stream",
                                          "checksum": data_checksum,
                                          "image_checksum": image_checksum}})
            blob = Blob(r_blob)

            # Send the file to the bucket
            blob.upload(f)

            return blob

    def _upload_trace_blob(self, filepath, name):
        # Generate the MD5 hash for the bucket
        data_checksum = self._data_checksum(filepath)
        # Check if file already exists on server
        r = self._post("/api/v1/checksum", {"checksum": data_checksum})
        if "accepted" not in r:
            return Blob(r, new=False)

        return self._upload_blob(filepath, name, data_checksum)

    def upload_trace(self, app_id, filepath, frame_ids, machine_tags):
        if not machine_tags:
            confirmation_message = ('I confirm the trace is uploaded from '
                                    'the same computer that produced the trace')
            machine_tags = list(self.machine_tags)
        else:
            confirmation_message = ('I confirm the machine tags provided are '
                                    'the ones produced at the same computer '
                                    'that produced the trace to be uploaded')

        app = self._find_app(app_id)
        trace_name = os.path.basename(filepath)

        print(f"""\nWARNING: You are about to upload a trace, please check that the following values are valid:

    Application/Game: {str(app)}
    Trace name: {trace_name}
    IDs of frames to capture: {frame_ids}
    Machine tags: {machine_tags}
""")
        if input(f'{confirmation_message} (y/N)'.format()).lower() != 'y':
            return

        # Upload the blob
        blob = self._upload_trace_blob(filepath, trace_name)
        if blob.record_type != BlobType.TRACE:
            raise ValueError(f'Expected a {BlobType.TRACE} in the blob, '
                             f'gotten {blob.record_type}')
        if not blob.new:
            print('Trace already exists in the server. Skipping upload.')
            return Trace.from_api(blob.record)

        # Create the trace from the blob
        r = self._post("/api/v1/traces/",
                       params={"trace": {"upload": blob.signed_id, "game_id": app.id,
                                         "metadata": {"machine_tags": machine_tags},
                                         "frames_to_capture": frame_ids}})

        return Trace.from_api(r)

    def _upload_frame_blob(self, filepath, name):
        image_md5 = hashlib.md5(Image.open(filepath).convert(mode="RGBA").tobytes())
        img_checksum = base64.b64encode(image_md5.digest()).decode()

        # Check if frame already exists on server
        r = self._post("/api/v1/image_checksum", {"checksum": img_checksum})
        if "id" in r:
            return Blob(r, new=False)

        # Generate the MD5 hash for the bucket
        data_checksum = self._data_checksum(filepath)

        return self._upload_blob(filepath, name, data_checksum,
                                 image_checksum=img_checksum)

    def _upload_logs_blob(self, filepath, name):
        # Generate the MD5 hash for the bucket
        data_checksum = self._data_checksum(filepath)

        return self._upload_blob(filepath, name, data_checksum)

    def job_get_or_create(self, name, metadata=None, timeline_metadata=None, is_released_code=False):
        # The object will be created if it does not exist already,
        # otherwise, it will return the job that has the same name
        params = {
            "job": {
                "name": name,
                "metadata": metadata,
                "timeline_metadata": timeline_metadata,
                "is_released_code": is_released_code
            }
        }
        job = self._post("/api/v1/jobs", params=params)
        return Job.from_api(job, client=self)

    def trace_exec_list(self, job_id, gpu_pciid):
        trace_execs = list()
        for te in self._get(f"/api/v1/trace_execs?q[job_id_eq]={job_id}&q[gpu_pciid_eq]={gpu_pciid}"):
            # Work around a rails oddity that if a field would be empty, it is not added
            if 'trace_frames' not in te:
                te['trace_frames'] = {}

            trace_execs.append(TraceExec.from_api(te, client=self))

        return trace_execs


@dataclass
class DedupedFrameOutput(SanitizedFieldsMixin):
    id: int
    url: str
    is_acceptable: bool
    found_in_release_code_run: bool
    outputs_count_for_gpu: int = dataclasses.field(init=False)

    # Only used to initialize other members
    gpus: dataclasses.InitVar[list] = None

    def __post_init__(self, gpus):
        self.outputs_count_for_gpu = gpus[0].get('frame_outputs_count', 0)


# Forward declaration for the dataclass. The real deal is lower
class TraceExec:
    pass


@dataclass
class Job(SanitizedFieldsMixin):
    client: Client

    id: int
    name: str
    metadata: dict
    is_released_code: bool = None

    def report_trace_execution(self, trace, gpu_pciid, frame_blobs, metadata=None, status=None, logs_blob_id=None,
                               execution_time=None):
        # Create the trace execution
        params = {
            "trace_exec": {
                "job_id": self.id,
                "trace_id": trace.id,
                "metadata": metadata,
                "status": status,
                "exec_log": logs_blob_id,
                "execution_time": execution_time,
            },
            "frame_blobs": frame_blobs,
            "pciid": gpu_pciid
        }
        r = self.client._post("/api/v1/trace_execs", params=params)

        # Work around a rail oddity that if a field would be empty, it is not added
        if 'trace_frames' not in r:
            r['trace_frames'] = {}

        return TraceExec.from_api(r, client=self.client,
                                  query_params=params,
                                  query_result=r)


@dataclass
class TraceExecFrameOutput(SanitizedFieldsMixin):
    client: Client
    job: Job
    gpu: GPU
    trace_exec: TraceExec
    trace_frame_id: str

    id: int
    frame_outputs_id: int = None
    deduped_frame_output_id: int = None
    blob_id: int = None
    is_acceptable: bool = None

    # Only used to initialize other members
    frame_outputs: dataclasses.InitVar[dict] = None

    def __post_init__(self, frame_outputs):
        self.frame_outputs_id = frame_outputs.get('id')

        deduped_frame_output = frame_outputs.get('deduped_frame_output', {})
        self.deduped_frame_output_id = deduped_frame_output.get('id')
        self.is_acceptable = deduped_frame_output.get("is_acceptable", False)
        self.blob_id = deduped_frame_output.get("blob_id")

    @cached_property
    def trace_frame_stats_for_gpu(self):
        # Only consider results from the past 100 runs
        oldest_job_id = max(0, self.job.id - 100)

        url = f"/api/v1/stats/trace_frames/{self.id}?q[gpus_pciid_cont]={self.gpu.pciid}&q[jobs_id_gt]={oldest_job_id}&q[jobs_id_lt]={self.job.id + 1}"
        r = self.client._get(url)
        return r.get("trace_frame", {})

    @property
    def trace_deduped_frame_outputs_for_gpu(self):
        return [DedupedFrameOutput.from_api(d) for d in self.trace_frame_stats_for_gpu.get('deduped_frames', [])]

    @cached_property
    def deduped_frame_output(self):
        for deduped_frame in self.trace_deduped_frame_outputs_for_gpu:
            if deduped_frame.id == self.deduped_frame_output_id:
                return deduped_frame

    @cached_property
    def unstable_output_for_gpu(self):
        frames = list()
        for deduped_frame in self.trace_deduped_frame_outputs_for_gpu:
            if deduped_frame.found_in_release_code_run and deduped_frame.outputs_count_for_gpu < 20:
                frames.append(deduped_frame)

        return frames

    @cached_property
    def trace_has_stable_output_for_gpu(self):
        return len(self.unstable_output_for_gpu) == 0

    @property
    def acceptability(self):
        if self.is_acceptable is None:
            if self.deduped_frame_output is None:
                # This should not be able to happen :o
                msg = f"""BUG: Could not find deduped frame output id {self.deduped_frame_output_id} in \
trace_frame_stats_for_gpu (pciid={self.gpu.pciid}) for the trace frame id {self.id}.

Constructed using the query parameters {self.trace_exec.query_params}, and the following return value {self.trace_exec.query_result}."""

                print(msg)
                return (False, msg)
            elif self.deduped_frame_output.found_in_release_code_run:
                return (True, "The frame has not been assessed yet, but is found in already-released code")
            elif not self.trace_has_stable_output_for_gpu:
                details = "List of frames that made the output considered unstable:\n"
                for deduped_frame in self.unstable_output_for_gpu:
                    details += f" - {self.client.url}/deduped_frame_outputs/{deduped_frame.id}: Seen {deduped_frame.outputs_count_for_gpu} on this GPU\n"
                return (True, f"The frame has never been seen before, but the output of the trace on this GPU is unstable: Ignore!\n\n{details}")
            else:
                return (False, "The frame has never been seen before, while the output of the trace on this GPU is stable: You need to review it!")
        elif self.is_acceptable:
            return (True, "The frame has been marked acceptable")
        else:
            return (True, "The frame has been marked as unacceptable, but since it is already-known we can ignore it :p")


@dataclass
class TraceExec(SanitizedFieldsMixin):
    client: Client

    id: int
    job: dataclasses.InitVar[Job]
    trace: dataclasses.InitVar[Trace]
    gpu: dataclasses.InitVar[GPU]
    trace_frames: dataclasses.InitVar[dict[str: TraceExecFrameOutput]]
    execution_time: float = 0.0
    status: str = "MISSING"

    # Debug information
    query_params: dict = None
    query_result: dict = None

    def __post_init__(self, job, trace, gpu, trace_frames):
        self.job = Job.from_api(job, client=self.client)
        self.trace = Trace.from_api(trace)
        self.gpu = GPU.from_api(gpu)

        self.trace_frames = dict()
        for trace_frame_id, frame_output in trace_frames.items():
            self.trace_frames[trace_frame_id] = TraceExecFrameOutput.from_api(frame_output,
                                                                              job=self.job,
                                                                              trace_exec=self,
                                                                              gpu=self.gpu, client=self.client,
                                                                              trace_frame_id=trace_frame_id)


def job_id():
    if 'CI_JOB_ID' in os.environ:
        # Be very careful not to pass a plain number as the job ID, everything explodes!
        return f'job-{os.environ["CI_JOB_ID"]}'
    return 'untitled'


def trace_name(trace):
    return f'{trace.id}-{trace.filename}'


def cache_all_traces_to_local_minio(minio_client, minio_bucket, traces):
    if not minio_client.bucket_exists(minio_bucket):
        print(f'ERROR: Bucket {minio_bucket} does not exist.')
        sys.exit(1)

    def exists(c, bucket, object_name, expected_size=-1):
        try:
            assert c.bucket_exists(bucket)
            st = c.stat_object(bucket, object_name)
            if expected_size > 0:
                if not st.size == expected_size:
                    print('%s/%s has an unexpected file size (%s vs %s)' %
                          (bucket, object_name, st.size, expected_size))
                    return False
            return True
        except minio.error.S3Error:
            return False

    for trace in traces:
        object_name = trace_name(trace)
        if exists(minio_client, minio_bucket, object_name, expected_size=trace.size):
            print("%s already exists, skipping caching..." % trace)
        else:
            with requests.get(trace.url, stream=True) as r:
                # print("Request headers: %s", r.headers)  # for caching debugging
                r.raise_for_status()
                print(f'Uploading {trace.filename} of size {naturalsize(trace.size)}...')
                minio_client.put_object(minio_bucket, object_name,
                                        r.raw, -1, part_size=10*1024*1024)


def str_to_safe_filename(s):
    """Make a modest effort to transform _s_ into a string that is
    safe to use as a file name. Get rid of the typically annoying
    characters for files."""
    return "".join(i for i in s if i not in r"\/:*?<>| '")


class GfxInfo:
    def __init__(self, fields):
        self.machine_tags = fields.get('tags', {})

        self.vram_size_gib = fields.get("vk:vram_size_gib", 0)
        self.gtt_size_gib = fields.get("vk:gtt_size_gib", 0)

        self.driver_name = fields.get("vk:driver:name", "N/A")
        self.driver_version = fields.get('mesa:version', 'N/A')
        self.driver_git_version = fields.get('mesa:git:version', 'N/A')

        self.device_name = fields.get('vk:device:name', 'N/A')
        self.device_type = fields.get('vk:device:type', 'N/A')

    @property
    def gpu_codename(self):
        for tag in self.machine_tags:
            if tag.startswith('amdgpu:codename:'):
                return tag[16:]

        return None

    @property
    def gpu_pciid(self):
        for tag in self.machine_tags:
            if tag.startswith('amdgpu:pciid:'):
                return tag[13:]

        return None

    @property
    def all_fields(self):
        return {
            "machine_tags": self.machine_tags,
            "driver": {
                "name": self.driver_name,
                "version": self.driver_version,
                "git_version": self.driver_git_version,
            },
            "device": {
                "name": self.device_name,
                "type": self.device_type,
            },
            "memory": {
                "vram_size_gib": self.vram_size_gib,
                "gtt_size_gib": self.gtt_size_gib,
            }
        }


class Report:
    class TraceExec:
        MIN_ACCEPTABLE_AGREEMENT_COUNT = 20

        def __init__(self, report, trace, folder_path):
            self.report = report
            self.trace = trace
            self.folder_path = folder_path

            self.start_time = None
            self.end_time = None
            self.retcode = None
            self.logs_path = None
            self.found_frames = dict()

            self.job = None
            self.upload_report = None

            for entry in os.scandir(path=folder_path):
                if entry.name == ".started":
                    with open(entry.path, 'r') as f:
                        lines = f.readlines()
                        self.start_time = datetime.datetime.strptime(lines[0].strip(), "%Y-%m-%d %H:%M:%S")
                elif entry.name == ".done":
                    with open(entry.path, 'r') as f:
                        lines = f.readlines()
                        self.end_time = datetime.datetime.strptime(lines[0].strip(), "%Y-%m-%d %H:%M:%S")
                        self.retcode = int(lines[1].strip())
                elif entry.name.endswith('.log'):
                    self.logs_path = entry.path
                elif entry.name.endswith('.png') or entry.name.endswith('.bmp'):
                    try:
                        filename = Path(entry.name).stem
                        frame_id = trace.filename_to_frame_id(filename)
                        self.found_frames[frame_id] = entry.path
                    except Exception as e:
                        print(e)

        @cached_property
        def logs(self):
            if self.logs_path is not None:
                return open(self.logs_path, 'r').read()
            else:
                return None

        @property
        def runtime(self):
            if self.end_time is not None:
                return self.end_time - self.start_time
            else:
                return datetime.timedelta()

        @property
        def frames(self):
            @dataclass
            class Frame:
                frame_id: str
                file_path: str
                is_acceptable: bool
                reason: str

            frames = []
            for expected_frame_id in self.trace.frames_to_capture:
                found_frame_path = self.found_frames.get(expected_frame_id)

                if found_frame_path:
                    if self.upload_report is not None:
                        if uploaded_frame := self.upload_report.trace_frames.get(expected_frame_id):
                            is_acceptable, reason = uploaded_frame.acceptability
                        else:
                            is_acceptable = False
                            reason = "The frame is missing from the trace exec upload: assume the frame is unacceptable"
                    else:
                        is_acceptable = False
                        reason = "The frame did not get uploaded and thus cannot be checked for acceptability: assume it is unacceptable"
                elif self.expected_to_work:
                    is_acceptable = False
                    reason = f"The frame ID {expected_frame_id} is missing, with the trace expected to work"
                else:
                    is_acceptable = True

                    deps = ", ".join(self.report.dependencies.keys()) if len(self.report.dependencies.keys()) > 0 else "None"
                    trace_reports_count = len(self.report.trace_compatibility_reports[self.trace.id])
                    applicable_reports_count = len(self.applicable_compatibility_reports)

                    reason = f"""The frame ID {expected_frame_id} is missing but the trace was not expected to work anyway

Debug information:
    - List of provided repos: {deps}
    - # of compatibility reports for this trace on this GPU: {trace_reports_count}
    - # of applicable reports count: {applicable_reports_count}
    - Lowest compatibility agreement count (needs {self.MIN_ACCEPTABLE_AGREEMENT_COUNT}): {self.lowest_compatibity_agreement_count}
"""

                frames.append(Frame(frame_id=expected_frame_id,
                                    file_path=found_frame_path,
                                    is_acceptable=is_acceptable,
                                    reason=reason))

            return frames

        @property
        def generated_all_wanted_frames(self):
            return set(self.trace.frames_to_capture) == set(self.found_frames)

        @property
        def all_frames_acceptable(self):
            for frame in self.frames:
                if not frame.is_acceptable:
                    return False

            return True

        @property
        def had_successful_execution(self):
            return self.retcode == 0 and self.generated_all_wanted_frames

        @cached_property
        def applicable_compatibility_reports(self):
            ignored_projects = set()

            # List all of the commits relevant for the trace
            reachable_commits = defaultdict(dict)
            for trace_report in self.report.trace_compatibility_reports[self.trace.id]:
                if (project := self.report.dependencies.get(trace_report.project.name)) is None:
                    # Ignore reports for unknown projects
                    ignored_projects.add(trace_report.project.name)
                    continue
                reachable_commits[project][trace_report.commit.version] = trace_report

            # Check for every project which commits are reachable
            reports = defaultdict(list)
            for found_project, commits in reachable_commits.items():
                for commit in found_project.find_first_accessible_commits_from_head(commits.keys()):
                    reports[found_project].append(commits[commit])

            return reports

        @property
        def lowest_compatibity_agreement_count(self):
            all_reports = list(itertools.chain(*self.applicable_compatibility_reports.values()))
            if len(all_reports) == 0:
                return 0

            return min([r.agreement_count for r in all_reports])

        @property
        def expected_to_work(self):
            all_reports = list(itertools.chain(*self.applicable_compatibility_reports.values()))
            if len(all_reports) == 0:
                return False

            for report in all_reports:
                if not report.is_working:
                    return False

            return self.lowest_compatibity_agreement_count > self.MIN_ACCEPTABLE_AGREEMENT_COUNT

        @property
        def is_success(self):
            return self.had_successful_execution or not self.expected_to_work

        def upload(self, job, frame_blobs, logs_blob_id=None):
            self.job = job

            gfxinfo = self.report.gfxinfo
            self.upload_report = job.report_trace_execution(metadata=gfxinfo.all_fields,
                                                            trace=self.trace,
                                                            gpu_pciid=gfxinfo.gpu_pciid,
                                                            frame_blobs=frame_blobs,
                                                            status=self.retcode,
                                                            logs_blob_id=logs_blob_id,
                                                            execution_time=self.runtime.total_seconds())

            # Report back whether execution went successfully or not
            for project_name, repo in self.report.dependencies.items():
                project_reports = self.applicable_compatibility_reports.get(project_name)

                # If the execution status agree with the existing reports for the project, re-use them!
                if project_reports is not None and self.expected_to_work == self.had_successful_execution:
                    for report in project_reports:
                        self.report.client.trace_report_compatibility(report.commit_id, report.trace_id,
                                                                      report.gpu_id, self.had_successful_execution)
                else:
                    # We do not have existing reports to re-use for this dependency, or the outcome is different.
                    # Create a new report!
                    project = self.report.client.project_get_or_create(project_name)
                    commit = self.report.client.commit_get_or_create(project, repo.head)
                    self.report.client.trace_report_compatibility(commit.id, self.trace.id,
                                                                  self.report.gpu.id, self.had_successful_execution)

        def set_upload_report(self, report):
            self.upload_report = report

    def __init__(self, client, run_name, dependencies, result_folder):
        self.client = client
        self.run_name = run_name
        self.dependencies = dependencies
        self.result_folder = result_folder

        self.trace_execs = list()

        traces = {str(t.id): t for t in self.client.list_traces([])}
        for entry in os.scandir(path=result_folder):
            if entry.is_dir():
                trace = traces.get(entry.name.split('-')[0])
                if trace and f'{trace.id}-{trace.filename}'.startswith(entry.name):
                    self.trace_execs.append(self.TraceExec(self, trace, entry.path))

    @property
    def is_postmerge(self):
        is_merge_request = "CI_MERGE_REQUEST_ID" in os.environ
        is_known_project = os.environ.get("CI_PROJECT_PATH") in ["tanty/mesa-valve-ci",
                                                                 "mesa/mesa"]  # TODO: Add more projects here as we grow
        is_official_branch = re.match(r"(staging/)?\d{2}\.\d|main",
                                      os.environ.get("CI_COMMIT_BRANCH", "")) is not None

        return not is_merge_request and is_known_project and is_official_branch

    @cached_property
    def gfxinfo(self):
        try:
            with open(f"{self.result_folder}/gfxinfo.json") as f:
                return GfxInfo(json.loads(f.read()))
        except Exception:
            return GfxInfo({})

    @cached_property
    def gpu(self):
        return self.client.gpu_get_by_pciid(self.gfxinfo.gpu_pciid)

    @cached_property
    def trace_compatibility_reports(self):
        return self.client.trace_list_compatibly_reports(self.gfxinfo.gpu_pciid)

    @classmethod
    def upload_frame(cls, client, frame_path):
        file_name = os.path.basename(frame_path)
        blob = client._upload_frame_blob(frame_path, file_name)

        return blob.signed_id

    @classmethod
    def upload_logs(cls, client, logs_path):
        if logs_path is None:
            return None

        file_name = os.path.basename(logs_path)
        blob = client._upload_logs_blob(logs_path, file_name)
        return blob.signed_id

    def error_callback(self, result):
        print(f"ERROR: {result}")

    @timeit
    def upload(self):
        print("Uploading the report")

        # Create the job in the website
        print(f" - Creating the job {self.run_name}")
        job = self.client.job_get_or_create(self.run_name,
                                            timeline_metadata={"project": os.environ.get('CI_PROJECT_PATH_SLUG')},
                                            is_released_code=self.is_postmerge)

        # Check what has already been uploaded, so we can ignore it :)
        print(" - Fetching the list of already-uploaded trace executions")
        existing_trace_execs = {te.trace.id: te for te in self.client.trace_exec_list(gpu_pciid=self.gfxinfo.gpu_pciid,
                                                                                      job_id=job.id)}
        print(f" - Found {len(existing_trace_execs)} already-uploaded trace executions")
        for trace_exec in self.trace_execs:
            if report := existing_trace_execs.get(trace_exec.trace.id):
                trace_exec.set_upload_report(report)

        # Perform the upload in multiple processes
        with Pool(processes=max(os.cpu_count(), 10)) as pool:
            # Upload in parallel all the generated frame outputs
            trace_execs_frame_uploads = dict()
            trace_execs_logs = dict()
            for trace_exec in self.trace_execs:
                # Ignore the trace executions we already reported
                if trace_exec.upload_report is not None:
                    continue

                # Schedule the upload of the generated frames
                trace_execs_frame_uploads[trace_exec] = dict()
                for frame_id, frame_path in trace_exec.found_frames.items():
                    async_job = pool.apply_async(self.upload_frame, (self.client, frame_path),
                                                 error_callback=self.error_callback)
                    trace_execs_frame_uploads[trace_exec][frame_id] = async_job

                # Schedule the upload of the execution log
                if trace_exec.logs_path is not None:
                    logs_upload_job = pool.apply_async(self.upload_logs, (self.client, trace_exec.logs_path),
                                                       error_callback=self.error_callback)
                else:
                    logs_upload_job = None
                trace_execs_logs[trace_exec] = logs_upload_job

            # Create all the trace execution objects
            for trace_exec, frames_tasks in trace_execs_frame_uploads.items():
                try:
                    print(f" - Uploading the results from {trace_exec.trace}")

                    frame_blobs = dict()
                    for frame_id, task in frames_tasks.items():
                        if not task.ready():
                            print(f"   - Waiting on the upload of the frame {frame_id}")

                        frame_blobs[str(frame_id)] = task.get()

                    if logs_task := trace_execs_logs[trace_exec]:
                        if not logs_task.ready():
                            print("   - Waiting on the upload of the execution log")
                        logs_blob_id = logs_task.get()
                    else:
                        logs_blob_id = None

                    trace_exec.upload(job, frame_blobs, logs_blob_id=logs_blob_id)
                except Exception:
                    traceback.print_exc()
                    print(" - Ignoring this trace execution")

            print(" - Done uploading the report")

    @property
    def all_frames(self):
        return list(itertools.chain(*[te.frames for te in self.trace_execs]))

    @property
    def all_unacceptable_frames(self):
        return [f for f in self.all_frames if not f.is_acceptable]

    @timeit
    def generate_junit_result(self):
        def strip_control_characters(input):
            if input:
                # unicode invalid characters
                RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                                 u'|' + \
                                 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                                 (chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                                  chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff),
                                  chr(0xd800), chr(0xdbff), chr(0xdc00), chr(0xdfff))
                input = re.sub(RE_XML_ILLEGAL, "", input)

                # ascii control characters
                input = re.sub(r"[\x01-\x09\x11-\x1F\x7F]", "", input)

            return input

        total_time = sum([te.runtime for te in self.trace_execs], start=datetime.timedelta())

        tree = ET.ElementTree("tree")

        run_id = f"{self.run_name}-{self.gfxinfo.gpu_codename}"
        testsuites = ET.Element('testsuites',
                                id=run_id,
                                name=f"Valve trace run for the job {self.run_name} on {self.gfxinfo.gpu_codename}",
                                tests=str(len(self.all_frames)),
                                failures=str(len(self.all_unacceptable_frames)),
                                time=str(total_time.total_seconds()))

        for trace_exec in self.trace_execs:
            ts_id = f"{run_id}-{trace_exec.trace.filename}"
            frames = trace_exec.frames
            failed_frames = [r for r in frames if not r.is_acceptable]

            ts = ET.SubElement(testsuites, "testsuite", id=ts_id,
                               name=f"{trace_exec.trace.filename} on {self.gfxinfo.gpu_codename}",
                               tests=str(1 + len(frames)),
                               failures=str((0 if trace_exec.is_success else 1) + len(failed_frames)),
                               time=str(trace_exec.runtime.total_seconds()))

            ts_exec = ET.SubElement(ts, "testcase",
                                    id=f"{ts_id}-execution",
                                    name=f"{trace_exec.trace.filename}'s overall execution",
                                    time=str(trace_exec.runtime.total_seconds()))

            if not trace_exec.had_successful_execution:
                ET.SubElement(ts_exec, "system-out").text = strip_control_characters(trace_exec.logs)

                if trace_exec.retcode is None:
                    msg = "ERROR: The trace execution failed to complete."
                else:
                    msg = f"ERROR: The trace execution's exit code was {trace_exec.retcode}."

                if not trace_exec.generated_all_wanted_frames:
                    msg += " Some frames are missing."

                if trace_exec.expected_to_work:
                    ET.SubElement(ts_exec, "failure", message=msg, type="ERROR")

            for frame in frames:
                frame_element = ET.SubElement(ts, "testcase",
                                              id=f"{ts_id}-{frame.frame_id}",
                                              name=f"{trace_exec.trace.filename}'s frame {frame.frame_id}",
                                              time=str(0))

                system_out = ""
                if frame.file_path:
                    system_out += f"[[ATTACHMENT|{frame.file_path}]]\n"

                if not frame.is_acceptable:
                    ET.SubElement(frame_element, "failure", message=f"ERROR: {frame.reason}", type="ERROR")
                else:
                    system_out += f"\n{frame.reason}"

                ET.SubElement(frame_element, "system-out").text = system_out

        # Generate the final XML file
        tree._setroot(testsuites)
        ET.indent(tree, space="\t", level=0)
        tree.write(os.path.join(self.result_folder, "junit.xml"), encoding="UTF-8", xml_declaration=True)

    @cached_property
    def is_success(self):
        for trace_exec in self.trace_execs:
            # The run was successful if all the traces executed
            if not trace_exec.had_successful_execution and trace_exec.expected_to_work:
                return False
            elif not trace_exec.all_frames_acceptable:
                return False

        return True


def traces_under_gb(traces_list, gb: float):
    """Return a list of traces from `traces_list` that are less than
    `gb` in total size. There's more than one way to solve a
    bin-packing problem like this, here the choice is to return the
    most traces that will fit, rather than the least."""
    max_bytes = gb * 1024**3
    taken_bytes = 0
    selected_traces = []
    for trace in sorted(traces_list, key=operator.attrgetter('size')):
        taken_bytes += trace.size
        if taken_bytes >= max_bytes:
            break
        selected_traces.append(trace)
    return selected_traces


def generate_job_results_folder_name():
    if 'CI_JOB_NAME' in os.environ:
        # Gitlab job IDs can be rather exotic, be safe.
        ci_job_name_safe = str_to_safe_filename(os.environ["CI_JOB_NAME"])
        return f'{ci_job_name_safe}-results'
    else:
        return 'results'


def run_job(traces_client, args):
    if args.access_token is None:
        print("ERROR: No access token given to the client")
        sys.exit(1)

    minio_client = minio.Minio(
        endpoint=urlparse(args.minio_url).netloc,
        access_key=args.user,
        secret_key=args.access_token,
        secure=args.secure)

    # Get the list of traces we want to run
    traces_to_cache = traces_client.list_traces([])

    # Limit the list of traces to fit in the storage limits of the machine
    if args.max_trace_db_size_gb is not None:
        traces_to_cache = traces_under_gb(traces_to_cache, args.max_trace_db_size_gb)

    if not args.skip_trace_download:
        cache_all_traces_to_local_minio(minio_client, args.bucket, traces_to_cache)

    # Create the root folder for the run
    job_folder_path = generate_job_results_folder_name()
    shutil.rmtree(job_folder_path, ignore_errors=True)
    ensure_dir(job_folder_path)

    # Debugging aid to know which job ID created this job folder.
    open(os.path.join(job_folder_path, f'{job_id()}.job'), 'w').close()

    # Create the execution scripts for every trace
    for trace in traces_to_cache:
        trace_file_path = os.path.join(args.traces_db, trace_name(trace))

        object_name = Path(trace_name(trace)).stem
        trace_job_path = os.path.join(job_folder_path, object_name)
        ensure_dir(trace_job_path)

        with open(f"{trace_job_path}/exec.sh", 'w') as f:
            f.write(trace.exec_script(trace_file_path, trace_job_path))

    if not args.generate_job_folder_only:
        if not args.local_run:
            # It is assumed here the job definition has been generated and place in this file.
            # Make it an argument?
            cp = subprocess.call([args.executor_client,
                                  "run",
                                  "-w",  # Wait for the machine to become available
                                  "-a", f"valvetraces:{args.access_token}",
                                  "-g", args.minio_valvetraces_group_name,
                                  "-j", job_id(),
                                  "-s", job_folder_path,
                                  args.executor_job_path])

            print(f"The client exited with the return code {cp}")
        else:
            cmd = f"find {job_folder_path} -name exec.sh -exec sh '{{}}' ';'"
            os.system(cmd)

        args.results = job_folder_path
        return report_results(traces_client, args)

    return 0


def report_results(traces_client, args):
    # Create a dictionary of dependencies for our execution
    dependencies = {}
    if args.mesa:
        dependencies["Mesa"] = GitRepo("Mesa", args.mesa)

    report = Report(client=traces_client, run_name=args.run_name,
                    dependencies=dependencies, result_folder=args.results)

    job_type = "post-merge" if report.is_postmerge else "pre-merge"
    print(f"Generating a {job_type} report")

    report.upload()
    report.generate_junit_result()

    return 0 if report.is_success else 1


def main():
    parser = argparse.ArgumentParser(prog='Valve trace runner')
    parser.add_argument("-s", '--valvetraces-url', dest='valvetraces_url',
                        default=os.environ.get("VALVETRACES_SERVER", 'https://linux-perf.steamos.cloud'))
    parser.add_argument("-u", '--valvetraces-user', dest='valvetraces_user',
                        default=os.environ.get("VALVETRACES_USERNAME", None))
    parser.add_argument("-r", '--run-name', dest='run_name', required=True)
    parser.add_argument('--mesa', help='Path to the mesa repo')

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser('run', help='Run the traces and report')
    run_parser.add_argument("-m", '--minio-url', dest='minio_url',
                            default=os.environ.get("VALVETRACES_MINIO_URL", "http://localhost:9000"),
                            help='URL to the Minio service')
    run_parser.add_argument('-u', '--user',
                            default=os.environ.get('VALVETRACES_MINIO_USER', 'valvetraces'),
                            help='User to access Minio with, default is "traces".')
    # REVIEW: Is there a way to have this pick its value from an
    # environment variable *and* be a required argument, that is,
    # absence of the environment variable won't require special casing
    # after argument parsing?
    run_parser.add_argument('-p', '--access-token',
                            default=os.environ.get('VALVETRACES_BUCKET_PASSWORD', None),
                            help='Access token for the traces bucket in the Minio instance.')
    run_parser.add_argument('-b', '--bucket', default=os.environ.get('VALVETRACES_BUCKET', 'valvetraces'),
                            help='The name of the bucket to cache matching traces into. Defaults to "valvetraces"')
    run_parser.add_argument('--traces-db', default=os.environ.get('VALVETRACES_TRACES_DB', '/traces'),
                            help='The path to directory containing all available traces. Defaults to /traces')
    run_parser.add_argument('--executor-client', default=os.environ.get('VALVETRACES_EXECUTOR_CLIENT', 'client.py'),
                            help='The path to the executor client command')
    run_parser.add_argument('--executor-job-path', default=os.environ.get('VALVETRACES_EXECUTOR_JOB', 'b2c.yml.jinja2'),
                            help='The path to the job definition for the executor to run')
    run_parser.add_argument('--minio-valvetraces-group-name', default=os.environ.get('VALVETRACES_GROUP_NAME', "valvetraces-ro"),
                            help="The group name to add the job user to for valve traces bucket access")
    run_parser.add_argument('--local-run', default=False, action='store_true',
                            help="Do not submit any jobs, useful for development")
    run_parser.add_argument('--max-trace-db-size-gb', type=float,
                            help="Stop collecting traces when the total download size would exceed N GB. Useful for quick tests and impoverished DUTs!")
    run_parser.add_argument('--skip-trace-download', default=False, action='store_true',
                            help="Do not attempt to resync remote trace files")
    run_parser.add_argument('--generate-job-folder-only', default=False, action='store_true',
                            help="Do not try to replay the traces, just generate the job folder")
    run_parser.add_argument('--secure', default=False,
                            help='Whether to use TLS to connect to the Minio endpoint. Default is False.')
    run_parser.set_defaults(func=run_job)

    report_parser = subparsers.add_parser('report', help='Report an already-created run')
    report_parser.add_argument('results', help='Folder containing the results to report')
    report_parser.set_defaults(func=report_results)

    args = parser.parse_args()

    if args.valvetraces_user is None:
        print("ERROR: No traces server username specified")
        sys.exit(1)

    traces_client = Client(url=args.valvetraces_url, username=args.valvetraces_user)

    try:
        entrypoint = args.func
    except AttributeError:
        parser.print_help()
        sys.exit(0)

    sys.exit(entrypoint(traces_client, args))


if __name__ == '__main__':
    main()
