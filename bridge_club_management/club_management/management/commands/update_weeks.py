import datetime
from django.core.management.base import BaseCommand
from club_management.models import Week

class Command(BaseCommand):
    help = 'Delete the previous week and ensure there are weeks created for the next 5 weeks'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        current_week_number = today.isocalendar()[1]
        current_year = today.year

        # Calculate the previous week
        previous_week_date = today - datetime.timedelta(weeks=1)
        previous_week_number = previous_week_date.isocalendar()[1]
        previous_year = previous_week_date.year

        # Delete the previous week
        Week.objects.filter(name=str(previous_week_number)).delete()

        # Ensure there are weeks created for the next 5 weeks
        for i in range(1, 6):
            future_date = today + datetime.timedelta(weeks=i)
            future_week_number = future_date.isocalendar()[1]
            future_year = future_date.year
            week_name = str(future_week_number)

            # Check if the week already exists
            if not Week.objects.filter(name=week_name).exists():
                Week.objects.create(name=week_name)

        self.stdout.write(self.style.SUCCESS('Successfully updated weeks'))