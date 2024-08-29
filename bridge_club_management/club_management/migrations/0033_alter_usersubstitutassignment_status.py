# Generated by Django 4.2.15 on 2024-08-29 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0032_alter_usersubstitutassignment_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubstitutassignment',
            name='status',
            field=models.CharField(choices=[('Free', 'Free'), ('Taken', 'Taken'), ('Fraværende', 'Fraværende')], default='Free', max_length=20),
        ),
    ]
