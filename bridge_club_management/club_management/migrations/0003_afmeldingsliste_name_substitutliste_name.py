# Generated by Django 4.1 on 2024-03-18 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0002_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='afmeldingsliste',
            name='name',
            field=models.CharField(default='unknown', max_length=100),
        ),
        migrations.AddField(
            model_name='substitutliste',
            name='name',
            field=models.CharField(default='unknown', max_length=100),
        ),
    ]
