"""pyvit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, register_converter
from datetime import date, datetime
from vita.views import panel, delete_news, update_news, edit_news, edit_templates, update_templates, delete_templates, \
    patients_files, delete_patient_files, update_patient, create_visit, pause_visit, doctor_visits, reserve_list, doctors_weekly_plan, fiz_weekly_plan
from django.contrib.auth import views as auth_views


class DateConverter:
    regex = r"\d{4}-\d{1,2}-\d{1,2}"
    format = "%Y-%m-%d"

    def to_python(self, value: str) -> date:
        return datetime.strptime(value, self.format).date()

    def to_url(self, value: date) -> str:
        return value.strftime(self.format)


register_converter(DateConverter, "date")

date = date.today()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vita.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('panel/<date:date>/', panel, name="panel"),
    path('panel/delete_news/<int:pk>', delete_news, name="delete_news"),
    path('panel/edit_news/<int:pk>', edit_news, name="edit_news"),
    path('panel/update_news/<int:pk>', update_news, name="update_news"),
    path('panel/edit_templates/<int:pk>', edit_templates, name="edit_templates"),
    path('panel/update_templates/<int:pk>', update_templates, name="update_templates"),
    path('panel/delete_templates/<int:pk>', delete_templates, name="delete_templates"),
    path('panel/patients/<int:pk>', patients_files, name="patients_files"),
    path('panel/patients/<int:pk>/delete', delete_patient_files, name="delete_patient_files"),
    path('panel/patients/<int:pk>/updates', update_patient, name="update_patient"),

    path('patient/doctor_visits/', doctor_visits, name='doctor_visits'),
    path('patient/doctor_visits/<int:offset>/', doctor_visits, name='doctor_visits'),
    path('panel/doctors_weekly_plan/<int:offset>/', doctors_weekly_plan, name='doctors_weekly_plan'),
    path('panel/fiz_weekly_plan/<int:offset>/', fiz_weekly_plan, name='fiz_weekly_plan'),





    # path('create_visit/date=<str:get_date>&time=<int:hour>', create_visit, name='create_visit'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)