import os
import datetime
import shutil
from django.core.management import call_command
from django.conf import settings

def backup_database():
    # Ensure the backup directory exists
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Generate a timestamp for the backup file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.json')

    # Use Django's dumpdata command to create a JSON backup
    with open(backup_file, 'w') as f:
        call_command('dumpdata', '--indent', '2', stdout=f)

    print(f"Backup created: {backup_file}")

    # Delete backups older than 30 days
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    for filename in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, filename)
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_modified < thirty_days_ago:
            os.remove(file_path)
            print(f"Deleted old backup: {file_path}")

if __name__ == '__main__':
    # Setup Django environment
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bridge_club_management.settings")
    django.setup()

    backup_database()
