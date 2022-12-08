from django.contrib import admin
from .models import News, Cel_wizyt, Patient, NoteTemplates, FizSchedule, DoctorSchedule

# Register your models here.
admin.site.register(News)
admin.site.register(Cel_wizyt)
admin.site.register(Patient)
admin.site.register(NoteTemplates)
