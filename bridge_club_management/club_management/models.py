from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
import logging
from django.utils.translation import gettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils import FieldTracker
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

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


@register_snippet
class Configuration(models.Model):
    welcome_text = RichTextField(verbose_name=_("Velkomsttekst"))
    afmeldingslister_text = RichTextField(verbose_name=_("Afmeldingslister Tekst"), blank=True, default="")
    substitutlister_text = RichTextField(verbose_name=_("Substitutlister Tekst"), blank=True, default="")
    tilmeldingslister_text = RichTextField(verbose_name=_("Tilmeldingslister Tekst"), blank=True, default="")
    name = models.CharField(verbose_name=_("Navn"), max_length=100, default="Brugerdefineret tekst")

    panels = [
        FieldPanel('name'),
        FieldPanel('welcome_text'),
        FieldPanel('substitutlister_text'),
        FieldPanel('afmeldingslister_text'),
        FieldPanel('tilmeldingslister_text'),
    ]

    def __str__(self):
        return f"Velkomsttekst"

    class Meta:
        verbose_name = "Brugerdefineret tekst"  # Change the verbose name of the model
        verbose_name_plural = "Brugerdefineret tekst"  # Change the verbose plural name of the model


@register_setting
class SiteTexts(BaseSiteSetting):
    welcome_text = RichTextField(verbose_name=_("Velkomsttekst"), blank=True)
    substitutlister_text = RichTextField(verbose_name=_("Substitutlister Tekst"), blank=True)
    afmeldingslister_text = RichTextField(verbose_name=_("Afmeldingslister Tekst"), blank=True)
    tilmeldingslister_text = RichTextField(verbose_name=_("Tilmeldingslister Tekst"), blank=True)

    panels = [
        FieldPanel('welcome_text'),
        FieldPanel('substitutlister_text'),
        FieldPanel('afmeldingslister_text'),
        FieldPanel('tilmeldingslister_text'),
    ]

    class Meta:
        verbose_name = "Website tekster"


