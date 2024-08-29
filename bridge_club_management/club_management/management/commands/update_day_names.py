from django.core.management.base import BaseCommand
from club_management.models import Day

class Command(BaseCommand):
    help = 'Updates the English names for existing Day objects'

    def handle(self, *args, **options):
        day_mapping = {
            'Mandag': 'Monday',
            'Tirsdag': 'Tuesday',
            'Onsdag': 'Wednesday',
            'Torsdag': 'Thursday',
            'Fredag': 'Friday',
            'Lørdag': 'Saturday',
            'Søndag': 'Sunday',
            'Alle': 'Any',
        }

        for day in Day.objects.all():
            if day.name in day_mapping:
                day.english_name = day_mapping[day.name]
                day.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {day.name} to {day.english_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'No English name found for {day.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated English names for days'))