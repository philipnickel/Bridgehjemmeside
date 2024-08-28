# Generated by Django 4.2.15 on 2024-08-28 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club_management', '0028_remove_unavailableday_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSubstitutAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Free', 'Free'), ('Taken', 'Taken')], default='Free', max_length=10)),
                ('substitutliste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_assignments', to='club_management.substitutliste')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='substitut_assignments', to='club_management.customuser')),
            ],
            options={
                'unique_together': {('user', 'substitutliste')},
            },
        ),
    ]
