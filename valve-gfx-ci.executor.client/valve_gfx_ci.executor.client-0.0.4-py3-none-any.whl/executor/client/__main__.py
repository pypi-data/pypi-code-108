from collections import namedtuple
import argparse
import sys
import os

from . import Job
from .client import logger


def run_job(args):
    # Perform validation on the share directory
    if args.share_directory:
        if not os.path.isdir(args.share_directory):
            if os.path.exists(args.share_directory):
                raise ValueError("The share directory is not a folder")
            else:
                os.makedirs(args.share_directory)

    minio_creds = None
    if args.minio_auth:
        MinIOCredentials = namedtuple('MinIOCredentials', ['access_key', 'secret_key'])

        fields = args.minio_auth.split(':')
        if len(fields) == 2:
            access, secret = fields
            minio_creds = MinIOCredentials(access, secret)
        else:
            raise ValueError("Incorrect format for the --minio-auth parameter. "
                             "Format: <Access Key>:<Secret Key>")

    job = Job.from_file(executor_url=args.executor_url, path=args.job,
                        wait_if_busy=args.wait, job_id=args.job_id,
                        callback_host=args.callback, machine_tags=args.machine_tags,
                        machine_id=args.machine_id, share_directory=args.share_directory,
                        minio_creds=minio_creds, minio_groups=args.minio_group)

    status = job.run()
    logger.info("status: %s", status)
    sys.exit(status.status_code)


def main():
    parser = argparse.ArgumentParser(prog='Executor client')
    parser.add_argument("-e", '--executor', dest='executor_url',
                        default="http://localhost",
                        help='URL to the executor service')

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser('run', help='run a job')
    run_parser.add_argument("-w", "--wait", action="store_true",
                            help="Wait for a machine to become available if all are busy")
    run_parser.add_argument("-c", "--callback",
                            help=("Hostname that the executor will use to connect back to this client, "
                                  "useful for non-trivial routing to the test device"))
    run_parser.add_argument("-t", "--machine-tag", action="append", dest="machine_tags",
                            help="Tag of the machine that should be running the job. Overrides the job's target.")
    run_parser.add_argument("-i", "--machine-id",
                            help="ID of the machine that should run the job. Overrides the job's target.")
    run_parser.add_argument("-s", "--share-directory",
                            help=("Directory that will be forwarded to the job, and whose changes will be "
                                  "forwarded back to"))
    run_parser.add_argument("-j", "--job-id", help="Identifier for the job, if you have one already.")
    run_parser.add_argument("-a", "--minio-auth", default=os.environ.get('VALVE_MINIO_AUTH_CREDENTIALS'),
                            help="MinIO credentials that has access to all the groups specified using '-g'")
    run_parser.add_argument("-g", "--minio-group", action="append",
                            help=("Add the MinIO job user to the specified group. Requires valid "
                                  "credentials specified using '--minio-auth' which already "
                                  "have access this group"))
    run_parser.add_argument("job", help='Job that should be run')
    run_parser.set_defaults(func=run_job)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
