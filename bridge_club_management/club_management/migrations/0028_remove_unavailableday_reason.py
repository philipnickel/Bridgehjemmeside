# Generated by Django 4.2.15 on 2024-08-28 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0027_unavailableday_remove_customuser_days_unavailable_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unavailableday',
            name='reason',
        ),
    ]
