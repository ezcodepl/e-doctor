from django.contrib.auth.models import User
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from .models import Patient
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit


# Create your forms here.

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
class PatientUpdateForm(forms.ModelForm):
    street = forms.CharField(required=True, label='Adres')
    post_code = forms.CharField(required=True, label='Kod pocztowy')
    city = forms.CharField(required=True, label='Miejscowość')
    phone = forms.CharField(required=True, label='Telefon')
    sms = forms.BooleanField(required=False,label='Powiadomienie SMS')
    class Meta:
        model = Patient

        fields = ['city','street','post_code','phone','pesel','sms']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.layout = Layout(
    #         Fieldset(
    #             'first arg is the legend of the fieldset',
    #             'like_website',
    #             'favorite_number',
    #             'favorite_color',
    #             'favorite_food',
    #             'notes'
    #         ),
    #         Submit('submit', 'Submit', css_class='btn btn-danger'),
    #     )

