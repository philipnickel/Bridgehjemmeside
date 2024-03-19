from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from django.db.models import Q


class CustomUser(AbstractUser):
    USER_TYPES = (
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
    
    class Meta:
        verbose_name = "Substitutliste"  # Change the verbose name of the model
        verbose_name_plural = "Substitutlister"  # Change the verbose plural name of the model

class Afmeldingsliste(models.Model):
    name = models.CharField(max_length=100, default='unknown')  # Add a name field
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    day = models.DateField()
    deadline = models.DateTimeField()
    afbud = models.TextField(default='Afbud')

    class Meta:
        verbose_name = "Afmeldingsliste"  # Change the verbose name of the model
        verbose_name_plural = "Afmeldingslister"  # Change the verbose plural name of the model

class Configuration(models.Model):
    welcome_text = models.TextField()
    name = models.CharField(max_length=100, default='Forsidetekst')  # Add a name field
    def __str__(self):
        return f"Velkomsttekst"

    class Meta:
        verbose_name = "Forsidetekst"  # Change the verbose name of the model
        verbose_name_plural = "Forsidetekst"  # Change the verbose plural name of the model
    
    def __str__(self):
        return f"Velkomsttekst"

class DayResponsibility(models.Model):
    day = models.ForeignKey('Day', on_delete=models.CASCADE)
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
    
