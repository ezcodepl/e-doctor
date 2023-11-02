from django.contrib import admin
from .models import News, Patient, NoteTemplates, FizSchedule, DoctorSchedule

# Register your models here.
admin.site.register(News)

admin.site.register(Patient)
admin.site.register(NoteTemplates)
