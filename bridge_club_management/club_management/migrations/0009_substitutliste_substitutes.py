# Generated by Django 4.1 on 2024-03-18 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0008_remove_substitutliste_substitutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='substitutliste',
            name='substitutes',
            field=models.ManyToManyField(blank=True, null=True, to='club_management.customuser'),
        ),
    ]