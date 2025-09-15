try:
    # Wagtail < 7: contrib.modeladmin
    from wagtail.contrib.modeladmin.options import (
        ModelAdmin, ModelAdminGroup, modeladmin_register
    )
    _USE_MODELADMIN = True
except Exception:
    # Wagtail >= 7: use admin viewsets + hooks registration
    from wagtail.admin.viewsets.model import ModelViewSet
    from wagtail.admin.viewsets import ViewSetGroup
    from wagtail import hooks
    _USE_MODELADMIN = False

from .models import (
    Configuration,
    Række,
    Day,
    DayResponsibility,
    Week,
    Substitutliste,
    UserSubstitutAssignment,
    Afmeldingsliste,
    Tilmeldingsliste,
    TilmeldingslistePair,
    CustomUser,
)


if _USE_MODELADMIN:
    class ConfigurationAdmin(ModelAdmin):
        model = Configuration
        menu_label = "Tekster"
        menu_icon = "cog"
        list_display = ("name",)
        search_fields = ("name", "welcome_text")
else:
    class ConfigurationAdmin(ModelViewSet):
        model = Configuration
        icon = "cog"
        menu_label = "Tekster"
        form_fields = "__all__"
        list_display = ("name",)
        search_fields = ("name",)


if _USE_MODELADMIN:
    class RaekkeAdmin(ModelAdmin):
        model = Række
        menu_label = "Rækker"
        menu_icon = "group"
        list_display = ("name",)
        search_fields = ("name",)
else:
    class RaekkeAdmin(ModelViewSet):
        model = Række
        icon = "group"
        menu_label = "Rækker"
        form_fields = "__all__"
        list_display = ("name",)
        search_fields = ("name",)


if _USE_MODELADMIN:
    class DayAdmin(ModelAdmin):
        model = Day
        menu_label = "Days"
        menu_icon = "date"
        list_display = ("name",)
        search_fields = ("name",)
else:
    class DayAdmin(ModelViewSet):
        model = Day
        icon = "date"
        menu_label = "Days"
        form_fields = "__all__"
        list_display = ("name",)
        search_fields = ("name",)


if _USE_MODELADMIN:
    class DayResponsibilityAdmin(ModelAdmin):
        model = DayResponsibility
        menu_label = "Day Responsibilities"
        menu_icon = "user"
        list_display = ("day", "coordinator")
        list_filter = ("day",)
        search_fields = ("coordinator__username", "coordinator__email")
else:
    class DayResponsibilityAdmin(ModelViewSet):
        model = DayResponsibility
        icon = "user"
        menu_label = "Day Responsibilities"
        form_fields = "__all__"
        list_display = ("day", "coordinator")
        list_filter = ("day",)
        search_fields = ("coordinator__username", "coordinator__email")


if _USE_MODELADMIN:
    class WeekAdmin(ModelAdmin):
        model = Week
        menu_label = "Weeks"
        menu_icon = "date"
        list_display = ("name",)
        search_fields = ("name",)
else:
    class WeekAdmin(ModelViewSet):
        model = Week
        icon = "date"
        menu_label = "Weeks"
        form_fields = "__all__"
        list_display = ("name",)
        search_fields = ("name",)


if _USE_MODELADMIN:
    class SubstitutlisteAdmin(ModelAdmin):
        model = Substitutliste
        menu_label = "Substitutlister"
        menu_icon = "list-ul"
        list_display = ("name", "week", "day", "deadline")
        list_filter = ("week", "day")
        search_fields = ("name",)
else:
    class SubstitutlisteAdmin(ModelViewSet):
        model = Substitutliste
        icon = "list-ul"
        menu_label = "Substitutlister"
        form_fields = "__all__"
        list_display = ("name", "week", "day", "deadline")
        list_filter = ("week", "day")
        search_fields = ("name",)


if _USE_MODELADMIN:
    class UserSubstitutAssignmentAdmin(ModelAdmin):
        model = UserSubstitutAssignment
        menu_label = "Assignments"
        menu_icon = "user"
        list_display = ("user", "substitutliste", "status")
        list_filter = ("status",)
        search_fields = ("user__username", "user__email")
else:
    class UserSubstitutAssignmentAdmin(ModelViewSet):
        model = UserSubstitutAssignment
        icon = "user"
        menu_label = "Assignments"
        form_fields = "__all__"
        list_display = ("user", "substitutliste", "status")
        list_filter = ("status",)
        search_fields = ("user__username", "user__email")


