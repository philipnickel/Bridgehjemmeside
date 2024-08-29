from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.db.models import Q

from .models import CustomUser, Day, Substitutliste, Række, UnavailableDay


class CustomUserForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")  # Include the username field
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.exclude(name__in=["Saturday", "Sunday"]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Days Available",
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


class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed


class SubstitutlisteForm(forms.ModelForm):

    class Meta:
        model = Substitutliste
        fields = "__all__"
