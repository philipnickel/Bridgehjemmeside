from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import Q
from django.utils import timezone
import logging
from django.utils.translation import gettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils import FieldTracker

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
    name = models.CharField(verbose_name=_("Navn"),max_length=100)

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
    username = models.CharField(_("Brugernavn"),max_length=100, unique=True)
    user_type = models.CharField(_("Brugertype"),max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(_("Telefonnummer"),max_length=15)
    email = models.EmailField(_("Email"),null=True, blank=True)
    række = models.ForeignKey(Række, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_days = models.ManyToManyField("DayResponsibility", related_name="assigned_users", blank=True)
    days_available = models.ManyToManyField("Day", related_name="available_users", blank=True)
    custom_note = models.TextField(_("Note til substitut"),blank=True, null=True, help_text="Note til substitut (Vises på forsiden).")
    
    groups = None
    user_permissions = None

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Substitutter"
        verbose_name_plural = "Substitutter"


class Week(models.Model):
    name = models.CharField(verbose_name=_("Ugenummer"),max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Uge"  # Change the verbose name of the model
        verbose_name_plural = "Uger"  # Change the verbose plural name of the model


class Substitutliste(models.Model):
    name = models.CharField(verbose_name=_("Navn"),max_length=100, default="unknown")
    week = models.ForeignKey(Week, verbose_name=_("Uge"), on_delete=models.CASCADE)
    day = models.DateField(verbose_name=_("Dag"))
    deadline = models.DateTimeField(verbose_name=_("Deadline"))

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
        day_of_week = self.day.strftime("%A")
        logger.info(f"Updating assignments for {self.name} on {day_of_week}")

        available_users = CustomUser.objects.filter(days_available__name__iexact=day_of_week)
        logger.info(f"Found {available_users.count()} available users")
        logger.info(f"Available users: {', '.join([user.username for user in available_users])}")

        all_days = Day.objects.all()
        logger.info(f"All days in database: {', '.join([day.name for day in all_days])}")

        all_users = CustomUser.objects.all()
        for user in all_users:
            logger.info(f"User {user.username} available days: {', '.join([day.name for day in user.days_available.all()])}")

        created_count = 0
        for user in available_users:
            assignment, created = UserSubstitutAssignment.objects.get_or_create(
                user=user,
                substitutliste=self,
                defaults={'status': 'Ledig'}
            )
            if created:
                created_count += 1

        logger.info(f"Created {created_count} new assignments")

    @property
    def day_name(self):
        return self.day.strftime("%A")

    class Meta:
        verbose_name = "Substitutliste"
        verbose_name_plural = "Substitutlister"


class UserSubstitutAssignment(models.Model):
    user = models.ForeignKey(verbose_name=_("Substitut"),to=CustomUser, on_delete=models.CASCADE)
    substitutliste = models.ForeignKey(Substitutliste, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Ledig', 'Ledig'),
        ('Optaget', 'Optaget'),
        ('Fraværende', 'Fraværende'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ledig')
    reservationsnote = models.TextField(blank=True, null=True)  # Add this line

    class Meta:
        unique_together = ('user', 'substitutliste')
        verbose_name = "Substitutliste tildelinger"
        verbose_name_plural = "Substitutliste tildelinger"

    def __str__(self):
        return f"{self.user} - {self.substitutliste} - {self.get_status_display()}"


class Afmeldingsliste(models.Model):
    name = models.CharField(_("Navn"), max_length=100, default="unknown")
    day = models.DateField(_("Dag"))
    deadline = models.DateTimeField()
    afbud = models.TextField(blank=True)  # Changed this line

    class Meta:
        verbose_name = "Afmeldingsliste"
        verbose_name_plural = "Afmeldingslister"

    def __str__(self):
        return f"{self.name} - {self.day}"


class Configuration(models.Model):
    welcome_text = models.TextField(verbose_name=_("Velkomsttekst"))
    afmeldingslister_text = models.TextField(verbose_name=_("Afmeldingslister Tekst"), default="Default text")
    substitutlister_text = models.TextField(verbose_name=_("Substitutlister Tekst"), default="Default text")
    tilmeldingslister_text = models.TextField(verbose_name=_("Tilmeldingslister Tekst"), default="Default text")
    name = models.CharField(verbose_name=_("Navn"),max_length=100, default="Brugerdefineret tekst")

    def __str__(self):
        return f"Velkomsttekst"

    class Meta:
        verbose_name = "Brugerdefineret tekst"  # Change the verbose name of the model
        verbose_name_plural = "Brugerdefineret tekst"  # Change the verbose plural name of the model


class Day(models.Model):
    name = models.CharField(_("Name"), max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Day")
        verbose_name_plural = _("Days")


class DayResponsibility(models.Model):
    day = models.ForeignKey(Day, verbose_name=_("Dag"), on_delete=models.CASCADE)
    coordinator = models.ForeignKey(User, verbose_name=_("Ansvarlig"), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.day}: {self.coordinator}"

    class Meta:
        verbose_name = "Ansvarlig for dag"
        verbose_name_plural = "Ansvarlig for dag"

@receiver(post_save, sender=Substitutliste)
def update_assignments_on_save(sender, instance, created, **kwargs):
    if not created:
        instance.update_assignments()

class Tilmeldingsliste(models.Model):
    name = models.CharField(_("Navn"), max_length=100, default="unknown")
    day = models.DateField(_("Dag"))
    deadline = models.DateTimeField(_("Deadline"))
    responsible_person = models.ForeignKey(User, verbose_name=_("Ansvarlig"), on_delete=models.CASCADE)
    antal_par = models.IntegerField(_("Antal Par"), default=24)

    class Meta:
        verbose_name = "Tilmeldingsliste"
        verbose_name_plural = "Tilmeldingslister"

    def __str__(self):
        return f"{self.name} - {self.day}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Tilmeldingsliste.objects.get(pk=self.pk)
            old_antal_par = old_instance.antal_par
            super().save(*args, **kwargs)
            if self.antal_par > old_antal_par:
                from .signals import move_pairs_from_waiting_list
                move_pairs_from_waiting_list(self)
        else:
            super().save(*args, **kwargs)

class Pair(models.Model):
    navn = models.CharField(_("Navn"), max_length=100, default="Unknown")
    makker = models.CharField(_("Makker"), max_length=100, blank=True, null=True)
    contact_info = models.CharField(_("Kontaktinformation"), max_length=100)

    def __str__(self):
        return f"{self.navn} & {self.makker or 'Ingen Makker'}"

class TilmeldingslistePair(models.Model):
    tilmeldingsliste = models.ForeignKey(Tilmeldingsliste, on_delete=models.CASCADE)
    navn = models.CharField(_("Navn"), max_length=100, default="Unknown", blank=True, null=True)
    makker = models.CharField(_("Makker"), max_length=100, blank=True, null=True)
    telefonnummer = models.CharField(_("Telefonnummer"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    på_venteliste = models.BooleanField(_("På Venteliste"), default=False)
    parnummer = models.IntegerField(_("Parnummer"), blank=True, null=True)
    is_single = models.BooleanField(_("Uden makker"), default=False)  # Add this line

    def __str__(self):
        return f"{self.navn} & {self.makker or 'Ingen Makker'}"

    class Meta:
        verbose_name = "Tilmeldingsliste Par"
        verbose_name_plural = "Tilmeldingsliste Par"
