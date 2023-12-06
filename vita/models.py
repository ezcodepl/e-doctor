import datetime

from django.db import models
from django import forms
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from tinymce import models as tinymce_models




# Create mode news
class News(models.Model):
    id_news = models.AutoField(primary_key=True, unique=True)
    temat = models.CharField(max_length=255)
    tresc = models.TextField()
    data_wpisu = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.temat


class Patient(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_patient = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=6, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    pesel = models.CharField(max_length=11, blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    insurance_number = models.CharField(max_length=255, blank=True, null=True)
    notes = tinymce_models.HTMLField(blank=True, null=True)
    id_healt = models.IntegerField(blank=True, null=True) #id kasa chorych
    id_status = models.IntegerField(blank=True, null=True) #id statusu
    id_nfz = models.IntegerField(blank=True, null=True) #id ubezpieczyciela
    patient_files = models.TextField(blank=True, null=True)
    birthplace = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True , null=True)
    district = models.CharField(max_length=255, blank=True, null=True) #powiat
    voivodeship = models.CharField(max_length=255, blank=True, null=True) #wojewodztwo
    maintainer = models.CharField(max_length=255, blank=True, null=True) #opiekun
    education = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=255 , blank=True, null=True) #stan cywilny
    number_of_children = models.IntegerField(default=0, blank=True, null=True)
    blood_group = models.CharField(max_length=50, blank=True, null=True)
    visits_int = models.IntegerField(blank=True, null=True)
    doctor_notes = tinymce_models.HTMLField(blank=True, null=True)
    sms = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} Pacjent'

class DoctorSchedule(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    date = models.DateField(blank=True, null=True)
    day_type = models.CharField(max_length=255, blank=True, null=True, default='Pracujący')
    work_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-21:00')
    scheme = models.CharField(max_length=255, blank=True, null=True, default='20')
    official_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-19:00')

    def __str__(self):
        return self.date

class FizSchedule(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    date = models.DateField(blank=True, null=True)
    day_type = models.CharField(max_length=255, blank=True, null=True, default='Pracujący')
    work_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-21:00')
    scheme = models.CharField(max_length=255, blank=True, null=True, default='20')
    official_hours = models.CharField(max_length=50, blank=True, null=True, default='8:00-19:00')

    def __str__(self):
        return self.date

class NoteTemplates(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    contents = models.TextField()
    status = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

def patient_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/patient_<id>/<filename>
    return 'patient_files/{0}/{1}'.format(instance.patient.id_patient, filename)
class FilesModel(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    files = models.FileField(upload_to=patient_directory_path)
    ext = models.CharField(max_length=255,null=True)
    upload_date = models.DateTimeField(default=timezone.now)

class Groups(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    status = models.IntegerField()
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.id

class PruposeVisit(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    purpose_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.cel

@receiver(post_migrate)
def dodaj_domyślne_rekordy(sender, **kwargs):
    if sender.name == "vita":  # Zastąp "twoja_aplikacja" nazwą Twojej aplikacji
        if not PruposeVisit.objects.exists():
            PruposeVisit.objects.create(purpose_name='badanie', description='badanie')
            PruposeVisit.objects.create(purpose_name='masaż', description='masaż')
            PruposeVisit.objects.create(purpose_name='masaż karnet', description='masaż karnet')
            PruposeVisit.objects.create(purpose_name='akupunktura', description='akupunktura')
            PruposeVisit.objects.create(purpose_name='przerwa', description='przerwa')

class StatusVisist(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    status_name = models.CharField()
    description = models.CharField()
    def __str__(self):
        return self.status_name

class Visits(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    date = models.DateField(null=True)
    time = models.CharField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prupose_visit = models.ForeignKey(PruposeVisit, on_delete=models.CASCADE)
    visit = models.CharField(null=True)
    status = models.CharField(null=True)
    pay = models.IntegerField(null=True)
    cancel = models.IntegerField(null=True)
    office = models.IntegerField(null=True, default='1')
    def __str__(self):
        return self.patient

class Visits_f(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    date = models.DateField(null=True)
    time = models.CharField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prupose_visit = models.ForeignKey(PruposeVisit, on_delete=models.CASCADE)
    visit = models.CharField(null=True)
    status = models.CharField(null=True)
    pay = models.IntegerField(null=True)
    cancel = models.IntegerField(null=True)
    office = models.IntegerField(null=True, default='1')
    def __str__(self):
        return self.patient

class ReversList(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    date = models.DateField(null=True)
    time = models.CharField(null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    phone = models.CharField()
    visist = models.CharField()
    status_name = models.CharField()
    description = models.CharField()
    call = models.IntegerField()
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.date

