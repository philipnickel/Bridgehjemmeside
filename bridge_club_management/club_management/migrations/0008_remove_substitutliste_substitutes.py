# Generated by Django 4.1 on 2024-03-18 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0007_alter_day_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='substitutliste',
            name='substitutes',
        ),
    ]
