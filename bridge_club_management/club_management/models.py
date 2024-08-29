from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import Q
from django.utils import timezone
import logging
from django.utils.translation import gettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

ENGLISH_TO_DANISH_DAYS = {
    'monday': 'Mandag',
    'tuesday': 'Tirsdag',
    'wednesday': 'Onsdag',
    'thursday': 'Torsdag',
    'friday': 'Fredag',
    'saturday': 'Lørdag',
    'sunday': 'Søndag'
}

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
    username = models.CharField(max_length=100, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15)
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

    class Meta:
        verbose_name = "Substitutliste"
        verbose_name_plural = "Substitutlister"

    def __str__(self):
        return f"{self.name} - {self.day}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.update_assignments()

    def update_assignments(self):
        # Get the day of the week for this Substitutliste
        day_of_week = self.day.strftime("%A")
        logger.info(f"Updating assignments for {self.name} on {day_of_week}")

        # Get all users available on this day
        available_users = CustomUser.objects.filter(days_available__name__iexact=day_of_week)
        logger.info(f"Found {available_users.count()} available users")
        logger.info(f"Available users: {', '.join([user.username for user in available_users])}")

        # Log all days in the database
        all_days = Day.objects.all()
        logger.info(f"All days in database: {', '.join([day.name for day in all_days])}")

        # Log all users and their available days
        all_users = CustomUser.objects.all()
        for user in all_users:
            logger.info(f"User {user.username} available days: {', '.join([day.name for day in user.days_available.all()])}")

        # Create or update assignments
        created_count = 0
        updated_count = 0
        for user in available_users:
            assignment, created = UserSubstitutAssignment.objects.get_or_create(
                user=user,
                substitutliste=self,
                defaults={'status': 'Free'}
            )
            if created:
                created_count += 1
            else:
                if assignment.status != 'Free':
                    assignment.status = 'Free'
                    assignment.save()
                    updated_count += 1

        # Delete assignments for users no longer available
        deleted_count, _ = UserSubstitutAssignment.objects.filter(substitutliste=self).exclude(user__in=available_users).delete()

        logger.info(f"Created {created_count} new assignments")
        logger.info(f"Updated {updated_count} existing assignments")
        logger.info(f"Deleted {deleted_count} obsolete assignments")

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
        ('Ledig', 'Ledig'),
        ('Optaget', 'Optaget'),
        ('Fraværende', 'Fraværende'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Free')

    class Meta:
        unique_together = ('user', 'substitutliste')
        verbose_name = "Substitutliste tildelinger"
        verbose_name_plural = "Substitutliste tildelinger"

    def __str__(self):
        return f"{self.user} - {self.substitutliste} - {self.get_status_display()}"


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
    name = models.CharField(_("Name"), max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Day")
        verbose_name_plural = _("Days")


class DayResponsibility(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day}: {self.coordinator}"

    class Meta:
        verbose_name = "Ansvarlig for dag"
        verbose_name_plural = "Ansvarlig for dag"

@receiver(post_save, sender=Substitutliste)
def update_assignments_on_save(sender, instance, created, **kwargs):
    if not created:
        instance.update_assignments()
