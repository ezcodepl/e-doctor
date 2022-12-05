from django.urls import path
from . import views
from datetime import date, datetime


urlpatterns = [

    path('', views.home, name='home'),
    path('panel/terminarz', views.terminarz, name='terminarz'),
    path('panel/terminarz_f', views.terminarz_fizykoterapii, name='terminarz_fizykoterapii'),
    path('panel/patients', views.patients_list, name='patients_list'),
    path('panel/new_patient', views.new_patient, name='new_patient'),
    path('panel/create_news', views.create_news, name='create_news'),
    path('panel/news_list', views.news_list, name='news_list'),
    path('panel/create_templates', views.create_templates, name='create_templates'),
    path('panel/templates_list', views.templates_list, name='templates_list'),
    path(f'panel', views.panel, name='panel'),
    path('news', views.news, name='news'),
    path('test', views.test, name='test'),
    path('laseroterapia', views.laseroterapia, name='laseroterapia'),
    path('', views.krioterapia, name='krioterapia'),
    path('news', views.elektroterapia, name='elektroterapia'),

    path('login', views.login_request, name='login_request'),
    path('logout', views.logout_request, name='logout_request'),
    path("register", views.register_user, name="register_user"),

    path("patient/profile", views.profile, name="profile"),
    path('patient/new-visit', views.new_visit, name='new_visit'),
    path('patient/appointments', views.appointments, name='appointments'),
    path('patient/history', views.history, name='history'),
]