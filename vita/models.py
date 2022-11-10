from django.db import models
from django import forms
from django.utils import timezone



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
    status = models.IntegerField(max_length=3)
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.temat