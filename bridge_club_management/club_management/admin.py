from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.db.models import Q
from .forms import CustomUserForm, SubstitutlisteForm
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

# Define the custom action
def update_substitutlister(modeladmin, request, queryset):
    for substitutliste in queryset:
        day_of_week = substitutliste.day.strftime("%A")
        available_users = CustomUser.objects.filter(
            Q(days_available__name=day_of_week) | Q(days_available__name="Any")
        )

        for user in available_users:
            UserSubstitutAssignment.objects.get_or_create(
                user=user, 
                substitutliste=substitutliste, 
                defaults={'status': 'Free'}
            )
        
        substitutliste.save()

    modeladmin.message_user(request, "Selected lists have been updated successfully.")

update_substitutlister.short_description = "Opdatér valgte lister"


# Inline class to manage UserSubstitutAssignment from within CustomUser and Substitutliste admin pages
class UserSubstitutAssignmentInline(admin.TabularInline):
    model = UserSubstitutAssignment
    extra = 1  # This controls how many empty forms are displayed by default

# Update SubstitutlisteAdmin to include the inline
class SubstitutlisteAdmin(admin.ModelAdmin):
    form = SubstitutlisteForm
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments
    actions = [update_substitutlister]  # Add the custom action

# Update AfmeldingslisteAdmin to display relevant fields
class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ["name", "day", "deadline"]

# Update CustomUserAdmin to include the inline and manage unavailable days
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments



# Admin form for managing Configuration with CKEditor
class ConfigurationAdminForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = "__all__"
        widgets = {
            "welcome_text": CKEditorWidget(),
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