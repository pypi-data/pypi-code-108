#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime

import traceback
import flask
import json

from .executor import SergentHartman, MachineState
from .mars import Mars, Machine
from .minioclient import MinioClient
from .boots import BootService
from .message import JobStatus
from .job import Job, Target
from . import config


class CustomJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JobStatus):
            return obj.name
        elif isinstance(obj, SergentHartman):
            return {
                "is_active": obj.is_active,
                "is_registered": obj.is_machine_registered,
                "boot_loop_counts": obj.boot_loop_counts,
                "qualifying_rate": obj.qualifying_rate,
                "current_loop_count": obj.cur_loop,
                "statuses": dict([(s.name, val) for s, val in obj.statuses.items()]),
            }
        elif isinstance(obj, MachineState):
            return obj.name
        elif isinstance(obj, Machine):
            return {
                "state": obj.executor.state,
                "ready_for_service": obj.ready_for_service,
                "has_pdu_assigned": obj.pdu_port is not None,
                "local_tty_device": obj.local_tty_device,
                "tags": list(obj.tags),
                "base_name": obj.base_name,
                "mac_address": obj.mac_address,
                "ip_address": obj.ip_address,
                "training": obj.executor.sergent_hartman
            }

        return super().default(obj)


app = flask.Flask(__name__)
app.json_encoder = CustomJSONEncoder


@app.errorhandler(ValueError)
def handle_valueError_exception(error):
    traceback.print_exc()
    response = flask.jsonify({"error": str(error)})
    response.status_code = 400
    return response


@app.route('/api/v1/machines', methods=['GET'])
def get_machine_list():
    with app.app_context():
        mars = flask.current_app.mars

    return {
        "machines": dict([(m.id, m) for m in mars.known_machines])
    }


@app.route('/api/v1/machine/', methods=['POST', 'PUT'])
def machine_add_or_update():
    with app.app_context():
        mars = flask.current_app.mars

    for key in flask.request.json:
        if key not in {"base_name", "tags", "mac_address", "ip_address", "local_tty_device"}:
            raise ValueError(f"The field {key} cannot be set/modified")

    machine = mars.add_or_update_machine(flask.request.json)
    return CustomJSONEncoder().default(machine)


@app.route('/api/v1/machine/<machine_id>/', methods=['GET'])
def machine_detail_get(machine_id):
    with app.app_context():
        mars = flask.current_app.mars

    machine = mars.get_machine_by_id(machine_id, raise_if_missing=True)
    return CustomJSONEncoder().default(machine)


@dataclass
class MinIOCredentials:
    access_key: str
    secret_key: str


