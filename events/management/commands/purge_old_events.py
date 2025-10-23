# events/management/commands/purge_old_events.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from events.models import Event   # make sure your app name is correct

class Command(BaseCommand):  # <-- this class name MUST be exactly 'Command'
    help = 'Deletes all events older than 6 months from the current date.'

    def handle(self, *args, **options):
        # Calculate 6 months ago (roughly 6x30 days)
        cutoff_date = timezone.now() - timedelta(days=6*30)

        # Get and delete events older than that date
        old_events = Event.objects.filter(date_time__lt=cutoff_date)
        count = old_events.count()
        old_events.delete()

        # Print result
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old event(s).'))
