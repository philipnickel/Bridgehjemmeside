# Generated by Django 4.2.15 on 2024-08-29 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0033_alter_usersubstitutassignment_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='day',
            options={'verbose_name': 'Dag', 'verbose_name_plural': 'Dage'},
        ),
        migrations.AddField(
            model_name='day',
            name='danish_name',
            field=models.CharField(default='', max_length=20),
        ),
    ]
