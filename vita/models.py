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
	id_patient = models.IntegerField()
	city = models.CharField(max_length=255)
	post_code = models.CharField(max_length=6)
	street = models.CharField(max_length=255)
	phone = models.IntegerField()
	pesel = models.CharField(max_length=11)
	data_of_birth = models.DateField()
	insurance_number = models.CharField(max_length=255)
	notes = models.TextField()
	id_healt = models.IntegerField() #id kasa chorych
	id_status = models.IntegerField() #id statusu
	id_nfz = models.IntegerField() #id ubezpieczyciela
	patient_files = models.IntegerField()
	birthplace = models.CharField(max_length=255)
	gender = models.CharField(max_length=255)
	district = models.CharField(max_length=255) #powiat
	voivodeship = models.CharField(max_length=255) #wojewodztwo
	maintainer = models.CharField(max_length=255) #opiekun
	education = models.CharField(max_length=255)
	marital_status = models.CharField(max_length=255) #stan cywilny
	number_of_children = models.IntegerField()
	blood_group = models.CharField(max_length=50)
	visits_int = models.IntegerField()
	doctor_notes = models.TextField()
	sms = models.IntegerField()
	created_at = models.DateTimeField()
	updated_at = models.DateTimeField()

	def __str__(self):
		return self.user.username