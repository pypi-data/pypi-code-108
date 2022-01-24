from django.core.management.base import BaseCommand

from security import requests


class Command(BaseCommand):

    def handle(self, **options):
        requests.post('http://localhost/test')
