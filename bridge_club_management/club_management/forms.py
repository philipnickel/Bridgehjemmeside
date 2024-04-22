from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.db.models import Q

from .models import CustomUser, Day, Substitutliste


class CustomUserForm(forms.ModelForm):
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Days Available",
    )

    class Meta:
        model = CustomUser
        fields = [
            "user_type",
            "phone_number",
            "email",
            "row",
            "days_available",
            "days_unavailable",
        ]


class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed


class SubstitutlisteForm(forms.ModelForm):

    class Meta:
        model = Substitutliste
        fields = "__all__"
