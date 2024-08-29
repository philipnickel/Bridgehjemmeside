from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.db.models import Q
from django.forms import DateInput

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
    day = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d']
    )
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Substitutliste
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['day'].initial = self.instance.day
            if self.instance.deadline:
                self.fields['deadline'].initial = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        deadline = cleaned_data.get('deadline')

        if day and deadline and day < deadline.date():
            raise forms.ValidationError(_("The deadline cannot be after the day."))

        return cleaned_data