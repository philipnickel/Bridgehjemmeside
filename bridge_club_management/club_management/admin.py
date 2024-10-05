from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from django.contrib import admin
from django.db.models import Q
from django.contrib.auth.models import User  # Import the User model
from .forms import CustomUserForm
from .models import (
    Afmeldingsliste,
    Configuration,
    CustomUser,
    DayResponsibility,
    Substitutliste,
    Week,
    Række, 
    UnavailableDay,
    UserSubstitutAssignment  # Import the new model
)

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Define the custom action
@admin.action(description="Opdatér valgte lister")
def update_substitutlister(modeladmin, request, queryset):
    logger.info(f"Updating {queryset.count()} substitutlister")
    for substitutliste in queryset:
        logger.info(f"Updating substitutliste: {substitutliste.name}")
        substitutliste.update_assignments()
    modeladmin.message_user(request, "Selected lists have been updated successfully.")
    logger.info("Finished updating substitutlister")

# Inline class to manage UserSubstitutAssignment from within CustomUser and Substitutliste admin pages
class UserSubstitutAssignmentInline(admin.TabularInline):
    model = UserSubstitutAssignment
    extra = 0  # This controls how many empty forms are displayed by default

# Update SubstitutlisteAdmin to include the inline
class SubstitutlisteAdmin(admin.ModelAdmin):
    list_display = ['name', 'week', 'day', 'deadline']
    list_filter = ['week', 'day']
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments
    actions = [update_substitutlister]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f"Saved Substitutliste {obj.name} for day {obj.day} ({obj.day})")

# Update AfmeldingslisteAdmin to display relevant fields
class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ["name", "day", "deadline"]

# Update CustomUserAdmin to include the inline and manage unavailable days
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments

    def get_list_display(self, request):
        return ('username', 'email', 'phone_number')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f"Saved user {obj.username} with available days: {', '.join(obj.days_available.values_list('name', flat=True))}")

# Admin form for managing Configuration with CKEditor
class ConfigurationAdminForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = "__all__"
        widgets = {
            "welcome_text": CKEditor5Widget(config_name='extends'),
        }

# ConfigurationAdmin to manage site configurations
class ConfigurationAdmin(admin.ModelAdmin):
    ordering = ()
    form = ConfigurationAdminForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ["name"]

# Register the models and admin classes
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Week)
admin.site.register(Række)
admin.site.register(DayResponsibility)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Substitutliste, SubstitutlisteAdmin)
admin.site.register(Afmeldingsliste, AfmeldingslisteAdmin)
admin.site.register(UserSubstitutAssignment)  # Register the new model

from .models import Tilmeldingsliste, Pair, TilmeldingslistePair

class TilmeldingslistePairInline(admin.TabularInline):
    model = TilmeldingslistePair
    extra = 1
    fields = ('pair',)
    verbose_name = "Tilmeldingsliste-pair-relation"
    verbose_name_plural = "Tilmeldingsliste-pair-relationer"
    can_delete = True

@admin.register(Tilmeldingsliste)
class TilmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'deadline', 'responsible_person')
    search_fields = ('name', 'responsible_person__username')
    list_filter = ('day',)
    inlines = [TilmeldingslistePairInline]
    exclude = ('pairs',)  # Exclude the pairs field from the form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['day'].initial = timezone.now().date()
        form.base_fields['deadline'].initial = timezone.now()
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "responsible_person":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Ensure Pair is not registered separately
# Remove any @admin.register(Pair) or similar lines