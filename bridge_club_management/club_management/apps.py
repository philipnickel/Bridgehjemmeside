from django.apps import AppConfig
import os

class ClubManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'club_management'
    path = os.path.dirname(os.path.abspath(__file__))

    def ready(self):
        import club_management.signals
