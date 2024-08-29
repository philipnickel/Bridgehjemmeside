from bootstrap_datepicker_plus.widgets import DatePickerInput
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


class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed


class SubstitutlisteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Substitutliste
        fields = "__all__"
        widgets = {
            'week': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean_day(self):
        day = self.cleaned_data['day']
        danish_weekdays = {
            'Monday': 'Mandag',
            'Tuesday': 'Tirsdag',
            'Wednesday': 'Onsdag',
            'Thursday': 'Torsdag',
            'Friday': 'Fredag',
            'Saturday': 'Lørdag',
            'Sunday': 'Søndag'
        }
        weekday = day.strftime("%A")
        return danish_weekdays.get(weekday, weekday)
