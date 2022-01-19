from django.core.management.base import BaseCommand
import boto3
import gzip
import shutil
import os
import subprocess
from datetime import datetime


class Command(BaseCommand):
    help = "Prints a list of environment variables for eb setenv"

    def add_arguments(self, parser):
        # parser.add_argument("example", type=str)
        pass

    def handle(self, *args, **options):

        # Configurable Settings
        home = os.path.expanduser("~")
        log_dir = os.environ.get('LOG_DIR', os.path.join(home, 'Documents', 'logs'))
        aws_key = os.environ.get('AWS_KEY', os.path.join(home, '.aws', 'config'))

        # Make sure local paths exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.isfile(aws_key):
            print(f"\nERROR: Missing AWS key file: {aws_key}")
            exit(1)

        # Get AWS key
        aws_access_key_id = aws_secret_access_key = None
        try:
            with open(aws_key, 'r') as f_in:
                for line in f_in.read().splitlines():
                    if line.startswith('aws_access_key_id'):
                        aws_access_key_id = line.split('=')[1].strip()
                    if line.startswith('aws_secret_access_key'):
                        aws_secret_access_key = line.split('=')[1].strip()
        except Exception as ee:
            print(f"Error reading file: {aws_key}")
        if not (aws_access_key_id and aws_secret_access_key):
            print("Could not locate AWS keys.")
            exit(1)

        # Bucket and S3 data
        bucket_name = 'elasticbeanstalk-us-west-2-921749119607'
        s3_log_path = "resources/environments/logs/publish/"

        # Get S3 access
        s3 = bucket = None
        try:
            s3 = boto3.resource(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
            bucket = s3.Bucket(bucket_name)
        except Exception as ee:
            print(f"Error getting S3 bucket: {ee}")
            exit(1)

        # Get environment name and instance IDs
        app_name = None
        instances = []
        try:
            process = subprocess.Popen(
                ["eb", "list", "-v"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
            (output, stderr) = process.communicate()
            for line in output.splitlines():
                line = str(line)
                if "['i-" in line:
                    ii = line.split('[')[1].replace("'", '').replace('"', '').replace(']', '').strip()
                    instances.append(ii)
                elif 'Application:' in line:
                    app_name = line.replace('Application:', '')[1:].replace("'", '').strip()
        except Exception as ee:
            print(f"Unable to list environments: {ee}")

        if not instances:
            print(f"\n\tNo environment instances were found. \n\n\tDo you need to run `eb init` ?\n")
            exit(1)

        if not app_name:
            app_name = os.path.basename(os.path.dirname(os.path.realpath('.')))

        # Get applications with S3 logging
        env_data = {}
        for object_summary in bucket.objects.filter(Prefix=s3_log_path):
            try:
                pieces = object_summary.key.replace(s3_log_path, '').split('/')
                app_id = pieces[0]
                env_id = pieces[1]
                file_name = pieces[2]
                if app_id not in env_data:
                    env_data[app_id] = {'name': None, 'env': {}}
                if env_id not in env_data[app_id]['env']:
                    env_data[app_id]['env'][env_id] = None
            except Exception as ee:
                print(f"App/Env detection exception: {ee}")

        # Determine current application ID
        print("\nLocating EB instances with S3 logs...")
        current_app_id = None
        for app_id, app_info in env_data.items():
            for env_id, sid in app_info['env'].items():
                if env_id in instances:
                    current_app_id = app_id

            pre = " *" if current_app_id == app_id else "  "
            print(f"{pre}{app_id} has logs from {len(app_info['env'])} instances")

        if not current_app_id:
            print(f"\n\tUnable to detect current application \n\n\tAre logs configured to be saved in S3?\n")
            exit(1)

        # Prepare download directories
        download_path = os.path.join(log_dir, app_name)
        log_types = {
            'web.stdout': os.path.join(download_path, 'web'),
            'access.log': os.path.join(download_path, 'access'),
            'error.log': os.path.join(download_path, 'error'),
            'eb-hooks.log': os.path.join(download_path, 'hooks'),
            'eb-engine.log': os.path.join(download_path, 'engine'),
            'daemon.log': os.path.join(download_path, 'daemon'),
            'unknown.log': download_path,
        }
        for flag, folder in log_types.items():
            if not os.path.isdir(folder):
                os.makedirs(folder)

        # Record the files already downloaded
        have_files = {}
        for flag, folder in log_types.items():
            have_files[flag] = os.listdir(folder)

        print(f"\nGetting logs for {app_name} ({current_app_id})...")

        file_stats = {flag: {'D': 0, 'S': 0, 'X': 0} for flag, folder in log_types.items()}
        app_log_path = os.path.join(s3_log_path, current_app_id)

        # Timestamp for file age comparison
        now = datetime.now().replace(tzinfo=None)

        for object_summary in bucket.objects.filter(Prefix=app_log_path):
            date_string = gz_path = gz_name = log_path = log_name = None

            # Determine log type key
            key = 'unknown.log'
            for flag, folder in log_types.items():
                if flag in object_summary.key:
                    key = flag
                    break

            try:
                file_date = object_summary.last_modified.replace(tzinfo=None)
                date_string = object_summary.last_modified.strftime("%Y-%m-%d_%H:%M:%S")
                gz_path = f"{log_types.get(key)}/{date_string}.gz"
                log_path = f"{log_types.get(key)}/{date_string}.log"
                gz_name = os.path.basename(gz_path)
                log_name = os.path.basename(log_path)
                have_it = log_name in have_files.get(key)
            except Exception as ee:
                print(f"  Unable to analyze {gz_path}: {ee}")
                continue

            if have_it:
                file_stats.get(key)['S'] += 1

            else:
                print(f"  {gz_name} --> {log_path}")
                bucket.download_file(object_summary.key, gz_path)
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(log_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.unlink(gz_path)
                file_stats.get(key)['D'] += 1

            # Delete if older than 30 days
            if (now - file_date).days > 30:
                try:
                    object_summary.delete()
                    file_stats.get(key)['X'] += 1
                except Exception as ee:
                    print(f"  Unable to delete {gz_path}: {ee}")

        print("\n")

        # Print summary of actions taken
        print(f"Summary of actions for {app_name}:\n")
        print(f"{'Log Type'.ljust(15)}    {'Downloaded'.ljust(15)}    {'Skipped'.ljust(15)}    {'Deleted'.ljust(15)}")
        print(f"{'='.ljust(15, '=')}    {'='.ljust(15, '=')}    {'='.ljust(15, '=')}    {'='.ljust(15, '=')}")
        for flag, folder in log_types.items():
            print(f"{flag.ljust(15)}    {str(file_stats.get(flag)['D']).ljust(15)}    {str(file_stats.get(flag)['S']).ljust(15)}    {str(file_stats.get(flag)['X']).ljust(15)}")
        print("\n")
