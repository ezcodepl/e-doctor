from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Patient, DoctorSchedule, FizSchedule, News, NoteTemplates, FilesModel, Visits


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

    def __init__(self, *args: object, **kwargs: object) -> object:
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] #'username',
class PatientUpdateForm(forms.ModelForm):
    street = forms.CharField(required=True, label='Adres')
    post_code = forms.CharField(required=True, label='Kod pocztowy')
    city = forms.CharField(required=True, label='Miejscowość')
    phone = forms.CharField(required=True, label='Telefon')
    sms = forms.BooleanField(required=False,label='Powiadomienie SMS')
    pesel = forms.CharField(max_length=11)
    date_of_birth = forms.DateField(widget = forms.SelectDateWidget, required=False)
    # insurance_number = forms.CharField(max_length=255, blank=True, null=True)
    notes = forms.CharField(required=False)
    # id_healt = forms.IntegerField(blank=True, null=True)  # id kasa chorych
    # id_status = forms.IntegerField(blank=True, null=True)  # id statusu
    # id_nfz = forms.IntegerField(blank=True, null=True)  # id ubezpieczyciela
    #patient_files = forms.TextField(blank=True, null=True)
    birthplace = forms.CharField(required=False)
    gender = forms.CharField()
    #district = forms.CharField(max_length=255, blank=True, null=True)  # powiat
    #voivodeship = forms.CharField(max_length=255, blank=True, null=True)  # wojewodztwo
    #maintainer = forms.CharField(max_length=255, blank=True, null=True)  # opiekun
    education = forms.CharField(required=False)
    marital_status = forms.CharField(required=False)  # stan cywilny
    number_of_children = forms.IntegerField(required=False)
    blood_group = forms.CharField(required=False)
    #visits_int = forms.IntegerField(blank=True, null=True)
    doctor_notes = forms.CharField(required=False)
    # sms = forms.IntegerField(blank=True, null=True)
    class Meta:
        model = Patient
        fields = ['city','street','post_code','phone','pesel','sms']

class PatientUpdateExtendForm(forms.ModelForm):

    street = forms.CharField(required=True, label='Adres')
    post_code = forms.CharField(required=True, label='Kod pocztowy')
    city = forms.CharField(required=True, label='Miejscowość')
    phone = forms.CharField(required=True, label='Telefon')
    sms = forms.BooleanField(required=False, label='Powiadomienie SMS')
    pesel = forms.CharField(label='PESEL')
    class Meta:
        model = Patient
        fields = ['city', 'street', 'post_code', 'phone', 'pesel', 'sms']

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
    files = forms.FileField(label='', widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))
    class Meta:
        model = FilesModel
        fields = ['files']


class VisitForm(forms.ModelForm):
    date_visit = forms.DateField(label='Data wpisu:', widget=DateInput)
    class Meta:
        model = Visits
        fields = ['date']

class PersonForm(forms.Form):
    person = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={"autocomplete": "on"}),
        limit_choices_to=Q(first_name__startswith="A"),
    )