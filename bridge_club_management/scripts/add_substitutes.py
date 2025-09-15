import os
import django
import csv
from io import StringIO

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bridge_club_management.settings")
django.setup()

from club_management.models import CustomUser, Day

# Your data as a CSV string
data = """
Erik Jørgensen,22247576,Blå,Mandag
Sonja Lindgren,44651714,Blå,Mandag
Jytte Jochumsen,21738940,Blå,Tirsdag
Ingrid Aggernæs,24611718,Blå,Tirsdag
Poul Erik Schouw,29469129,Blå,Tirsdag
Kirsten Rasmussen,20618895,Blå,Tirsdag
Susanne Wennicke,31102261,Rød/Blå,Tirsdag,Par sammen med Søren Kann
Søren Kann,21784039,Rød/Blå,Tirsdag,Par sammen med Susanne Wennicke
Villy Bonke,21250818,Rød,Onsdag
Anne-Lise Sloth Nielsen,26322235,Blå,Onsdag
Charlotte Carstensen,53762463,Blå,Onsdag
Aage Bromann,41812108,Rør/Blå,Onsdag
Lone Schønberg Villadsen,40706129,Blå,Torsdag
Villy Bonke,21250818,Rød,Torsdag
Jill Merry,24243966,Blå,Torsdag
Else Ostenfeld,20479554,Rød/Blå,Torsdag
Birte Justesen,23729854,Rød/Blå,Torsdag,par sammen med Else Ostenfeld
Elsebeth Rathgen,20297486,Blå,Torsdag
Vibeke Schneider,30422320,Blå,Torsdag
Trine Haagensen,21968410,Blå,Torsdag
Iris Hansen,30230433,Blå,Torsdag,kun i lige uger
Martin Bodholdt,42940416,Blå,Fredag
Morten Jørgensen,30740085,Blå,Fredag,Par sammen med Betty Westphal Jørgensen
Betty Westphal Jørgensen,30740085,Blå,Fredag
Klaus Gundertofte,31622838,Rød,Fredag
Steen Højlund,20943778,Rød,Fredag
Lars Skovenboe,22992424,Rød,Fredag
"""

# Parse the CSV data
csv_data = csv.reader(StringIO(data.strip()), delimiter=',')

for row in csv_data:
    if len(row) >= 4:
        name, phone, level, day = row[:4]
        notes = row[4] if len(row) > 4 else ''

        # Split the name into first_name and last_name
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Create or get the user
        user, created = CustomUser.objects.get_or_create(
            username=name.replace(' ', '_').lower(),
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': '',  # Email is now optional
            }
        )

        # Update user information
        user.profile.phone_number = phone
        user.profile.level = level
        user.profile.notes = notes
        user.profile.save()

        # Add the available day
        day_obj, _ = Day.objects.get_or_create(name=day)
        user.days_available.add(day_obj)

        print(f"Added/Updated user: {name}")

print("Batch addition complete!")