from django.db import models
from django.contrib.auth.models import User, AbstractUser



class CustomUser(AbstractUser):
    USER_TYPES = (
        ('Admin', 'Admin'),
        ('Substitutter', 'Substitutter'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    row = models.CharField(max_length=50)
    assigned_days = models.ManyToManyField('DayResponsibility', related_name='assigned_users', blank=True)
    days_available = models.CharField(max_length=100, blank=True)

    groups = None
    user_permissions = None

    def __str__(self):
        return self.username

class Week(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Substitutliste(models.Model):
    name = models.CharField(max_length=100, default='unknown')  # Add a name field
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    substitutes = models.ManyToManyField('club_management.CustomUser', related_name='substitutes')

class Afmeldingsliste(models.Model):
    name = models.CharField(max_length=100, default='unknown')  # Add a name field
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    afbud = models.TextField(default='Afbud')

class Configuration(models.Model):
    welcome_text = models.TextField()

class DayResponsibility(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)