if _USE_MODELADMIN:
    class AfmeldingslisteAdmin(ModelAdmin):
        model = Afmeldingsliste
        menu_label = "Afmeldingslister"
        menu_icon = "list-ul"
        list_display = ("name", "day", "deadline")
        list_filter = ("day",)
        search_fields = ("name",)
else:
    class AfmeldingslisteAdmin(ModelViewSet):
        model = Afmeldingsliste
        icon = "list-ul"
        menu_label = "Afmeldingslister"
        form_fields = "__all__"
        list_display = ("name", "day", "deadline")
        list_filter = ("day",)
        search_fields = ("name",)


if _USE_MODELADMIN:
    class TilmeldingslisteAdmin(ModelAdmin):
        model = Tilmeldingsliste
        menu_label = "Tilmeldingslister"
        menu_icon = "list-ul"
        list_display = ("name", "day", "deadline", "antal_par", "responsible_person")
        list_filter = ("day",)
        search_fields = ("name", "responsible_person__username", "responsible_person__email")
else:
    class TilmeldingslisteAdmin(ModelViewSet):
        model = Tilmeldingsliste
        icon = "list-ul"
        menu_label = "Tilmeldingslister"
        form_fields = "__all__"
        list_display = ("name", "day", "deadline", "antal_par", "responsible_person")
        list_filter = ("day",)
        search_fields = ("name", "responsible_person__username", "responsible_person__email")


if _USE_MODELADMIN:
    class TilmeldingslistePairAdmin(ModelAdmin):
        model = TilmeldingslistePair
        menu_label = "Tilmeldingsliste Par"
        menu_icon = "user"
        list_display = ("tilmeldingsliste", "navn", "makker", "på_venteliste", "is_single", "parnummer")
        list_filter = ("på_venteliste", "is_single")
        search_fields = ("navn", "makker", "email", "telefonnummer")
else:
    class TilmeldingslistePairAdmin(ModelViewSet):
        model = TilmeldingslistePair
        icon = "user"
        menu_label = "Tilmeldingsliste Par"
        form_fields = "__all__"
        list_display = ("tilmeldingsliste", "navn", "makker", "på_venteliste", "is_single", "parnummer")
        list_filter = ("på_venteliste", "is_single")
        search_fields = ("navn", "makker", "email", "telefonnummer")


if _USE_MODELADMIN:
    class CustomUserAdmin(ModelAdmin):
        model = CustomUser
        menu_label = "Substitutter"
        menu_icon = "user"
        list_display = ("username", "række", "phone_number", "email")
        search_fields = ("username", "email", "phone_number")
        list_filter = ("række",)
else:
    class CustomUserAdmin(ModelViewSet):
        model = CustomUser
        icon = "user"
        menu_label = "Substitutter"
        form_fields = "__all__"
        list_display = ("username", "række", "phone_number", "email")
        search_fields = ("username", "email", "phone_number")
        list_filter = ("række",)


if _USE_MODELADMIN:
    class ClubManagementGroup(ModelAdminGroup):
        menu_label = "Club Management"
        menu_icon = "folder-open-inverse"
        items = (
            ConfigurationAdmin,
            RaekkeAdmin,
            DayAdmin,
            DayResponsibilityAdmin,
            WeekAdmin,
            SubstitutlisteAdmin,
            UserSubstitutAssignmentAdmin,
            AfmeldingslisteAdmin,
            TilmeldingslisteAdmin,
            TilmeldingslistePairAdmin,
            CustomUserAdmin,
        )

    modeladmin_register(ClubManagementGroup)
else:
    class ClubManagementGroup(ViewSetGroup):
        menu_label = "Club Management"
        icon = "folder-open-inverse"
        items = [
            ConfigurationAdmin,
            RaekkeAdmin,
            DayAdmin,
            DayResponsibilityAdmin,
            WeekAdmin,
            SubstitutlisteAdmin,
            UserSubstitutAssignmentAdmin,
            AfmeldingslisteAdmin,
            TilmeldingslisteAdmin,
            TilmeldingslistePairAdmin,
            CustomUserAdmin,
        ]

    @hooks.register('register_admin_viewset')
    def register_club_management_group():
        return ClubManagementGroup()
