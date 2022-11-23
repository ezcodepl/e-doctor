from django.contrib.auth.models import User
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from .models import Patient, DoctorSchedule
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV2Checkbox

# Create your forms here.

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, max_length=50, label='Imię', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, max_length=50, label='Nazwisko', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class PatientRegisterForm(forms.ModelForm):
    street = forms.CharField(required=True, label='Adres')
    post_code = forms.CharField(required=True, label='Kod pocztowy')
    city = forms.CharField(required=True, label='Miejscowość')
    phone = forms.CharField(required=True, label='Telefon')
    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    class Meta:
        model = Patient
        fields = ['street', 'city', 'post_code', 'phone']

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

class DoctorsSchedule(forms.ModelForm):
    work_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-21:00')
    official_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-19:00')
    class Meta:
        model = DoctorSchedule

        fields = ['date', 'day_type', 'work_hours', 'scheme', 'official_hours']