from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from django.db.models import Q


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
    days_available = models.ManyToManyField('Day', related_name='available_users', blank=True)
    


    groups = None
    user_permissions = None

    def __str__(self):
        return self.username

class Week(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Substitutliste(models.Model):
    name = models.CharField(max_length=100, default='unknown')
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    #substitutes = models.ManyToManyField('club_management.CustomUser', related_name='substitutes')
    substitutes = models.ManyToManyField('club_management.CustomUser', blank=True)  # Adjust 'YourUserModel' to your actual user model


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Call the super method to perform the default save behavior
        super().save(*args, **kwargs)
        
        # Get the day of the week from the selected date
        day_of_week = self.day.strftime('%A')

        # Query CustomUser model to find users available on the selected day
        available_users = CustomUser.objects.filter(Q(days_available__name=day_of_week) | Q(days_available__name='Any'))

        # Update the substitutes field with the retrieved users
        self.substitutes.set(available_users)

class Afmeldingsliste(models.Model):
    name = models.CharField(max_length=100, default='unknown')  # Add a name field
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    afbud = models.TextField(default='Afbud')

class Configuration(models.Model):
    welcome_text = models.TextField()

class DayResponsibility(models.Model):
    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day}: {self.coordinator}"

class Day(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
