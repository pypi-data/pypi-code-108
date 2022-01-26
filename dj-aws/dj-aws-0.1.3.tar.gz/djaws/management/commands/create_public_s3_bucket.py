from django.core.management.base import BaseCommand

from djaws import s3_api


class Command(BaseCommand):
    help = 'Create Public S3 Bucket'

    def add_arguments(self, parser):
        parser.add_argument(
            "--bucket_name",
            required=True,
            type=str,
            help="S3 Bucket Name",
        )
        parser.add_argument(
            "--region",
            default='us-east-1',
            type=str,
            help="S3 Region",
        )

    def handle(self, *args, **kwargs):

        bucket = kwargs['bucket_name']
        region = kwargs['region']
        self.stdout.write(self.style.MIGRATE_LABEL(f'Creating Public S3 Bucket: {bucket}'))
        s3_client = s3_api.s3_session_client()
        try:
            s3_api.create_public_access_bucket(s3_client, bucket=bucket, region=region)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error while running command:\n{str(e)}'))
            raise e
        else:
            self.stdout.write(self.style.MIGRATE_LABEL(f'Successfully created Public S3 Bucket: {bucket}'))

