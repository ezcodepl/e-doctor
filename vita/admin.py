from django.contrib import admin
from .models import News, Cel_wizyt, Patient

# Register your models here.
admin.site.register(News)
admin.site.register(Cel_wizyt)
admin.site.register(Patient)