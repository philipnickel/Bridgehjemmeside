from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from club_management.models import Substitutliste

class Command(BaseCommand):
    help = 'Automatically creates and deletes substitution lists'

    def handle(self, *args, **options):
        # Calculate the dates for two months ahead and the current date
        today = datetime.now().date()
        two_months_ahead = today + timedelta(days=60)

        # Create substitution lists for dates two months ahead
        for date in range(today, two_months_ahead):
            # Check if a substitution list already exists for the date
            if not Substitutliste.objects.filter(day=date).exists():
                Substitutliste.objects.create(day=date)  # Create a new substitution list

        # Delete old substitution lists prior to the current date
        Substitutliste.objects.filter(day__lt=today).delete()

