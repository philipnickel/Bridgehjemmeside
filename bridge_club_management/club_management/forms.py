from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput
from django import forms
from django.db.models import Q

from .models import CustomUser, Day, Substitutliste, Række, UnavailableDay


class CustomUserForm(forms.ModelForm):
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.exclude(name__in=["Lørdag", "Søndag"]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tilgængelige dage",
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "user_type",
            "phone_number",
            "email",
            "række",
            "days_available",
            "custom_note"
        ]


