from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.db.models import Q

from .models import CustomUser, Day, Substitutliste, Række, UnavailableDay


class CustomUserForm(forms.ModelForm):
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.exclude(name__in=["Saturday", "Sunday"]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Days Available",
    )
    unavailable_days = forms.ModelMultipleChoiceField(
        queryset=UnavailableDay.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            "user_type",
            "phone_number",
            "email",
            "række",
            "days_available",
            "unavailable_days",
            "custom_note"
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # for an existing instance, populate the unavailable days
            self.fields['unavailable_days'].initial = self.instance.unavailable_days.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # save the unavailable days
            if self.cleaned_data['unavailable_days']:
                instance.unavailable_days.set(self.cleaned_data['unavailable_days'])
            else:
                instance.unavailable_days.clear()
        return instance

class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed


class SubstitutlisteForm(forms.ModelForm):

    class Meta:
        model = Substitutliste
        fields = "__all__"
