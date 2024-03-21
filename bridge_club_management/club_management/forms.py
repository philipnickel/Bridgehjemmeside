from django import forms
from .models import CustomUser, Substitutliste, Day
from django.db.models import Q
from bootstrap_datepicker_plus.widgets import DatePickerInput



class CustomUserForm(forms.ModelForm):
    days_available = forms.ModelMultipleChoiceField(
        queryset=Day.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False, 
        label='Days Available'
    )

    days_unavailable = forms.DateField(
        widget=DatePickerInput(
            options={
                "format": "yyyy-mm-dd",
                "todayHighlight": True,
                "autoclose": True,
                "clearBtn": True,
                "multidate": True,  # Enable selecting multiple dates
            }
        ),
        required=False,
        label='Days Unavailable',
        help_text='Select the range of days when the user is unavailable.'
    )

    class Meta:
        model = CustomUser
        fields = ['user_type', 'phone_number', 'email', 'row', 'days_available','days_unavailable']


class CustomUserModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.username  # Customize the display label for each option if needed

class SubstitutlisteForm(forms.ModelForm):

    class Meta:
        model = Substitutliste
        fields = '__all__'


