from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

CustomUser = get_user_model()

class Række(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Rækker"  # Plural name in the admin panel

class UnavailableDay(models.Model):
    date = models.DateField()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d")


class CustomUser(AbstractUser):
    USER_TYPES = (("Substitutter", "Substitutter"),)

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    række = models.ForeignKey(Række, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_days = models.ManyToManyField("DayResponsibility", related_name="assigned_users", blank=True)
    days_available = models.ManyToManyField("Day", related_name="available_users", blank=True)
    custom_note = models.TextField(blank=True, null=True, help_text="Enter a custom note for the user.")
    
    groups = None
    user_permissions = None

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Substitutter"
        verbose_name_plural = "Substitutter"


class Week(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Uge"  # Change the verbose name of the model
        verbose_name_plural = "Uger"  # Change the verbose plural name of the model


class Substitutliste(models.Model):
    name = models.CharField(max_length=100, default="unknown")
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_assignments()

    def update_assignments(self):
        weekday = self.day.strftime("%A")
        logger.info(f"Updating assignments for {self.name} on {weekday}")

        # Get the Danish name for the weekday
        danish_weekday = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag',
            'Saturday': 'Lørdag',
            'Sunday': 'Søndag'
        }.get(weekday, weekday)

        available_users = CustomUser.objects.filter(
            Q(days_available__name=danish_weekday) | Q(days_available__name="Alle")
        )
        logger.info(f"Found {available_users.count()} available users")

        # Remove existing assignments
        deleted_count, _ = UserSubstitutAssignment.objects.filter(substitutliste=self).delete()
        logger.info(f"Deleted {deleted_count} existing assignments")

        # Create new assignments
        created_count = 0
        for user in available_users:
            UserSubstitutAssignment.objects.create(
                user=user,
                substitutliste=self,
                status='Ledig'
            )
            created_count += 1

        logger.info(f"Created {created_count} new assignments")

    @property
    def day_name(self):
        return self.day.strftime("%A")

    class Meta:
        verbose_name = "Substitutliste"
        verbose_name_plural = "Substitutlister"


class UserSubstitutAssignment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    substitutliste = models.ForeignKey(Substitutliste, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Free', 'Free'),
        ('Taken', 'Taken'),
        ('Fraværende', 'Fraværende'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Free')

    class Meta:
        unique_together = ('user', 'substitutliste')

    def __str__(self):
        return f"{self.user} - {self.substitutliste} - {self.status}"


class Afmeldingsliste(models.Model):
    name = models.CharField(max_length=100, default="unknown")
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    afbud = models.TextField(default="Afbud")

    class Meta:
        verbose_name = "Afmeldingsliste"  # Change the verbose name of the model
        verbose_name_plural = "Afmeldingslister"  # Change the verbose plural name of the model


class Configuration(models.Model):
    welcome_text = models.TextField()
    name = models.CharField(max_length=100, default="Forsidetekst")

    def __str__(self):
        return f"Velkomsttekst"

    class Meta:
        verbose_name = "Forsidetekst"  # Change the verbose name of the model
        verbose_name_plural = "Forsidetekst"  # Change the verbose plural name of the model


class Day(models.Model):
    name = models.CharField(max_length=20, verbose_name='Navn')
    english_name = models.CharField(max_length=20, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dag"
        verbose_name_plural = "Dage"


class DayResponsibility(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day}: {self.coordinator}"

    class Meta:
        verbose_name = "Ansvarlig for dag"
        verbose_name_plural = "Ansvarlig for dag"
