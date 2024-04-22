# Generated by Django 4.1 on 2024-04-22 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "club_management",
            "0023_unavailabledate_remove_customuser_days_unavailable_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="unavailable_dates",
        ),
        migrations.AddField(
            model_name="customuser",
            name="days_unavailable",
            field=models.TextField(blank=True),
        ),
        migrations.DeleteModel(
            name="UnavailableDate",
        ),
    ]