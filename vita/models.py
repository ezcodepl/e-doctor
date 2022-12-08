import datetime

from django.db import models
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User



# Create your models here.
class Cel_wizyt(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    cel = models.CharField(max_length=100)
    id_lekarza = models.IntegerField()
    opis = models.TextField()

    def __str__(self):
        return self.cel

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
    data_of_birth = models.DateField(blank=True, null=True)
    insurance_number = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
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
    number_of_children = models.IntegerField(blank=True, null=True)
    blood_group = models.CharField(max_length=50, blank=True, null=True)
    visits_int = models.IntegerField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
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

