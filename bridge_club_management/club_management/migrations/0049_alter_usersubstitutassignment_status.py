# Generated by Django 4.2.15 on 2024-08-29 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0048_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubstitutassignment',
            name='status',
            field=models.CharField(choices=[('Ledig', 'Ledig'), ('Optaget', 'Optaget'), ('Fraværende', 'Fraværende')], default='Ledig', max_length=20),
        ),
    ]
