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
    Række  
)


class SubstitutlisteAdmin(admin.ModelAdmin):
    # list_display = ['name', 'day', 'deadline']  # Add 'name' field to the list display
    form = SubstitutlisteForm


class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ["name", "day", "deadline"]  # Add 'name' field to the list display


class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm


class ConfigurationAdminForm(forms.ModelForm):
    class Meta:
        model = Configuration
        fields = "__all__"
        widgets = {
            "welcome_text": CKEditorWidget(),
        }


class ConfigurationAdmin(admin.ModelAdmin):
    ordering = ()
    form = ConfigurationAdminForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ["name"]


admin.site.register(Configuration, ConfigurationAdmin)

admin.site.register(Week)
admin.site.register(Række)
admin.site.register(DayResponsibility)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Substitutliste, SubstitutlisteAdmin)
admin.site.register(Afmeldingsliste, AfmeldingslisteAdmin)
