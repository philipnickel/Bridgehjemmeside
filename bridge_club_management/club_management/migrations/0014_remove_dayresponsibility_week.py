# Generated by Django 4.1 on 2024-03-18 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0013_remove_customuser_unavailable_days_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dayresponsibility',
            name='week',
        ),
    ]
