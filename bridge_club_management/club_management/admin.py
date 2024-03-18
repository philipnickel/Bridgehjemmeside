from django.contrib import admin
from .models import Week, Substitutliste, Afmeldingsliste, Configuration, DayResponsibility, CustomUser

admin.site.register(Week)
admin.site.register(Substitutliste)
admin.site.register(Afmeldingsliste)
admin.site.register(Configuration)
admin.site.register(DayResponsibility)
admin.site.register(CustomUser)

