from django import forms
from .models import CustomUser, Substitutliste, Day
from django.db.models import Q


class CustomUserForm(forms.ModelForm):
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['user_type', 'phone_number', 'email', 'row', 'days_available']


class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed

class SubstitutlisteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the choices for substitutes based on days_available
        if self.instance.day:
            day_of_week = self.instance.day.strftime('%A')
            available_substitutes = CustomUser.objects.filter(
                Q(days_available__name=day_of_week) | Q(days_available__name='Any')
            )
            self.fields['substitutes'].queryset = available_substitutes

    class Meta:
        model = Substitutliste
        fields = '__all__'


