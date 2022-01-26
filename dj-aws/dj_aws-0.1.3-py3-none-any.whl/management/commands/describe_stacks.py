from django.core.management.base import BaseCommand

from djaws import cloudformation_api


class Command(BaseCommand):
    help = 'Describe Cloud Formation Stack'

    def add_arguments(self, parser):
        parser.add_argument(
            "--stack_name",
            type=str,
            help="S3 Region",
        )

    def handle(self, *args, **kwargs):

        stack_name = kwargs['stack_name']
        cf_client = cloudformation_api.cf_session_client()
        try:
            r_stacks = cloudformation_api.describe_stacks(cf_client, stack_name=stack_name)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error while running command:\n{str(e)}'))
            raise e
        else:
            stack = r_stacks.first_stack
            self.stdout.write(self.style.MIGRATE_LABEL(f'Successfully got stack details.'))
            msg = f'id: {stack.stack_id}\nname: {stack.stack_name}\nstatus: {stack.stack_status}'
            self.stdout.write(self.style.MIGRATE_LABEL(msg))


