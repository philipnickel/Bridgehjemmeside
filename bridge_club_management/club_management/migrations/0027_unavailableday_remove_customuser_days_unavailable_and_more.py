# Generated by Django 4.2.15 on 2024-08-28 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0026_customuser_custom_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnavailableDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='days_unavailable',
        ),
        migrations.AddField(
            model_name='customuser',
            name='unavailable_days',
            field=models.ManyToManyField(blank=True, to='club_management.unavailableday'),
        ),
    ]
