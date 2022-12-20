from django.contrib.auth.models import User
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from .models import Patient, DoctorSchedule, FizSchedule, News, NoteTemplates, FilesModel
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

class RegisterUserStForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}),)
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

class DoctorsScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ['date', 'day_type', 'work_hours', 'official_hours','scheme']

class FizScheduleForm(forms.ModelForm):
    class Meta:
        model = FizSchedule
        fields = ['date', 'day_type', 'work_hours', 'official_hours','scheme']

class DateInput(forms.DateInput):
    input_type = 'date'
class NewsForm(forms.ModelForm):
    status_check = [
        ('1', 'Aktywny'),
        ('0', 'Nieaktywny')
    ]
    data_wpisu = forms.DateField(label='Data wpisu:', widget=DateInput)
    status = forms.CharField(label='Wybierz status dostępności:', widget=forms.RadioSelect(choices=status_check))
    class Meta:
        model = News
        fields = ['temat', 'tresc', 'data_wpisu', 'status']

class NoteTemplatesForm(forms.ModelForm):
    status_check = [
        ('1', 'Aktywna'),
        ('0', 'Nieaktywna')
    ]
    name = forms.CharField(label='Tytuł notatki')
    contents = forms.CharField(label='Treść notatki', help_text="", widget=forms.Textarea())
    status = forms.CharField(label='Wybierz status dostępności:', widget=forms.RadioSelect(choices=status_check))
    class Meta:
        model = NoteTemplates
        fields = ['name', 'contents', 'status']

class uploadFilesForm(forms.ModelForm):
    files = forms.FileField(label='', widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = FilesModel
        fields = ['files']
