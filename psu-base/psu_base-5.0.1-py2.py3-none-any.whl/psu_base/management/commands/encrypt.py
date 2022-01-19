from django.core.management.base import BaseCommand, CommandError
from psu_base.classes.Encryptor import Encryptor


class Command(BaseCommand):
    help = "Encrypts a value using the PSU Base secret key."

    def add_arguments(self, parser):
        parser.add_argument("value", type=str)

    def handle(self, *args, **options):
        encryptor = Encryptor()
        result = encryptor.encrypt(options["value"])
        print("\nThe encrypted value is:\n")
        print(result)
        print()
        # self.stdout.write(result)
