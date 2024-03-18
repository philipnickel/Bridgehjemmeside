from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    DAYS_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    days_available = forms.MultipleChoiceField(choices=DAYS_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)


    class Meta:
        model = CustomUser
        fields = ['user_type', 'phone_number', 'email', 'row', 'days_available']
