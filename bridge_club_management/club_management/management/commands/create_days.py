from django.core.management.base import BaseCommand
from club_management.models import Day

class Command(BaseCommand):
    help = 'Creates the days of the week with English and Danish names'

    def handle(self, *args, **options):
        days = [
            ('Monday', 'Mandag'),
            ('Tuesday', 'Tirsdag'),
            ('Wednesday', 'Onsdag'),
            ('Thursday', 'Torsdag'),
            ('Friday', 'Fredag'),
            ('Saturday', 'Lørdag'),
            ('Sunday', 'Søndag'),
            ('Any', 'Alle'),
        ]
        for english, danish in days:
            Day.objects.get_or_create(name=danish, english_name=english)
        self.stdout.write(self.style.SUCCESS('Successfully created days'))
