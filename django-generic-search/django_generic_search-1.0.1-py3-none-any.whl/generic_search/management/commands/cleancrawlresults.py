from django.core.management.base import BaseCommand
from ...searchbot.utils.base import clean_data

class Command(BaseCommand):
    help = 'Cleans data received after crawler completes crawling and saves data'

    def handle(self, *args, **kwargs):
        clean_data()