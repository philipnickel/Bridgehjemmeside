
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

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

# Inline class to manage UserSubstitutAssignment from within CustomUser and Substitutliste admin pages
class UserSubstitutAssignmentInline(admin.TabularInline):
    model = UserSubstitutAssignment
    extra = 1  # This controls how many empty forms are displayed by default

# Update SubstitutlisteAdmin to include the inline
class SubstitutlisteAdmin(admin.ModelAdmin):
    form = SubstitutlisteForm
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments

# Update AfmeldingslisteAdmin to display relevant fields
class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ["name", "day", "deadline"]

# Update CustomUserAdmin to include the inline and manage unavailable days
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    inlines = [UserSubstitutAssignmentInline]  # Include the inline for managing assignments

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['unavailable_days'].queryset = UnavailableDay.objects.all()
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'unavailable_days' in form.cleaned_data:
            obj.unavailable_days.set(form.cleaned_data['unavailable_days'])
        else:
            obj.unavailable_days.clear()

    def get_list_display(self, request):
        return ('username', 'email', 'unavailable_days_display')

    def unavailable_days_display(self, obj):
        return ", ".join(day.date.strftime("%Y-%m-%d") for day in obj.unavailable_days.all())
    unavailable_days_display.short_description = 'Unavailable Days'

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
