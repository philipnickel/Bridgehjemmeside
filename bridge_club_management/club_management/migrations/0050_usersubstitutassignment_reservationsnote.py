# Generated by Django 4.2.15 on 2024-09-01 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0049_alter_usersubstitutassignment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubstitutassignment',
            name='reservationsnote',
            field=models.TextField(blank=True, null=True),
        ),
    ]