@register_setting
class SiteCopy(BaseSiteSetting):
    # Navbar / Site
    site_title = models.CharField(max_length=100, blank=True, default="")
    nav_substitutlister = models.CharField(max_length=100, blank=True, default="")
    nav_afmeldingslister = models.CharField(max_length=100, blank=True, default="")
    nav_tilmeldingslister = models.CharField(max_length=100, blank=True, default="")
    nav_login = models.CharField(max_length=100, blank=True, default="")

    # Page titles
    front_title = models.CharField(max_length=150, blank=True, default="")
    substitutlister_title = models.CharField(max_length=150, blank=True, default="")
    afmeldingslister_title = models.CharField(max_length=150, blank=True, default="")
    tilmeldingslister_title = models.CharField(max_length=150, blank=True, default="")

    # Common labels
    select_week_label = models.CharField(max_length=100, blank=True, default="")
    select_day_label = models.CharField(max_length=100, blank=True, default="")
    select_list_label = models.CharField(max_length=150, blank=True, default="")
    responsible_label = models.CharField(max_length=100, blank=True, default="")
    deadline_label = models.CharField(max_length=100, blank=True, default="")
    day_label = models.CharField(max_length=100, blank=True, default="")
    time_label = models.CharField(max_length=100, blank=True, default="")
    capacity_label = models.CharField(max_length=150, blank=True, default="")
    afbud_label = models.CharField(max_length=100, blank=True, default="")

    # Buttons
    go_to_substitutlister_btn = models.CharField(max_length=200, blank=True, default="")
    go_to_afmeldingslister_btn = models.CharField(max_length=200, blank=True, default="")
    go_to_tilmeldingslister_btn = models.CharField(max_length=200, blank=True, default="")
    add_pair_btn = models.CharField(max_length=100, blank=True, default="")
    add_single_btn = models.CharField(max_length=150, blank=True, default="")
    deadline_exceeded_btn = models.CharField(max_length=150, blank=True, default="")
    confirm_btn = models.CharField(max_length=100, blank=True, default="")
    close_btn = models.CharField(max_length=100, blank=True, default="")

    # Substitutlister modal labels
    confirm_substitut_title = models.CharField(max_length=200, blank=True, default="")
    absent_person_label = models.CharField(max_length=150, blank=True, default="")
    your_email_label = models.CharField(max_length=150, blank=True, default="")
    your_phone_label = models.CharField(max_length=150, blank=True, default="")
    prearranged_label = models.CharField(max_length=255, blank=True, default="")
    confirmation_title = models.CharField(max_length=200, blank=True, default="")
    confirmation_msg = models.CharField(max_length=300, blank=True, default="")

    # Afmeldingslister form
    afbud_form_label = models.CharField(max_length=150, blank=True, default="")
    afbud_placeholder = models.CharField(max_length=150, blank=True, default="")
    afbud_submit = models.CharField(max_length=100, blank=True, default="")
    deadline_exceeded = models.CharField(max_length=150, blank=True, default="")

    # Tilmeldingslister labels
    pair_no_header = models.CharField(max_length=100, blank=True, default="")
    name_header = models.CharField(max_length=100, blank=True, default="")
    partner_header = models.CharField(max_length=100, blank=True, default="")
    waitlist_title = models.CharField(max_length=100, blank=True, default="")
    waitlist_description = models.TextField(blank=True, default="")
    modal_add_pair_title = models.CharField(max_length=150, blank=True, default="")
    modal_add_single_title = models.CharField(max_length=150, blank=True, default="")
    player1_label = models.CharField(max_length=100, blank=True, default="")
    player2_label = models.CharField(max_length=100, blank=True, default="")
    submit_pair_btn = models.CharField(max_length=150, blank=True, default="")
    submit_single_btn = models.CharField(max_length=150, blank=True, default="")
    tl_confirm_title = models.CharField(max_length=150, blank=True, default="")
    tl_confirm_msg = models.CharField(max_length=300, blank=True, default="")
    error_title = models.CharField(max_length=100, blank=True, default="")

    # Login page text
    login_title = models.CharField(max_length=150, blank=True, default="")
    back_to_home_label = models.CharField(max_length=120, blank=True, default="")
    django_admin_label = models.CharField(max_length=120, blank=True, default="")
    django_admin_desc = models.CharField(max_length=200, blank=True, default="")
    wagtail_admin_label = models.CharField(max_length=120, blank=True, default="")
    wagtail_admin_desc = models.CharField(max_length=200, blank=True, default="")
    login_hint = models.CharField(max_length=240, blank=True, default="")

    # Afmeldingslister messages
    afbud_success_msg = models.CharField(max_length=200, blank=True, default="")
    input_required_msg = models.CharField(max_length=200, blank=True, default="")
    generic_error_msg = models.CharField(max_length=200, blank=True, default="")

    panels = [
        FieldPanel('site_title'),
        FieldPanel('nav_substitutlister'), FieldPanel('nav_afmeldingslister'),
        FieldPanel('nav_tilmeldingslister'), FieldPanel('nav_login'),
        FieldPanel('front_title'), FieldPanel('substitutlister_title'),
        FieldPanel('afmeldingslister_title'), FieldPanel('tilmeldingslister_title'),
        FieldPanel('select_week_label'), FieldPanel('select_day_label'),
        FieldPanel('select_list_label'), FieldPanel('responsible_label'),
        FieldPanel('deadline_label'), FieldPanel('day_label'),
        FieldPanel('time_label'), FieldPanel('capacity_label'), FieldPanel('afbud_label'),
        FieldPanel('go_to_substitutlister_btn'), FieldPanel('go_to_afmeldingslister_btn'),
        FieldPanel('go_to_tilmeldingslister_btn'),
        FieldPanel('add_pair_btn'), FieldPanel('add_single_btn'), FieldPanel('deadline_exceeded_btn'),
        FieldPanel('confirm_btn'), FieldPanel('close_btn'),
        FieldPanel('confirm_substitut_title'), FieldPanel('absent_person_label'),
        FieldPanel('your_email_label'), FieldPanel('your_phone_label'), FieldPanel('prearranged_label'),
        FieldPanel('confirmation_title'), FieldPanel('confirmation_msg'),
        FieldPanel('afbud_form_label'), FieldPanel('afbud_placeholder'), FieldPanel('afbud_submit'),
        FieldPanel('deadline_exceeded'),
        FieldPanel('pair_no_header'), FieldPanel('name_header'), FieldPanel('partner_header'),
        FieldPanel('waitlist_title'), FieldPanel('waitlist_description'),
        FieldPanel('modal_add_pair_title'), FieldPanel('modal_add_single_title'),
        FieldPanel('player1_label'), FieldPanel('player2_label'),
        FieldPanel('submit_pair_btn'), FieldPanel('submit_single_btn'),
        FieldPanel('tl_confirm_title'), FieldPanel('tl_confirm_msg'), FieldPanel('error_title'),
        # Login
        FieldPanel('login_title'), FieldPanel('back_to_home_label'),
        FieldPanel('django_admin_label'), FieldPanel('django_admin_desc'),
        FieldPanel('wagtail_admin_label'), FieldPanel('wagtail_admin_desc'),
        FieldPanel('login_hint'),
        # Afmeldingslister messages
        FieldPanel('afbud_success_msg'), FieldPanel('input_required_msg'), FieldPanel('generic_error_msg'),
    ]

    class Meta:
        verbose_name = "Website labels"


class HomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['club_management.SubstitutlisterPage', 'club_management.AfmeldingslisterPage', 'club_management.TilmeldingslisterPage']

    def get_context(self, request, *args, **kwargs):
        from django.db.models import Prefetch
        context = super().get_context(request, *args, **kwargs)
        # Build same context as front_page view
        from .models import Substitutliste, UserSubstitutAssignment, Afmeldingsliste, Week, Day, DayResponsibility
        substitutlister = Substitutliste.objects.prefetch_related(
            Prefetch(
                'usersubstitutassignment_set',
                queryset=UserSubstitutAssignment.objects.select_related('user'),
                to_attr='assignments'
            )
        ).all()
        afmeldingslister = Afmeldingsliste.objects.all().order_by('day')
        weeks = Week.objects.all()
        try:
            weeks = sorted(weeks, key=lambda week: int(week.name.split('-')[0]))
        except Exception:
            weeks = list(weeks)
        day_name_mapping = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag',
            'Saturday': 'Lørdag',
            'Sunday': 'Søndag'
        }
        responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
        responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in responsibilities}
        for substitutliste in substitutlister:
            day_name = substitutliste.day.strftime("%A")
            try:
                day = Day.objects.get(name=day_name)
            except Day.DoesNotExist:
                day = None
            substitutliste.responsible_name = ""
            substitutliste.responsible_email = ""
            if day:
                rc = responsibility_dict.get(day.name.lower())
                if rc:
                    substitutliste.responsible_name = rc.get_full_name() or rc.username
                    substitutliste.responsible_email = rc.email
            substitutliste.assigned_substitutter = [
                {
                    'name': a.user.get_full_name() or a.user.username,
                    'phone': a.user.phone_number,
                    'note': a.user.custom_note,
                    'email': a.user.email,
                    'id': a.user.id,
                    'status': a.get_status_display(),
                    'reservationsnote': a.reservationsnote,
                    'række': a.user.række.name if a.user.række else 'N/A'
                }
                for a in getattr(substitutliste, 'assignments', [])
            ]
        context.update({
            'welcome_text': self.intro,
            'substitutlister': substitutlister,
            'afmeldingslister': afmeldingslister,
            'weeks': weeks,
            'days': Day.objects.all(),
            'day_name_mapping': day_name_mapping,
        })
        return context


class SubstitutlisterPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['club_management.HomePage', 'wagtailcore.Page']
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        from django.db.models import Prefetch
        context = super().get_context(request, *args, **kwargs)
        from .models import Substitutliste, UserSubstitutAssignment, Week, Day, DayResponsibility
        substitutlister = Substitutliste.objects.prefetch_related(
            Prefetch(
                'usersubstitutassignment_set',
                queryset=UserSubstitutAssignment.objects.select_related('user'),
                to_attr='assignments'
            )
        ).all()
        weeks = Week.objects.all()
        try:
            weeks = sorted(weeks, key=lambda week: int(week.name.split('-')[0]))
        except Exception:
            weeks = list(weeks)
        day_name_mapping = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag',
            'Saturday': 'Lørdag',
            'Sunday': 'Søndag'
        }
        responsibilities = DayResponsibility.objects.select_related('day', 'coordinator').all()
        responsibility_dict = {resp.day.name.lower(): resp.coordinator for resp in responsibilities}
        for substitutliste in substitutlister:
            day_name = substitutliste.day.strftime("%A")
            try:
                day = Day.objects.get(name=day_name)
            except Day.DoesNotExist:
                day = None
            substitutliste.responsible_name = ""
            substitutliste.responsible_email = ""
            if day:
                rc = responsibility_dict.get(day.name.lower())
                if rc:
                    substitutliste.responsible_name = rc.get_full_name() or rc.username
                    substitutliste.responsible_email = rc.email
            substitutliste.assigned_substitutter = [
                {
                    'name': a.user.get_full_name() or a.user.username,
                    'phone': a.user.phone_number,
                    'note': a.user.custom_note,
                    'email': a.user.email,
                    'id': a.user.id,
                    'status': a.get_status_display(),
                    'reservationsnote': a.reservationsnote,
                    'række': a.user.række.name if a.user.række else 'N/A'
                }
                for a in getattr(substitutliste, 'assignments', [])
            ]
        context.update({
            'substitutlister_text': self.intro,
            'substitutlister': substitutlister,
            'weeks': weeks,
            'days': Day.objects.all(),
            'day_name_mapping': day_name_mapping,
        })
        return context


class AfmeldingslisterPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['club_management.HomePage', 'wagtailcore.Page']
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        import json
        context = super().get_context(request, *args, **kwargs)
        from .models import Afmeldingsliste
        afmeldingslister = Afmeldingsliste.objects.all()
        afmeldingslister_data = [
            {
                'id': str(liste.id),
                'name': liste.name,
                'day': liste.day.isoformat(),
                'deadline': liste.deadline.isoformat(),
                'afbud': liste.afbud or ''
            }
            for liste in afmeldingslister
        ]
        context.update({
            'afmeldingslister_text': self.intro,
            'afmeldingslister': afmeldingslister,
            'afmeldingslister_json': json.dumps(afmeldingslister_data),
        })
        return context


class TilmeldingslisterPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    parent_page_types = ['club_management.HomePage', 'wagtailcore.Page']
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        from django.db.models import Min, Q
        context = super().get_context(request, *args, **kwargs)
        from .models import Tilmeldingsliste, TilmeldingslistePair
        tilmeldingslister = Tilmeldingsliste.objects.all().order_by('day')
        for liste in tilmeldingslister:
            liste.tilmeldte_par = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, på_venteliste=False, is_single=False).order_by('parnummer')
            liste.venteliste_par = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, på_venteliste=True, is_single=False).order_by('parnummer')
            liste.single_players = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, is_single=True).order_by('id')
            liste.all_pairs = TilmeldingslistePair.objects.filter(tilmeldingsliste=liste, is_single=False).order_by('parnummer')
        selected_list_id = request.GET.get('selected_list_id')
        if selected_list_id:
            try:
                selected_list = Tilmeldingsliste.objects.get(id=selected_list_id)
            except Tilmeldingsliste.DoesNotExist:
                selected_list = None
        else:
            oldest_date = Tilmeldingsliste.objects.aggregate(Min('day'))['day__min']
            selected_list = Tilmeldingsliste.objects.filter(day=oldest_date).first()
        context.update({
            'tilmeldingslister_text': self.intro,
            'tilmeldingslister': tilmeldingslister,
            'selected_list': selected_list,
        })
        return context


class Day(models.Model):
    name = models.CharField(_("Name"), max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Day")
        verbose_name_plural = _("Days")


class DayResponsibility(models.Model):
    day = models.ForeignKey(Day, verbose_name=_("Dag"), on_delete=models.CASCADE)
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Ansvarlig"), on_delete=models.CASCADE)

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
    responsible_person = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Ansvarlig"), on_delete=models.CASCADE)
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
