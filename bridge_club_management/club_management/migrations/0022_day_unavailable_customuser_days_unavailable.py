# Generated by Django 4.1 on 2024-03-21 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0021_remove_substitutliste_substitutes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day_unavailable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='days_unavailable',
            field=models.ManyToManyField(blank=True, related_name='unavailable_users', to='club_management.day_unavailable'),
        ),
    ]
