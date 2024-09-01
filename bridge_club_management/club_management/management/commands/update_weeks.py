import datetime
from django.core.management.base import BaseCommand
from club_management.models import Week

class Command(BaseCommand):
    help = 'Delete the current week and ensure there are weeks created for the next 5 weeks'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        current_week_number = today.isocalendar()[1]

        # Delete the current week
        Week.objects.filter(name=str(current_week_number)).delete()

        # Ensure there are weeks created for the next 5 weeks
        for i in range(1, 6):
            future_date = today + datetime.timedelta(weeks=i)
            future_week_number = future_date.isocalendar()[1]
            week_name = str(future_week_number)
            Week.objects.get_or_create(name=week_name)

        self.stdout.write(self.style.SUCCESS('Successfully updated weeks'))