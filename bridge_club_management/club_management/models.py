
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import Q
from django.utils import timezone

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
        verbose_name = "Substitutter"  # Change the verbose name of the model
        verbose_name_plural = "Substitutter"  # Change the verbose plural name of the model


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
    substitutes_text = models.TextField(blank=True)  # Change to TextField

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        day_of_week = self.day.strftime("%A")
        available_users = CustomUser.objects.filter(Q(days_available__name=day_of_week) | Q(days_available__name="Any"))

        for user in available_users:
            # Automatically create UserSubstitutAssignment for each available user
            UserSubstitutAssignment.objects.get_or_create(
                user=user, 
                substitutliste=self, 
                defaults={'status': 'Free'}
            )

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Substitutliste"  # Change the verbose name of the model
        verbose_name_plural = "Substitutlister"  # Change the verbose plural name of the model


class UserSubstitutAssignment(models.Model):
    STATUS_CHOICES = [
        ('Free', 'Free'),
        ('Taken', 'Taken'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='substitut_assignments')
    substitutliste = models.ForeignKey(Substitutliste, on_delete=models.CASCADE, related_name='user_assignments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Free')

    class Meta:
        unique_together = ('user', 'substitutliste')

    def __str__(self):
        return f"{self.user.username} - {self.substitutliste.name} ({self.get_status_display()})"


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


class DayResponsibility(models.Model):
    day = models.ForeignKey("Day", on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day}: {self.coordinator}"

    class Meta:
        verbose_name = "Ansvarlig for dag"  # Change the verbose name of the model
        verbose_name_plural = "Ansvarlig for dag"  # Change the verbose plural name of the model


class Day(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
