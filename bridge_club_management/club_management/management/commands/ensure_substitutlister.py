import datetime
from django.core.management.base import BaseCommand
from club_management.models import Week, Substitutliste

class Command(BaseCommand):
    help = 'Ensure there are substitutlister for all weekdays in all weeks and delete old ones'

    def handle(self, *args, **kwargs):
        # Define the weekdays in Danish
        weekdays = ['mandag', 'tirsdag', 'onsdag', 'torsdag', 'fredag']

        # Get all weeks
        weeks = Week.objects.all()
        week_names = weeks.values_list('name', flat=True)

        # Delete substitutlister for old weeks
        Substitutliste.objects.exclude(week__name__in=week_names).delete()

        for week in weeks:
            # Extract the week number and year from the week's name
            week_number, year = map(int, week.name.split('-'))

            for i, weekday in enumerate(weekdays):
                # Calculate the date for the given weekday in the given week
                week_start_date = datetime.date.fromisocalendar(year, week_number, 1)
                weekday_date = week_start_date + datetime.timedelta(days=i)

                # Calculate the deadline (6 PM the day before)
                deadline = datetime.datetime.combine(weekday_date, datetime.time(18, 0)) - datetime.timedelta(days=1)

                # Create the name for the substitutliste
                substitutliste_name = f"{weekday}_{week_number}-{year}"

                # Ensure the substitutliste exists
                Substitutliste.objects.get_or_create(
                    name=substitutliste_name,
                    week=week,
                    day=weekday_date,
                    defaults={'deadline': deadline}
                )

        self.stdout.write(self.style.SUCCESS('Successfully ensured substitutlister for all weekdays in all weeks and deleted old ones'))