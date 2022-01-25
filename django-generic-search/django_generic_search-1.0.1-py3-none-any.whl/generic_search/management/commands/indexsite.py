from django.core.management.base import BaseCommand
from ...searchbot.utils.base import generate_tfidf_index

class Command(BaseCommand):
    help = 'Triggers the searchbot crawler to crawl this site'

    def handle(self, *args, **kwargs):
        generate_tfidf_index()