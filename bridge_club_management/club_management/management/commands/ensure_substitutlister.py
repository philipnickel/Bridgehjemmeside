import datetime
from django.core.management.base import BaseCommand
from club_management.models import Week, Substitutliste

class Command(BaseCommand):
    help = 'Ensure there are substitutlister for all weekdays in all weeks and delete old ones'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        current_week_number = today.isocalendar()[1]
        current_year = today.year

        # Get all weeks
        weeks = Week.objects.all()
        week_numbers = weeks.values_list('name', flat=True)

        # Define the weekdays in Danish
        weekdays = ['mandag', 'tirsdag', 'onsdag', 'torsdag', 'fredag']

        # Delete substitutlister for old weeks
        Substitutliste.objects.exclude(week__name__in=week_numbers).delete()

        for week in weeks:
            week_number = int(week.name)
            for i, weekday in enumerate(weekdays):
                # Calculate the date for the given weekday in the given week
                week_start_date = datetime.date.fromisocalendar(current_year, week_number, 1)
                weekday_date = week_start_date + datetime.timedelta(days=i)

                # Handle year transition
                if weekday_date.year != current_year:
                    current_year = weekday_date.year

                # Calculate the deadline (6 PM the day before)
                deadline = datetime.datetime.combine(weekday_date, datetime.time(18, 0)) - datetime.timedelta(days=1)

                # Create the name for the substitutliste
                substitutliste_name = f"{weekday}_{week_number}"

                # Ensure the substitutliste exists
                Substitutliste.objects.get_or_create(
                    name=substitutliste_name,
                    week=week,
                    day=weekday_date,
                    defaults={'deadline': deadline}
                )

        self.stdout.write(self.style.SUCCESS('Successfully ensured substitutlister for all weekdays in all weeks and deleted old ones'))