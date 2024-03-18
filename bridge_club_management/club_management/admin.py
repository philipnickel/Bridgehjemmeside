from django.contrib import admin
from .models import Week, Substitutliste, Afmeldingsliste, Configuration, DayResponsibility, CustomUser

class SubstitutlisteAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'deadline']  # Add 'name' field to the list display

class AfmeldingslisteAdmin(admin.ModelAdmin):
    list_display = ['name', 'day', 'deadline']  # Add 'name' field to the list display


admin.site.register(Week)
admin.site.register(Configuration)
admin.site.register(DayResponsibility)
admin.site.register(CustomUser)
admin.site.register(Substitutliste, SubstitutlisteAdmin)
admin.site.register(Afmeldingsliste, AfmeldingslisteAdmin)
