from django.core.management.base import BaseCommand

from ingress.models import Message


class Command(BaseCommand):
    def handle(self, *args, **options):
        result = Message.objects.consumed().delete()
        self.stdout.write(f"Deleted {result[0]} consumed messages from the queue.")
