import argparse
from datetime import datetime
from django.utils.text import slugify
from tasq_cli import jobs
from tasq_cli import projects
from tasq_cli import settings
from tasq_cli.upload import do_upload, create_csv_from_currently_uploaded_files, upload_csv


def main():
    parser = argparse.ArgumentParser(prog='tasq')
    parser.add_argument('-V', '--version', action='version', version=f'Tasq CLI {settings.VERSION}')
    parser.add_argument('-d', '--dataset-name', action='store', help='set current dataset name')
    parser.add_argument('-c', '--client-id', action='store', help='override client id')
    parser.add_argument('-b', '--bucket-name', action='store', help='override bucket name')

    # NOTE
    # in Python 3.8 you can pass an additional argument to add_subparsers
    # required=True
    subparsers = parser.add_subparsers(dest='action', metavar='action', help='action to run')

    images_parser = subparsers.add_parser('upload', help='upload files')
    images_parser.add_argument('-p', '--path', default=False, help='path to directory with images')
    images_parser.add_argument('-e', '--exclude', help='File extensions to exclude.', action='append', nargs='*')
    images_parser.add_argument('--dry', help='create upload file but dont actually upload anything', action='store_true')

    csv_parser = subparsers.add_parser('create-csv', help='create csv for files that were already uploaded')
    csv_parser.add_argument('-d', '--csv-dataset-name', action='store', help='dataset name of csv to create')
    csv_parser.add_argument('-f', '--file-name', action='store', help='one file from dataset of csv to create')
    csv_parser.add_argument('--dry', help='create upload file but dont actually upload anything', action='store_true')

    upload_csv_parser = subparsers.add_parser('upload-csv', help='upload files')
    upload_csv_parser.add_argument('project_id', default=False, help='project in which to run a job')
    upload_csv_parser.add_argument('file_name', help='csv file to upload to project')
    upload_csv_parser.add_argument('--tag', help='tag to set on all uploaded images. If not set, the file name will be the tag')
    upload_csv_parser.add_argument('--dry', help='run but dont actually upload anything', action='store_true')

    run_job_parser = subparsers.add_parser('run-job', help='run a job')
    run_job_parser.add_argument('project_id', default=False, help='project in which to run a job')
    run_job_parser.add_argument('--tag', help='tag to include')
    run_job_parser.add_argument('--type', help='job type: annotation/composite')

    list_job_parser = subparsers.add_parser('list-jobs', help='list all jobs in a project')
    list_job_parser.add_argument('project_id', help='the project id')

    export_job_parser = subparsers.add_parser('export-job', help='exports a job')
    export_job_parser.add_argument('job_id', help='the job id')
    export_job_parser.add_argument('--raw', action='store_true', help='the job id')
    export_job_parser.add_argument('--worker_data', action='store_true', help='include worker data')

    list_projects_parser = subparsers.add_parser('list-projects', help='list all projects')

    args = parser.parse_args()
    logger = settings.get_logger()

    logger.info(f'Tasq CLI {settings.VERSION}')

    # override client id if flag is present
    if args.client_id:
        settings.CLIENT_ID = args.client_id
        logger.info(f'Overriding client id with {settings.CLIENT_ID}')

    # override bucket name if flag is present
    if args.bucket_name:
        if args.bucket_name == 'tasq':
            logger.info('Setting default bucket name gits-active-storage')
            settings.BUCKET = 'gits-active-storage'
            logger.info('Setting CDN_URL to cdn.tasq.ai')
            settings.CDN_URL = 'https://cdn.tasq.ai/{object_name}'
        else:
            settings.BUCKET = args.bucket_name
            logger.info(f'Overriding bucket name with {settings.BUCKET}')

    if args.dataset_name:
        DATASET_NAME = slugify(f'{args.dataset_name}')
    else:
        # NOTE
        # This could be set as a default on line 13, but this way we get to
        # inform the user what is happening.
        dataset_timestamp = datetime.now().strftime("%Y-%m-%d")
        logger.warning(f'Dataset name required. Setting dataset name to {dataset_timestamp}')
        DATASET_NAME = dataset_timestamp

    if args.action == 'upload':
        if not args.path:
            logger.error('Path to upload is required.')
            exit(1)

        settings.dry = args.dry
        do_upload(DATASET_NAME, args.path, args.exclude, settings)

    if args.action == 'create-csv':
        create_csv_from_currently_uploaded_files(args.csv_dataset_name, args.file_name, settings) 

    if args.action == 'upload-csv':
        upload_csv(args.file_name, args.project_id, args.tag)

    result = None
    if args.action == 'run-job':
        result = jobs.run_job(args.project_id, args.tag)
    if args.action == 'list-jobs':
        result = jobs.list_jobs(args.project_id)
    if args.action == 'export-job':
        result = jobs.export_job(args.job_id, args.raw, args.worker_data)
    if args.action == 'list-projects':
        result = projects.list_projects()

    if result:
        print(result)


if __name__ == "__main__":
    main()
