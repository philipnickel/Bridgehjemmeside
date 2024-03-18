from django.contrib import admin
from .models import Week, Substitutliste, Afmeldingsliste, Configuration, DayResponsibility, CustomUser
from .forms import CustomUserForm


class SubstitutlisteAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'deadline']  # Add 'name' field to the list display

class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'deadline']  # Add 'name' field to the list display

class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm


admin.site.register(Week)
admin.site.register(Configuration)
admin.site.register(DayResponsibility)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Substitutliste, SubstitutlisteAdmin)
admin.site.register(Afmeldingsliste, AfmeldingslisteAdmin)