@app.route('/api/v1/jobs', methods=['POST'])
def post_job():
    def find_suitable_machine(target):
        with app.app_context():
            mars = flask.current_app.mars

        wanted_tags = set(target.tags)

        # If the target id is specified, check the tags
        if target.id is not None:
            machine = mars.get_machine_by_id(target.id)
            if machine is None:
                return None, 404, f"Unknown machine with ID {target.id}"
            elif not wanted_tags.issubset(machine.tags):
                return None, 406, (f"The machine {target.id} does not matching tags "
                                   f"(asked: {wanted_tags}, actual: {machine.tags})")
            elif machine.executor.state != MachineState.IDLE:
                return None, 409, (f"The machine {target.id} is unavailable: "
                                   f"Current state is {machine.executor.state.name}")
            return machine, 200, None
        else:
            found_a_candidate_machine = False
            for machine in mars.known_machines:
                if not wanted_tags.issubset(machine.tags):
                    continue

                found_a_candidate_machine = True
                if machine.executor.state == MachineState.IDLE:
                    return machine, 200, "success"

            if found_a_candidate_machine:
                return None, 409, f"All machines matching the tags {wanted_tags} are busy"
            else:
                return None, 406, f"No machines found matching the tags {wanted_tags}"

    class JobRequest:
        def __init__(self, request, version, raw_job, target, callback_endpoint,
                     job_bucket_initial_state_tarball_file=None, job_id=None,
                     minio_credentials=None, minio_groups=None):
            self.request = request
            self.version = version
            self.raw_job = raw_job
            self.target = target
            self.callback_endpoint = callback_endpoint
            self.minio_credentials = minio_credentials
            self.minio_groups = minio_groups

            # Clients may specify a starting state for the job bucket,
            # this will be a tarball that is extracted prior to the
            # job starting.
            self.job_bucket_initial_state_tarball_file = job_bucket_initial_state_tarball_file

            # The executor will ensure job IDs are unique, but use the
            # client-provided prefix for as a naming convention.
            if job_id is None:
                now = int(datetime.utcnow().timestamp())
                job_id = f"untitled-{now}"
            self.job_id = job_id

            # Callback validation
            if callback_endpoint[0] is None:
                raise ValueError("callback's host cannot be None. Leave empty to get the default value")
            if callback_endpoint[1] is None:
                raise ValueError("callback's port cannot be None")

        @classmethod
        def parse(cls, request):
            if request.mimetype == "application/json":
                return JSONJobRequest(request)
            elif request.mimetype == "multipart/form-data":
                return MultipartJobRequest(request)
            else:
                raise ValueError("Unknown job request format")

    # DEPRECATED: To be removed when we are sure all the clients out there have been updated
    class JSONJobRequest(JobRequest):
        def __init__(self, request):
            job_params = request.json
            metadata = job_params["metadata"]
            job = Job.from_job(job_params["job"])

            # Use the client-provided host callback if available, or default to the remote addr
            remote_addr = metadata.get("callback_host", flask.request.remote_addr)
            endpoint = (remote_addr, metadata.get("callback_port"))

            super().__init__(request=request, version=0, raw_job=job_params["job"],
                             target=job.target, callback_endpoint=endpoint)

    class MultipartJobRequest(JobRequest):
        def __init__(self, request):
            metadata_file = request.files.get('metadata')
            if metadata_file is None:
                raise ValueError("No metadata file found")

            if metadata_file.mimetype != "application/json":
                raise ValueError("The metadata file has the wrong mimetype: "
                                 "{metadata_file.mimetype}} instead of application/json")

            try:
                metadata = json.loads(metadata_file.read())
            except json.JSONDecodeError as e:
                raise ValueError(f"The metadata file is not a valid JSON file: {e.msg}")

            version = metadata.get('version')
            if version == 1:
                self.parse_v1(request, metadata)
            else:
                raise ValueError(f"Invalid request version {version}")

        def parse_v1(self, request, metadata):
            # Get the job file, and check its mimetype
            job_file = request.files['job']
            if job_file.mimetype != "application/x-yaml":
                raise ValueError("The metadata file has the wrong mimetype: "
                                 "{job_file.mimetype}} instead of application/x-yaml")

            initial_state_tarball_file = request.files.get('job_bucket_initial_state_tarball_file', None)
            if initial_state_tarball_file and initial_state_tarball_file.mimetype != "application/octet-stream":
                raise ValueError("The job_bucket_initial_state_tarball file has the wrong mimetype: "
                                 "{initial_state_tarball_file.mimetype}} instead of application/octet-stream")

            # Create a Job object
            raw_job = job_file.read().decode()
            job = Job.from_job(raw_job)

            # Get the target that will run the job. Use the job's target by default,
            # but allow the client to override the target
            if "target" in metadata:
                target = metadata.get('target', {})
                job_target = Target(target.get('id'), target.get('tags', []))
            else:
                job_target = job.target

            # Use the client-provided host callback if available, or default to the remote addr
            callback = metadata.get('callback', {})
            remote_addr = callback.get("host", request.remote_addr)
            endpoint = (remote_addr, callback.get("port"))

            # Parse the minio-related arguments request
            minio = metadata.get('minio', {})
            minio_credentials = minio.get('credentials', {})
            credentials = MinIOCredentials(access_key=minio_credentials.get("access_key"),
                                           secret_key=minio_credentials.get("secret_key"))

            super().__init__(request=request, version=1, raw_job=raw_job,
                             target=job_target, callback_endpoint=endpoint,
                             job_bucket_initial_state_tarball_file=initial_state_tarball_file,
                             job_id=metadata.get('job_id'),
                             minio_credentials=credentials,
                             minio_groups=minio.get('groups', []))

    def check_minio_credentials(job_request):
        credentials = job_request.minio_credentials

        # If no groups are requested, then exit directly
        if job_request.minio_groups is None or len(job_request.minio_groups) == 0:
            return True, ""

        # Some groups are requested, make sure some credentials have been set
        if credentials is None:
            return False, "Requested access to some groups, but the credentials are missing"

        # Make sure all the requested groups are in the list of groups the
        # provided-credentials have access to
        try:
            timestamp = int(datetime.now().timestamp())
            client = MinioClient(user=credentials.access_key,
                                 secret_key=credentials.secret_key,
                                 alias=f"a_{job_request.job_id}-{timestamp}")

            user_groups = set(client.groups_user_is_in())
            for group in job_request.minio_groups:
                if group not in user_groups:
                    return False, (f"The provided MinIO credentials do not belong to the group {group}")

            return True, ""
        except ValueError:
            return False, "Invalid MinIO credentials"
        finally:
            try:
                client.remove_alias()
            except UnboundLocalError:
                pass

    parsed = JobRequest.parse(flask.request)

    ok, error_msg = check_minio_credentials(parsed)
    if ok:
        machine, error_code, error_msg = find_suitable_machine(parsed.target)
        if machine is not None:
            machine.executor.start_job(parsed)
    else:
        error_code = 403

    if parsed.version == 0:
        response = {
            "reason": error_msg
        }
    elif parsed.version == 1:
        response = {
            # protocol version
            "version": 1,
            "error_msg": error_msg

            # TODO: Store the job in memory, and show the ID here
        }
    return flask.make_response(flask.jsonify(response), error_code)


def run():  # pragma: nocover
    # Make sure the farm name has been set
    if config.FARM_NAME is None:
        raise ValueError("Please the FARM_NAME environment variable")

    # Start the network boot service
    boots = BootService(config_paths={
        'BOOTS_ROOT': config.BOOTS_ROOT,
        'TFTP_DIR': config.BOOTS_TFTP_ROOT,
        'PXELINUX_CONFIG_DIR': config.BOOTS_PXELINUX_CONFIG_DIR,
    })

    # Create all the workers based on the machines found in MaRS
    mars = Mars(boots)
    mars.start()

    # Start flask
    with app.app_context():
        flask.current_app.mars = mars
    app.run(host=config.EXECUTOR_HOST, port=config.EXECUTOR_PORT)

    # Shutdown
    mars.stop(wait=True)
    boots.stop()


if __name__ == '__main__':  # pragma: nocover
    run()
