# Generated by Django 4.1 on 2024-03-18 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0019_alter_afmeldingsliste_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='name',
            field=models.CharField(default='Forsidetekst', max_length=100),
        ),
    ]
