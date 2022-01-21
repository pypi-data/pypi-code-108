import subprocess, os
from django.core.management import BaseCommand
import askbot

DOC_DIR = os.path.join(askbot.get_install_directory(), 'doc')

class Command(BaseCommand):
    def handle(self, **options):
        os.chdir(DOC_DIR)
        subprocess.call(['make', 'html'])
