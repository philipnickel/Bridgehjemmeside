# Generated by Django 4.2.15 on 2024-08-29 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0036_alter_day_name_alter_usersubstitutassignment_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usersubstitutassignment',
            options={'verbose_name': 'Substitutliste tildelinger', 'verbose_name_plural': 'Substitutliste tildelinger'},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
