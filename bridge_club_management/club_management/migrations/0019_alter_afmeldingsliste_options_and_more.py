# Generated by Django 4.1 on 2024-03-18 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0018_alter_week_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='afmeldingsliste',
            options={'verbose_name': 'Afmeldingsliste', 'verbose_name_plural': 'Afmeldingslister'},
        ),
        migrations.AlterModelOptions(
            name='configuration',
            options={'verbose_name': 'Forsidetekst', 'verbose_name_plural': 'Forsidetekst'},
        ),
        migrations.AlterModelOptions(
            name='customuser',
            options={'verbose_name': 'Substitutter', 'verbose_name_plural': 'Substitutter'},
        ),
        migrations.AlterModelOptions(
            name='dayresponsibility',
            options={'verbose_name': 'Ansvarlig for dag', 'verbose_name_plural': 'Ansvarlig for dag'},
        ),
        migrations.AlterModelOptions(
            name='substitutliste',
            options={'verbose_name': 'Substitutliste', 'verbose_name_plural': 'Substitutlister'},
        ),
        migrations.AlterModelOptions(
            name='week',
            options={'verbose_name': 'Uge', 'verbose_name_plural': 'Uger'},
        ),
    ]
